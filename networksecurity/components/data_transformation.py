import sys
import os
import numpy as np
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline
from networksecurity.constant.training_pipeline import (
    TARGET_COLUMN,
    DATA_TRANSFORMATION_IMPUTER_PARAMS
)
from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact, 
    DataValidationArtifact
)
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.utils.main_utils.utils import (
    save_numpy_array_data,
    save_object
)

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

class DataTransformation:
    def __init__(
            self, 
            data_validation_artifact: DataValidationArtifact,
            data_transformation_config: DataTransformationConfig
    ):
        try: 
            self.data_validation_artifact: DataValidationArtifact = data_validation_artifact
            self.data_transformation_config: DataTransformationConfig = data_transformation_config
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    @staticmethod
    def read_data(file_path) -> pd.DataFrame: 
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def get_data_transformer_object(cls) -> Pipeline:
        """
        Initialize a KNN imputer object with the parameters specified in training_pipeline folder's
        __init__.py file and return a Pipeline object with the KNNImputer object as the 
        first_step

        Args:
            cls: DataTransformation

        Returns:
            Pipeline: _description_
        """
        logging.info(
            "Entered get_data_transformer_object method of DataTransformation class"
        )

        try:
            imputer: KNNImputer = KNNImputer(**DATA_TRANSFORMATION_IMPUTER_PARAMS)
            logging.info(
                f"initialize KNNImputer with {DATA_TRANSFORMATION_IMPUTER_PARAMS}"
            )

            processor: Pipeline = Pipeline(
                [
                    ("imputer", imputer)
                ]
            )
            return processor
        except Exception as e:
            raise NetworkSecurityException(e, sys)


    def initiate_data_transformation(self) -> DataTransformationArtifact:
        """Creates data transformation artifacts

        Raises:
            NetworkSecurityException: Custom Exception Handler

        Returns:
            DataTransformationArtifact: Class present in training_pipeline dir's __init__.py
        """
        logging.info("Entered initiate_data_transformation method of DataTransformation Class")
        try:
            logging.info("Starting Data Transformation")
            train_df = DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df = DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)

            # Train dataframe
            input_features_train_df = train_df.drop(columns=[TARGET_COLUMN])
            target_feature_train_df = train_df[TARGET_COLUMN]
            target_feature_train_df = target_feature_train_df.replace(-1, 0)

            # Test dataframe
            input_features_test_df = test_df.drop(columns=[TARGET_COLUMN])
            target_feature_test_df = test_df[TARGET_COLUMN]
            target_feature_test_df = target_feature_test_df.replace(-1, 0)

            # Processing train and test dataframes
            preprocessor = self.get_data_transformer_object()
            preprocessor_object = preprocessor.fit(input_features_train_df)

            transformed_input_train_feature = preprocessor_object.transform(input_features_train_df)
            transformed_input_test_feature = preprocessor_object.transform(input_features_test_df)

            train_arr = np.c_[
                transformed_input_train_feature, 
                np.array(target_feature_train_df)
            ]

            test_arr = np.c_[
                transformed_input_test_feature, 
                np.array(target_feature_test_df)
            ]

            # Save numpy array data
            save_numpy_array_data(
                file_path=self.data_transformation_config.transformed_train_file_path,
                array=train_arr
            )
            save_numpy_array_data(
                self.data_transformation_config.transformed_test_file_path,
                array=test_arr
            )
            save_object(
                self.data_transformation_config.transformed_object_file_path,
                preprocessor_object                
            )

            # Prepare artifacts
            data_transformation_artifact = DataTransformationArtifact(
                transformed_object_file_path=self.data_transformation_config.transformed_object_file_path,
                transformed_train_file_path=self.data_transformation_config.transformed_train_file_path,
                transformed_test_file_path=self.data_transformation_config.transformed_test_file_path,
            )

            return data_transformation_artifact



        except Exception as e:
            raise NetworkSecurityException(e, sys)


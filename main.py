import sys
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.entity.artifact_entity import DataIngestionArtifact

from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig
)


from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

if __name__ == "__main__":
    try:
        training_pipeline = TrainingPipelineConfig()
        data_ingestion_config = DataIngestionConfig(
            training_pipeline_config=training_pipeline
        )
        data_ingestion = DataIngestion(
            data_ingestion_config=data_ingestion_config
        )
        logging.info("Initiate Data Ingestion")
        data_ingestion_artifact = data_ingestion.initiate_data_ingestion()
        logging.info("Datas Ingestion successful !!!")
        
        logging.info("Initiate Data Validation")
        data_validation_config = DataValidationConfig(
            training_pipeline_config=training_pipeline
        )

        data_validation = DataValidation(
            data_ingestion_artifact=data_ingestion_artifact,
            data_validation_config=data_validation_config
        )
        data_validation_artifact = data_validation.initiate_data_validation()
        logging.info("Data Validation successful !!!")

        data_transformation_config = DataTransformationConfig(training_pipeline)
        data_transformation = DataTransformation(
            data_transformation_config=data_transformation_config,
            data_validation_artifact=data_validation_artifact
        )

        logging.info("Initiate Data Transformation")
        data_transformation_artifact = data_transformation.initiate_data_transformation()
        logging.info("Data Transformation successful !!!")

        logging.info("Model training started")
        model_trainer_config = ModelTrainerConfig(training_pipeline_config=training_pipeline)
        model_trainer = ModelTrainer(
            model_trainer_config=model_trainer_config, 
            data_transformation_artifact=data_transformation_artifact
        )
        model_trainer_artifact = model_trainer.initiate_model_trainer()
        logging.info("Model training artifact artifact created")


    except Exception as e:
        raise NetworkSecurityException(e, sys)
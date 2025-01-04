import os
import os.path as op
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact,
    ModelTrainerArtifact
)
from networksecurity.entity.config_entity import ModelTrainerConfig

from networksecurity.utils.main_utils.utils import (
    save_object,
    load_object,
    load_numpy_array_data,
    evaluate_models
)

from networksecurity.utils.ml_utils.model.estimator import NetworkModel
from networksecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier
)
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV


class ModelTrainer:
    def __init__(
            self, 
            model_trainer_config: ModelTrainerConfig,
            data_transformation_artifact: DataTransformationArtifact
    ):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
        
    def train_model(self, X_train, y_train, X_test, y_test):
        models = {
            "Random Forest": RandomForestClassifier(verbose=1),
            "Decision Tree": DecisionTreeClassifier(),
            "Gradient Boosting": GradientBoostingClassifier(verbose=1),
            "Logistic Regression": LogisticRegression(verbose=1),
            "AdaBoost": AdaBoostClassifier()
        }

        params = {
            "Decision Tree": {
                "criterion": ["gini", "entropy", "log_loss"],
                # "splitter": ["best", "random"],
                "max_features": ["sqrt", "log2"]
            },
            "Random Forest": {
                # "criterion": ["gini", "entropy", "log_loss"],
                "max_features": ["sqrt", "log2"],
                "n_estimators": [8, 16, 32, 128, 256]
            },
            "Gradient Boosting": {
                "loss": ["log_loss", "exponential"],
                "learning_rate": [0.001, 0.01, 0.05, 0.1],
                "subsample":[0.6, 0.7, 0.75, 0.85, 0.9],
                "n_estimators": [8, 16, 32, 64, 128, 256]
            },
            "Logistic Regression":{},
            "AdaBoost": {
                "learning_rate": [0.001, 0.01, 0.1],
                "n_estimators": [8, 16, 32, 64, 128, 256]
            }

        }

        model_report: dict = evaluate_models(
            X_train=X_train, 
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            models=models,
            params=params
        )

        # Get best model score from dict
        best_model_score = max(sorted(model_report.values()))

        # Get best model name from dict
        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]

        best_model = models[best_model_name]
        y_train_pred = best_model.predict(X_train)
        classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)
        
        # Create a function to track run on MLFLOW

        y_test_pred = best_model.predict(X_test)
        classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)

        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)

        model_dir_path = op.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path, exist_ok=True)

        network_model = NetworkModel(preprocessor=preprocessor, model=best_model)

        save_object(
            file_path=self.model_trainer_config.trained_model_file_path,
            obj=network_model
        )

        # Model trainer artifact
        model_trainer_artifact = ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
            train_metric_artifact=classification_train_metric,
            test_metric_artifact=classification_test_metric
        )

        logging.info(f"Model trainer artifact: {model_trainer_artifact}")

        return model_trainer_artifact

        
    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            train_file_path: str = self.data_transformation_artifact.transformed_train_file_path
            test_file_path: str = self.data_transformation_artifact.transformed_test_file_path

            # Load train and test array
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            X_train, y_train, X_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1]
            )

            model = self.train_model(X_train, y_train, X_test, y_test)
        except Exception as e:
            raise NetworkSecurityException(e, sys)
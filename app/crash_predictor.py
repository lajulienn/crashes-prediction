from catboost import CatBoostClassifier

from . import config


class CrashPredictor:
    def __init__(self, model_filename: str=config.MODEL_FILENAME):
        clf = CatBoostClassifier()
        clf.load_model(model_filename, format=config.DUMP_FORMAT)
        self.model = clf

    def predict(self, features: list) -> float:
        proba = self.model.predict_proba(features)

        return proba[1]

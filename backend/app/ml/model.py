import pickle
import os
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from app.core.config import settings
class PurchasePredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_cols = []
        self.is_trained = False
    def train(self, df: pd.DataFrame, feature_cols: list, target_col: str = "purchased"):
        if df.empty or len(df) < 10:
            self.is_trained = False
            return
        X = df[feature_cols].fillna(0).values
        y = df[target_col].values if target_col in df.columns else np.zeros(len(df))
        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)
        self.model = LogisticRegression(class_weight="balanced", max_iter=1000, random_state=42, C=0.5)
        self.model.fit(X_scaled, y)
        self.feature_cols = feature_cols
        self.is_trained = True
    def predict_proba(self, features: dict) -> float:
        if not self.is_trained or not self.model:
            return np.random.uniform(0.3, 0.7)
        try:
            vec = np.array([[features.get(f, 0) for f in self.feature_cols]])
            if self.scaler:
                vec = self.scaler.transform(vec)
            prob = self.model.predict_proba(vec)[0][1]
            return float(prob)
        except Exception:
            return np.random.uniform(0.3, 0.7)
    def get_feature_importance(self) -> dict:
        if not self.is_trained or not self.model:
            return {}
        coefs = self.model.coef_[0]
        return {f: float(c) for f, c in zip(self.feature_cols, coefs)}
    def save(self, path: str = None):
        path = path or settings.MODEL_PATH
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            pickle.dump({"model": self.model, "scaler": self.scaler, "feature_cols": self.feature_cols}, f)
    def load(self, path: str = None):
        path = path or settings.MODEL_PATH
        if os.path.exists(path):
            with open(path, "rb") as f:
                data = pickle.load(f)
            self.model = data["model"]
            self.scaler = data["scaler"]
            self.feature_cols = data["feature_cols"]
            self.is_trained = True
        else:
            self.is_trained = False
model_predictor = PurchasePredictor()
model_predictor.load()
def get_model() -> PurchasePredictor:
    return model_predictor
def train_model(df: pd.DataFrame, feature_cols: list, y: np.ndarray = None):
    predictor = PurchasePredictor()
    predictor.train(df, feature_cols)
    predictor.save()
    return predictor

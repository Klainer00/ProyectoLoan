import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

class FeatureEngineering(BaseEstimator, TransformerMixin):
    def __init__(
        self,
        date_col=None,
        lat_cliente=None,
        lon_cliente=None,
        lat_comercio=None,
        lon_comercio=None,
        drop_originals=True
    ):
        self.date_col = date_col
        self.lat_cliente = lat_cliente
        self.lon_cliente = lon_cliente
        self.lat_comercio = lat_comercio
        self.lon_comercio = lon_comercio
        self.drop_originals = drop_originals

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        X = X.copy()
        if self.date_col and self.date_col in X.columns:
            X[self.date_col] = pd.to_datetime(X[self.date_col], errors="coerce")
            X["hora"] = X[self.date_col].dt.hour
            X["dia"] = X[self.date_col].dt.day
            X["mes"] = X[self.date_col].dt.month
            X["dia_semana"] = X[self.date_col].dt.dayofweek
            X["es_fin_semana"] = X["dia_semana"].isin([5, 6]).astype(int)
            X["hora_sen"] = np.sin(2 * np.pi * X["hora"] / 24)
            X["hora_cos"] = np.cos(2 * np.pi * X["hora"] / 24)
            X["mes_sin"] = np.sin(2 * np.pi * X["mes"] / 12)
            X["mes_cos"] = np.cos(2 * np.pi * X["mes"] / 12)
            if self.drop_originals:
                X = X.drop(columns=[self.date_col, "hora", "mes"], errors="ignore")

        if all([self.lat_cliente, self.lon_cliente, self.lat_comercio, self.lon_comercio]):
            if all(col in X.columns for col in [self.lat_cliente, self.lon_cliente, self.lat_comercio, self.lon_comercio]):
                lat1 = np.radians(X[self.lat_cliente])
                lon1 = np.radians(X[self.lon_cliente])
                lat2 = np.radians(X[self.lat_comercio])
                lon2 = np.radians(X[self.lon_comercio])
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = np.sin(dlat / 2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2)**2
                c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
                X["distancia_km"] = 6371.0 * c
                if self.drop_originals:
                    X = X.drop(columns=[self.lat_cliente, self.lon_cliente, self.lat_comercio, self.lon_comercio], errors="ignore")
        return X
import pandas as pd
import numpy as np

class QualityCheck:
    def __init__(self, data: pd.DataFrame, exclude_inconsistencies: list = None):
        self.data = data
        if exclude_inconsistencies is None:
            self.exclude_inconsistencies = []
        else:
            self.exclude_inconsistencies = exclude_inconsistencies

    def has_nulls(self) -> bool:
        return bool(self.data.isnull().values.any())

    def has_duplicates(self) -> bool:
        return bool(self.data.duplicated().any())

    def has_outliers(self) -> bool:
        numeric_cols = self.data.select_dtypes(include=["number"])
        for col in numeric_cols.columns:
            Q1 = numeric_cols[col].quantile(0.25)
            Q3 = numeric_cols[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - 1.5 * IQR
            upper = Q3 + 1.5 * IQR
            if ((numeric_cols[col] < lower) | (numeric_cols[col] > upper)).any():
                return True
        return False

    def has_negative_values(self) -> bool:
        numeric_cols = self.data.select_dtypes(include=["number"])
        for col in numeric_cols.columns:
            if col not in self.exclude_inconsistencies:
                if (numeric_cols[col] < 0).any():
                    return True
        return False

    def has_categorical_inconsistencies(self) -> bool:
        cat_cols = self.data.select_dtypes(include=["object", "category"])
        for col in cat_cols.columns:
            values = cat_cols[col].dropna().astype(str)
            normalized = values.str.strip().str.lower()
            if len(values.unique()) != len(normalized.unique()):
                return True
        return False

    def has_inconsistencies(self) -> bool:
        return self.has_negative_values() or self.has_categorical_inconsistencies()

    def quality_score_weighted(self) -> float:
        weights = {
            "nulos/faltantes": 0.3,
            "duplicados": 0.2,
            "outliers": 0.2,
            "inconsistencias": 0.3
        }
        checks = {
            "nulos/faltantes": self.has_nulls(),
            "duplicados": self.has_duplicates(),
            "outliers": self.has_outliers(),
            "inconsistencias": self.has_inconsistencies()
        }
        score = 1.0
        for key, has_issue in checks.items():
            if has_issue:
                score -= weights[key]
        return max(0.0, score)

    def quality_report(self) -> dict:
        return {
            "nulos/faltantes": bool(self.has_nulls()),
            "duplicados": bool(self.has_duplicates()),
            "outliers": self.has_outliers(),
            "inconsistencias": self.has_inconsistencies(),
            "quality_score": self.quality_score_weighted()
        }
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from feature_engineering import FeatureEngineering
from correlation_filter import CorrelationFilter
from winsorizer import Winsorizer


def tratar_duplicados(X: pd.DataFrame, drop=True):
    return X.drop_duplicates() if drop else X


data_for_preparation = pd.read_csv("data/02_loan_data.csv")
target = "loan_status"

X = data_for_preparation.drop(columns=[target], errors="ignore")
y = data_for_preparation[target]

num_cols = [
    "person_age",
    "person_income",
    "person_emp_exp",
    "loan_amnt",
    "loan_int_rate",
    "loan_percent_income",
    "cb_person_cred_hist_length",
    "credit_score"
]

cat_cols = [
    "person_gender",
    "person_education",
    "person_home_ownership",
    "loan_intent",
    "previous_loan_defaults_on_file"
]

preprocessor = ColumnTransformer(
    transformers=[
        ("num", Pipeline([
            ("winsorizer", Winsorizer()),
            ("imputer", SimpleImputer(strategy="mean")),
            ("scaler", StandardScaler())
        ]), num_cols),
        
        ("cat", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ]), cat_cols)
    ]
)

fe = FeatureEngineering()

pipeline_preparacion = Pipeline(steps=[
    ("duplicados", FunctionTransformer(tratar_duplicados, kw_args={"drop": True})),
    ("feature_engineering", fe),
    ("preprocesador", preprocessor),
    ("colinealidad", CorrelationFilter(threshold=0.9))
])

pipeline_preparacion.fit(X)

feature_names = pipeline_preparacion.named_steps["preprocesador"].get_feature_names_out()
pipeline_preparacion.named_steps["colinealidad"].set_feature_names(feature_names)

X_transformada = pipeline_preparacion.transform(X)
cols_finales = pipeline_preparacion.named_steps["colinealidad"].features_

print("\n=======================================================")
print(" REFINERÍA DE DATOS -- LOAN APPROVAL CLASSIFICATION")
print("=======================================================")
print(f"Dimensiones originales: {X.shape}")
print(f"Dimensiones tras pipeline: {X_transformada.shape}")
print(f"\nDesbalance de clases (target):")
print(data_for_preparation[target].value_counts())
print(f"\nColumnas finales resultantes ({len(cols_finales)}):")
print(cols_finales)
print("=======================================================\n")

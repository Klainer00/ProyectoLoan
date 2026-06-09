import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import FunctionTransformer
from sklearn.metrics import average_precision_score, roc_auc_score
from imblearn.pipeline import Pipeline as imbPipeline
from imblearn.over_sampling import SMOTE

# Importaciones de tu arquitectura local
from limpieza_transformacion import preprocessor, target
from feature_engineering import FeatureEngineering
from correlation_filter import CorrelationFilter

# Función simple para tratar duplicados en el pipeline
def tratar_duplicados(X):
    return X.drop_duplicates()

# 1. Cargar los datos limpios
data = pd.read_csv("data/03_loan_data_cleaned.csv")

X = data.drop(columns=[target], errors="ignore")
y = data[target]

# 2. División Train/Test (80% / 20%) con random_state=29 exigido
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=29, stratify=y
)

# Instanciar Ingeniería de Características
fe = FeatureEngineering()

# 3. Pipeline Integrado (Procesamiento + Balanceo SMOTE + Modelo)
pipeline_modelo = imbPipeline(steps=[
    ("duplicados", FunctionTransformer(tratar_duplicados, kw_args={"drop": True})),
    ("feature_engineering", fe),
    ("preprocesador", preprocessor), # Tu ColumnTransformer con Winsorizer y Encoders
    ("colinealidad", CorrelationFilter(threshold=0.9)),
    ("smote", SMOTE(random_state=29)),
    ("modelo", RandomForestClassifier(n_estimators=100, class_weight="balanced", random_state=29))
])
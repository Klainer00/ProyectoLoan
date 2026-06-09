import pandas as pd
import pickle
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier



# Crear carpetas de resultados y de modelos
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs("models", exist_ok=True)

# -------------------------------------------------
# Cargar datos
# -------------------------------------------------
data = pd.read_csv("data/03_loan_data_cleaned.csv")

# Variable objetivo
target = "loan_status"

X = data.drop(columns=[target])
y = data[target]

# Revisa la distribución de la variable objetivo
# En este caso se obtiene un gráfico de torta
counts = data[target].value_counts()
labels = [("Impago" if idx == 1 else "Solvente") for idx in counts.index]
counts.plot(kind='pie', autopct='%1.1f%%',
            labels=labels,
            figsize=(6, 6))
plt.title("Distribución de variable objetivo", fontsize=14, fontweight="bold")
plt.tight_layout()
plt.savefig(
    os.path.join(RESULTS_DIR, "distribucion_clases.png"),
    dpi=300,
    bbox_inches="tight"
)
plt.close()

# -------------------------------------------------
# Variables categóricas y numéricas
# -------------------------------------------------
categorical_features = X.select_dtypes(include=["object", "string", "category"]).columns.tolist()
numeric_features = X.select_dtypes(exclude=["object", "string", "category"]).columns.tolist()

# -------------------------------------------------
# Preprocesamiento
# -------------------------------------------------
preprocessor = ColumnTransformer(
    transformers=[
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            categorical_features
        )
    ],
    remainder="passthrough"
)

# -------------------------------------------------
# Modelo
# -------------------------------------------------
model = RandomForestClassifier(
    n_estimators=200,
    random_state=29,
    n_jobs=-1,
    class_weight="balanced"
)

# Pipeline
pipeline = Pipeline([
    ("preprocessor", preprocessor),
    ("classifier", model)
])

# -------------------------------------------------
# Split
# -------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=29,
    stratify=y
)

# -------------------------------------------------
# Entrenamiento
# -------------------------------------------------
pipeline.fit(X_train, y_train)

# -------------------------------------------------
# Guardar modelo
# -------------------------------------------------
with open("models/modelo_prestamo.pkl", "wb") as f:
    pickle.dump(pipeline, f)
    print("Modelo guardado como modelo_prestamo.pkl")

print("Entrenamiento finalizado ...")
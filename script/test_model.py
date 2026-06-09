import pickle
import os
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
    roc_curve,
    precision_recall_curve,
    auc,
    ConfusionMatrixDisplay
)

# Crear carpeta de resultados
RESULTS_DIR = "results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# -------------------------------------------------
# Cargar datos
# -------------------------------------------------
data = pd.read_csv("data/02_loan_data.csv")

target = "loan_status"

X = data.drop(columns=[target])
y = data[target]

# -------------------------------------------------
# Matriz de correlación
# -------------------------------------------------
corr = data.corr(numeric_only=True)

fig, ax = plt.subplots(figsize=(12, 10))
im = ax.imshow(corr, cmap="coolwarm", vmin=-1, vmax=1)

# Barra de color
fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)

# Configurar ticks
ax.set_xticks(np.arange(len(corr.columns)))
ax.set_yticks(np.arange(len(corr.columns)))
ax.set_xticklabels(corr.columns, rotation=45, ha="right", fontsize=9)
ax.set_yticklabels(corr.columns, fontsize=9)

# Anotaciones numéricas en cada celda
for i in range(len(corr.columns)):
    for j in range(len(corr.columns)):
        val = corr.iloc[i, j]
        # Color del texto dinámico para legibilidad
        color = "white" if abs(val) > 0.5 else "black"
        ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=9)

plt.title("Matriz de Correlación", fontsize=14, fontweight="bold", pad=20)
plt.tight_layout()
plt.savefig(
    os.path.join(RESULTS_DIR, "matriz_correlacion.png"),
    dpi=300,
    bbox_inches="tight"
)
plt.close()

# -------------------------------------------------
# Split
# -------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=29,
    stratify=y
)

# -------------------------------------------------
# Cargar modelo
# -------------------------------------------------
with open("models/modelo_prestamo.pkl", "rb") as f:
    model = pickle.load(f)
    print("Modelo descargado exitosamente")

# -------------------------------------------------
# Predicciones
# -------------------------------------------------
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:, 1]

# -------------------------------------------------
# Métricas
# -------------------------------------------------
accuracy = accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred)
recall = recall_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)
roc_auc = roc_auc_score(y_test, y_prob)

print("\n========== MÉTRICAS ==========")
print(f"Accuracy : {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall   : {recall:.4f}")
print(f"F1-Score : {f1:.4f}")
print(f"ROC-AUC  : {roc_auc:.4f}")

print("\n========== REPORTE ==========")
print(classification_report(y_test, y_pred))

# -------------------------------------------------
# Matriz de confusión visual
# -------------------------------------------------
cm = confusion_matrix(y_test, y_pred)

fig, ax = plt.subplots(figsize=(6, 5))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Solvente", "Impago"])
disp.plot(cmap="Blues", values_format="d", ax=ax, colorbar=False)

plt.title("Matriz de Confusión", fontsize=14, fontweight="bold", pad=15)
plt.xlabel("Predicción", fontsize=12, fontweight="bold")
plt.ylabel("Valor Real", fontsize=12, fontweight="bold")

plt.tight_layout()
plt.savefig(
    os.path.join(RESULTS_DIR, "matriz_confusion.png"),
    dpi=300,
    bbox_inches="tight"
)
plt.close()

# -------------------------------------------------
# Curva ROC
# -------------------------------------------------
fpr, tpr, _ = roc_curve(y_test, y_prob)

plt.figure(figsize=(8, 6))

plt.plot(
    fpr,
    tpr,
    label=f"AUC = {roc_auc:.4f}"
)

plt.plot([0, 1], [0, 1], "--")

plt.xlabel("False Positive Rate", fontsize=12, fontweight="bold")
plt.ylabel("True Positive Rate", fontsize=12, fontweight="bold")
plt.title("Curva ROC", fontsize=14, fontweight="bold")
plt.legend()

plt.savefig(
    os.path.join(RESULTS_DIR, "curva_roc.png"),
    dpi=300,
    bbox_inches="tight"
)
plt.close()

# -------------------------------------------------
# Curva Precision Recall
# -------------------------------------------------
precision_curve, recall_curve, _ = precision_recall_curve(
    y_test,
    y_prob
)

pr_auc = auc(recall_curve, precision_curve)

plt.figure(figsize=(8, 6))

plt.plot(
    recall_curve,
    precision_curve,
    label=f"PR-AUC = {pr_auc:.4f}"
)

plt.xlabel("Recall", fontsize=12, fontweight="bold")
plt.ylabel("Precision", fontsize=12, fontweight="bold")
plt.title("Curva Precision-Recall", fontsize=14, fontweight="bold")
plt.legend()

plt.savefig(
    os.path.join(RESULTS_DIR, "curva_precision_recall.png"),
    dpi=300,
    bbox_inches="tight"
)
plt.close()

# -------------------------------------------------
# Importancia de variables
# -------------------------------------------------
rf_model = model.named_steps["classifier"]

# Recuperamos nombres de variables tras el preprocesamiento directamente del preprocessor
feature_names = model.named_steps["preprocessor"].get_feature_names_out()

importances = rf_model.feature_importances_

importance_data = pd.DataFrame({
    "Variable": feature_names,
    "Importancia": importances
})

importance_data = importance_data.sort_values(
    by="Importancia",
    ascending=False
)

print("\n========== TOP K VARIABLES ==========")
k = 5
print(importance_data.head(k))

plt.figure(figsize=(10, 8))
# Tomamos los 20 más importantes y los invertimos para tener el de mayor importancia en el tope del barh
top_features = importance_data.head(20).iloc[::-1]
plt.barh(top_features["Variable"], top_features["Importancia"], color="skyblue", edgecolor="gray")

plt.title(f"{k} Variables más Importantes", fontsize=14, fontweight="bold")
plt.xlabel("Importancia")
plt.ylabel("Variable")

plt.tight_layout()
plt.savefig(
    os.path.join(RESULTS_DIR, "importancia_variables.png"),
    dpi=300,
    bbox_inches="tight"
)
plt.close()

# -------------------------------------------------
# Guarda importancia de variables en un CSV
# -------------------------------------------------
importance_data.to_csv(
    os.path.join(
        RESULTS_DIR,
        "importancia_variables.csv"
    ),
    index=False
)

# -------------------------------------------------
# Distribución de probabilidades
# -------------------------------------------------
plt.figure(figsize=(8, 5))

plt.hist(
    y_prob,
    bins=30,
    color="steelblue",
    edgecolor="black"
)

plt.title("Distribución de Probabilidades Predichas", fontsize=14, fontweight="bold")
plt.xlabel("Probabilidad de Impago", fontsize=12, fontweight="bold")
plt.ylabel("Frecuencia", fontsize=12, fontweight="bold")

plt.tight_layout()
plt.savefig(
    os.path.join(RESULTS_DIR, "distribucion_probabilidades.png"),
    dpi=300,
    bbox_inches="tight"
)
plt.close()

# Guarda las métricas en archivo de texto
with open(
    os.path.join(RESULTS_DIR, "metricas.txt"),
    "w",
    encoding="utf-8"
) as f:

    f.write("RESULTADOS DEL MODELO\n")
    f.write("=" * 40 + "\n\n")

    f.write(f"Accuracy : {accuracy:.4f}\n")
    f.write(f"Precision: {precision:.4f}\n")
    f.write(f"Recall   : {recall:.4f}\n")
    f.write(f"F1-Score : {f1:.4f}\n")
    f.write(f"ROC-AUC  : {roc_auc:.4f}\n\n")

    f.write("REPORTE DE CLASIFICACIÓN\n")
    f.write("=" * 40 + "\n")
    f.write(classification_report(y_test, y_pred))

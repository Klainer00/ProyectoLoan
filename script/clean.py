"""
clean.py -- Pipeline de Limpieza y Transformacion
==================================================
Lee el CSV de prestamos, ejecuta una serie de pasos de limpieza y
transformacion, y devuelve un DataFrame listo para ser cargado en PostgreSQL.

Pasos del pipeline:
  1. Carga del CSV
  2. Eliminacion de duplicados
  3. Manejo de valores nulos
  4. Filtrado de outliers
  5. Validacion de variables categoricas
  6. Conversion y normalizacion de tipos
"""

import pandas as pd
import numpy as np
import os

# --- Rutas -------------------------------------------------------------------
CSV_PATH = os.path.join(os.path.dirname(__file__), "../data/02_loan_data.csv")

# --- Dominios validos para variables categoricas -----------------------------
VALID_EDUCATION      = {"High School", "Bachelor", "Master", "Associate", "Doctorate"}
VALID_HOME_OWNERSHIP = {"RENT", "OWN", "MORTGAGE", "OTHER"}
VALID_LOAN_INTENT    = {"PERSONAL", "EDUCATION", "MEDICAL", "VENTURE",
                        "HOMEIMPROVEMENT", "DEBTCONSOLIDATION"}
VALID_GENDER         = {"male", "female"}

# Orden de columnas que coincide con el INSERT en la BD
COLUMNAS_BD = [
    "person_age", "person_gender", "person_education", "person_income",
    "person_emp_exp", "person_home_ownership", "loan_amnt", "loan_intent",
    "loan_int_rate", "loan_percent_income", "cb_person_cred_hist_length",
    "credit_score", "previous_loan_defaults_on_file", "loan_status",
]


# --- Paso 1: Carga -----------------------------------------------------------
def cargar_csv(path=CSV_PATH):
    """Lee el archivo CSV y devuelve un DataFrame."""
    df = pd.read_csv(path)
    print(f"[CARGA]        {len(df):>7,} filas leidas desde '{os.path.basename(path)}'")
    return df


# --- Paso 2: Duplicados ------------------------------------------------------
def eliminar_duplicados(df):
    """Elimina filas completamente duplicadas."""
    antes = len(df)
    df = df.drop_duplicates()
    print(f"[DUPLICADOS]   {antes - len(df):>7,} filas eliminadas  ->  {len(df):,} restantes")
    return df


# --- Paso 3: Valores nulos ---------------------------------------------------
def limpiar_nulos(df):
    """
    - Elimina filas con nulos en columnas criticas.
    - Los nulos restantes se conservan como None para insertarlos como NULL en PostgreSQL.
    """
    nulos_por_col = df.isnull().sum()
    cols_con_nulos = nulos_por_col[nulos_por_col > 0]
    if not cols_con_nulos.empty:
        lineas = "\n".join(f"               - {c}: {n}" for c, n in cols_con_nulos.items())
        print(f"[NULOS]        Valores nulos detectados:\n{lineas}")
    else:
        print("[NULOS]        Sin valores nulos detectados")

    cols_criticas = [
        "person_age", "person_income", "loan_amnt",
        "loan_status", "credit_score", "loan_int_rate",
    ]
    antes = len(df)
    df = df.dropna(subset=cols_criticas)
    print(f"[NULOS]        {antes - len(df):>7,} filas eliminadas  ->  {len(df):,} restantes")
    return df


# --- Paso 4: Coercion de tipos numericos ------------------------------------
def coercionar_numericas(df):
    """
    Convierte las columnas numericas a sus tipos correctos usando
    pd.to_numeric(errors='coerce'): cualquier valor que no pueda
    convertirse (ej. strings como 'veinte' o 'N/A') se transforma
    en NaN y es descartado antes de comparar rangos.
    Esto previene el TypeError al filtrar outliers.
    """
    cols_enteras  = ["person_age", "person_income", "person_emp_exp",
                     "loan_amnt", "cb_person_cred_hist_length", "credit_score"]
    cols_flotantes = ["loan_int_rate", "loan_percent_income"]

    invalidos = 0
    for col in cols_enteras + cols_flotantes:
        antes = df[col].isna().sum()
        df[col] = pd.to_numeric(df[col], errors="coerce")
        nuevos_nan = df[col].isna().sum() - antes
        if nuevos_nan > 0:
            print(f"[COERCION]     {col}: {nuevos_nan} valor(es) no numerico(s) -> NaN")
            invalidos += nuevos_nan

    # Descartar filas donde columnas criticas quedaron como NaN tras coercion
    cols_criticas = ["person_age", "person_income", "loan_amnt",
                     "credit_score", "loan_int_rate"]
    antes = len(df)
    df = df.dropna(subset=cols_criticas)
    eliminados = antes - len(df)
    if eliminados > 0:
        print(f"[COERCION]     {eliminados} fila(s) eliminadas por valores no numericos en cols criticas")
    if invalidos == 0:
        print("[COERCION]     Todas las columnas numericas tienen tipos correctos")
    return df


# --- Paso 5: Outliers --------------------------------------------------------
def filtrar_outliers(df):
    """
    Aplica reglas de negocio para descartar registros con valores
    estadistica o logicamente imposibles.
    """
    antes = len(df)

    # Edad: entre 18 y 80 anos
    df = df[(df["person_age"] >= 18) & (df["person_age"] <= 80)]

    # Experiencia laboral: no puede superar (edad - 18) ni ser negativa
    df = df[(df["person_emp_exp"] >= 0) & (df["person_emp_exp"] <= df["person_age"] - 18)]

    # Monto del prestamo: rango documentado en el dataset
    df = df[(df["loan_amnt"] >= 500) & (df["loan_amnt"] <= 35_000)]

    # Tasa de interes: entre 5% y 25%
    df = df[(df["loan_int_rate"] >= 5.0) & (df["loan_int_rate"] <= 25.0)]

    # Credit score: escala estandar FICO
    df = df[(df["credit_score"] >= 300) & (df["credit_score"] <= 850)]

    # Porcentaje del ingreso: 0-1 (0%-100%)
    df = df[(df["loan_percent_income"] >= 0.0) & (df["loan_percent_income"] <= 1.0)]

    # Ingreso minimo razonable
    df = df[df["person_income"] >= 1_000]

    # Historial crediticio: minimo 2 anos, maximo 30
    df = df[(df["cb_person_cred_hist_length"] >= 2) & (df["cb_person_cred_hist_length"] <= 30)]

    print(f"[OUTLIERS]     {antes - len(df):>7,} filas eliminadas  ->  {len(df):,} restantes")
    return df


# --- Paso 5: Validacion de categoricas --------------------------------------
def validar_categoricas(df):
    """
    Normaliza el texto de las variables categoricas y descarta cualquier
    fila con un valor fuera del dominio conocido.
    """
    antes = len(df)

    # Normalizacion de texto
    df["person_gender"]         = df["person_gender"].str.strip().str.lower()
    df["person_education"]      = df["person_education"].str.strip().str.title()
    df["person_home_ownership"] = df["person_home_ownership"].str.strip().str.upper()
    df["loan_intent"]           = df["loan_intent"].str.strip().str.upper()

    # Filtrado por dominio valido
    df = df[df["person_gender"].isin(VALID_GENDER)]
    df = df[df["person_education"].isin(VALID_EDUCATION)]
    df = df[df["person_home_ownership"].isin(VALID_HOME_OWNERSHIP)]
    df = df[df["loan_intent"].isin(VALID_LOAN_INTENT)]

    print(f"[CATEGORICAS]  {antes - len(df):>7,} filas eliminadas  ->  {len(df):,} restantes")
    return df


# --- Paso 6: Conversion de tipos --------------------------------------------
def convertir_tipos(df):
    """
    Garantiza que cada columna tenga el tipo Python/NumPy correcto
    antes de la insercion en PostgreSQL.
    """
    # Booleanos
    df["previous_loan_defaults_on_file"] = df["previous_loan_defaults_on_file"].map(
        {"Yes": True, "No": False, True: True, False: False}
    )
    df["loan_status"] = df["loan_status"].astype(bool)

    # Enteros
    for col in ["person_age", "person_income", "person_emp_exp",
                "loan_amnt", "cb_person_cred_hist_length", "credit_score"]:
        df[col] = df[col].astype(int)

    # Flotantes
    for col in ["loan_int_rate", "loan_percent_income"]:
        df[col] = df[col].astype(float).round(4)

    # NaN residuales -> None (compatibilidad con psycopg2 / NULL en PostgreSQL)
    df = df.where(pd.notnull(df), None)

    print(f"[TIPOS]        Conversion de tipos completada")
    return df


# --- Pipeline principal ------------------------------------------------------
def pipeline_limpieza(path=CSV_PATH):
    """
    Ejecuta todos los pasos de limpieza y transformacion en orden y
    devuelve un DataFrame con las columnas en el orden esperado por la BD.
    """
    sep = "=" * 55
    print(f"\n{sep}")
    print("  PIPELINE DE LIMPIEZA -- Loan Approval Dataset")
    print(sep)

    df = cargar_csv(path)
    df = eliminar_duplicados(df)
    df = limpiar_nulos(df)
    df = coercionar_numericas(df)   # <-- nuevo: convierte strings invalidos a NaN
    df = filtrar_outliers(df)
    df = validar_categoricas(df)
    df = convertir_tipos(df)

    # Reordenar columnas segun el esquema de la BD
    df = df[COLUMNAS_BD]

    print(sep)
    print(f"  PIPELINE COMPLETADO: {len(df):,} filas limpias y listas")
    print(f"{sep}\n")
    return df


# --- Verificacion de calidad post-limpieza -----------------------------------
def generar_reporte(df):
    """
    Valida explicitamente cada regla de negocio sobre el DataFrame ya limpio
    e imprime un reporte con PASS / FAIL por cada check.
    """
    sep = "-" * 55
    checks_ok   = 0
    checks_fail = 0

    def check(nombre, condicion, detalle=""):
        nonlocal checks_ok, checks_fail
        estado = "[PASS]" if condicion else "[FAIL]"
        if condicion:
            checks_ok += 1
        else:
            checks_fail += 1
        sufijo = f"  ({detalle})" if detalle else ""
        print(f"  {estado}  {nombre}{sufijo}")

    print(f"\n{sep}")
    print("  REPORTE DE CALIDAD -- DataFrame Limpio")
    print(sep)

    # -- Estructura -----------------------------------------------------------
    print("\n  [ESTRUCTURA]")
    check("Sin filas duplicadas",
          df.duplicated().sum() == 0,
          f"{df.duplicated().sum()} duplicados")
    check("Sin nulos en columnas criticas",
          df[["person_age", "person_income", "loan_amnt",
              "loan_status", "credit_score", "loan_int_rate"]].isnull().sum().sum() == 0)
    check("14 columnas presentes",
          len(df.columns) == 14,
          f"encontradas: {len(df.columns)}")

    # -- Rangos numericos -----------------------------------------------------
    print("\n  [RANGOS NUMERICOS]")
    check("person_age: 18-80",
          df["person_age"].between(18, 80).all(),
          f"min={df['person_age'].min()}, max={df['person_age'].max()}")
    check("person_emp_exp: 0 <= exp <= (age-18)",
          (df["person_emp_exp"] <= df["person_age"] - 18).all() and
          (df["person_emp_exp"] >= 0).all(),
          f"max exp={df['person_emp_exp'].max()}")
    check("loan_amnt: 500-35000",
          df["loan_amnt"].between(500, 35_000).all(),
          f"min={df['loan_amnt'].min()}, max={df['loan_amnt'].max()}")
    check("loan_int_rate: 5-25%",
          df["loan_int_rate"].between(5.0, 25.0).all(),
          f"min={df['loan_int_rate'].min():.2f}, max={df['loan_int_rate'].max():.2f}")
    check("credit_score: 300-850",
          df["credit_score"].between(300, 850).all(),
          f"min={df['credit_score'].min()}, max={df['credit_score'].max()}")
    check("loan_percent_income: 0-1",
          df["loan_percent_income"].between(0.0, 1.0).all(),
          f"max={df['loan_percent_income'].max():.4f}")
    check("person_income >= 1000",
          (df["person_income"] >= 1_000).all(),
          f"min={df['person_income'].min():,}")
    check("cb_person_cred_hist_length: 2-30",
          df["cb_person_cred_hist_length"].between(2, 30).all(),
          f"min={df['cb_person_cred_hist_length'].min()}, max={df['cb_person_cred_hist_length'].max()}")

    # -- Variables categoricas ------------------------------------------------
    print("\n  [VARIABLES CATEGORICAS]")
    check("person_gender: solo male/female",
          df["person_gender"].isin(VALID_GENDER).all(),
          str(sorted(df["person_gender"].unique().tolist())))
    check("person_education: dominio valido (5 niveles)",
          df["person_education"].isin(VALID_EDUCATION).all(),
          str(sorted(df["person_education"].unique().tolist())))
    check("person_home_ownership: RENT/OWN/MORTGAGE/OTHER",
          df["person_home_ownership"].isin(VALID_HOME_OWNERSHIP).all(),
          str(sorted(df["person_home_ownership"].unique().tolist())))
    check("loan_intent: dominio valido (6 categorias)",
          df["loan_intent"].isin(VALID_LOAN_INTENT).all(),
          str(sorted(df["loan_intent"].unique().tolist())))

    # -- Tipos de datos -------------------------------------------------------
    print("\n  [TIPOS DE DATOS]")
    check("loan_status es bool",
          str(df["loan_status"].dtype) == "bool")
    check("previous_loan_defaults_on_file es bool",
          str(df["previous_loan_defaults_on_file"].dtype) == "bool")
    check("person_age es entero",
          pd.api.types.is_integer_dtype(df["person_age"]))
    check("credit_score es entero",
          pd.api.types.is_integer_dtype(df["credit_score"]))
    check("loan_int_rate es flotante",
          pd.api.types.is_float_dtype(df["loan_int_rate"]))

    # -- Distribucion de la variable objetivo ---------------------------------
    print("\n  [VARIABLE OBJETIVO -- loan_status]")
    conteo = df["loan_status"].value_counts()
    total  = len(df)
    for val, cnt in conteo.items():
        etiqueta = "Default (impago)" if val else "Pagado"
        print(f"       {etiqueta}: {cnt:,}  ({cnt / total * 100:.1f}%)")

    # -- Resumen final --------------------------------------------------------
    resultado = "DATASET VALIDO" if checks_fail == 0 else "REVISAR FALLOS"
    print(f"\n{sep}")
    print(f"  Total filas limpias : {len(df):,}")
    print(f"  Checks aprobados    : {checks_ok}")
    print(f"  Checks fallidos     : {checks_fail}")
    print(f"  Resultado global    : {resultado}")
    print(f"{sep}\n")


# --- Ejecucion directa (modo prueba) -----------------------------------------
if __name__ == "__main__":
    df_limpio = pipeline_limpieza()
    generar_reporte(df_limpio)
    
    out_path = os.path.join(os.path.dirname(__file__), "../data/03_loan_data_cleaned.csv")
    df_limpio.to_csv(out_path, index=False)
    print(f"[EXPORTACION] DataFrame limpio guardado en: {out_path}")

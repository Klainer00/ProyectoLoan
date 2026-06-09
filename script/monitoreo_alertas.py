import pandas as pd
import os
from quality_check import QualityCheck

def ejecutar_monitoreo(csv_path):
    print("=======================================================")
    print("  SISTEMA DE MONITOREO Y ALERTAS DE CALIDAD DATAOPS")
    print("=======================================================")
    
    df = pd.read_csv(csv_path)
    print(f"[MONITOREO] Evaluando dataset: {os.path.basename(csv_path)} con {len(df)} registros.")
    
    qc = QualityCheck(data=df)
    
    reporte = qc.quality_report()
    score = reporte["quality_score"]
    
    print("\n[KPIs DETECTADOS]")
    print(f" - ¿Contiene Nulos/Faltantes?: {reporte['nulos/faltantes']}")
    print(f" - ¿Contiene Duplicados?:      {reporte['duplicados']}")
    print(f" - ¿Contiene Outliers?:        {reporte['outliers']}")
    print(f" - ¿Contiene Inconsistencias?: {reporte['inconsistencias']}")
    
    print(f"\n[METRICA GLOBAL] Quality Score: {score * 100:.1f}%")
    
    print("\n[ESTADO DE ALERTAS]")
    
    UMBRAL_ACEPTACION = 0.80 
    
    if score < UMBRAL_ACEPTACION:
        print(f" [ALERTA CRITICA] El Quality Score ({score*100:.1f}%) esta por debajo del umbral ({UMBRAL_ACEPTACION*100:.1f}%).")
        print(" [ACCION] Pipeline detenido. Se requiere revision manual de los datos.")
        return False
    else:
        print(" [OK] Calidad de datos dentro de los parametros aceptables. Continuando pipeline...")
        return True

if __name__ == "__main__":
    ruta_principal = "data/02_loan_data.csv"
    ejecutar_monitoreo(ruta_principal)
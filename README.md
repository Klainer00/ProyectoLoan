# Predicción de Préstamos — Loan Approval Classification
## Descripción del Proyecto

Este proyecto consiste en el diseño y desarrollo de una solución técnica integral orientada a predecir la probabilidad de incumplimiento o aprobación de préstamos bancarios.

Utilizando el dataset **Loan Approval Classification**, el sistema abarca desde la ingesta y procesamiento de datos de los solicitantes, hasta el entrenamiento de un modelo predictivo de Inteligencia Artificial y su disponibilización mediante un servicio backend.

---

## Arquitectura del Sistema

El sistema ha sido diseñado separando las responsabilidades en tres etapas lógicas clave para garantizar un flujo de datos eficiente:

1. **Etapa de Ingesta:** Extracción de los datos (archivos crudos) y carga inicial en el sistema. Los scripts de ingesta automatizan la lectura y validación preliminar de la estructura del dataset.

2. **Etapa de Procesamiento:** Utilizando **Python 3.12**, se realiza la limpieza, el manejo de valores nulos, la codificación de variables categóricas y la transformación de características. Posteriormente, se entrena y evalúa el modelo de Machine Learning.

3. **Etapa de Servicio:** El modelo entrenado se expone a través de una API backend desplegada en la nube mediante **Render**. Los datos estructurados y los resultados de las predicciones se almacenan de forma segura en una base de datos relacional **PostgreSQL** alojada en **Supabase**.

### Justificación Técnica de la Arquitectura

La elección de estas tecnologías se fundamenta en tres pilares críticos exigidos para sistemas en producción:

- **Escalabilidad:** El uso de **Docker** para contenerizar la aplicación, sumado al despliegue en Render, permite que el backend escale horizontalmente (levantando más instancias) de manera automática si el volumen de peticiones de predicción aumenta bruscamente.

- **Seguridad:** Al utilizar **Supabase**, se delega el manejo de accesos mediante políticas de seguridad a nivel de fila (Row Level Security — RLS). Esto garantiza que las credenciales y los datos sensibles de los préstamos estén encriptados y aislados de accesos no autorizados.

- **Interoperabilidad:** El sistema expone sus funcionalidades mediante interfaces estándar (**APIs REST**). Esto asegura que cualquier cliente, ya sea una aplicación web o un dashboard analítico, pueda consumir las predicciones independientemente del lenguaje en que esté programado.


## Requisitos Técnicos y Entorno

Para replicar o contribuir a este proyecto, el entorno local debe cumplir con los siguientes requisitos:

- **Lenguaje:** Python 3.12
- **Control de Versiones:** Git
- **Contenerización:** Docker y Docker Compose
- **Base de Datos:** PostgreSQL
- **CI/CD:** GitHub Actions 
- **Editor Sugerido:** Visual Studio Code

## Estructura del Repositorio

├── .github/  
│   └── workflows/          # GitHub Actions (CI/CD)  
├── data/  
│   └── 02_loan_data.csv    # Dataset original  
├── scripts/  
│   ├── ingesta.py  
│   ├── limpieza.py  
│   ├── carga_bd.py  
│   └── entrenamiento.py  
├── docs/  
│   └── DISEÑO_TECNICO.md   # Documento técnico completo  
├── .env                    # Credenciales (No versionado)  
├── Dockerfile  
├── README.md  
└── requirements.txt  

  
## Equipo
**Eduardo Paredes** – Procesamiento y limpieza
**Bryan Jara** – Modelado y entrenamiento
**Jeremy Concha** – Visualización y documentación

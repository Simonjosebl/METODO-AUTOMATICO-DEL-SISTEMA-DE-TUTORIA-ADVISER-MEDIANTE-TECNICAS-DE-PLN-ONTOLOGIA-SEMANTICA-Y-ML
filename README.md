# Método Automático para Análisis de Narrativas Escritas - Sistema ADVISER

[![Licencia](https://img.shields.io/badge/Licencia-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/deed.es)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)
[![NLP](https://img.shields.io/badge/NLP-SpaCy-blueviolet.svg)](https://spacy.io/)

## 📝 Descripción General

Este repositorio contiene el desarrollo del trabajo de grado para la **Universidad Católica de Colombia**. El proyecto implementa un **método automático** para analizar las narrativas escritas de los registros de tutorías del sistema **ADVISER**.

El objetivo principal es **clasificar automáticamente** los textos de las tutorías para identificar:

- **Niveles cognitivos** según las taxonomías **Bloom** y **SOLO**
- **Temas centrales** del área de software
- **Resultados de Aprendizaje (RA)** asociados a las asignaturas

Este enfoque busca transformar datos textuales no estructurados en información valiosa para la institución, ayudando a combatir la **deserción estudiantil** y mejorar la **calidad educativa** mediante el uso de técnicas de **Procesamiento de Lenguaje Natural (PLN)** y **Machine Learning**.

## 🎯 Contexto del Problema

| Indicador | Dato |
|:---|:---:|
| Deserción anual en educación superior (Colombia) | **11%** |
| Deserción en programas de ingeniería | **42% - 55%** |
| Registros de tutorías sin analizar | **+3,000** |
| Tiempo de clasificación manual (vs automática) | **40+ min vs 6-8 min** |

Los registros de tutorías del sistema ADVISER se almacenan pero **no se analizan**, y no existe una herramienta que identifique automáticamente temas recurrentes, asignaturas con más dificultades o niveles de comprensión de los estudiantes.

## 🚀 Objetivos

### Objetivo General
Implementar un método automático para el análisis de narrativas escritas en los registros de tutorías del sistema ADVISER, para la identificación de los temas tratados, niveles cognitivos y su asociación a los resultados de aprendizaje.

### Objetivos Específicos
1. Construir un **diccionario taxonómico** a partir de las competencias y temáticas del programa.
2. **Diseñar** un método automático usando PLN y Machine Learning.
3. **Desarrollar** el método en un entorno de programación (Python).
4. **Evaluar** la calidad del método mediante métricas de desempeño.

## 🛠️ Tecnologías y Herramientas

| Categoría | Tecnologías |
|:---|:---|
| **Lenguaje** | Python 3.8+ |
| **Procesamiento de Texto (PLN)** | SpaCy, NLTK, Sentence-Transformers, Unicode |
| **Machine Learning / Embeddings** | Scikit-learn, SBERT (`paraphrase-multilingual-MiniLM-L12-v2`) |
| **LLM (Comparativo)** | OpenAI GPT-4o Mini (vía API) |
| **Manipulación de Datos** | Pandas, NumPy |
| **Visualización** | Matplotlib, Seaborn |
| **API y Despliegue** | FastAPI, Uvicorn |
| **Ontologías** | Protégé |
| **Entorno de Desarrollo** | Google Colab, VS Code |

## 🏗️ Arquitectura del Método Automático

El sistema se compone de un **pipeline** de procesamiento de 4 etapas:
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│ ENTRADA │ -> │ PROCESAMIENTO│ -> │ CLASIFICACIÓN│ -> │ SALIDA │
│ DATOS │ │ Y FILTRO │ │ SEMÁNTICA │ │ RESULTADOS │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
│ │ │ │
▼ ▼ ▼ ▼
Dataset Limpieza Diccionarios Archivo Excel
ADVISER Tokenización + Embeddings + Columnas:
(Excel/CSV) Lematización + Similitud BLOOM, SOLO,
Coseno TEMA, RA

text

### Detalle de cada etapa:

1. **Entrada de Datos**: Carga el dataset histórico del sistema ADVISER.
2. **Procesamiento y Filtrado**: 
   - Filtra registros de **Ingeniería de Sistemas y Computación**
   - Selecciona asignaturas del **área de software**
   - Limpieza: eliminación de caracteres especiales, tokenización y **lematización** (SpaCy)
3. **Clasificación Semántica** (Método Principal):
   - Diccionarios taxonómicos preconstruidos (Bloom, SOLO, Temas, RA)
   - Modelo de comparación semántica con **embeddings** (SentenceTransformer) y **similitud coseno**
4. **Salida de Resultados**: Archivo Excel con columnas `BLOOM`, `SOLO`, `TEMA_CLASIFICADO`, `APRENDIZAJE_ASIGNATURA`

## 📂 Estructura del Repositorio

```text
/
├── data/                      # Datasets de ejemplo (anónimos)
│   ├── tutorias_adviser.xlsx
│   └── dataset_control_mejorado.xlsx
├── diccionarios/              # Diccionarios taxonómicos
│   ├── bloom_taxonomia.json
│   ├── solo_taxonomia.json
│   ├── temas_programacion.json
│   └── resultados_aprendizaje.json
├── src/                       # Código fuente
│   ├── preprocesamiento.py    # Limpieza, tokenización, lematización
│   ├── clasificadores.py      # Lógica de similitud coseno y ML
│   ├── main.py                # Pipeline principal
│   └── utils.py               # Funciones auxiliares
├── api/                       # Prototipo de API con FastAPI
│   ├── app.py
│   └── templates/
│       └── index.html
├── notebooks/                 # Experimentación
│   └── evaluacion_modelos.ipynb
├── resultados/                # Archivos de salida
├── requirements.txt
├── README.md
└── LICENSE
📊 Métricas de Desempeño (Resultados Clave)
El método fue evaluado con 3,794 registros reales del sistema ADVISER y un dataset de control mejorado.

Método Evaluado	Accuracy	Precisión (Macro)	Recall (Macro)	F1-Score (Macro)
Método Lingüístico (Principal)	0.842	0.858	0.831	0.837
Método MMAS (ML + Perceptrones)	0.651	0.639	0.672	0.608
Método LLM-API (GPT-4o Mini)	0.071	0.043	0.040	0.022
Método Lingüístico (Dataset Control)	0.978	0.897	0.897	0.897
Rendimiento por Taxonomía (Método Lingüístico)
Taxonomía	Accuracy	Precisión	Recall	F1-Score
Bloom	0.996	0.982	0.982	0.982
SOLO	0.906	0.816	0.647	0.673
Temas	0.958	0.993	0.935	0.948
Resultados Aprendizaje	0.510	0.814	0.814	0.814
Hallazgos Principales
✅ El método lingüístico supera significativamente a ML estándar y LLMs genéricos sin ajuste fino

📝 La calidad del texto (presencia de verbos, estructura gramatical) es el factor más determinante

🔄 El método es consistente (F1 ~0.45-0.47) frente a criterios de diferentes docentes

⏱️ Procesa +3,000 registros en 6-8 minutos (vs 40+ minutos manual)

🧪 Cómo Usar el Proyecto
Prerrequisitos
Python 3.8 o superior

Pip (gestor de paquetes)

Instalación
bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/analisis-tutorias-adviser.git
cd analisis-tutorias-adviser

# Instalar dependencias
pip install -r requirements.txt

# Descargar modelo de lenguaje de SpaCy para español
python -m spacy download es_core_news_md
Ejecución (Modo Línea de Comando)
bash
python src/main.py --input data/tutorias_adviser.xlsx --output resultados/clasificacion.xlsx
Ejecución (Modo Web - Prototipo)
bash
uvicorn api.app:app --reload
Luego abre tu navegador en http://127.0.0.1:8000 y sube un archivo de tutorías.

Archivo de requirements.txt
txt
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
spacy>=3.7.0
sentence-transformers>=2.2.0
nltk>=3.8.0
matplotlib>=3.7.0
seaborn>=0.12.0
fastapi>=0.100.0
uvicorn>=0.23.0
openai>=1.0.0
rdflib>=7.0.0
📌 Limitaciones Actuales
Limitación	Descripción
Alcance	Restringido al área de software de Ingeniería de Sistemas
Variables externas	No incluye factores psicosociales o económicos
Calidad del texto	El rendimiento depende de la calidad de redacción de los registros
Sin verbos	Registros telegráficos o sin verbos afectan la clasificación
🔮 Trabajos Futuros
Soporte para múltiples formatos (CSV, JSON, bases de datos)

Dashboards interactivos (Power BI, Tableau) para visualización de resultados

Seguridad - Detección de archivos maliciosos

Extensión a todas las áreas del programa de Ingeniería de Sistemas

Mejora de diccionarios con más verbos y términos técnicos

📄 Licencia
Este proyecto está bajo la licencia Creative Commons Attribution 4.0 International (CC BY 4.0). Puede compartir y adaptar el material, siempre que se dé el crédito adecuado.

👨‍💻 Autores
Autor	Contacto
Simón José Bravo Lozano	simonjbl@example.com
Felipe Cuervo Lorenzana	fcuervol@example.com
Docente Tutor: MsC. Juan Carlos Barrero Calixto

Universidad Católica de Colombia
Facultad de Ingeniería - Programa de Ingeniería de Sistemas y Computación
Bogotá D.C., 2025-3

📚 Referencia
Si usas este trabajo en tu investigación, por favor cita como:

Bravo Lozano, S. J., Cuervo Lorenzana, F. (2025). Método automático para el análisis de narrativas escritas del sistema de tutorías ADVISER mediante técnicas de procesamiento de lenguaje natural de texto, ontologías semánticas y Machine Learning. (Trabajo de grado). Universidad Católica de Colombia, Bogotá.

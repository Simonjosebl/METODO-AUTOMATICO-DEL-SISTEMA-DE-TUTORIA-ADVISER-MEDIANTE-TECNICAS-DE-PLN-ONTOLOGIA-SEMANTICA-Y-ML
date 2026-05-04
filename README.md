# Método Automático para Análisis de Narrativas Escritas - Sistema ADVISER

[![Licencia](https://img.shields.io/badge/Licencia-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/deed.es)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)](https://fastapi.tiangolo.com/)

## 📝 Descripción General

Este repositorio contiene el desarrollo del trabajo de grado para la **Universidad Católica de Colombia**. El proyecto implementa un **método automático** para analizar las narrativas escritas de los registros de tutorías del sistema **ADVISER**.

El objetivo principal es **clasificar automáticamente** los textos de las tutorías para identificar:
- **Niveles cognitivos** según las taxonomías **Bloom** y **SOLO**.
- **Temas centrales** del área de software.
- **Resultados de Aprendizaje (RA)** asociados a las asignaturas.

Este enfoque busca transformar datos textuales no estructurados en información valiosa para la institución, ayudando a combatir la **deserción estudiantil** y mejorar la **calidad educativa** mediante el uso de técnicas de **Procesamiento de Lenguaje Natural (PLN)** y **Machine Learning**.

## 🎯 Contexto del Problema

- La deserción en la educación superior en Colombia es del **11% anual** (2023), superando el 42% en programas de ingeniería.
- Los registros de tutorías del sistema ADVISER se almacenan pero **no se analizan**.
- No existe una herramienta que identifique automáticamente temas recurrentes, asignaturas con más dificultades o niveles de comprensión de los estudiantes.

## 🚀 Objetivos Específicos

1.  **Construir** un diccionario taxonómico basado en las competencias y temáticas del programa de Ingeniería de Sistemas.
2.  **Diseñar** un método automático usando PLN y Machine Learning para identificar taxonomías y temas.
3.  **Desarrollar** el método en un entorno de programación (Python).
4.  **Evaluar** la calidad del método mediante métricas de desempeño (Precisión, Recall, F1-Score, Matriz de Confusión).

## 🛠️ Tecnologías y Herramientas

| Categoría | Tecnologías |
| :--- | :--- |
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

1.  **Entrada de Datos**: Carga el dataset histórico del sistema ADVISER.
2.  **Procesamiento y Filtrado**: Filtra por programa (Ingeniería de Sistemas), área de software, y aplica limpieza, tokenización y lematización.
3.  **Clasificación Semántica**: Usa diccionarios taxonómicos + embeddings (SentenceTransformer) + similitud coseno.
4.  **Salida de Resultados**: Genera archivo Excel con columnas `BLOOM`, `SOLO`, `TEMA_CLASIFICADO`, `APRENDIZAJE_ASIGNATURA`.

## 📂 Estructura del Repositorio

```text
/
├── data/                      # Datasets de ejemplo (anónimos)
│   ├── tutorias_adviser.xlsx
│   └── dataset_control_mejorado.xlsx
├── diccionarios/              # Diccionarios taxonómicos (JSON/CSV)
│   ├── bloom_taxonomia.json
│   ├── solo_taxonomia.json
│   ├── temas_programacion.json
│   └── resultados_aprendizaje.json
├── src/                       # Código fuente
│   ├── preprocesamiento.py
│   ├── clasificadores.py
│   ├── main.py
│   └── utils.py
├── api/                       # Prototipo API con FastAPI
│   ├── app.py
│   └── templates/index.html
├── notebooks/                 # Experimentación
│   └── evaluacion_modelos.ipynb
├── resultados/                # Archivos de salida
├── docs/images/               # Imágenes para el README
├── requirements.txt
├── README.md
└── LICENSE

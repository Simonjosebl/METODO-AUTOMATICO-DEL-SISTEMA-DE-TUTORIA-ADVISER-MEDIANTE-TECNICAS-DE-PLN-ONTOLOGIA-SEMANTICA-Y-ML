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
| **Procesamiento de Texto (PLN)** | SpaCy, NLTK, Sentence-Transformers, Unicode (normalización) |
| **Machine Learning / Embeddings** | Scikit-learn (Random Forest, Naive Bayes, métricas), SBERT (`paraphrase-multilingual-MiniLM-L12-v2`) |
| **LLM (Comparativo)** | OpenAI GPT-4o Mini (vía API) |
| **Manipulación de Datos** | Pandas, NumPy |
| **Visualización** | Matplotlib, Seaborn |
| **API y Despliegue (Prototipo)** | FastAPI, Uvicorn |
| **Ontologías (Backend conceptual)** | Protégé |
| **Entorno de Desarrollo** | Google Colab, Visual Studio Code |

## 🏗️ Arquitectura del Método Automático

El sistema se compone de un **pipeline** de procesamiento de 4 etapas:

1.  **Entrada de Datos**:
    - Carga el dataset histórico del sistema ADVISER (archivo Excel/CSV con columnas: `ASIGNATURA`, `TEMA O CONCEPTO`).

2.  **Procesamiento y Filtrado**:
    - Filtra los registros del programa de **Ingeniería de Sistemas y Computación**.
    - Selecciona solo las asignaturas del **área de software**.
    - Limpieza de texto: eliminación de caracteres especiales, tokenización y **lematización** (con SpaCy).

3.  **Clasificación Semántica (Método Principal)**:
    - Utiliza **diccionarios taxonómicos** preconstruidos (Bloom, SOLO, Temas, RA).
    - Aplica un **modelo de comparación semántica** mediante **embeddings** (SentenceTransformer) y **similitud coseno**.
    - *(Opcional/Comparativo)*: También se probaron un modelo **híbrido (MMAS)** y un método basado en **LLM (GPT-4o Mini)**.

4.  **Salida de Resultados**:
    - Genera un archivo de Excel con las columnas originales más cuatro nuevas: `BLOOM`, `SOLO`, `TEMA_CLASIFICADO`, `APRENDIZAJE_ASIGNATURA`.

## 📂 Estructura del Repositorio (Propuesta)

```text
/
├── data/                      # Datasets de ejemplo (anónimos)
│   ├── tutorias_adviser.xlsx
│   └── dataset_control_mejorado.xlsx
├── diccionarios/              # Diccionarios taxonómicos en formato JSON o CSV
│   ├── bloom_taxonomia.json
│   ├── solo_taxonomia.json
│   ├── temas_programacion.json
│   └── resultados_aprendizaje.json
├── src/                       # Código fuente del método
│   ├── preprocesamiento.py    # Limpieza, tokenización, lematización
│   ├── clasificadores.py      # Lógica de similitud coseno y ML
│   ├── main.py                # Pipeline principal
│   └── utils.py               # Funciones auxiliares
├── api/                       # Prototipo de API con FastAPI
│   ├── app.py
│   └── templates/
│       └── index.html         # Interfaz web simple
├── notebooks/                 # Notebooks de experimentación
│   └── evaluacion_modelos.ipynb
├── resultados/                # Ejemplos de archivos de salida
│   └── tutorias_clasificadas.xlsx
├── docs/                      # Documentación adicional
│   └── Anexo_Diccionarios.pdf
├── requirements.txt           # Dependencias del proyecto
├── README.md                  # Este archivo
└── LICENSE                    # Licencia Creative Commons BY 4.0
📊 Métricas de Desempeño (Resultados Clave)
El método fue evaluado con 3.794 registros reales y un dataset de control mejorado. El método Lingüístico (SBERT + similitud coseno) fue el de mejor rendimiento.

Método Evaluado	Accuracy (Global)	Precisión (Macro)	Recall (Macro)	F1-Score (Macro)
Método Lingüístico (Principal)	0.842	0.858	0.831	0.837
Método MMAS (ML + Perceptrones)	0.651	0.639	0.672	0.608
Método LLM-API (GPT-4o Mini)	0.071	0.043	0.040	0.022
Método Lingüístico (Dataset Control con verbos explícitos)	0.978	0.897	0.897	0.897
Hallazgos Principales:
El método lingüístico supera significativamente a los enfoques de ML estándar y a LLMs genéricos sin ajuste fino.

La calidad del texto (presencia de verbos, estructura gramatical) es el factor más determinante para una alta precisión.

El método es consistente (F1 ~0.47-0.45) incluso cuando se compara con criterios de clasificación manual de diferentes docentes.

El tiempo de procesamiento es de 6 a 8 minutos para clasificar más de 3,000 registros.

🧪 Cómo Usar el Proyecto
Prerrequisitos
Python 3.8 o superior

Pip (gestor de paquetes)

Instalación
Clona el repositorio:

bash
git clone https://github.com/tu-usuario/analisis-tutorias-adviser.git
cd analisis-tutorias-adviser
Instala las dependencias:

bash
pip install -r requirements.txt
(Opcional) Descarga el modelo de lenguaje de SpaCy para español:

bash
python -m spacy download es_core_news_md
Ejecución (Modo Línea de Comando)
bash
python src/main.py --input data/tutorias_adviser.xlsx --output resultados/clasificacion.xlsx
Ejecución (Modo Web - Prototipo)
bash
uvicorn api.app:app --reload
Luego abre tu navegador en http://127.0.0.1:8000 y sube un archivo de tutorías.

📌 Limitaciones y Trabajos Futuros
Limitaciones Actuales
El análisis está restringido a las asignaturas del área de software de Ingeniería de Sistemas.

No se incluyen factores psicosociales o económicos de los estudiantes.

El método depende de la calidad de redacción de los registros (sin verbos o telegráficos, el rendimiento baja).

Trabajos Futuros Propuestos
Soporte para múltiples formatos de archivo (CSV, JSON, bases de datos).

Integración con paneles de control interactivos (Power BI, Tableau) para visualización de resultados.

Implementación de medidas de seguridad y detección de archivos maliciosos.

Extensión a todas las áreas del programa de Ingeniería de Sistemas y Computación.

📄 Licencia
Este proyecto está bajo la licencia Creative Commons Attribution 4.0 International (CC BY 4.0). Puede compartir y adaptar el material, siempre que se dé el crédito adecuado.

👨‍💻 Autores e Institución
Simón José Bravo Lozano (simonjbl@example.com)

Felipe Cuervo Lorenzana (fcuervol@example.com)

Docente Tutor: MsC. Juan Carlos Barrero Calixto

Universidad Católica de Colombia
Facultad de Ingeniería - Programa de Ingeniería de Sistemas y Computación
Bogotá D.C., 2025-3

📚 Referencia
Si usas este trabajo en tu investigación, por favor cita como:

Bravo Lozano, S. J., Cuervo Lorenzana, F. (2025). Método automático para el análisis de narrativas escritas del sistema de tutorías ADVISER mediante técnicas de procesamiento de lenguaje natural de texto, ontologías semánticas y Machine Learning. (Trabajo de grado). Universidad Católica de Colombia, Bogotá.

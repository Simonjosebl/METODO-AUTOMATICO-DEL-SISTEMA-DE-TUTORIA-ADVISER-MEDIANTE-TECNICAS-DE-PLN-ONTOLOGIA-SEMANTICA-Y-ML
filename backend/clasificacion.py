# ========== IMPORTS ==========
import pandas as pd, unicodedata, re, sys, numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
sbert = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
import spacy
try:
    nlp = spacy.load("es_core_news_md")
except:
    import subprocess
    subprocess.run([sys.executable, "-m", "spacy", "download", "es_core_news_md"])
    nlp = spacy.load("es_core_news_md")

UMBRAL_BLOOM = 0.30
UMBRAL_SOLO  = 0.30
UMBRAL_TEMA  = 0.32

# ===============================================================
# 🧠 UTILIDADES
# ===============================================================
def normalize_header(s): return re.sub(r'\s+', ' ', str(s)).strip().upper()

def normalize_text(x):
    if pd.isna(x): return ''
    x = str(x).strip()
    x = unicodedata.normalize('NFKD', x)
    x = ''.join(ch for ch in x if not unicodedata.combining(ch))
    x = re.sub(r'\s+', ' ', x).strip().upper()
    return x

def normalize_str_nlp(s):
    if pd.isna(s): return ""
    s = unicodedata.normalize('NFD', str(s).lower())
    s = ''.join(ch for ch in s if unicodedata.category(ch) != 'Mn')
    s = re.sub(r'[^\w\s]', ' ', s)
    return re.sub(r'\s+', ' ', s).strip()

def encode_list(lst):
    if not lst: return np.zeros((0, sbert.get_sentence_embedding_dimension()), dtype=np.float32)
    return sbert.encode(lst, convert_to_numpy=True, normalize_embeddings=True)

def ensure_cols(df, cols):
    for c in cols:
        if c not in df.columns: df[c] = ""
    return df

# ===============================================================
# ✅ PASO 1: LECTURA ROBUSTA + FILTRO SOLO POR TEMA
#    - Soporte CSV / XLSX / XLS
#    - Encoding UTF-8 / Latin-1 automático
#    - Detecta separador
# ===============================================================
# ===============================================================
# ✅ PASO 1: FILTRAR DATA
# ===============================================================

def paso1_filtra(csv_input, csv_out):
    df = pd.read_csv(csv_input, sep=';', encoding='latin1', on_bad_lines='skip')

    col_programa = next((c for c in df.columns if 'PROGRAMA' in normalize_header(c)), None)
    col_asig = next((c for c in df.columns if 'ASIGNATURA' in normalize_header(c)), None)
    col_tema = next((c for c in df.columns if 'TEMA' in normalize_header(c)), None)

    programas = {
        normalize_text("INGENIERÍA DE SISTEMAS Y COMPUTACIÓN"),
        normalize_text("INGENIERÍA DE SISTEMAS")
    }

    asignaturas = {
        normalize_text(a) for a in [
            "ALGORITMIA Y PROGRAMACIÓN",
            "ALGORITMOS Y ANÁLISIS ESTOCÁSTICO",
            "ANÁLISIS Y DISEÑO DE ALGORITMOS",
            "ARQUITECTURA DE SOFTWARE",
            "CONSTRUCCIÓN DE SOFTWARE",
            "DISEÑO Y PROGRAMACIÓN ORIENTADA A OBJETOS",
            "ESTRUCTURAS DE DATOS",
            "INGENIERÍA DE SOFTWARE",
            "INGENIERÍA WEB",
            "PROGRAMACIÓN IMPERATIVA",
            "PROGRAMACIÓN PARA DISPOSITIVOS ANDROID",
            "SISTEMAS DISTRIBUIDOS COMPUTACIONALES"
        ]
    }

    df['_prog'] = df[col_programa].map(normalize_text)
    df['_asig'] = df[col_asig].map(normalize_text)

    dff = df[df['_prog'].isin(programas) & df['_asig'].isin(asignaturas)]
    dff = dff[[col_asig, col_tema]].dropna()

    dff.to_csv(csv_out, index=False, encoding='utf-8-sig', sep=';')
    print(f"✅ PASO 1: Filtrado → {len(dff)} filas")

    return dff


# ===============================================================
# ✅ DICCIONARIOS INTELIGENTES
# ===============================================================
# Sustantivos → verbos (acción implícita)
derivados_accion = {
    "explicacion":"explicar", "análisis":"analizar","analisis":"analizar","justificacion":"justificar",
    "implementacion":"implementar","programacion":"programar","revision":"revisar","desarrollo":"desarrollar",
    "evaluacion":"evaluar","solucion":"resolver","presentacion":"presentar","diagramas":"modelar",
    "proyecto":"desarrollar","patrones":"analizar","uml":"modelar","deploy":"desplegar","matriz":"modelar"
}

# Verbos técnicos según términos frecuentes
verbos_tecnicos = {
    "deploy web":"desplegar","deploy":"desplegar","patrones":"analizar patrones","uml":"modelar",
    "api":"consumir","react":"programar","node":"programar","frontend":"desarrollar interfaz",
    "backend":"desarrollar backend","sql":"consultar","base de datos":"modelar bd",
    "django":"programar","python":"programar","java":"programar","javascript":"programar"
}

# Verbos sugeridos por asignatura (contexto académico)
verbos_por_asignatura = {
    "ARQUITECTURA DE SOFTWARE":"diseñar arquitectura",
    "INGENIERÍA DE SOFTWARE":"analizar requerimientos",
    "ANÁLISIS Y DISEÑO DE ALGORITMOS":"resolver algoritmos",
    "ESTRUCTURAS DE DATOS":"implementar estructuras",
    "INGENIERÍA WEB":"desplegar aplicación web",
    "PROGRAMACIÓN IMPERATIVA":"programar algoritmos",
    "CONSTRUCCIÓN DE SOFTWARE":"construir software",
    "DISEÑO Y PROGRAMACIÓN ORIENTADA A OBJETOS":"modelar objetos"
}

# ===============================================================
# ✅ TAXONOMÍAS (tu lista robusta anterior)
# ===============================================================
bloom_taxonomia = {

    'Recordar': [
        'definir','enumerar','nombrar','identificar','describir','listar','reconocer',
        'recordar','consultar','anunciar','bosquejar','citar','contar','copiar',
        'deletrear','decir','encontrar','escoger','escribir','etiquetar','indicar',
        'leer','localizar','nominar','mostrar','recitar','relatar','repetir',
        'reportar','reproducir','rotular','seleccionar','registrar','ordenar',
        'memorizar','clasificar','relacionar','parear','subrayar'
    ],

    'Comprender': [
        'explicar','resumir','interpretar','clasificar','comparar','contrastar','inferir',
        'parafrasear','comprender','discutir','distinguir','expresar','ilustrar','informar',
        'ordenar','traducir','revisar','seleccionar','exponer','ejemplificar',
        'organizar','relacionar','reafirmar'
    ],

    'Aplicar': [
        'resolver','utilizar','implementar','aplicar','programar','construir','ejecutar',
        'usar','configurar','realizar','practicar','calcular','cambiar','comprobar',
        'computar','demostrar','desarrollar','dibujar','dramatizar','emplear',
        'ensamblar','entrevistar','estimar','extrapolar','fabricar','interpolar',
        'manipular','modelar','modificar','operar','organizar','planear','preparar',
        'producir', 'transformar'
    ],

    'Analizar': [
        'analizar','examinar','diferenciar','diagnosticar','estructurar','profundizar',
        'diagramar','asociar','asumir','categorizar','clasificar','comparar',
        'concluir','contrastar','cuestionar','criticar','descubrir','desmenuzar',
        'destacar','discriminar','dividir','elegir','encuestar','estimar',
        'experimentar','explicar','inspeccionar','inferir','subdividir'
    ],

    'Evaluar': [
        'evaluar','juzgar','justificar','valorar','verificar','validar','argumentar',
        'criticar','aceptar','apreciar','aprobar','categorizar','calificar',
        'considerar','debatir','decidir','defender','determinar','estimar',
        'opinar','percibir','priorizar','probar','recomendar','reglamentar',
        'significar','otorgar'
    ],

    'Crear': [
        'diseñar','crear','integrar','planificar','modelar','elaborar','innovar','generar',
        'desarrollar','proponer','adaptar','arreglar','coleccionar','combinar','compilar',
        'componer','deducir','definir','dirigir','escribir','establecer','especificar',
        'formular','generalizar','hipotetizar','idear','imaginar','inventar','maximizar',
        'minimizar','modificar','originar','prescribir','reconstruir','reunir','suponer',
        'teorizar','sintetizar','identificar'
    ]
}

solo_taxonomia = {
    'Preestructural': [
        'transmitir', 'comentar', 'copiar', 'describir', 'anotar', 'nombrar',
        'repetir', 'recitar', 'memorizar'
    ],

    'Uniestructural': [
        'identificar', 'bosquejar', 'decidir', 'calcular', 'organizar', 'reproducir',
        'elegir', 'encontrar', 'reconocer', 'definir', 'contar', 'buscar', 'escoger',
        'parafrasear', 'seleccionar', 'recordar'
    ],

    'Multiestructural': [
        'ejecutar', 'resolver', 'aplicar', 'formular', 'enlistar', 'combinar',
        'completar', 'probar', 'clasificar', 'enumerar', 'usar', 'caracterizar',
        'ilustrar', 'expresar', 'informar', 'extender', 'revisar', 'entrevistar',
        'simbolizar', 'examinar', 'secuenciar', 'recolectar'
    ],

    'Relacional': [
        'explicar', 'referir', 'analizar', 'sostener', 'comparar', 'interpretar',
        'diseñar', 'construir', 'planear', 'resumir', 'relacionar', 'argumentar',
        'relatar', 'adaptar', 'ejemplificar', 'investigar',
        'distinguir', 'mapear', 'contrastar', 'categorizar', 'observar',
        'predecir', 'combinar', 'demostrar', 'integrar', 'conectar'
    ],

    'Abstracto Extendido': [
        'discutir', 'estructurar', 'evaluar', 'razonar', 'teorizar', 'estimar',
        'criticar', 'reflejar', 'programar', 'juzgar', 'generalizar', 'implementar',
        'imaginar', 'elaborar', 'crear', 'sintetizar', 'hipotetizar', 'validar',
        'originar', 'visualizar', 'valorar', 'apreciar', 'comprender', 'desarrollar',
        'debatir', 'reflexionar', 'generar', 'proponer', 'verificar', 'innovar',
        'transformar', 'redefinir'
    ]
}

# Temas (tomamos tu última lista válida)
temas_programacion = {
    'Programación Python': [
            'matrices en python', 'listas doblemente enlazadas', 'manejo de tda listas',
            'clases en entornos de programacion python - seguimiento estudiante',
            'revision de proyecto de aplicacion en python',
            'listas', 'listas simplemente encadenadas', 'multilistas', 'impresion listas',
            'listas - tutoria de diego rincon', 'arreglos en phyton',
            'instalacion python', 'listas doblemente enlazada circular',
            'tipos abstractos de datos aplicados en python', 'listas dobles',
            'multilistas para productos de tienda',
            'algoritmos en python comando range y for', 'rpc en python',
            'recorrido de listas', 'ejercicio multilistas maquinas dispensadoras',
            'recorrido listas', 'funciones en python', 'listas enlazdas',
            'arreglos en python', 'listas enlazada simples', 'ejercicio multilistas',
            'listas enlazadas', 'algoritmos con python', 'listas enlazadas simples',
            'matrices y listas', 'listas enlazadas proyectos',
            'arreglos y tuplas en python', 'multi listas',
            'multilistas para maquinas dispensadoras', 'listas simples',
            'ejercicios de listas enlazadas en c++',
            'programa de python mvc error de conexion db',
            'codificacion de python para manejo de instancias en uso de listas',
            'mutilistas', 'listas en lazadas',
            'programacion de clases y objetos en python - seguimiento estudiante',
            'update y delete con firebase desde python',
            'listas simplemente enlazadas',
            'manejo de variables y tipos de datos en python',
            'listas doblemente enlazadas circulares', 'uso de libreria tk inter',
            'apuntadores sobre listas', 'manejo de archivos y listas',
            'implementacion de tads en codigos python. validacion parcial',
            'listas cadenas', 'mutlilistas'
        ],
        'Programación VBA': [
            'sentencias en vba.', 'dudas visual basic',
            'creacion de formularios de interfaz de usuario en vba',
            'dudas matrices en visual basic',
            'especificacion del problema de investigacion para solucionarlo atraves de programacion en vba',
            'configuracion de la pestana programador en vba.',
            'error ejercicio interface grafica vba.',
            'matrices y vectores en vba integrados al proyecto integrador',
            'dudas en realizacion de algoritmos y visual basic',
            'concepto basicos visual basic',
            'dudas matrices visual basic',
            'series de taylor implementadas en vba',
            'dudas en algoritmos y visual basic',
            'dudas en programacion en visual basic',
            'arreglos y vectores en vba integrados al proyecto integrador',
            'dudas con matrices en visual basic',
            'vectores en visual basic',
            'aplicacion de vba centrada en el proyecto integrador',
            'vba sentencias.', 'matrices en vba.',
            'conceptos introduccion visual basic', 'matrices en vba',
            'visual basic - introduccion', 'vba'
        ],
        'Programación JavaScript': [
            'desarrollo de crud integrando html javascript java y postgres',
            'expresiones regulares en java script',
            'funciones en javascript',
            'funciones java script', 'javascript',
            'validacion de tipos abstractos de datos en javascript para proyecto integrador.'
        ],

        'Programación Java': [
        'programa java recurrencias java',
        'programa en java - librería swing',
        'interfaz gráfica en java',
        'sumatoria finita en java',
        'desarrollo java',
        'archivos en java',
        'lenguaje java',
        'proyecto integrador y ejercicios java',
        'programa en java',
        'migración de modelo vista controlador a java sever faces',
        'programas de recurrencia java',
        'diseño y poo - código java',
        'sumatoria finita java',
        'programas de recurrencia en java',
        'programación java',
        'programas recurrencia java',
        'array list en java',
        'presentación programas java',
        'codificación de objetos en java',
        'conceptos java-objetos',
        'interfaces en java',
        'conexión entre java y html utilizando javascript y postgress',
        'ecuaciones de recurrencia en java',
        'java - objetos',
        'revisión de código con énfasis en condicionales en código java',
        'programas java',
        'acompañamiento java_home para taller',
        'lectura de datos en java',
        'programas en java clases y métodos',
        'programas en java métodos de recurrencia.',
        'dudas en java',
        'dudas taller de java',
        'java y clases',
        'programación clases y objetos en java',
        'bases de datos _ código en java',
        'java rmi',
        'programas en java clases y métodos.',
        'programas java recurriencia.',
        'dudas en el desarrollo de programas en java',
        'programación en java',
        'java interfaces',
        'pilas  en java',
        'interfaz gráfica de java'
    ],
    'Programación Robot': [
        'arduino',
        'diseño de prototipo de arduino y diagrama de gantt',
        'configuración robot obstáculos',
        'arduino en c++',
        'configuración robot de obstáculos',
        'programación robot velocista',
        'programación de robot velocista con sensores'
    ],
    'Algoritmia': [
        'aplicación de algoritmos de npl',
        'algoritmos de ordenamiento',
        'algoritmos ruta minima',
        'consulta taller algoritmos',
        'algoritmo ruta minima',
        'algoritmo de ruta mínima.',
        'algoritmos de programacion dinamica ruta minima',
        'proyecto algoritmos',
        'algoritmos prim programación dinámica',
        'instrucciones de entrada y salida - pseint',
        'aplicaicón de algoritmos',
        'algoritmo ruta  minima',
        'investigación algoritmos para gaming',
        'algoritmos recursivos e iterativos',
        'algoritmo',
        'algoritmo en psint',
        'algoritmo de ruta minima',
        'algoritmo de euler',
        'algoritmos con pseint',
        'algoritmoa aplicados',
        'proyecto final- aplicación de algoritmos estocásticos y redes bayesianas',
        'dudas en pseint',
        'algoritmo de divide y vencerás',
        'algoritmo de vuelta atrás o backtracking',
        'consulta taller algoritmo',
        'algoritmo ruta mas corta grafo matriz',
        'algoritmos para recorrido de grafos',
        'algoritmo kruskal',
        'duda de algoritmos',
        'codificación algoritmos',
        'variables y tipos de algoritmos',
        'pregunta de investigación para algoritmos de perfilamiento de clientes',
        'conceptos de algoritmos',
        'aplicación de algoritmos de ordenamiento',
        'estructura de los algoritmos',
        'algoritmo de conway',
        'algoritmos de predicción',
        'algoritmo divide y vencerás',
        'algoritmo round robin y memoria dinamica',
        'programación en pseint',
        'aplicación de algoritmos',
        'algoritmos de arboles',
        'algoritmo ruta critica mínma',
        'algoritmos de árboles',
        'algoritmo de naive bayes dataset del clima',
        'algoritmo cinetico de montecarlo',
        'algoritmo de dijkstra',
        'introducción a algoritmos',
        'pseudocódigo',
        'algoritmos de recomendación',
        'duda sobre algoritmo de dikjstra',
        'algoritmo cyk',
        'algoritmo de ruta más corta  matrices',
        'algoritmo de euclides',
        'algoritmo de prim',
        'varianza en el algoritmo de k-means',
        'algoritmos voraces',
        'algoritmo de montecarlo',
        'implementacion del algoritmo de regresion',
        'consulta sobre algoritmo dijkstra',
        'duda sobre análisis y el diseño de un algoritmo',
        'complejidad de algoritmos',
        'algoritmo de arrreglo librería numpy plt',
        'algoritmo ruta màs corta vía matrices',
        'algoritmos en los video juegos',
        'algoritmo de k-means',
        'pseudocódigo para el diseño de algoritmos',
        'algoritmos de ruta minima',
        'algoritmos',
        'algoritmo de ruta mìnima',
        'pseudocódigos',
        'consulta sobre algoritmos',
        'operaciones elementales en algoritmos',
        'algoritmo de vuelta atrás (backtracking)',
        'consulta algoritmo voraz.',
        'algoritmos aplicados',
        'algoritmo de ordenamiento',
        'algoritmos en video juegos',
        'algoritmo dijkstra',
        'algoritmo ruta critica',
        'algoritmos de recurrencia',
        'algoritmos de euclides',
        'algoritmo backtracking',
        'algoritmos para aplicaciones',
        'diagramas de flujo',
        'codificación de algoritmo de cifrado en c++',
        'algoritmo cinètico de montecarlo',
        'implementación del algoritmo de regresión',
        'algoritmos backtracking',
        'algoritmos recursivos',
        'investigación algoritmos para web services',
        'algoritmo de descenso de gradiente',
        'algoritmo implicito de euler'
    ],
      'Proyecto Integrador': [
        'revisión documento diseño e implementación de un sistema de visión artificial para detectar basuras',
        'proyecto integrador.',
        'revisión proyecto integrador',
        'definición de problema en proyecto integrador',
        'proyecto integrador - sistema de visión artificial',
        'integracion de sentencias repetitivas y condicionales al proyecto integrador',
        'recomendación proyecto integrador',
        'validación de tipos abstractos de datos para proyecto integrador.',
        'requisitos funcionales y no funcionales en proyecto integrador',
        'revisión documento aplicación cero colillas en las zonas aledañas de la universidad catolica de colombia',
        'complejidad computacional en proyecto integrador',
        'atributos de calidad de software en el proyecto integrador',
        'proyecto integrador',
        'consulta proyecto integrador',
        'introducción proyecto integrador',
        'revisión mecanismo de validación de formularios del proyecto integrador',
        'verificación artefactos proyecto integrador',
        'integración de sentencias repetitivas al proyecto integrador',
        'recomendaciones proyecto integrador',
        'sentencias selectivas y proyecto integrador',
        'revisión del contexto del desarrollo del proyecto integrador en el marco del ciclo de vida de la metodología scrum',
        'análisis de algortimos para proyecto integrador',
        'definición y estructuración de proyecto integrador de las asignaturas de ingeniería web y arquitectura de software',
        'definición de problema ? proyecto integrador',
        'problemas de dos diemsnione y proyecto integrador',
        'revisión de pregunta problema y justificación de proyecto integrador',
        'introducción a proyecto integrador',
        'documentación proyecto integrador en repositorio remoto',
        'diligenciamiento de formatos de proyecto integrador',
        'proyecto integrador - sistema de reutilización de aguas residuales',
        'proyecto integrador ? diseño de página web ? concientización contaminación ambiental.',
        'revisión documento recolección de agua lluvia para su uso en cultivos',
        'programación aplicada al proyecto integrador',
        'ingeniería de software aplicada a proyecto integrador.',
        'proyecto integrador multilista',
        'ingeniería de software aplicada a proyecto integrador',
        'definición del proyecto integrador',
        'especificaciones proyecto integrador',
        'validación proyecto integrador'
    ],
    'Investigación': [
        'validación requerimientos para criterios de aceptación 1',
        'validación criterios 2',
        'customer relationship management - validación conferencia coniiti',
        'validación del alcance del ensayo',
        'validación de arquitectura del sistema',
        'validación requerimientos y alcance de proyecto de automatización',
        'validación del modelo de clases',
        'validación de la implementación del sw',
        'validación requerimientos lazycolumn',
        'validación del mockup definido para la aplicación',
        'validación taller teorema del consenso',
        'validación de arquitectura para proyecto de grado - motivaciones arquitecturales y atributos de calidad',
        'infraestructura de ti para el futuro - validación coniiti',
        'validación alcance y uml diseño',
        'instrumento de validación de datos para estudio estocástico con cadenas de markov',
        'validación de requerimientos para aplicación',
        'validación del alcance del software',
        'validación de requerimientos para proyecto',
        'revisión documento final de definición y alcance',
        'validación html y css - parcial',
        'validación criterios de endpoints',
        'validación de proyecto y alcance de navega seguro',
        'herramientas en la construcción de software - validación coniiti',
        'validación scope para propuestas de proyecto',
        'revisión documento el cambio climático y sus efectos en la agricultura colombiana',
        'apoyo revisión metodología de investigación',
        'metodos de validación producto desplegado',
        'validación de kotlin',
        'validación del documento de arquitectura',
        'validación prototipo',
        'validación desarrollo aplicación movíl coniiti',
        'validación de requerimientos según criterios del modelo web',
        'validación del alcance de la arquitectura en el documento',
        'validación objetivos de la arquitectura',
        'determinación de criterios de validación',
        'validación de alcance de la investigación',
        'validación de aplicación móvil android',
        'validación de prototipo',
        'validación de criterios de aceptacion',
        'validación de arquitectura',
        'validación metodología',
        'validación propuesta pi',
        'validación del alcance del entregable final'
    ],
    'Estadística y Matemáticas': [
        'medidas de tendencia central',
        'teoría de colas mmm multicanal',
        'cadenas de markov',
        'serie fibonacci',
        'cadenas de markov.',
        'cadenas de markov - vector de estados iniciales',
        'formulación de objetivos para el problema de teoría de colas',
        'teoría de colas multicanal',
        'aplicación de las cadenas de markov en análisis de datos',
        'aplicación de cadenas de markov en análisis de datos',
        'cadenas de markov - ejercicio propuesto taller',
        'repaso markov y teoría de colas',
        'cadena de markov',
        'teoría de colas'
    ],
    'Bases de Datos': [
        'bases de datos datamart olap'
    ],
      'Otros':[
          'estructura de datos colas',
    'pruebas en sistemas distribuidos',
    'arbor recubridor mínimo',
    'matrices e imagenes',
    'flujo de trabajo en el software knime para el dataset del vino',
    'despliegue en servidor deta',
    'compartir el alcance del proyecto navega seguro',
    'accesando a las api',
    'clases y métodos',
    'simetría en funciones.',
    'modelo entidad relación',
    'calculo de valor esperado y varianza',
    'kubernetes',
    'verificación requerimientos',
    'arreglos unidimensaionales',
    'definición del alcance del entregable del software',
    'dudas en tema pilas',
    'definir el alcance de la aplicación navega seguro',
    'revisión programas en c++ funciones y p. íntegrador',
    'integración de backen y frontend utilizando srpring boot y react',
    'escalas de gráficas',
    'programas de recurrencias',
    'consulta sobre interfaz gráfica',
    'cifrado con matrices',
    'método cinètico de montecarlo',
    'adición en namespace de gitlab',
    'definicion del alcance de la aplicacion del tercer corte',
    'complejidad computacionl',
    'levantamiento de requerimientos',
    'dudas en poo',
    'conexión repositorio en servidor remoto',
    'árbol avl',
    'diagramas uml diferencias y usos ejemplos.',
    'consulta problema agente viajero',
    'diseño del sistema',
    'caos de uso',
    'condicional if',
    'preguntas quiz',
    'programación dinámica',
    'requerimientos.',
    'modelado a través de uml',
    'diseño orientado a objetos',
    'árbol binario de búsqueda',
    'estructura de los objetivos específicos para el proyecto de series de tiempo de clima',
    'definición prototipo y diagrama de gantt',
    'pruebas de funcionalidad',
    'defiicion de apificacion',
    'recepción documento proyecto',
    'aplicación android',
    'redes de computadoras',
    'arreglos',
    'apuntadores a matrices',
    'evaluación de arquitecturas de software',
    'manejo de referencias',
    'lema de arden',
    'programación web - css',
    'definición del problema para la asignatura programación imperativa.',
    'corrección parcial.',
    'ajustes en gitlab',
    'operadores y orden de operadores',
    'definicion del alcance de la aplicacion',
    'conectores',
    'inducción matemática',
    'multilista para minimercado',
    'bayes',
    'apoyo en la aclaración de dudas sobre metodología methontology para el desarrollo de una ontología de propósito especifico.',
    'complejidad computacional y máquina de turing',
    'codificación de iteraciones',
    'ciclos',
    'customer relationship management',
    'especificación del alcance del proyecto de clase',
    'proyecto integrado y proyecto de curso',
    'documentación',
    'software dudas',
    'jbutton',
    'aloritmo ruta minima',
    'definición problema objetivos y relación con la programación imperativa',
    'algortimo ruta más corta matrices',
    'método de euler',
    'archivos',
    'estructuras selectivas',
    'vectores y matrices en c',
    'arbol recurrente recubridor mínimo.',
    'struct',
    'revisión general del alcance del anteproyecto',
    'conexión a mysql',
    'estructura condicional if',
    'límites de sumatoria',
    'servidor dns aws',
    'redacción escrito texto crítico',
    'instrucciones de entrada y salida',
    'revisión ejecución taller de raft consensus',
    'revisión criterios de aceptación pi',
    'consulta sobre selenium',
    'resolución de problema sobre triangulo egipcio',
    'conexion a repositorio remoto',
    'métodos',
    'consulta estructuras pilas y colas',
    'complejidad polinomial',
    'determinación de arquitectura sgc',
    'peer to peer',
    'evaluación de los elementos mínimos de un proyecto',
    'creación subgrupo gitlab',
    'definicion del alcance de la arquitectura a implementar',
    'cadenas y caracteres',
    'revisión test unitarios',
    'taller',
    'resolución de un diagrama de flujo datos teniendo como referente para los objetos la norma iso 5807',
    'cálculo de pendiente ejercicio.',
    'dudas en realización de programas en vb',
    'estructura de objetivo general y específicos para un proyecto',
    'manejo de intents',
    'proyecto',
    'distribución bninomial',
    'revisión manual técnico del proyecto de aula',
    'derivadas parciales',
    'formulación del planteamiento del proyecto de aplicativo para seguridad en taxis y de pregunta de investigación.',
    'validaciones html',
    'casos de uso',
    'estructuras anidadas en pilas',
    'cadenas en c++',
    'actividad proyecto práctico',
    'definición de arquitectura',
    'requerimientos funionales',
    'transacción a 2 fases - 2pc, transacción a 3 fases - 3pc',
    'definir el alcance de la arquitectura de procesos',
    'definición plan de trabajo proceso de migración',
    'dudas arreglos en c++',
    'matrices y funciones',
    'proyecto colas',
    'xtreme programing',
    'grafos',
    'variables en programación',
    'como plantear un saas para un anteproyecto siguiendo los lineamientos de as.',
    'definición el alcance y evolución de la herramienta',
    'actualización de metodología',
    'lenguaje c++',
    'ciclos y razones de cambio',
    'arreglos vectores',
    'operaciones entre matrices',
    'revisión de temas tratados (timestamp) para próxima evaluación.',
    'árboles n-arios',
    'proyecto qa',
    'algebra booleana',
    'configuración wordpress',
    'revisión referencias y construcción documento',
    'manejo de presupuestos proyecto web-firebase',
    'problemas con colas de enlace simple',
    'capa de presentación',
    'manejo de estructuras en c++',
    'revisión endpoints',
    'concepción del ciclo de vida desde el enfoque devops asociado a scrum',
    'repositorios remotos en gitlab',
    'funciones y procedimientos',
    'repositorio remoto',
    'revisión de redacción de premisas y conclusiones en la estructuración de un artículo de investigación en ingeniería de software',
    'litas enlazadas',
    'complejidad temporal',
    'impresion 3d',
    'uso de sistema de control de versiones',
    'creación de contenidos dinámicos con .net',
    'metodologias',
    'manejo de variables globales locales y pilas',
    'revisión de proyecto de procesamiento de imágenes',
    'distribución binomial',
    'estimación de software',
    'dudas del estudiante',
    'librerías en c++',
    'métodos y objetos',
    'aws concepto historia y servicios',
    'resolución de ecuacion de 2do grado a partir del signo del discriminante',
    'definición de arquitectura de la aplicación',
    'uso de la norma ieee 830',
    'exposición prototipos',
    'vistas de arquitectura',
    'conexión de la base de datos',
    'cadenas en c',
    'consulta o-grande',
    'vectores',
    'ecuacion caracterìstica',
    'definición del alcance del proyecto',
    'dudas arreglos',
    'consulta sobre metodología methontology para el desarrollo de una ontología de propósito especifico',
    'distribución normal',
    'taller docker y dragon boat',
    'métodos de ordenamiento',
    'cronograma y presupuestos',
    'arreglos y matrices en c++',
    'remisión',
    'errores de logica y operadores logicos',
    'programación dinámica problema de la mochila',
    'revision proyecto',
    'definir la arquitectura de referencia',
    'definición de objetivos para una app android',
    'resolucion ejercicio indices separados lectura y escritura',
    'inquietud sobre tipos de arquitectura',
    'estructuras simples y anidadas',
    'revisión de arquitectura y alcance',
    'tutoría estudio financiero',
    'proceso de cadenas',
    'lectura de cadenas',
    'protocolo rpc',
    'manejo de gitlab para trabajo colaborativo',
    'complejidad computacional ecuaciones de recurrencia temas de examen',
    'dudas cilos',
    'conceptos de objetos y gui',
    'grafor',
    'vista arquitectural - consulta práctica empresarial',
    'try catch',
    'conectando a las apis',
    'creación de subgrupos en gitlab',
    'problema de la mochila',
    'revisión taller sd',
    'ecuaciones y su función',
    'vectores y apuntadores en c++',
    'presentación artículo académico',
    'arquitectura de datos',
    'api',
    'dudas en ciclos',
    'creación de objetos',
    'ieee 830',
    'retrofit criterios',
    'practica de presentación de proyecto',
    'proyecto final - dudas de aplicación en inteligencia artificial',
    'desarrollo de móviles',
    'requerimientos aplicación android',
    'diagramas de gantt',
    'documentación de repositorio en proyecto web',
    'arquitectura de software',
    'repetitivas o bucles',
    'corrección planteamiento del problema',
    'revision endpoints',
    'preparación del despliegue',
    'diseño documental del proyecto',
    'duda arreglos',
    'ciclo mientras',
    'vistas arquitecturales - seguimiento cierre materia',
    'revisión uml: casos de uso',
    'funciones y límites',
    'retroalimentación de proyecto',
    'redacción de objetivos',
    'procesos iterativos',
    'estructuras',
    'adición subgrupos en repositorio remoto',
    'manual de documentaciòn técnica',
    'reglas del tena de exposición.',
    'estructura if then else',
    'aplicación de sistemas distribuidos',
    'revisión seguimiento sobre estado en asignaturas.',
    'threads, comunicaciones, tipos, acid ,transacción a 2 fases - 2pc transacción a 3 fases - 3pc, bloqueo a 2 fases - 2pl'
    ]
}


# ===============================================================
# ✅ DETECCIÓN HÍBRIDA DE ACCIÓN
# ===============================================================
def detect_action_words(text_norm, doc, asignatura):
    lemmas = [normalize_str_nlp(t.lemma_) for t in doc if t.pos_=='VERB' and not t.is_stop]

    for w,v in derivados_accion.items():
        if w in text_norm and v not in lemmas: lemmas.append(v)

    for w,v in verbos_tecnicos.items():
        if w in text_norm and v not in lemmas: lemmas.append(v)

    if asignatura:
        for key, v in verbos_por_asignatura.items():
            if key in asignatura.upper() and v not in lemmas:
                lemmas.append(v)

    return lemmas

# ===============================================================
# ✅ CLASIFICACIONES
# ===============================================================
def classify_by_taxonomy(doc, taxonomy_docs, umbral, kind, asignatura):
    text_norm = normalize_str_nlp(doc.text)

    if any(w in text_norm for w in ['duda','no entiendo','no se','pregunta']):
        return ('Preestructural' if kind=='solo' else 'Recordar',1.0)

    lemmas = detect_action_words(text_norm, doc, asignatura)
    if not lemmas: return ('NO HAY VERBO',0)

    emb = encode_list(lemmas)
    scores = {cat: float(cosine_similarity(emb, vecs).max()) for cat, vecs in taxonomy_docs.items() if vecs.size>0}

    best = max(scores, key=scores.get); score = scores[best]
    return (best, score) if score>=umbral else ('NO HAY VERBO', score)

def classify_tema(text, norm, umbral):
    for tema, keys in temas_normalizados.items():
        if any(k in norm for k in keys): return tema
    emb = encode_list([norm])
    best,score='NO TEMA',0
    for tema,vec in tema_docs.items():
        sim=float(cosine_similarity(emb,vec).max())
        if sim>score: best,score=tema,sim
    return best if score>=umbral else 'NO TEMA'

# ===============================================================
# ✅ CONSTRUCCIÓN DE EMBEDDINGS TAXONOMÍAS
# ===============================================================

# Embeddings para BLOOM
bloom_docs = {}
for cat, verbs in bloom_taxonomia.items():
    textos = [normalize_str_nlp(v) for v in verbs]
    bloom_docs[cat] = encode_list(textos)

# Embeddings para SOLO
solo_docs = {}
for cat, verbs in solo_taxonomia.items():
    textos = [normalize_str_nlp(v) for v in verbs]
    solo_docs[cat] = encode_list(textos)

# ===============================================================
# ✅ PREPARAR EMBEDDINGS PARA TEMAS
# ===============================================================

temas_normalizados = {t: [normalize_str_nlp(k) for k in keys]
                      for t, keys in temas_programacion.items()}

tema_docs = {}
for tema, keys in temas_normalizados.items():
    embeddings = encode_list(keys)
    tema_docs[tema] = embeddings if embeddings.size>0 else encode_list([])


def clasificar_dataset(df, out):
    df = ensure_cols(df,['SOLO','BLOOM','TEMA_CLASIFICADO'])
    docs=list(nlp.pipe(df['TEMA O CONCEPTO'].fillna('').astype(str)))

    for i,doc in enumerate(docs):
        asignatura = df.iloc[i,0] if df.shape[1]>0 else None
        text = doc.text; norm = normalize_str_nlp(text)

        solo,_  = classify_by_taxonomy(doc, solo_docs, UMBRAL_SOLO,'solo', asignatura)
        bloom,_ = classify_by_taxonomy(doc, bloom_docs,UMBRAL_BLOOM,'bloom',asignatura)

        df.at[i,'SOLO']=solo; df.at[i,'BLOOM']=bloom
        df.at[i,'TEMA_CLASIFICADO']=classify_tema(text, norm, UMBRAL_TEMA)

    df.to_csv(out,sep=';',index=False)
    return df

# ===============================================================
# ✅ PASO MATCH RA
# ===============================================================
def paso3(xin,xout):
    df=pd.read_excel(xin).copy()
    df.columns=df.columns.str.strip()
    ra_col=[c for c in df.columns if 'APREND' in c.upper() or 'RESULT' in c.upper()][0]
    df.rename(columns={ra_col:'APRENDIZAJE DE ASIGNATURA','Materia ':'TEMA','Materia':'TEMA'},inplace=True)
    df.to_excel(xout,index=False); return df

def paso4(ccsv,cref,out):
    df_csv=pd.read_csv(ccsv,sep=';'); df_ref=pd.read_excel(cref)
    L=df_csv['TEMA O CONCEPTO'].fillna('').map(normalize_str_nlp).tolist()
    R=df_ref['APRENDIZAJE DE ASIGNATURA'].fillna('').map(normalize_str_nlp).tolist()
    q,r=encode_list(L),encode_list(R)
    best = cosine_similarity(q,r).argmax(axis=1)
    df_csv['APRENDIZAJE_ASIGNATURA']=[df_ref.at[j,'APRENDIZAJE DE ASIGNATURA'] for j in best]
    df_csv.to_excel(out,index=False); return df_csv


# ----------------- Ejecutar pipeline para un archivo dado -----------------
import matplotlib.pyplot as plt
from pathlib import Path

def ejecutar_pipeline(nombre_archivo_csv: str):
    base = Path(__file__).parent
    uploads = base / "uploads"
    uploads.mkdir(exist_ok=True)

    # Rutas base
    CSV_INPUT_DATA = uploads / nombre_archivo_csv
    CSV_FILTRADO = uploads / f"{CSV_INPUT_DATA.stem}_filtrado.csv"
    CSV_CLASIFICADO = uploads / f"{CSV_INPUT_DATA.stem}_clasificado.csv"
    XLSX_INPUT_REF = base / "Resultados-de-aprendizaje-Sistemas.xlsx"
    XLSX_REF_PROCESADO = uploads / f"{CSV_INPUT_DATA.stem}_procesado.xlsx"
    OUTPUT_FINAL_XLSX = uploads / f"{CSV_INPUT_DATA.stem}_resultado.xlsx"

    paso1_filtra(CSV_INPUT_DATA, CSV_FILTRADO)
    df = pd.read_csv(CSV_FILTRADO, sep=';', on_bad_lines='skip')
    clasificar_dataset(df, CSV_CLASIFICADO)
    paso3(XLSX_INPUT_REF, XLSX_REF_PROCESADO)
    paso4(CSV_CLASIFICADO, XLSX_REF_PROCESADO, OUTPUT_FINAL_XLSX)
    rutas_graficas = generar_graficas(OUTPUT_FINAL_XLSX)
    print("Pipeline completado exitosamente.")
    print("Gráficas generadas:", rutas_graficas)
    return OUTPUT_FINAL_XLSX

# -------------------------
# Función para generar gráficas
# -------------------------
def generar_graficas(output_final_xlsx: Path):
    df = pd.read_excel(output_final_xlsx)
    columnas = ["SOLO", "BLOOM", "TEMA_CLASIFICADO"]

    base = Path(__file__).parent
    graficas_dir = base / "uploads" / "graficas"
    graficas_dir.mkdir(parents=True, exist_ok=True)

    rutas_imagenes = []
    for columna in columnas:
        if columna not in df.columns:
            print(f"⚠️ Columna '{columna}' no encontrada en el archivo. Se omite.")
            continue

        conteo = df[columna].value_counts()
        plt.figure(figsize=(10, 6))
        conteo.plot(kind='bar', color='skyblue')
        plt.title(f"Conteo de {columna}")
        plt.xlabel(columna)
        plt.ylabel("Frecuencia")
        plt.xticks(rotation=45)
        plt.tight_layout()

        ruta_imagen = graficas_dir / f"{columna}_conteo.png"
        plt.savefig(ruta_imagen)
        plt.close()

        rutas_imagenes.append(ruta_imagen.name)

    return rutas_imagenes
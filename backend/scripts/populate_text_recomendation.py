import os
import sys
import django
import pandas as pd
from django.utils.encoding import smart_str

# [JV] If working without venv, run this
if False:
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if path not in sys.path:
        sys.path.append(path)


# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from prevcad.models import TextRecomendation

# Ruta al archivo Excel
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'text_recomendation.xlsx')

# Cargar el archivo Excel con manejo de errores
try:
    df = pd.read_excel(file_path)
    print("Archivo Excel cargado exitosamente.")
except FileNotFoundError:
    print(f"Error: No se encontró el archivo en la ruta {file_path}.")
    exit()
except Exception as e:
    print(f"Error al cargar el archivo Excel: {e}")
    exit()

# Limpiar los nombres de las columnas
df.columns = df.columns.str.strip()

# Normalizar nombres de columnas si es necesario
column_map = {
    'TEMA (Templado)': 'theme',
    'Categoría': 'category',
    'Sub-categoría': 'sub_category',
    '¿Sabía qué?': 'learn',
    'Recuerde!': 'remember',
    'Dato': 'data',
    'Dato práctico': 'practic_data',
    'Contexto/Explicación': 'context_explanation',
    'Link (zbib.org para citas APA)': 'quote_link',
    'Keywords': 'keywords'
}

df.rename(columns=column_map, inplace=True)

# Validar columnas faltantes
missing_columns = [col for col in column_map.values() if col not in df.columns]
if missing_columns:
    print(f"Error: Faltan las siguientes columnas en el archivo Excel: {missing_columns}")
    exit()

# Reemplazar valores NaN por cadenas vacías para evitar errores
df.fillna('', inplace=True)

# Función para validar datos por fila
def validate_row(row, index):
    required_fields = ['category', 'data']
    for field in required_fields:
        if not row[field]:
            print(f"Advertencia: Fila {index + 1} tiene el campo obligatorio '{field}' vacío.")
            return False
    return True

# Iterar sobre las filas y guardarlas en la base de datos
success_count = 0
error_count = 0
for index, row in df.iterrows():
    if not validate_row(row, index):
        print(f"Fila {index + 1} omitida debido a datos incompletos.")
        error_count += 1
        continue

    recomendation = TextRecomendation(
        theme=smart_str(row['theme']),
        category=smart_str(row['category']),
        sub_category=smart_str(row['sub_category']),
        learn=smart_str(row['learn']),
        remember=smart_str(row['remember']),
        data=smart_str(row['data']),
        practic_data=smart_str(row['practic_data']),
        context_explanation=smart_str(row['context_explanation']),
        quote_link=smart_str(row['quote_link']),
        keywords=smart_str(row['keywords'])
    )
    try:
        # Guardar la recomendación en la base de datos
        recomendation.save()
        success_count += 1
        print(f"Fila {index + 1} guardada exitosamente.")
    except Exception as e:
        print(f"Error al guardar la fila {index + 1}: {e}")
        error_count += 1

print(f"Proceso completado: {success_count} filas guardadas exitosamente, {error_count} errores encontrados.")

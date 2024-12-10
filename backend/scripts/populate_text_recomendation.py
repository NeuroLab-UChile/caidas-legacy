

# Importar el modelo
import os
import django

# Configura el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()
from prevcad.models import TextRecomendation
from django.utils.encoding import smart_str
import pandas as pd

# Cargar el archivo Excel
current_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_dir, 'text_recomendation.xlsx')

df = pd.read_excel(file_path)

# Limpiar los nombres de las columnas
df.columns = df.columns.str.strip()

# Verificar nombres de columnas
print(df.columns)

# Mapea las columnas de Excel a los campos del modelo
for index, row in df.iterrows():
  recomendation = TextRecomendation(
    theme=(row['TEMA (Templado)']),
    category=smart_str(row['Categoría']),
    sub_category=smart_str(row.get('Sub-categoría', '')),
    learn=smart_str(row.get('¿Sabía qué?', '')),
    remember=smart_str(row.get('Recuerde!', '')),
    data=smart_str(row.get('Dato', '')),
    practic_data=smart_str(row.get('Dato práctico', '')),
    context_explanation=smart_str(row.get('Contexto/Explicación', '')),
    quote_link=row.get('Link (zbib.org para citas APA)', ''),
    keywords=smart_str(row.get('Keywords', ''))
  )

  # Guardar la recomendación en la base de datos
  recomendation.save()

print("Datos cargados exitosamente.")

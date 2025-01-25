#!/bin/bash
#./run_local.sh
# Puertos definidos por el usuario
BACKEND_PORT=8000
FLUTTER_PORT=8081
REACT_PORT=3001

# Obtener el directorio del script

SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

# Navegar al directorio del backend y ejecutar los comandos

cd "$SCRIPT_DIR/backend"
python3 -m venv .venv

source .venv/bin/activate
poetry install
python manage.py makemigrations
python manage.py migrate
python manage.py runserver &
cd "$SCRIPT_DIR/frontend"
#flutter pub get
#flutter run -d chrome



# Navegar al directorio de la aplicación Flutter y ejecutar los comandos

# Descomentar las siguientes líneas si quieres ejecutar la aplicación React
# Navegar al directorio de la aplicación React y ejecutar los comandos
# cd "$SCRIPT_DIR/admin-interface"
# npm install
# npm start -- --port $REACT_PORT &

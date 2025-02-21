WeFlow - Sistema de Gestión Médica

Descripción General

WeFlow es un sistema integral para la gestión de evaluaciones médicas, citas y recomendaciones profesionales. Su objetivo es facilitar la administración de pacientes y profesionales de la salud mediante una plataforma moderna y eficiente.

Características Principales

Gestión de usuarios y perfiles médicos

Sistema de evaluaciones y recomendaciones personalizadas

Agenda para la programación de citas médicas

Plantillas de categorías de salud

Interfaz moderna basada en Tailwind CSS

Tecnologías Utilizadas

Backend

Django (Framework principal)

PostgreSQL (Base de datos)

Django Rest Framework (DRF) (API REST)

SimpleJWT (Autenticación con tokens)

Apache2 (Servidor web)

Frontend

React Native (Interfaz móvil)

TypeScript (Tipado estático)

Expo (Desarrollo y despliegue)

AsyncStorage (Almacenamiento local)

Instalación y Configuración

1. Clonar el repositorio

git clone https://github.com/tu-usuario/weflow.git
cd weflow

2. Configurar el entorno virtual (Backend)

python -m venv .venv
source .venv/bin/activate  # En Windows usar: .venv\Scripts\activate

3. Instalar dependencias (Backend)

pip install -r backend/requirements.txt

4. Configurar variables de entorno

Crear un archivo .env en la carpeta backend con las siguientes variables:

SECRET_KEY=tu_clave_secreta
DEBUG=True
DATABASE_URL=postgres://usuario:password@localhost:5432/weflow_db

5. Aplicar migraciones y crear un superusuario

python backend/manage.py migrate
python backend/manage.py createsuperuser

6. Iniciar el servidor de desarrollo (Backend)

python backend/manage.py runserver

7. Iniciar el frontend (React Native)

cd frontend
npm install
npx expo start

Despliegue en Producción

1. Configurar Apache2 para Django

Asegurarse de que el servicio Apache2 está activo:

sudo systemctl restart apache2
sudo tail -f /var/log/apache2/error.log  # Ver logs de errores
sudo tail -f /var/www/we-flow/backend/django.log  # Ver logs de Django

2. Asignar permisos correctos al backend

sudo chown -R www-data:www-data /var/www/we-flow/backend
sudo chmod -R 755 /var/www/we-flow/backend

3. Recargar el servicio Apache2

sudo systemctl restart apache2

Documentación Adicional

Para detalles sobre la configuración y uso del panel administrativo, consulta la siguiente documentación:
Documentación del Panel Administrativo

Contribución

Si deseas contribuir a WeFlow, sigue estos pasos:

Haz un fork del repositorio.

Crea una rama para tu funcionalidad (git checkout -b mi-nueva-funcionalidad).

Realiza tus cambios y haz commit (git commit -m "Agregada nueva funcionalidad").

Haz push a tu rama (git push origin mi-nueva-funcionalidad).

Abre un Pull Request.

Licencia

Este proyecto está bajo la licencia MIT.
"""
Configuración central de la aplicación.

Aquí se define todo lo que la app necesita para arrancar. Se puede sobreescribir
con variables de entorno para no tener que tocar el código al cambiar de máquina
o de motor de base de datos.
"""
import os


class Config:
    # Clave usada por Flask para firmar cookies/sesiones y mensajes flash.
    # En producción SIEMPRE define SECRET_KEY como variable de entorno.
    SECRET_KEY = os.environ.get("SECRET_KEY", "clave-de-desarrollo-cambiar-en-produccion")

    # Cadena de conexión a la base de datos.
    #   - Si NO defines nada, la app usa SQLite (un solo archivo, sin instalar servidor).
    #   - Para MySQL/MariaDB:  mysql+pymysql://usuario:password@localhost/cotizador
    #   - Para PostgreSQL:     postgresql+psycopg2://usuario:password@localhost/cotizador
    # Se toma de la variable de entorno DATABASE_URL si existe.
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # Desactiva un sistema de eventos que no usamos y que gasta memoria.
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Pon SQL_ECHO=1 para ver en la terminal cada consulta SQL que se ejecuta.
    # Muy útil para aprender qué hace SQLAlchemy por debajo.
    SQLALCHEMY_ECHO = os.environ.get("SQL_ECHO", "0") == "1"

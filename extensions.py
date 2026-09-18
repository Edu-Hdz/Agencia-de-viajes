"""
Extensiones de Flask.

Creamos aquí las extensiones (por ahora solo la base de datos) SIN atarlas
todavía a una aplicación. Se atan después dentro de la fábrica `create_app`
usando `db.init_app(app)`. Este patrón evita las importaciones circulares:
los modelos importan `db` desde este archivo, y la fábrica también.
"""
from flask_sqlalchemy import SQLAlchemy

# `db` es el objeto central del ORM. Con él definimos modelos (db.Model),
# columnas (db.Column), relaciones (db.relationship) y ejecutamos consultas.
db = SQLAlchemy()

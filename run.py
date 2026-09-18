"""
Punto de entrada de la aplicación.

Formas de arrancar el servidor de desarrollo:

  1) python run.py
  2) flask --app run run       (equivale a lo anterior)

Los comandos de base de datos también usan este archivo:
  flask --app run init-db
  flask --app run reset-db
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    # host y port por defecto para desarrollo local.
    # debug=True recarga el servidor al guardar cambios y muestra errores.
    app.run(host="127.0.0.1", port=5000, debug=True)

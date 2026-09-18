"""
Fábrica de la aplicación.

`create_app()` construye y devuelve la app de Flask ya configurada. Usar una
función (en lugar de crear la app en el nivel superior del módulo) es el patrón
recomendado: facilita las pruebas y evita importaciones circulares.

Pasos que hace:
  1. Crea la app y carga la configuración.
  2. Define la base de datos SQLite por defecto (si no configuraste otra).
  3. Inicializa SQLAlchemy y registra los modelos.
  4. Registra los blueprints (rutas) y los comandos de terminal.
  5. Registra filtros de plantilla y páginas de error.
"""
import os

from flask import Flask, render_template

from config import Config
from app.extensions import db


def create_app(config_class=Config):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    # Si no se definió una base de datos, usamos SQLite dentro de /instance.
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        os.makedirs(app.instance_path, exist_ok=True)
        ruta_db = os.path.join(app.instance_path, "cotizador.db")
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + ruta_db

    # Conecta la extensión de base de datos con esta app.
    db.init_app(app)

    # Importa los modelos para que SQLAlchemy conozca las tablas.
    from app import models  # noqa: F401

    _registrar_blueprints(app)
    _registrar_filtros(app)
    _registrar_errores(app)

    return app


def _registrar_blueprints(app):
    from app.routes.main import bp as main_bp
    from app.routes.viajes import bp as viajes_bp
    from app.routes.items import bp as items_bp
    from app.routes.cotizaciones import bp as cotizaciones_bp
    from app.routes.monedas import bp as monedas_bp
    from app.commands import bp as cli_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(viajes_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(cotizaciones_bp)
    app.register_blueprint(monedas_bp)
    app.register_blueprint(cli_bp)  # aporta los comandos flask init-db, etc.


def _registrar_filtros(app):
    """Filtros de Jinja para dar formato a dinero y fechas en las plantillas."""

    @app.template_filter("money")
    def money(valor):
        try:
            return "{:,.2f}".format(float(valor or 0))
        except (TypeError, ValueError):
            return "0.00"

    @app.template_filter("fecha")
    def fecha(valor):
        return valor.strftime("%d/%m/%Y") if valor else "—"

    @app.template_filter("fechahora")
    def fechahora(valor):
        return valor.strftime("%d/%m/%Y %H:%M") if valor else "—"

    @app.context_processor
    def variables_globales():
        from datetime import date
        hoy = date.today()
        return {"anio_actual": hoy.year, "hoy_iso": hoy.isoformat()}


def _registrar_errores(app):
    @app.errorhandler(404)
    def no_encontrado(e):
        return render_template("error.html", codigo=404,
                               mensaje="No encontramos lo que buscabas."), 404

    @app.errorhandler(500)
    def error_servidor(e):
        return render_template("error.html", codigo=500,
                               mensaje="Ocurrió un error inesperado."), 500

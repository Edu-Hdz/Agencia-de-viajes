"""
Rutas principales: el tablero con la lista de viajes.
"""
from flask import Blueprint, render_template

from app.models import Viaje
from app.services import presupuesto_service

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    """Tablero: muestra todos los viajes registrados con su costo estimado."""
    viajes = Viaje.query.order_by(Viaje.idViaje.desc()).all()

    # Mantenemos el total de cada viaje al día antes de mostrarlo.
    for viaje in viajes:
        presupuesto_service.recalcular(viaje, commit=False)
    from app.extensions import db
    db.session.commit()

    return render_template("index.html", viajes=viajes)

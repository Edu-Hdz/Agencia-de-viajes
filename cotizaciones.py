"""
Rutas de Cotización: generar una nueva, verla (formato imprimible) y borrarla.
"""
from datetime import datetime

from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, abort)

from app.extensions import db
from app.models import Viaje, Moneda, Cotizacion
from app.services import cotizacion_service

bp = Blueprint("cotizaciones", __name__)


@bp.route("/viajes/<int:viaje_id>/cotizaciones/nueva", methods=["POST"])
def nueva(viaje_id):
    viaje = db.session.get(Viaje, viaje_id) or abort(404)

    # Moneda de destino (opcional pero recomendable).
    moneda = None
    id_moneda = request.form.get("idMoneda")
    if id_moneda:
        moneda = db.session.get(Moneda, int(id_moneda))

    # Tipo de cambio.
    try:
        tipo_cambio = float((request.form.get("tipoCambio") or "1").replace(",", "."))
    except ValueError:
        flash("El tipo de cambio debe ser un número.", "error")
        return redirect(url_for("viajes.detalle", viaje_id=viaje_id) + "#cotizaciones")

    # Fecha (opcional): si no se manda, se usa hoy.
    fecha = None
    fecha_txt = request.form.get("fecha")
    if fecha_txt:
        try:
            fecha = datetime.strptime(fecha_txt, "%Y-%m-%d").date()
        except ValueError:
            flash("La fecha de la cotización es inválida.", "error")
            return redirect(url_for("viajes.detalle", viaje_id=viaje_id) + "#cotizaciones")

    cotizacion_service.generar(viaje, moneda, tipo_cambio, fecha)
    flash("Cotización generada.", "ok")
    return redirect(url_for("viajes.detalle", viaje_id=viaje_id) + "#cotizaciones")


@bp.route("/cotizaciones/<int:cotizacion_id>")
def detalle(cotizacion_id):
    cotizacion = db.session.get(Cotizacion, cotizacion_id) or abort(404)
    return render_template("cotizacion_detalle.html", cotizacion=cotizacion,
                           viaje=cotizacion.viaje, presupuesto=cotizacion.viaje.presupuesto)


@bp.route("/cotizaciones/<int:cotizacion_id>/eliminar", methods=["POST"])
def eliminar(cotizacion_id):
    cotizacion = db.session.get(Cotizacion, cotizacion_id) or abort(404)
    viaje_id = cotizacion.idViaje
    db.session.delete(cotizacion)
    db.session.commit()
    flash("Cotización eliminada.", "ok")
    return redirect(url_for("viajes.detalle", viaje_id=viaje_id) + "#cotizaciones")

"""
Rutas de Viaje: crear, ver (detalle), editar, borrar; y editar el presupuesto.

El "detalle" del viaje es la pantalla central de la app: ahí se agregan viajeros,
vuelos, hospedajes, transporte y actividades, se ve el presupuesto y se generan
cotizaciones.
"""
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, abort)

from app.extensions import db
from app.models import Viaje, Moneda
from app.services import presupuesto_service
from app.field_specs import F, RESOURCES
from app.forms_util import (aplicar_formulario, valores_para_formulario,
                            valores_por_defecto)

bp = Blueprint("viajes", __name__)


def _campos_viaje():
    """Campos del formulario de viaje. La moneda principal se elige del catálogo."""
    codigos = [m.codigo for m in Moneda.query.order_by(Moneda.codigo).all()]
    if not codigos:
        codigos = ["MXN", "EUR", "USD"]
    return [
        F("origen", "Origen", "text", requerido=True, placeholder="Ciudad de México"),
        F("destino", "Destino", "text", requerido=True, placeholder="París"),
        F("fechaSalida", "Fecha de salida", "date"),
        F("fechaRegreso", "Fecha de regreso", "date"),
        F("numViajeros", "Número de viajeros", "int", requerido=True, predeterminado=1),
        F("monedaPrincipal", "Moneda principal", "select", opciones=codigos,
          requerido=True, predeterminado=("MXN" if "MXN" in codigos else codigos[0])),
    ]


def _campos_presupuesto():
    """Campos manuales del presupuesto (el resto se calcula solo)."""
    return [
        F("montoDisponible", "Dinero disponible", "money",
          ayuda="Cuánto dinero tienes planeado o ahorrado para el viaje."),
        F("costoAlimentos", "Comida (estimado)", "money"),
        F("gastosExtras", "Gastos extra / imprevistos", "money"),
    ]


@bp.route("/viajes/nuevo", methods=["GET", "POST"])
def nuevo():
    campos = _campos_viaje()
    if request.method == "POST":
        viaje = Viaje()
        errores = aplicar_formulario(viaje, campos, request.form)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("viaje_form.html", campos=campos,
                                   valores=request.form, modo="crear")
        db.session.add(viaje)
        db.session.commit()
        presupuesto_service.recalcular(viaje)  # crea el presupuesto vacío
        flash("Viaje creado.", "ok")
        return redirect(url_for("viajes.detalle", viaje_id=viaje.idViaje))

    return render_template("viaje_form.html", campos=campos,
                           valores=valores_por_defecto(campos), modo="crear")


@bp.route("/viajes/<int:viaje_id>")
def detalle(viaje_id):
    viaje = db.session.get(Viaje, viaje_id) or abort(404)
    # Aseguramos presupuesto al día cada vez que se abre el detalle.
    presupuesto = presupuesto_service.recalcular(viaje)
    monedas = Moneda.query.order_by(Moneda.codigo).all()

    # Metadatos de campos y valores iniciales para los formularios "Agregar…".
    defaults = {clave: valores_por_defecto(r["campos"]) for clave, r in RESOURCES.items()}

    return render_template("viaje_detalle.html", viaje=viaje,
                           presupuesto=presupuesto, monedas=monedas,
                           recursos=RESOURCES, defaults=defaults)


@bp.route("/viajes/<int:viaje_id>/editar", methods=["GET", "POST"])
def editar(viaje_id):
    viaje = db.session.get(Viaje, viaje_id) or abort(404)
    campos = _campos_viaje()
    if request.method == "POST":
        errores = aplicar_formulario(viaje, campos, request.form)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("viaje_form.html", campos=campos,
                                   valores=request.form, modo="editar", viaje=viaje)
        db.session.commit()
        presupuesto_service.recalcular(viaje)
        flash("Viaje actualizado.", "ok")
        return redirect(url_for("viajes.detalle", viaje_id=viaje.idViaje))

    valores = valores_para_formulario(viaje, campos)
    return render_template("viaje_form.html", campos=campos, valores=valores,
                           modo="editar", viaje=viaje)


@bp.route("/viajes/<int:viaje_id>/eliminar", methods=["POST"])
def eliminar(viaje_id):
    viaje = db.session.get(Viaje, viaje_id) or abort(404)
    db.session.delete(viaje)
    db.session.commit()
    flash("Viaje eliminado.", "ok")
    return redirect(url_for("main.index"))


@bp.route("/viajes/<int:viaje_id>/presupuesto/editar", methods=["GET", "POST"])
def editar_presupuesto(viaje_id):
    viaje = db.session.get(Viaje, viaje_id) or abort(404)
    presupuesto = presupuesto_service.obtener_o_crear(viaje)
    campos = _campos_presupuesto()
    if request.method == "POST":
        errores = aplicar_formulario(presupuesto, campos, request.form)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("presupuesto_form.html", campos=campos,
                                   valores=request.form, viaje=viaje)
        presupuesto_service.recalcular(viaje)  # recalcula totales con lo nuevo
        flash("Presupuesto actualizado.", "ok")
        return redirect(url_for("viajes.detalle", viaje_id=viaje.idViaje) + "#presupuesto")

    valores = valores_para_formulario(presupuesto, campos)
    return render_template("presupuesto_form.html", campos=campos,
                           valores=valores, viaje=viaje)

"""
Rutas del catálogo de Monedas.

Las monedas se usan como destino de las cotizaciones. Aquí se listan, crean,
editan y borran.
"""
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, abort)

from app.extensions import db
from app.models import Moneda
from app.field_specs import F
from app.forms_util import (aplicar_formulario, valores_para_formulario,
                            valores_por_defecto)

bp = Blueprint("monedas", __name__)


def _campos_moneda():
    return [
        F("nombre", "Nombre", "text", requerido=True, placeholder="Euro"),
        F("codigo", "Código ISO", "text", requerido=True, placeholder="EUR"),
        F("tipoCambio", "Tipo de cambio sugerido", "float",
          ayuda="Unidades de esta moneda por 1 unidad de la moneda principal del viaje."),
    ]


@bp.route("/monedas")
def index():
    monedas = Moneda.query.order_by(Moneda.codigo).all()
    return render_template("monedas.html", monedas=monedas,
                           campos=_campos_moneda(),
                           valores=valores_por_defecto(_campos_moneda()))


@bp.route("/monedas/nueva", methods=["POST"])
def nueva():
    campos = _campos_moneda()
    moneda = Moneda()
    errores = aplicar_formulario(moneda, campos, request.form)

    # El código debe ser único.
    if not errores and Moneda.query.filter_by(codigo=moneda.codigo).first():
        errores.append(f"Ya existe una moneda con el código «{moneda.codigo}».")

    if errores:
        for e in errores:
            flash(e, "error")
        return redirect(url_for("monedas.index"))

    db.session.add(moneda)
    db.session.commit()
    flash("Moneda agregada.", "ok")
    return redirect(url_for("monedas.index"))


@bp.route("/monedas/<int:moneda_id>/editar", methods=["GET", "POST"])
def editar(moneda_id):
    moneda = db.session.get(Moneda, moneda_id) or abort(404)
    campos = _campos_moneda()
    if request.method == "POST":
        errores = aplicar_formulario(moneda, campos, request.form)
        otra = Moneda.query.filter_by(codigo=moneda.codigo).first()
        if not errores and otra and otra.idMoneda != moneda.idMoneda:
            errores.append(f"Ya existe otra moneda con el código «{moneda.codigo}».")
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("moneda_form.html", campos=campos,
                                   valores=request.form, moneda=moneda)
        db.session.commit()
        flash("Moneda actualizada.", "ok")
        return redirect(url_for("monedas.index"))

    valores = valores_para_formulario(moneda, campos)
    return render_template("moneda_form.html", campos=campos, valores=valores,
                           moneda=moneda)


@bp.route("/monedas/<int:moneda_id>/eliminar", methods=["POST"])
def eliminar(moneda_id):
    moneda = db.session.get(Moneda, moneda_id) or abort(404)
    if moneda.cotizaciones:
        flash("No se puede eliminar: la moneda tiene cotizaciones asociadas.", "error")
        return redirect(url_for("monedas.index"))
    db.session.delete(moneda)
    db.session.commit()
    flash("Moneda eliminada.", "ok")
    return redirect(url_for("monedas.index"))

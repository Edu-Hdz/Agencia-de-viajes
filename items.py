"""
Rutas genéricas para las entidades "hijas" de un viaje.

En vez de escribir alta/edición/baja por separado para viajeros, vuelos,
hospedajes, transporte, actividades y documentación, usamos el registro
`RESOURCES` (ver field_specs.py) y unas pocas rutas que sirven para todas.

URLs:
  Crear:   /viajes/<id>/<recurso>/nuevo           (recurso hijo de un viaje)
           /viajeros/<id>/<recurso>/nuevo          (recurso hijo de un viajero)
  Editar:  /<recurso>/<id>/editar
  Borrar:  /<recurso>/<id>/eliminar
  Alternar:/<recurso>/<id>/alternar   (cambia un sí/no como "incluido")
"""
from flask import (Blueprint, render_template, request, redirect,
                   url_for, flash, abort)

from app.extensions import db
from app.models import Viaje, Viajero
from app.field_specs import RESOURCES
from app.forms_util import (aplicar_formulario, valores_para_formulario,
                            valores_por_defecto)
from app.services import presupuesto_service

bp = Blueprint("items", __name__)


def _recurso(nombre):
    """Obtiene la definición del recurso o devuelve 404 si no existe."""
    if nombre not in RESOURCES:
        abort(404)
    return RESOURCES[nombre]


def _volver_al_detalle(viaje_id, anchor):
    """URL del detalle del viaje, saltando a la sección correspondiente."""
    return url_for("viajes.detalle", viaje_id=viaje_id) + f"#{anchor}"


# Hay dos endpoints de creación (uno por tipo de padre) para que las URLs sean
# claras y sin ambigüedad: /viajes/... para hijos de un viaje y /viajeros/...
# para la documentación de un viajero. Ambos usan la misma lógica compartida.

@bp.route("/viajes/<int:parent_id>/<recurso>/nuevo", methods=["GET", "POST"])
def crear_en_viaje(parent_id, recurso):
    return _crear(parent_id, recurso, parent_kind="viaje")


@bp.route("/viajeros/<int:parent_id>/<recurso>/nuevo", methods=["GET", "POST"])
def crear_en_viajero(parent_id, recurso):
    return _crear(parent_id, recurso, parent_kind="viajero")


def _crear(parent_id, recurso, parent_kind):
    r = _recurso(recurso)
    campos = r["campos"]

    # El tipo de padre de la URL debe coincidir con el definido para el recurso.
    if r["parent"] != parent_kind:
        abort(404)

    # Verificamos que el "padre" exista y obtenemos el viaje al que pertenece.
    if parent_kind == "viaje":
        padre = db.session.get(Viaje, parent_id) or abort(404)
    else:  # "viajero"
        padre = db.session.get(Viajero, parent_id) or abort(404)
    viaje_id = padre.idViaje

    if request.method == "POST":
        obj = r["model"]()
        setattr(obj, r["parent_fk"], parent_id)   # enlaza con su padre
        errores = aplicar_formulario(obj, campos, request.form)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("item_form.html", campos=campos,
                                   valores=request.form, recurso=recurso,
                                   titulo=r["titulo"], modo="crear",
                                   parent_id=parent_id, viaje_id=viaje_id)
        db.session.add(obj)
        db.session.commit()
        presupuesto_service.recalcular(db.session.get(Viaje, viaje_id))
        flash(f"{r['titulo']} agregado.", "ok")
        return redirect(_volver_al_detalle(viaje_id, r["anchor"]))

    return render_template("item_form.html", campos=campos,
                           valores=valores_por_defecto(campos), recurso=recurso,
                           titulo=r["titulo"], modo="crear",
                           parent_id=parent_id, viaje_id=viaje_id)


@bp.route("/<recurso>/<int:item_id>/editar", methods=["GET", "POST"])
def editar(recurso, item_id):
    r = _recurso(recurso)
    campos = r["campos"]
    obj = db.session.get(r["model"], item_id) or abort(404)
    viaje_id = r["viaje_id"](obj)

    if request.method == "POST":
        errores = aplicar_formulario(obj, campos, request.form)
        if errores:
            for e in errores:
                flash(e, "error")
            return render_template("item_form.html", campos=campos,
                                   valores=request.form, recurso=recurso,
                                   titulo=r["titulo"], modo="editar",
                                   item_id=item_id, viaje_id=viaje_id)
        db.session.commit()
        presupuesto_service.recalcular(db.session.get(Viaje, viaje_id))
        flash(f"{r['titulo']} actualizado.", "ok")
        return redirect(_volver_al_detalle(viaje_id, r["anchor"]))

    valores = valores_para_formulario(obj, campos)
    return render_template("item_form.html", campos=campos, valores=valores,
                           recurso=recurso, titulo=r["titulo"], modo="editar",
                           item_id=item_id, viaje_id=viaje_id)


@bp.route("/<recurso>/<int:item_id>/eliminar", methods=["POST"])
def eliminar(recurso, item_id):
    r = _recurso(recurso)
    obj = db.session.get(r["model"], item_id) or abort(404)
    viaje_id = r["viaje_id"](obj)
    db.session.delete(obj)
    db.session.commit()
    presupuesto_service.recalcular(db.session.get(Viaje, viaje_id))
    flash(f"{r['titulo']} eliminado.", "ok")
    return redirect(_volver_al_detalle(viaje_id, r["anchor"]))


@bp.route("/<recurso>/<int:item_id>/alternar", methods=["POST"])
def alternar(recurso, item_id):
    """Invierte un campo booleano (ej. 'incluido' o 'porPersona') desde la tabla."""
    r = _recurso(recurso)
    obj = db.session.get(r["model"], item_id) or abort(404)
    viaje_id = r["viaje_id"](obj)

    campo = request.form.get("campo", "")
    # Solo permitimos alternar campos booleanos definidos para este recurso.
    booleanos = [c["name"] for c in r["campos"] if c["tipo"] == "bool"]
    if campo not in booleanos:
        abort(400)

    setattr(obj, campo, not getattr(obj, campo))
    db.session.commit()
    presupuesto_service.recalcular(db.session.get(Viaje, viaje_id))
    return redirect(_volver_al_detalle(viaje_id, r["anchor"]))

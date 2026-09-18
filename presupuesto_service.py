"""
Servicio de Presupuesto.

Responsable de:
  - Asegurar que cada viaje tenga un objeto Presupuesto (crearlo si no existe).
  - Recalcular los costos a partir de las opciones marcadas como "incluidas".

Regla de cálculo (todo en la moneda principal del viaje):
    costoVuelo       = suma de vuelos incluidos
    costoHospedaje   = suma de hospedajes incluidos
    costoTransporte  = suma de transportes incluidos
    costoActividades = suma de actividades incluidas
    costoAlimentos   = valor manual
    gastosExtras     = valor manual
    costoTotal       = suma de todo lo anterior
    costoPorPersona  = costoTotal / numViajeros
"""
from app.extensions import db
from app.models.presupuesto import Presupuesto


def obtener_o_crear(viaje):
    """Devuelve el presupuesto del viaje; si no existe, lo crea vacío."""
    if viaje.presupuesto is None:
        presupuesto = Presupuesto(
            idViaje=viaje.idViaje,
            montoDisponible=0, costoAlimentos=0, gastosExtras=0,
        )
        db.session.add(presupuesto)
        db.session.flush()          # Deja el objeto listo y ligado al viaje
        viaje.presupuesto = presupuesto
    return viaje.presupuesto


def recalcular(viaje, commit=True):
    """
    Recalcula los costos del presupuesto del viaje.
    NO toca los valores manuales (montoDisponible, costoAlimentos, gastosExtras).
    """
    presupuesto = obtener_o_crear(viaje)

    num = viaje.numViajeros or 1
    if num < 1:
        num = 1

    # Costos calculados desde las opciones incluidas.
    presupuesto.costoVuelo = sum(v.costo_linea(num) for v in viaje.vuelos if v.incluido)
    presupuesto.costoHospedaje = sum(h.costo_linea(num) for h in viaje.hospedajes if h.incluido)
    presupuesto.costoTransporte = sum(t.costo_linea(num) for t in viaje.transportes if t.incluido)
    presupuesto.costoActividades = sum(a.costo_linea(num) for a in viaje.actividades if a.incluido)

    # Valores manuales: si estuvieran vacíos, los tratamos como 0.
    presupuesto.costoAlimentos = presupuesto.costoAlimentos or 0
    presupuesto.gastosExtras = presupuesto.gastosExtras or 0
    presupuesto.montoDisponible = presupuesto.montoDisponible or 0

    # Totales.
    presupuesto.costoTotal = (
        presupuesto.costoVuelo + presupuesto.costoHospedaje +
        presupuesto.costoTransporte + presupuesto.costoActividades +
        presupuesto.costoAlimentos + presupuesto.gastosExtras
    )
    presupuesto.costoPorPersona = presupuesto.costoTotal / num

    if commit:
        db.session.commit()
    return presupuesto

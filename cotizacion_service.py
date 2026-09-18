"""
Servicio de Cotización.

Genera una cotización a partir del presupuesto actual del viaje, convirtiendo el
total a una moneda de destino con un tipo de cambio dado.

Conversión:
    total_destino = costoTotal (moneda principal) * tipoCambio
donde tipoCambio = unidades de la moneda de destino por 1 unidad de la principal.
"""
from datetime import date as _date

from app.extensions import db
from app.models.cotizacion import Cotizacion
from app.services import presupuesto_service


def generar(viaje, moneda_destino, tipo_cambio, fecha=None):
    """
    Crea y guarda una nueva cotización para el viaje.

    - Primero recalcula el presupuesto para partir de cifras frescas.
    - Convierte el total y el costo por persona a la moneda de destino.
    """
    presupuesto = presupuesto_service.recalcular(viaje, commit=False)

    num = viaje.numViajeros or 1
    if num < 1:
        num = 1

    total_convertido = (presupuesto.costoTotal or 0) * (tipo_cambio or 1)

    cotizacion = Cotizacion(
        idViaje=viaje.idViaje,
        idMoneda=(moneda_destino.idMoneda if moneda_destino else None),
        fecha=fecha or _date.today(),
        tipoCambio=tipo_cambio or 1,
        costoTotal=total_convertido,
        costoPorPersona=total_convertido / num,
    )
    db.session.add(cotizacion)
    db.session.commit()
    return cotizacion

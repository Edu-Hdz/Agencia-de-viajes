"""
Paquete de modelos.

Importamos aquí TODAS las clases para que:
  1) SQLAlchemy las conozca al crear las tablas.
  2) Se puedan importar de forma cómoda, por ejemplo:
       from app.models import Viaje, Viajero
"""
from app.models.viaje import Viaje
from app.models.viajero import Viajero
from app.models.documentacion import Documentacion
from app.models.hospedaje import Hospedaje
from app.models.vuelo import Vuelo
from app.models.transporte import Transporte
from app.models.actividad import Actividad
from app.models.presupuesto import Presupuesto
from app.models.cotizacion import Cotizacion
from app.models.moneda import Moneda

__all__ = [
    "Viaje", "Viajero", "Documentacion", "Hospedaje", "Vuelo",
    "Transporte", "Actividad", "Presupuesto", "Cotizacion", "Moneda",
]

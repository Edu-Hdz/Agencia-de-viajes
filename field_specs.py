"""
Especificación de campos y registro de recursos.

Aquí describimos, para cada entidad "hija" de un viaje (viajero, vuelo,
hospedaje, transporte, actividad, documentación), QUÉ campos tiene su
formulario y de qué TIPO es cada uno.

Con esta información, una sola plantilla y unas pocas rutas genéricas pueden
crear/editar/borrar cualquiera de estos recursos, sin escribir código repetido
para cada uno. Si mañana necesitas un campo nuevo, lo agregas al modelo y aquí,
y el formulario se actualiza solo.

Tipos de campo admitidos (`tipo`):
    "text"      -> texto corto
    "textarea"  -> texto largo (varias líneas)
    "int"       -> número entero
    "money"     -> monto de dinero (decimal)
    "float"     -> número decimal (ej. una puntuación)
    "date"      -> fecha (año-mes-día)
    "datetime"  -> fecha y hora
    "bool"      -> casilla de sí/no
    "select"    -> lista de opciones cerradas
"""
from app.models.viajero import Viajero
from app.models.documentacion import Documentacion
from app.models.hospedaje import Hospedaje
from app.models.vuelo import Vuelo
from app.models.transporte import Transporte
from app.models.actividad import Actividad


def F(name, label, tipo="text", requerido=False, ayuda=None,
      opciones=None, placeholder=None, predeterminado=None):
    """Crea la descripción de un campo de formulario (un simple diccionario)."""
    return {
        "name": name, "label": label, "tipo": tipo, "requerido": requerido,
        "ayuda": ayuda, "opciones": opciones, "placeholder": placeholder,
        "predeterminado": predeterminado,
    }


# Estados posibles para un documento (lista cerrada).
ESTADOS_DOCUMENTO = ["Pendiente", "En trámite", "Vigente", "Vencido", "No aplica"]


# --- Registro central de recursos ---
# Cada clave es el nombre que aparece en la URL (ej. /viajes/1/vuelos/nuevo).
RESOURCES = {
    "viajeros": {
        "model": Viajero,
        "pk": "idViajero",
        "titulo": "Viajero",
        "parent": "viaje",          # de quién "cuelga" este recurso
        "parent_fk": "idViaje",     # columna llave foránea
        "anchor": "viajeros",       # sección a la que se regresa en el detalle
        "viaje_id": lambda o: o.idViaje,
        "campos": [
            F("nombre", "Nombre completo", "text", requerido=True),
            F("nacionalidad", "Nacionalidad", "text", placeholder="Mexicana"),
            F("pasaporte", "Número de pasaporte", "text"),
        ],
    },
    "documentacion": {
        "model": Documentacion,
        "pk": "idDocumentacion",
        "titulo": "Documento",
        "parent": "viajero",
        "parent_fk": "idViajero",
        "anchor": "viajeros",
        "viaje_id": lambda o: o.viajero.idViaje,
        "campos": [
            F("tipoDocumento", "Tipo de documento", "text", requerido=True,
              placeholder="Pasaporte, Visa, ETIAS, Seguro…"),
            F("estado", "Estado", "select", opciones=ESTADOS_DOCUMENTO,
              predeterminado="Pendiente"),
            F("descripcion", "Descripción", "text"),
            F("fechaVencimiento", "Fecha de vencimiento", "date"),
            F("observaciones", "Observaciones", "textarea"),
        ],
    },
    "vuelos": {
        "model": Vuelo,
        "pk": "idVuelo",
        "titulo": "Vuelo",
        "parent": "viaje",
        "parent_fk": "idViaje",
        "anchor": "vuelos",
        "viaje_id": lambda o: o.idViaje,
        "campos": [
            F("aeropuertoSalida", "Aeropuerto de salida (IATA)", "text", placeholder="MEX"),
            F("aeropuertoLlegada", "Aeropuerto de llegada (IATA)", "text", placeholder="CDG"),
            F("fechaSalida", "Salida (fecha y hora)", "datetime"),
            F("fechaRegreso", "Regreso (fecha y hora)", "datetime"),
            F("precio", "Precio", "money"),
            F("porPersona", "El precio es por persona", "bool", predeterminado=True,
              ayuda="Actívalo si el precio es de un boleto; desactívalo si ya es el total del grupo."),
            F("equipaje", "Equipaje", "text", placeholder="1 maleta 23kg"),
            F("incluido", "Incluir en el presupuesto", "bool", predeterminado=True),
        ],
    },
    "hospedajes": {
        "model": Hospedaje,
        "pk": "idHospedaje",
        "titulo": "Hospedaje",
        "parent": "viaje",
        "parent_fk": "idViaje",
        "anchor": "hospedaje",
        "viaje_id": lambda o: o.idViaje,
        "campos": [
            F("nombre", "Nombre", "text", requerido=True),
            F("tipoAlojamiento", "Tipo", "text", placeholder="Hotel, Airbnb, Hostal"),
            F("categoria", "Categoría", "text", placeholder="4 estrellas"),
            F("costoGrupo", "Costo total (grupo)", "money",
              ayuda="Costo total del alojamiento para todo el grupo."),
            F("costoPersona", "Costo por persona", "money",
              ayuda="Solo se usa si dejas vacío el costo del grupo."),
            F("desayuno", "Incluye desayuno", "bool"),
            F("ubicacion", "Ubicación", "text"),
            F("puntuacion", "Puntuación", "float", placeholder="4.5"),
            F("incluido", "Incluir en el presupuesto", "bool", predeterminado=True),
        ],
    },
    "transportes": {
        "model": Transporte,
        "pk": "idTransporte",
        "titulo": "Transporte",
        "parent": "viaje",
        "parent_fk": "idViaje",
        "anchor": "transporte",
        "viaje_id": lambda o: o.idViaje,
        "campos": [
            F("tipo", "Tipo", "text", requerido=True, placeholder="Metro/RER, Navigo…"),
            F("costo", "Costo", "money"),
            F("porPersona", "El costo es por persona", "bool", predeterminado=True,
              ayuda="Actívalo para abonos individuales (ej. Navigo); desactívalo si es total."),
            F("unidad", "Empresa / unidad", "text"),
            F("zonas", "Zonas", "text", placeholder="Zona 1-3"),
            F("descripcion", "Descripción", "text"),
            F("incluido", "Incluir en el presupuesto", "bool", predeterminado=True),
        ],
    },
    "actividades": {
        "model": Actividad,
        "pk": "idActividad",
        "titulo": "Actividad",
        "parent": "viaje",
        "parent_fk": "idViaje",
        "anchor": "actividades",
        "viaje_id": lambda o: o.idViaje,
        "campos": [
            F("nombre", "Nombre", "text", requerido=True),
            F("ubicacion", "Ubicación", "text"),
            F("precio", "Precio (entrada)", "money"),
            F("porPersona", "El precio es por persona", "bool", predeterminado=True),
            F("descripcion", "Descripción", "textarea"),
            F("incluido", "Incluir en el presupuesto", "bool", predeterminado=True),
        ],
    },
}

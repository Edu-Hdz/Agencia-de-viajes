"""
Modelo: Viaje

Es la clase CENTRAL del sistema. Concentra la información general del viaje
(origen, destino, fechas, número de viajeros y moneda principal) y se relaciona
con casi todas las demás clases.

Cada atributo de la clase se convierte en una columna de la tabla `viaje`.
Cada `db.relationship` describe cómo se conecta este viaje con otras tablas.
"""
from app.extensions import db


class Viaje(db.Model):
    __tablename__ = "viaje"

    # --- Atributos (columnas de la tabla) ---
    idViaje = db.Column(db.Integer, primary_key=True)          # Llave primaria
    origen = db.Column(db.String(120), nullable=False)          # Ciudad/país de salida
    destino = db.Column(db.String(120), nullable=False)         # Ciudad/país de llegada
    fechaSalida = db.Column(db.Date)                            # Fecha de inicio
    fechaRegreso = db.Column(db.Date)                           # Fecha de fin
    numViajeros = db.Column(db.Integer, nullable=False, default=1)
    monedaPrincipal = db.Column(db.String(10), nullable=False, default="MXN")  # Código ISO

    # --- Relaciones ---
    # Un viaje tiene MUCHOS viajeros, hospedajes, vuelos, etc. (1:N)
    # `cascade="all, delete-orphan"` => al borrar el viaje se borran sus hijos.
    viajeros = db.relationship(
        "Viajero", back_populates="viaje",
        cascade="all, delete-orphan", order_by="Viajero.idViajero"
    )
    hospedajes = db.relationship(
        "Hospedaje", back_populates="viaje",
        cascade="all, delete-orphan", order_by="Hospedaje.idHospedaje"
    )
    vuelos = db.relationship(
        "Vuelo", back_populates="viaje",
        cascade="all, delete-orphan", order_by="Vuelo.idVuelo"
    )
    transportes = db.relationship(
        "Transporte", back_populates="viaje",
        cascade="all, delete-orphan", order_by="Transporte.idTransporte"
    )
    actividades = db.relationship(
        "Actividad", back_populates="viaje",
        cascade="all, delete-orphan", order_by="Actividad.idActividad"
    )
    cotizaciones = db.relationship(
        "Cotizacion", back_populates="viaje",
        cascade="all, delete-orphan", order_by="Cotizacion.fecha.desc()"
    )
    # Un viaje tiene UN solo presupuesto (1:1) => uselist=False
    presupuesto = db.relationship(
        "Presupuesto", back_populates="viaje",
        cascade="all, delete-orphan", uselist=False
    )

    # --- Propiedades de apoyo (no son columnas, se calculan al momento) ---
    @property
    def duracion_dias(self):
        """Número de días del viaje, o None si faltan fechas."""
        if self.fechaSalida and self.fechaRegreso:
            return (self.fechaRegreso - self.fechaSalida).days
        return None

    def __repr__(self):
        return f"<Viaje {self.idViaje}: {self.origen} -> {self.destino}>"

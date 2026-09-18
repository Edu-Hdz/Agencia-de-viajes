"""
Modelo: Hospedaje

Almacena las alternativas de alojamiento que se comparan para el viaje.
Relación: un Viaje tiene muchas opciones de Hospedaje (1:N).

Campo de apoyo (no venía en la matriz original):
  - `incluido`: si esta opción cuenta o no dentro del presupuesto. Permite
    registrar varias alternativas y elegir cuál(es) sumar.
"""
from app.extensions import db


class Hospedaje(db.Model):
    __tablename__ = "hospedaje"

    idHospedaje = db.Column(db.Integer, primary_key=True)
    idViaje = db.Column(db.Integer, db.ForeignKey("viaje.idViaje"), nullable=False)

    nombre = db.Column(db.String(150), nullable=False)
    categoria = db.Column(db.String(40))        # Ej. "5 estrellas", "Lujo"
    costoGrupo = db.Column(db.Float)            # Costo total de la habitación/casa
    costoPersona = db.Column(db.Float)         # Costo dividido por viajero
    desayuno = db.Column(db.Boolean, default=False)
    ubicacion = db.Column(db.String(200))
    tipoAlojamiento = db.Column(db.String(60))  # Ej. "Hotel", "Airbnb"
    puntuacion = db.Column(db.Float)           # Ej. 4.5

    incluido = db.Column(db.Boolean, default=True, nullable=False)

    viaje = db.relationship("Viaje", back_populates="hospedajes")

    def costo_linea(self, num_viajeros):
        """
        Costo total de esta opción para el presupuesto.
        Usa el costo del grupo; si no existe, multiplica el costo por persona
        por el número de viajeros.
        """
        if self.costoGrupo is not None:
            return self.costoGrupo
        if self.costoPersona is not None:
            return self.costoPersona * (num_viajeros or 1)
        return 0

    def __repr__(self):
        return f"<Hospedaje {self.idHospedaje}: {self.nombre}>"

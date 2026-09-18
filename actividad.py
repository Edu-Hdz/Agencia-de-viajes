"""
Modelo: Actividad

Actividades o lugares turísticos que los viajeros pueden visitar (Louvre, Torre
Eiffel, Arco del Triunfo, etc.).
Relación: un Viaje tiene muchas Actividades (1:N).

Campos de apoyo (no venían en la matriz original):
  - `incluido`:   si esta actividad cuenta dentro del presupuesto.
  - `porPersona`: si el `precio` (entrada) es por persona o total.
"""
from app.extensions import db


class Actividad(db.Model):
    __tablename__ = "actividad"

    idActividad = db.Column(db.Integer, primary_key=True)
    idViaje = db.Column(db.Integer, db.ForeignKey("viaje.idViaje"), nullable=False)

    nombre = db.Column(db.String(150), nullable=False)
    ubicacion = db.Column(db.String(200))
    precio = db.Column(db.Float)
    descripcion = db.Column(db.String(255))

    incluido = db.Column(db.Boolean, default=True, nullable=False)
    porPersona = db.Column(db.Boolean, default=True, nullable=False)

    viaje = db.relationship("Viaje", back_populates="actividades")

    def costo_linea(self, num_viajeros):
        """Costo total de esta actividad para el presupuesto."""
        base = self.precio or 0
        return base * (num_viajeros or 1) if self.porPersona else base

    def __repr__(self):
        return f"<Actividad {self.idActividad}: {self.nombre}>"

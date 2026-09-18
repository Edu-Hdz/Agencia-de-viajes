"""
Modelo: Transporte

Alternativas de transporte durante el viaje (Metro/RER, Navigo, Paris Visite,
traslado aeropuerto-ciudad, etc.).
Relación: un Viaje tiene muchas opciones de Transporte (1:N).

Campos de apoyo (no venían en la matriz original):
  - `incluido`:   si esta opción cuenta dentro del presupuesto.
  - `porPersona`: si el `costo` es por persona (habitual en abonos) o total.
"""
from app.extensions import db


class Transporte(db.Model):
    __tablename__ = "transporte"

    idTransporte = db.Column(db.Integer, primary_key=True)
    idViaje = db.Column(db.Integer, db.ForeignKey("viaje.idViaje"), nullable=False)

    tipo = db.Column(db.String(80), nullable=False)   # Ej. "Metro/RER", "Navigo Semaine"
    costo = db.Column(db.Float)
    unidad = db.Column(db.String(80))                 # Empresa o número de línea/servicio
    descripcion = db.Column(db.String(200))
    zonas = db.Column(db.String(80))                  # Ej. "Zona 1-3"

    incluido = db.Column(db.Boolean, default=True, nullable=False)
    porPersona = db.Column(db.Boolean, default=True, nullable=False)

    viaje = db.relationship("Viaje", back_populates="transportes")

    def costo_linea(self, num_viajeros):
        """Costo total de esta opción para el presupuesto."""
        base = self.costo or 0
        return base * (num_viajeros or 1) if self.porPersona else base

    def __repr__(self):
        return f"<Transporte {self.idTransporte}: {self.tipo}>"

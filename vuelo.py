"""
Modelo: Vuelo

Contiene las alternativas/cotizaciones de vuelo del viaje.
Relación: un Viaje tiene muchas opciones de Vuelo (1:N).

Campos de apoyo (no venían en la matriz original):
  - `incluido`:   si esta opción cuenta dentro del presupuesto.
  - `porPersona`: si el `precio` es por persona (habitual en vuelos) o total.
"""
from app.extensions import db


class Vuelo(db.Model):
    __tablename__ = "vuelo"

    idVuelo = db.Column(db.Integer, primary_key=True)
    idViaje = db.Column(db.Integer, db.ForeignKey("viaje.idViaje"), nullable=False)

    aeropuertoSalida = db.Column(db.String(10))    # Código IATA, ej. "MEX"
    aeropuertoLlegada = db.Column(db.String(10))   # Código IATA, ej. "CDG"
    fechaSalida = db.Column(db.DateTime)           # Fecha y hora de despegue
    fechaRegreso = db.Column(db.DateTime)          # Fecha y hora de retorno
    precio = db.Column(db.Float)
    equipaje = db.Column(db.String(120))           # Ej. "1 maleta 23kg"

    incluido = db.Column(db.Boolean, default=True, nullable=False)
    porPersona = db.Column(db.Boolean, default=True, nullable=False)

    viaje = db.relationship("Viaje", back_populates="vuelos")

    def costo_linea(self, num_viajeros):
        """Costo total de esta opción para el presupuesto."""
        base = self.precio or 0
        return base * (num_viajeros or 1) if self.porPersona else base

    def __repr__(self):
        return f"<Vuelo {self.idVuelo}: {self.aeropuertoSalida}-{self.aeropuertoLlegada}>"

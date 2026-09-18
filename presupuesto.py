"""
Modelo: Presupuesto

Concentra y controla los gastos estimados del viaje.
Relación: un Viaje tiene UN Presupuesto (1:1).

Cómo se llenan los campos:
  - Manuales (los escribe la persona): montoDisponible, costoAlimentos, gastosExtras.
  - Calculados (los pone el sistema a partir de las opciones "incluidas"):
    costoVuelo, costoHospedaje, costoTransporte, costoActividades,
    costoTotal y costoPorPersona.

El recálculo lo hace `app/services/presupuesto_service.py`.
Todos los montos están en la moneda principal del viaje.
"""
from app.extensions import db


class Presupuesto(db.Model):
    __tablename__ = "presupuesto"

    idPresupuesto = db.Column(db.Integer, primary_key=True)
    # unique=True refuerza la relación 1:1 (un viaje no puede tener dos presupuestos).
    idViaje = db.Column(db.Integer, db.ForeignKey("viaje.idViaje"), nullable=False, unique=True)

    montoDisponible = db.Column(db.Float, default=0)   # Dinero total planeado/ahorrado
    costoVuelo = db.Column(db.Float, default=0)
    costoHospedaje = db.Column(db.Float, default=0)
    costoAlimentos = db.Column(db.Float, default=0)
    costoTransporte = db.Column(db.Float, default=0)
    costoActividades = db.Column(db.Float, default=0)
    gastosExtras = db.Column(db.Float, default=0)      # Fondo de emergencia / compras
    costoTotal = db.Column(db.Float, default=0)
    costoPorPersona = db.Column(db.Float, default=0)

    viaje = db.relationship("Viaje", back_populates="presupuesto")

    @property
    def restante(self):
        """Cuánto sobra (o falta, si es negativo) respecto al dinero disponible."""
        return (self.montoDisponible or 0) - (self.costoTotal or 0)

    def __repr__(self):
        return f"<Presupuesto viaje={self.idViaje} total={self.costoTotal}>"

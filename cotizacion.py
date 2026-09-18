"""
Modelo: Cotizacion

Registra las propuestas de precio generadas durante la planeación, expresadas
en una moneda de destino (por ejemplo, convertir el total de MXN a EUR).
Relaciones:
  - un Viaje tiene muchas Cotizaciones (1:N).
  - una Moneda se usa en muchas Cotizaciones (1:N).

Cada cotización es una "foto" del presupuesto en un momento y a un tipo de
cambio dados, por eso guarda sus propios totales ya convertidos.
"""
from app.extensions import db


class Cotizacion(db.Model):
    __tablename__ = "cotizacion"

    idCotizacion = db.Column(db.Integer, primary_key=True)
    idViaje = db.Column(db.Integer, db.ForeignKey("viaje.idViaje"), nullable=False)
    idMoneda = db.Column(db.Integer, db.ForeignKey("moneda.idMoneda"))

    fecha = db.Column(db.Date, nullable=False)
    # tipoCambio: unidades de la moneda de destino por 1 unidad de la moneda principal.
    tipoCambio = db.Column(db.Float, nullable=False, default=1)
    costoTotal = db.Column(db.Float, default=0)        # Total ya convertido
    costoPorPersona = db.Column(db.Float, default=0)   # Total convertido / num viajeros

    viaje = db.relationship("Viaje", back_populates="cotizaciones")
    moneda = db.relationship("Moneda", back_populates="cotizaciones")

    def __repr__(self):
        return f"<Cotizacion {self.idCotizacion}: viaje={self.idViaje} total={self.costoTotal}>"

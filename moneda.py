"""
Modelo: Moneda

Administra las monedas usadas para expresar los costos (MXN, EUR, USD, ...).
Relación: una Moneda se usa en muchas Cotizaciones (1:N).

`tipoCambio` aquí sirve como valor sugerido al crear una cotización
(unidades de esta moneda por 1 unidad de la moneda principal del viaje).
Siempre se puede ajustar al generar cada cotización.
"""
from app.extensions import db


class Moneda(db.Model):
    __tablename__ = "moneda"

    idMoneda = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(60), nullable=False)          # Ej. "Euro"
    codigo = db.Column(db.String(10), nullable=False, unique=True)  # Código ISO, ej. "EUR"
    tipoCambio = db.Column(db.Float, default=1)

    cotizaciones = db.relationship("Cotizacion", back_populates="moneda")

    def __repr__(self):
        return f"<Moneda {self.idMoneda}: {self.codigo}>"

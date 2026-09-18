"""
Modelo: Viajero

Guarda la información de cada persona que participa en el viaje.
Relación: un Viaje tiene muchos Viajeros (1:N).
"""
from app.extensions import db


class Viajero(db.Model):
    __tablename__ = "viajero"

    idViajero = db.Column(db.Integer, primary_key=True)
    # Llave foránea que conecta al viajero con su viaje.
    idViaje = db.Column(db.Integer, db.ForeignKey("viaje.idViaje"), nullable=False)

    nombre = db.Column(db.String(150), nullable=False)
    nacionalidad = db.Column(db.String(80))
    pasaporte = db.Column(db.String(40))   # Lleva letras y números

    # Lado "muchos" de la relación con Viaje.
    viaje = db.relationship("Viaje", back_populates="viajeros")

    # Un viajero puede tener varios documentos/requisitos (1:N).
    documentacion = db.relationship(
        "Documentacion", back_populates="viajero",
        cascade="all, delete-orphan", order_by="Documentacion.idDocumentacion"
    )

    def __repr__(self):
        return f"<Viajero {self.idViajero}: {self.nombre}>"

"""
Modelo: Documentacion

Controla los documentos y requisitos que debe cumplir cada viajero antes del
viaje (pasaporte, seguro, ETIAS, comprobantes, etc.).
Relación: un Viajero tiene muchos Documentos (1:N).
"""
from app.extensions import db


class Documentacion(db.Model):
    __tablename__ = "documentacion"

    idDocumentacion = db.Column(db.Integer, primary_key=True)
    idViajero = db.Column(db.Integer, db.ForeignKey("viajero.idViajero"), nullable=False)

    tipoDocumento = db.Column(db.String(80), nullable=False)   # Ej. "Pasaporte", "ETIAS"
    descripcion = db.Column(db.String(255))
    estado = db.Column(db.String(40), default="Pendiente")     # Ej. "Vigente", "Pendiente"
    fechaVencimiento = db.Column(db.Date)
    observaciones = db.Column(db.String(255))

    viajero = db.relationship("Viajero", back_populates="documentacion")

    def __repr__(self):
        return f"<Documentacion {self.idDocumentacion}: {self.tipoDocumento} ({self.estado})>"

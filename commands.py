"""
Comandos de terminal (CLI) para administrar la base de datos.

Se ejecutan con `flask <comando>` (requiere FLASK_APP=run.py):

    flask init-db     Crea las tablas si no existen y carga las monedas base.
    flask seed-demo   Carga un viaje de ejemplo (Ciudad de México -> París).
    flask reset-db    BORRA todo y vuelve a crear tablas + monedas + ejemplo.
"""
from datetime import date, datetime

import click
from flask import Blueprint

from app.extensions import db
from app.models import (Viaje, Viajero, Documentacion, Hospedaje, Vuelo,
                        Transporte, Actividad, Moneda)
from app.services import presupuesto_service, cotizacion_service

# Usamos un blueprint solo para colgar comandos CLI de forma ordenada.
bp = Blueprint("cli", __name__)


def _crear_monedas_base():
    """Inserta MXN, EUR y USD si aún no existen. Devuelve dict por código."""
    base = [
        ("Peso mexicano", "MXN", 1.0),
        ("Euro", "EUR", 0.055),      # 1 MXN ≈ 0.055 EUR (valor de ejemplo)
        ("Dólar estadounidense", "USD", 0.058),
    ]
    monedas = {}
    for nombre, codigo, tc in base:
        m = Moneda.query.filter_by(codigo=codigo).first()
        if not m:
            m = Moneda(nombre=nombre, codigo=codigo, tipoCambio=tc)
            db.session.add(m)
        monedas[codigo] = m
    db.session.commit()
    return monedas


@bp.cli.command("init-db")
def init_db():
    """Crea las tablas (si no existen) y carga las monedas base."""
    db.create_all()
    _crear_monedas_base()
    click.echo("Base de datos lista y monedas base cargadas.")


@bp.cli.command("reset-db")
def reset_db():
    """Borra TODO, recrea las tablas y carga monedas + viaje de ejemplo."""
    db.drop_all()
    db.create_all()
    _crear_monedas_base()
    _seed_demo()
    click.echo("Base de datos reiniciada con datos de ejemplo.")


@bp.cli.command("seed-demo")
def seed_demo():
    """Carga un viaje de ejemplo (Ciudad de México -> París)."""
    db.create_all()
    _crear_monedas_base()
    _seed_demo()
    click.echo("Viaje de ejemplo cargado.")


def _seed_demo():
    """
    Crea el viaje de ejemplo con datos ilustrativos basados en la matriz del
    proyecto (los montos en MXN son de referencia, ajústalos a tu caso real).
    """
    monedas = _crear_monedas_base()

    viaje = Viaje(
        origen="Ciudad de México", destino="París",
        fechaSalida=date(2026, 7, 10), fechaRegreso=date(2026, 7, 20),
        numViajeros=5, monedaPrincipal="MXN",
    )
    db.session.add(viaje)
    db.session.flush()  # para tener viaje.idViaje

    # --- Viajeros y su documentación ---
    for i in range(1, 6):
        v = Viajero(idViaje=viaje.idViaje, nombre=f"Viajero {i}",
                    nacionalidad="Mexicana", pasaporte=f"G{10000000 + i}")
        db.session.add(v)
        db.session.flush()
        db.session.add_all([
            Documentacion(idViajero=v.idViajero, tipoDocumento="Pasaporte",
                          estado="Vigente", fechaVencimiento=date(2030, 5, 1)),
            Documentacion(idViajero=v.idViajero, tipoDocumento="Seguro de viaje",
                          estado="Pendiente"),
            Documentacion(idViajero=v.idViajero, tipoDocumento="ETIAS",
                          estado="Pendiente",
                          descripcion="Autorización de viaje para el espacio Schengen"),
        ])

    # --- Hospedajes (se elige Le Rayz Vendôme) ---
    db.session.add_all([
        Hospedaje(idViaje=viaje.idViaje, nombre="Le Rayz Vendôme",
                  tipoAlojamiento="Hotel", categoria="4 estrellas",
                  costoGrupo=65000, desayuno=True, ubicacion="Centro de París",
                  puntuacion=4.6, incluido=True),
        Hospedaje(idViaje=viaje.idViaje, nombre="Hôtel Montmartre",
                  tipoAlojamiento="Hotel", categoria="3 estrellas",
                  costoGrupo=52000, desayuno=False, ubicacion="Montmartre",
                  puntuacion=4.2, incluido=False),
        Hospedaje(idViaje=viaje.idViaje, nombre="Apartamento Le Marais",
                  tipoAlojamiento="Airbnb", categoria="Completo",
                  costoGrupo=58000, desayuno=False, ubicacion="Le Marais",
                  puntuacion=4.5, incluido=False),
    ])

    # --- Vuelos (se elige el más económico) ---
    db.session.add_all([
        Vuelo(idViaje=viaje.idViaje, aeropuertoSalida="MEX", aeropuertoLlegada="CDG",
              fechaSalida=datetime(2026, 7, 10, 21, 30),
              fechaRegreso=datetime(2026, 7, 20, 12, 0),
              precio=18000, equipaje="1 maleta 23kg", porPersona=True, incluido=True),
        Vuelo(idViaje=viaje.idViaje, aeropuertoSalida="MEX", aeropuertoLlegada="CDG",
              fechaSalida=datetime(2026, 7, 10, 8, 0),
              fechaRegreso=datetime(2026, 7, 20, 18, 0),
              precio=21500, equipaje="1 maleta 23kg", porPersona=True, incluido=False),
    ])

    # --- Transporte ---
    db.session.add_all([
        Transporte(idViaje=viaje.idViaje, tipo="Traslado aeropuerto (RER B)",
                   costo=250, unidad="RATP", zonas="Zona 1-5",
                   descripcion="Aeropuerto CDG <-> centro", porPersona=True, incluido=True),
        Transporte(idViaje=viaje.idViaje, tipo="Navigo Semaine",
                   costo=600, unidad="RATP", zonas="Todas las zonas",
                   descripcion="Abono semanal de transporte", porPersona=True, incluido=True),
        Transporte(idViaje=viaje.idViaje, tipo="Paris Visite",
                   costo=850, unidad="RATP", zonas="Zona 1-3",
                   descripcion="Pase turístico", porPersona=True, incluido=False),
    ])

    # --- Actividades ---
    db.session.add_all([
        Actividad(idViaje=viaje.idViaje, nombre="Museo del Louvre",
                  ubicacion="Rue de Rivoli", precio=400,
                  descripcion="Entrada general", porPersona=True, incluido=True),
        Actividad(idViaje=viaje.idViaje, nombre="Torre Eiffel",
                  ubicacion="Champ de Mars", precio=700,
                  descripcion="Acceso a la cima", porPersona=True, incluido=True),
        Actividad(idViaje=viaje.idViaje, nombre="Arco del Triunfo",
                  ubicacion="Place Charles de Gaulle", precio=300,
                  descripcion="Acceso a la terraza", porPersona=True, incluido=True),
    ])

    db.session.commit()

    # --- Presupuesto (valores manuales) y recálculo ---
    presupuesto = presupuesto_service.obtener_o_crear(viaje)
    presupuesto.montoDisponible = 200000
    presupuesto.costoAlimentos = 25000
    presupuesto.gastosExtras = 10000
    presupuesto_service.recalcular(viaje)

    # --- Una cotización de ejemplo en EUR ---
    cotizacion_service.generar(viaje, monedas["EUR"], monedas["EUR"].tipoCambio)

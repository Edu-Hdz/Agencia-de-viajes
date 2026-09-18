"""
Paquete de rutas (la capa web).

Cada archivo define un "Blueprint": un grupo de rutas relacionadas. Los
blueprints se registran en la fábrica `create_app` (ver app/__init__.py).

  - main.py         -> tablero / página de inicio
  - viajes.py       -> crear, ver, editar y borrar viajes; editar presupuesto
  - items.py        -> alta/edición/baja de viajeros, vuelos, hospedajes, etc.
  - cotizaciones.py -> generar y ver cotizaciones
  - monedas.py      -> catálogo de monedas
"""

# Cotizador de Viajes Internacionales

Aplicación web para planear y presupuestar un viaje internacional: registra
viajeros y su documentación, compara opciones de vuelo, hospedaje, transporte
y actividades, calcula el presupuesto total automáticamente y genera
cotizaciones convertidas a otra moneda.

Este README está escrito para un equipo de programadores **junior**. Si es tu
primera vez tocando este proyecto, léelo completo antes de modificar código.

---

## Tabla de contenido

1. [¿Qué hace la app?](#qué-hace-la-app)
2. [Tecnologías usadas](#tecnologías-usadas)
3. [Estructura de carpetas](#estructura-de-carpetas)
4. [Cómo está pensado el backend (OOP + SQL)](#cómo-está-pensado-el-backend-oop--sql)
5. [Las 10 clases del modelo de datos](#las-10-clases-del-modelo-de-datos)
6. [Campos que se añadieron y por qué](#campos-que-se-añadieron-y-por-qué)
7. [Cómo funciona el presupuesto](#cómo-funciona-el-presupuesto)
8. [Cómo funciona una cotización](#cómo-funciona-una-cotización)
9. [Rutas (URLs) de la aplicación](#rutas-urls-de-la-aplicación)
10. [El "truco" DRY: field_specs.py](#el-truco-dry-field_specspy)
11. [Frontend: plantillas, CSS y JS](#frontend-plantillas-css-y-js)
12. [Despliegue en local — paso a paso](#despliegue-en-local--paso-a-paso)
13. [Cambiar a MySQL o PostgreSQL](#cambiar-a-mysql-o-postgresql)
14. [Preguntas frecuentes / errores comunes](#preguntas-frecuentes--errores-comunes)

---

## ¿Qué hace la app?

1. Creas un **Viaje** (origen, destino, fechas, número de viajeros, moneda
   principal, ej. MXN).
2. Agregas **Viajeros** y a cada uno su **Documentación** (pasaporte, visa,
   seguro, etc.).
3. Registras varias alternativas de **Hospedaje**, **Vuelo**, **Transporte** y
   **Actividades**, y marcas cuáles quieres "incluidas" en el presupuesto —
   así puedes comparar opciones sin perder las que descartaste.
4. La pantalla del viaje muestra un panel de **Presupuesto** que se recalcula
   solo, con el total, el costo por persona y una barra que reparte el gasto
   por categoría.
5. Puedes generar una **Cotización**: una "foto" del presupuesto convertida a
   otra **Moneda** (por ejemplo, ver el total en euros).

## Tecnologías usadas

| Pieza | Herramienta | Por qué |
|---|---|---|
| Lenguaje | Python 3.12 | |
| Framework web | Flask 3.1 | Ligero, ideal para aprender sin "magia" oculta |
| Acceso a datos | Flask-SQLAlchemy 3.1 (ORM) | Las clases de Python SON las tablas; no se escribe SQL a mano |
| Base de datos | SQLite (por defecto) | Un solo archivo, cero configuración; migrable a MySQL/PostgreSQL |
| Plantillas | Jinja2 (incluido en Flask) | HTML renderizado en el servidor, sencillo de seguir |
| Frontend | HTML + CSS + JS "vanilla" | Sin frameworks de JS que aprender; todo el JS cabe en un archivo |

No hay una API JSON ni un frontend separado (React, Vue, etc.) a propósito:
todo el ciclo petición → base de datos → HTML ocurre en el servidor, que es
el patrón más fácil de seguir para quien empieza con Flask.

## Estructura de carpetas

```
cotizador-viajes/
├── run.py                     # Punto de entrada: arranca el servidor Flask
├── config.py                  # Configuración (lee variables de entorno)
├── requirements.txt           # Dependencias de Python
├── database/
│   └── schema.sql              # DDL de referencia (documentación, NO se ejecuta)
└── app/
    ├── __init__.py             # Fábrica create_app(): arma la aplicación
    ├── extensions.py           # Objeto `db` (SQLAlchemy) compartido
    ├── commands.py             # Comandos `flask init-db / seed-demo / reset-db`
    ├── field_specs.py          # Definición de campos por tipo de recurso (ver sección DRY)
    ├── forms_util.py           # Funciones para leer/validar formularios genéricos
    ├── models/                 # Las 10 clases (una tabla cada una)
    │   ├── viaje.py
    │   ├── viajero.py
    │   ├── documentacion.py
    │   ├── hospedaje.py
    │   ├── vuelo.py
    │   ├── transporte.py
    │   ├── actividad.py
    │   ├── presupuesto.py
    │   ├── cotizacion.py
    │   └── moneda.py
    ├── services/                # Lógica de negocio (cálculos)
    │   ├── presupuesto_service.py
    │   └── cotizacion_service.py
    ├── routes/                  # Controladores (blueprints de Flask)
    │   ├── main.py              # Página de inicio
    │   ├── viajes.py            # CRUD de Viaje + editar Presupuesto
    │   ├── items.py             # CRUD genérico de viajeros/vuelos/hospedajes/...
    │   ├── cotizaciones.py      # Generar/ver/borrar cotizaciones
    │   └── monedas.py           # CRUD de Moneda
    ├── templates/                # Vistas HTML (Jinja2)
    └── static/
        ├── css/styles.css
        └── js/app.js
```

## Cómo está pensado el backend (OOP + SQL)

- Cada **clase de Python** en `app/models/` hereda de `db.Model`. Cada
  atributo de la clase (`db.Column(...)`) es una columna de la tabla, y el
  nombre de la clase define la tabla (`__tablename__`).
- Las relaciones entre clases (`db.relationship(...)`) son las llaves foráneas
  del PDF original ya "traducidas" a objetos: por ejemplo, `viaje.viajeros`
  te da directamente la lista de objetos `Viajero` de ese viaje, sin escribir
  ningún `SELECT`.
- SQLAlchemy es el **ORM** (Object-Relational Mapper): traduce entre objetos
  Python y filas de una tabla SQL. Tú trabajas con objetos (`viaje.destino`,
  `viajero.nombre`); SQLAlchemy genera el SQL por debajo.
- La lógica que hace cálculos (sumar el presupuesto, convertir una moneda) NO
  vive en los modelos ni en las rutas: vive en `app/services/`. Esto separa
  "qué son los datos" (models) de "qué hacemos con ellos" (services) de "cómo
  responde el servidor" (routes).

## Las 10 clases del modelo de datos

| # | Clase | Relación | Descripción |
|---|---|---|---|
| 1 | `Viaje` | Central | Origen, destino, fechas, número de viajeros, moneda principal |
| 2 | `Viajero` | Viaje 1:N | Persona que viaja |
| 3 | `Documentacion` | Viajero 1:N | Pasaporte, visa, seguro... de cada viajero |
| 4 | `Hospedaje` | Viaje 1:N | Alternativas de alojamiento |
| 5 | `Vuelo` | Viaje 1:N | Alternativas de vuelo |
| 6 | `Transporte` | Viaje 1:N | Metro, abonos, traslados |
| 7 | `Actividad` | Viaje 1:N | Museos, tours, entradas |
| 8 | `Presupuesto` | Viaje 1:1 | Concentrado de costos del viaje |
| 9 | `Cotizacion` | Viaje 1:N, Moneda 1:N | "Foto" del presupuesto en otra moneda |
| 10 | `Moneda` | — | Catálogo de monedas y tipo de cambio |

El detalle exacto de columnas de cada tabla está documentado en
`database/schema.sql` (en SQL puro) y en el docstring de cada archivo dentro
de `app/models/`.

## Campos que se añadieron y por qué

El modelo original (PDF) no incluía forma de decir "esta opción de vuelo es la
que elegí" ni "este precio es por persona o total". Se agregaron dos campos de
apoyo en `Hospedaje`, `Vuelo`, `Transporte` y `Actividad`:

- **`incluido`** (booleano): si la opción cuenta o no dentro del presupuesto.
  Así puedes registrar 3 hoteles distintos para comparar y solo uno de ellos
  suma al total.
- **`porPersona`** (booleano, no aplica a `Hospedaje` porque ya tenía
  `costoGrupo`/`costoPersona`): si el precio guardado es por persona (se
  multiplica por `numViajeros`) o ya es el total del grupo.

Sin estos dos campos sería imposible calcular un presupuesto realista cuando
hay varias alternativas que comparar.

También se usa `db.Float` para todos los montos de dinero, por ser lo más
simple de entender para quien empieza. **En un sistema de producción real**
se recomendaría `db.Numeric` / `DECIMAL` para evitar errores de redondeo con
números de punto flotante — se deja como nota para una futura mejora.

## Cómo funciona el presupuesto

Vive en `app/services/presupuesto_service.py`.

1. Tres campos son **manuales** (los escribe la persona en el formulario de
   presupuesto): `montoDisponible`, `costoAlimentos`, `gastosExtras`.
2. Los demás se **calculan** recorriendo las opciones marcadas como
   `incluido=True`:
   - `costoVuelo` = suma de `vuelo.costo_linea(numViajeros)` de los vuelos incluidos.
   - `costoHospedaje` = suma de `hospedaje.costo_linea(numViajeros)` de los incluidos
     (usa `costoGrupo`, o `costoPersona * numViajeros` si no hay `costoGrupo`).
   - `costoTransporte` y `costoActividades` funcionan igual que vuelo.
3. `costoTotal` = suma de las 6 categorías (vuelo + hospedaje + alimentos +
   transporte + actividades + extras).
4. `costoPorPersona` = `costoTotal / numViajeros`.
5. `restante` (propiedad, no columna) = `montoDisponible - costoTotal`. Si es
   negativo, el viaje se está excediendo del presupuesto disponible — la
   interfaz lo marca en rojo.

El recálculo se dispara automáticamente cada vez que agregas, editas, borras
o cambias el "incluido" de un vuelo/hospedaje/transporte/actividad, y también
al editar el presupuesto manual. No necesitas llamarlo tú mismo si usas las
rutas ya existentes en `app/routes/items.py`.

## Cómo funciona una cotización

Vive en `app/services/cotizacion_service.py`.

Una cotización convierte el `costoTotal` (ya calculado) del presupuesto a otra
moneda, usando un `tipoCambio` = *unidades de la moneda destino por 1 unidad
de la moneda principal del viaje*. Por ejemplo, si el viaje está en MXN y
`tipoCambio = 0.055` (EUR), entonces:

```
costoTotal_en_EUR = presupuesto.costoTotal * 0.055
costoPorPersona_en_EUR = costoTotal_en_EUR / numViajeros
```

La cotización guarda estos dos valores ya convertidos junto con la fecha y el
tipo de cambio usado, como una "foto" — si luego cambias el presupuesto, las
cotizaciones anteriores no se alteran, quedan como historial.

## Rutas (URLs) de la aplicación

| Método | Ruta | Qué hace |
|---|---|---|
| GET | `/` | Tablero con todos los viajes |
| GET/POST | `/viajes/nuevo` | Crear viaje |
| GET | `/viajes/<id>` | Detalle completo del viaje (pantalla principal) |
| GET/POST | `/viajes/<id>/editar` | Editar datos generales del viaje |
| POST | `/viajes/<id>/eliminar` | Borrar viaje (y todo lo relacionado, en cascada) |
| GET/POST | `/viajes/<id>/presupuesto` | Editar los 3 montos manuales del presupuesto |
| POST | `/viajes/<id>/<recurso>/nuevo` | Crear viajero/vuelo/hospedaje/transporte/actividad |
| POST | `/viajeros/<id>/documentacion/nuevo` | Crear un documento para un viajero |
| GET/POST | `/<recurso>/<id>/editar` | Editar cualquier item hijo |
| POST | `/<recurso>/<id>/eliminar` | Borrar cualquier item hijo |
| POST | `/<recurso>/<id>/alternar/<campo>` | Alternar un booleano (`incluido`/`porPersona`) sin recargar un formulario completo |
| GET/POST | `/viajes/<id>/cotizaciones/nueva` | Generar una cotización |
| GET | `/cotizaciones/<id>` | Ver/imprimir una cotización |
| POST | `/cotizaciones/<id>/eliminar` | Borrar una cotización |
| GET | `/monedas` | Catálogo de monedas |
| GET/POST | `/monedas/nueva`, `/monedas/<id>/editar` | Crear/editar moneda |
| POST | `/monedas/<id>/eliminar` | Borrar moneda |

`<recurso>` es uno de: `viajeros`, `documentacion`, `vuelos`, `hospedajes`,
`transportes`, `actividades` (ver siguiente sección).

## El "truco" DRY: field_specs.py

En vez de escribir 5 formularios casi idénticos (uno por cada tipo de item
hijo), el proyecto define **un solo** diccionario `RESOURCES` en
`app/field_specs.py` que describe, para cada recurso, su modelo, su llave
primaria, y la lista de campos con su tipo (`text`, `int`, `money`, `float`,
`date`, `datetime`, `bool`, `select`, `textarea`).

`app/routes/items.py` tiene rutas **genéricas** (crear/editar/eliminar/
alternar) que leen ese diccionario y funcionan para cualquier recurso. La
plantilla `item_form.html` + las macros de `_macros.html` dibujan el
formulario correcto según el tipo de cada campo.

**Ventaja:** si mañana quieres agregar un campo nuevo a `Actividad`, solo
tocas dos lugares: el modelo (`app/models/actividad.py`) y su entrada en
`RESOURCES` dentro de `field_specs.py`. No hay que tocar rutas ni plantillas.

## Frontend: plantillas, CSS y JS

- `templates/base.html` es el layout común (barra de navegación, mensajes
  flash, pie de página). Todas las demás plantillas heredan de él con
  `{% extends "base.html" %}`.
- `templates/_macros.html` contiene funciones reutilizables de Jinja para
  dibujar campos de formulario, interruptores (switches) y botones de
  acción — evita repetir HTML en cada plantilla.
- `templates/viaje_detalle.html` es la pantalla más importante: muestra el
  panel de presupuesto y todas las secciones (viajeros, vuelos, hospedajes,
  transporte, actividades, cotizaciones).
- `static/css/styles.css` define la paleta de colores y tipografía mediante
  variables CSS (`:root { --color-... }`), y es totalmente responsivo (se
  adapta a pantallas pequeñas) e imprimible (la cotización se puede imprimir
  con buen formato).
- `static/js/app.js` es JavaScript sencillo (sin frameworks) para: confirmar
  antes de borrar, enviar automáticamente un interruptor al hacer clic,
  prellenar el tipo de cambio al elegir una moneda, e imprimir la cotización.

## Despliegue en local — paso a paso

Requiere tener **Python 3.10 o superior** instalado.

```bash
# 1) Entra a la carpeta del proyecto
cd cotizador-viajes

# 2) Crea un entorno virtual (aísla las dependencias de este proyecto)
python3 -m venv venv

# 3) Actívalo
source venv/bin/activate        # En macOS/Linux
venv\Scripts\activate           # En Windows (PowerShell/cmd)

# 4) Instala las dependencias
pip install -r requirements.txt

# 5) Indica a Flask cuál es el archivo principal
export FLASK_APP=run.py         # En macOS/Linux
set FLASK_APP=run.py            # En Windows (cmd)
$env:FLASK_APP="run.py"         # En Windows (PowerShell)

# 6) Crea la base de datos con datos de ejemplo (recomendado la primera vez)
flask reset-db
#    (esto crea las tablas, carga MXN/EUR/USD y un viaje de ejemplo
#     Ciudad de México -> París con viajeros, vuelos, hospedajes, etc.)
#
#    Si prefieres empezar con la base vacía, usa en su lugar:
#    flask init-db

# 7) Arranca el servidor
flask run
#    (alternativa equivalente: python run.py)

# 8) Abre en el navegador
http://127.0.0.1:5000
```

Para detener el servidor, presiona `Ctrl+C` en la terminal.

La próxima vez que trabajes en el proyecto, solo repite los pasos 3 (activar
el entorno virtual) y 7 (arrancar el servidor) — no hace falta reinstalar
dependencias ni recrear la base de datos, a menos que quieras reiniciarla.

### Comandos disponibles

| Comando | Efecto |
|---|---|
| `flask init-db` | Crea las tablas si no existen y carga las monedas base (no borra nada) |
| `flask seed-demo` | Agrega el viaje de ejemplo (no borra nada existente) |
| `flask reset-db` | **Borra toda la base de datos** y la vuelve a crear con monedas + ejemplo |

## Cambiar a MySQL o PostgreSQL

Por defecto, si no configuras nada, la app crea un archivo SQLite dentro de la
carpeta `instance/` (se genera solo, no se sube a git). Para usar otro motor:

1. Instala el controlador correspondiente (descomenta la línea en
   `requirements.txt` y vuelve a correr `pip install -r requirements.txt`):
   - MySQL/MariaDB → `PyMySQL`
   - PostgreSQL → `psycopg2-binary`
2. Define la variable de entorno `DATABASE_URL` antes de arrancar la app:

   ```bash
   # MySQL
   export DATABASE_URL="mysql+pymysql://usuario:password@localhost/cotizador"

   # PostgreSQL
   export DATABASE_URL="postgresql+psycopg2://usuario:password@localhost/cotizador"
   ```

3. Crea la base de datos vacía en el motor elegido (con tu cliente de MySQL o
   psql), y luego corre `flask reset-db` como de costumbre — SQLAlchemy se
   encarga de crear las tablas dentro de esa base.

No hace falta cambiar ni una línea de código en `app/models/` ni en las
rutas: todo el código de la aplicación es independiente del motor de base de
datos gracias al ORM.

## Preguntas frecuentes / errores comunes

**"flask: command not found" o "No module named flask"**
El entorno virtual no está activado, o no instalaste las dependencias.
Repite los pasos 3 y 4 de despliegue.

**"Error: No such command 'init-db'."**
Falta definir `FLASK_APP=run.py` en tu terminal actual (paso 5). Esta
variable no se guarda entre sesiones de terminal distintas.

**Quiero borrar todo y empezar de cero**
Corre `flask reset-db`. Si además quieres eliminar el archivo físico de
SQLite, borra la carpeta `instance/` (se regenera sola al volver a arrancar).

**¿Dónde agrego un campo nuevo a una tabla?**
1. Agrega la columna en el modelo correspondiente (`app/models/<tabla>.py`).
2. Si el campo debe aparecer en el formulario web, agrégalo también a la
   lista `campos` de ese recurso en `app/field_specs.py`.
3. Borra la base (`flask reset-db`) o migra manualmente, ya que SQLAlchemy
   solo crea tablas nuevas, no modifica las existentes automáticamente
   (para proyectos reales se usaría una herramienta de migraciones como
   Flask-Migrate/Alembic — no incluida aquí para mantener el proyecto simple).

**¿Por qué los montos de dinero a veces muestran decimales raros?**
Por usar `Float` en vez de `Decimal` (ver sección de campos añadidos). Para
esta aplicación educativa no es un problema, pero anótalo si algún día esto
pasa a producción con dinero real.

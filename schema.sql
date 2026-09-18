-- ============================================================================
--  Cotizador de Viajes Internacionales — Esquema SQL de REFERENCIA
-- ============================================================================
--
--  IMPORTANTE (léelo, es de una línea):
--  La aplicación NO usa este archivo para crear la base de datos. Las tablas
--  se generan automáticamente desde los modelos de Python (SQLAlchemy) al
--  ejecutar `flask init-db`. Este archivo existe solo como DOCUMENTACIÓN:
--  te muestra, en SQL puro, cómo quedan las tablas y sus relaciones, para que
--  el equipo entienda la estructura sin leer el código Python.
--
--  Dialecto: escrito para SQLite (la base por defecto del proyecto).
--  Si migras a MySQL o PostgreSQL, revisa las notas marcadas con «-- MySQL:».
--
--  Orden de creación: primero las tablas sin llaves foráneas y luego las que
--  dependen de ellas, para que las FOREIGN KEY siempre apunten a algo que ya
--  existe (moneda y viaje van primero).
-- ============================================================================

PRAGMA foreign_keys = ON;   -- SQLite: activa el respeto a las llaves foráneas.

-- ----------------------------------------------------------------------------
-- 1) MONEDA  — catálogo de monedas (MXN, EUR, USD, ...)
-- ----------------------------------------------------------------------------
CREATE TABLE moneda (
    idMoneda    INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      VARCHAR(60)  NOT NULL,          -- Ej. "Euro"
    codigo      VARCHAR(10)  NOT NULL UNIQUE,   -- Código ISO, ej. "EUR"
    tipoCambio  REAL         DEFAULT 1          -- Valor sugerido (destino por 1 de la principal)
);

-- ----------------------------------------------------------------------------
-- 2) VIAJE  — tabla CENTRAL del sistema
-- ----------------------------------------------------------------------------
CREATE TABLE viaje (
    idViaje         INTEGER PRIMARY KEY AUTOINCREMENT,
    origen          VARCHAR(120) NOT NULL,       -- Ciudad/país de salida
    destino         VARCHAR(120) NOT NULL,       -- Ciudad/país de llegada
    fechaSalida     DATE,                        -- Fecha de inicio
    fechaRegreso    DATE,                        -- Fecha de fin
    numViajeros     INTEGER      NOT NULL DEFAULT 1,
    monedaPrincipal VARCHAR(10)  NOT NULL DEFAULT 'MXN'  -- Código ISO de la moneda base
);

-- ----------------------------------------------------------------------------
-- 3) VIAJERO  — personas del viaje.  Viaje 1:N Viajero
-- ----------------------------------------------------------------------------
CREATE TABLE viajero (
    idViajero    INTEGER PRIMARY KEY AUTOINCREMENT,
    idViaje      INTEGER NOT NULL,               -- FK -> viaje
    nombre       VARCHAR(150) NOT NULL,
    nacionalidad VARCHAR(80),
    pasaporte    VARCHAR(40),                    -- Lleva letras y números
    FOREIGN KEY (idViaje) REFERENCES viaje (idViaje) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 4) DOCUMENTACION  — requisitos por viajero.  Viajero 1:N Documentacion
-- ----------------------------------------------------------------------------
CREATE TABLE documentacion (
    idDocumentacion  INTEGER PRIMARY KEY AUTOINCREMENT,
    idViajero        INTEGER NOT NULL,           -- FK -> viajero
    tipoDocumento    VARCHAR(80) NOT NULL,       -- Ej. "Pasaporte", "ETIAS"
    descripcion      VARCHAR(255),
    estado           VARCHAR(40) DEFAULT 'Pendiente',  -- Ej. "Vigente", "Pendiente", "Vencido"
    fechaVencimiento DATE,
    observaciones    VARCHAR(255),
    FOREIGN KEY (idViajero) REFERENCES viajero (idViajero) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 5) HOSPEDAJE  — alternativas de alojamiento.  Viaje 1:N Hospedaje
--    Campo de apoyo: "incluido" (si suma o no al presupuesto).
-- ----------------------------------------------------------------------------
CREATE TABLE hospedaje (
    idHospedaje     INTEGER PRIMARY KEY AUTOINCREMENT,
    idViaje         INTEGER NOT NULL,            -- FK -> viaje
    nombre          VARCHAR(150) NOT NULL,
    categoria       VARCHAR(40),                 -- Ej. "4 estrellas"
    costoGrupo      REAL,                        -- Costo total del alojamiento     -- MySQL: DECIMAL(12,2)
    costoPersona    REAL,                        -- Costo por viajero (alternativa)  -- MySQL: DECIMAL(12,2)
    desayuno        BOOLEAN DEFAULT 0,           -- 0 = no, 1 = sí
    ubicacion       VARCHAR(200),
    tipoAlojamiento VARCHAR(60),                 -- Ej. "Hotel", "Airbnb"
    puntuacion      REAL,                        -- Ej. 4.5
    incluido        BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (idViaje) REFERENCES viaje (idViaje) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 6) VUELO  — opciones de vuelo.  Viaje 1:N Vuelo
--    Campos de apoyo: "incluido" y "porPersona" (si el precio es por persona).
-- ----------------------------------------------------------------------------
CREATE TABLE vuelo (
    idVuelo           INTEGER PRIMARY KEY AUTOINCREMENT,
    idViaje           INTEGER NOT NULL,          -- FK -> viaje
    aeropuertoSalida  VARCHAR(10),               -- Código IATA, ej. "MEX"
    aeropuertoLlegada VARCHAR(10),               -- Código IATA, ej. "CDG"
    fechaSalida       DATETIME,                  -- Fecha y hora de despegue
    fechaRegreso      DATETIME,                  -- Fecha y hora de retorno
    precio            REAL,                      -- MySQL: DECIMAL(12,2)
    equipaje          VARCHAR(120),              -- Ej. "1 maleta 23kg"
    incluido          BOOLEAN NOT NULL DEFAULT 1,
    porPersona        BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (idViaje) REFERENCES viaje (idViaje) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 7) TRANSPORTE  — transporte local.  Viaje 1:N Transporte
--    Campos de apoyo: "incluido" y "porPersona".
-- ----------------------------------------------------------------------------
CREATE TABLE transporte (
    idTransporte INTEGER PRIMARY KEY AUTOINCREMENT,
    idViaje      INTEGER NOT NULL,               -- FK -> viaje
    tipo         VARCHAR(80) NOT NULL,           -- Ej. "Navigo Semaine"
    costo        REAL,                           -- MySQL: DECIMAL(12,2)
    unidad       VARCHAR(80),                    -- Empresa o número de servicio
    descripcion  VARCHAR(200),
    zonas        VARCHAR(80),                    -- Ej. "Zona 1-3"
    incluido     BOOLEAN NOT NULL DEFAULT 1,
    porPersona   BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (idViaje) REFERENCES viaje (idViaje) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 8) ACTIVIDAD  — lugares/tours.  Viaje 1:N Actividad
--    Campos de apoyo: "incluido" y "porPersona".
-- ----------------------------------------------------------------------------
CREATE TABLE actividad (
    idActividad INTEGER PRIMARY KEY AUTOINCREMENT,
    idViaje     INTEGER NOT NULL,                -- FK -> viaje
    nombre      VARCHAR(150) NOT NULL,
    ubicacion   VARCHAR(200),
    precio      REAL,                            -- MySQL: DECIMAL(12,2)
    descripcion VARCHAR(255),
    incluido    BOOLEAN NOT NULL DEFAULT 1,
    porPersona  BOOLEAN NOT NULL DEFAULT 1,
    FOREIGN KEY (idViaje) REFERENCES viaje (idViaje) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 9) PRESUPUESTO  — un presupuesto por viaje.  Viaje 1:1 Presupuesto
--    El UNIQUE en idViaje es lo que fuerza la relación 1:1.
--    Montos manuales: montoDisponible, costoAlimentos, gastosExtras.
--    El resto los calcula la aplicación desde las opciones "incluidas".
-- ----------------------------------------------------------------------------
CREATE TABLE presupuesto (
    idPresupuesto    INTEGER PRIMARY KEY AUTOINCREMENT,
    idViaje          INTEGER NOT NULL UNIQUE,    -- FK -> viaje (1:1)
    montoDisponible  REAL DEFAULT 0,
    costoVuelo       REAL DEFAULT 0,
    costoHospedaje   REAL DEFAULT 0,
    costoAlimentos   REAL DEFAULT 0,
    costoTransporte  REAL DEFAULT 0,
    costoActividades REAL DEFAULT 0,
    gastosExtras     REAL DEFAULT 0,
    costoTotal       REAL DEFAULT 0,
    costoPorPersona  REAL DEFAULT 0,
    FOREIGN KEY (idViaje) REFERENCES viaje (idViaje) ON DELETE CASCADE
);

-- ----------------------------------------------------------------------------
-- 10) COTIZACION  — propuestas de precio ya convertidas a una moneda.
--     Viaje 1:N Cotizacion  y  Moneda 1:N Cotizacion
-- ----------------------------------------------------------------------------
CREATE TABLE cotizacion (
    idCotizacion    INTEGER PRIMARY KEY AUTOINCREMENT,
    idViaje         INTEGER NOT NULL,            -- FK -> viaje
    idMoneda        INTEGER,                     -- FK -> moneda
    fecha           DATE NOT NULL,
    tipoCambio      REAL NOT NULL DEFAULT 1,     -- Destino por 1 de la moneda principal
    costoTotal      REAL DEFAULT 0,              -- Total ya convertido
    costoPorPersona REAL DEFAULT 0,
    FOREIGN KEY (idViaje)  REFERENCES viaje  (idViaje)  ON DELETE CASCADE,
    FOREIGN KEY (idMoneda) REFERENCES moneda (idMoneda)
);

-- ----------------------------------------------------------------------------
--  Datos base sugeridos (opcional). `flask init-db` ya inserta estas monedas.
-- ----------------------------------------------------------------------------
-- INSERT INTO moneda (nombre, codigo, tipoCambio) VALUES
--     ('Peso mexicano', 'MXN', 1.0),
--     ('Euro', 'EUR', 0.055),
--     ('Dólar estadounidense', 'USD', 0.058);

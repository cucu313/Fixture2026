# Conexión y creación de la base de datos SQLite

import sqlite3
import os

# Ruta donde se va a guardar el archivo de la base de datos
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mundial.db")

def get_connection():
    """Devuelve una conexión a la base de datos"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn

def inicializar_db():
    """Crea todas las tablas si no existen"""
    conn = get_connection()
    cursor = conn.cursor()

    # Tabla de equipos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS equipos (
            id      TEXT PRIMARY KEY,
            nombre  TEXT NOT NULL,
            grupo   TEXT NOT NULL,
            bandera TEXT
        )
    """)

    # Tabla de partidos (fase de grupos)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS partidos (
            id               TEXT PRIMARY KEY,
            grupo            TEXT NOT NULL,
            jornada          INTEGER NOT NULL,
            local            TEXT NOT NULL,
            visitante        TEXT NOT NULL,
            fecha            TEXT NOT NULL,
            hora             TEXT NOT NULL,
            sede             TEXT,
            goles_local      INTEGER,
            goles_visitante  INTEGER,
            FOREIGN KEY (local)     REFERENCES equipos(id),
            FOREIGN KEY (visitante) REFERENCES equipos(id)
        )
    """)

    # Tabla de partidos de playoffs
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS playoffs (
            id          TEXT PRIMARY KEY,
            ronda       TEXT NOT NULL,
            equipo_a    TEXT,
            equipo_b    TEXT,
            goles_a     INTEGER,
            goles_b     INTEGER,
            ganador     TEXT,
            definido_en TEXT
        )
    """)

    # Tabla de estadísticas de jugadores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estadisticas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            jugador     TEXT NOT NULL,
            equipo      TEXT NOT NULL,
            goles       INTEGER DEFAULT 0,
            asistencias INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()
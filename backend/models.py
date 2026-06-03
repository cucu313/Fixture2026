# Funciones para insertar y consultar datos en la base de datos

from contextlib import contextmanager
from database import get_connection


@contextmanager
def get_cursor():
    """
    Abre la conexión, entrega el cursor y cierra todo automáticamente.
    El try/finally garantiza que la conexión se cierre siempre,
    incluso si ocurre un error externo (disco lleno, archivo bloqueado, etc.)
    """
    conn = get_connection()
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        conn.close()


# ─────────────────────────────────────────
# EQUIPOS
# ─────────────────────────────────────────

def insertar_equipo(id, nombre, grupo, bandera):
    """Inserta un equipo. Si ya existe lo ignora."""
    with get_cursor() as cursor:
        cursor.execute("""
            INSERT OR IGNORE INTO equipos (id, nombre, grupo, bandera)
            VALUES (?, ?, ?, ?)
        """, (id, nombre, grupo, bandera))


def obtener_equipos():
    """Devuelve todos los equipos ordenados por grupo."""
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM equipos ORDER BY grupo, nombre")
        return [dict(fila) for fila in cursor.fetchall()]


def obtener_equipos_por_grupo(grupo):
    """Devuelve los equipos de un grupo específico."""
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM equipos WHERE grupo = ?", (grupo,))
        return [dict(fila) for fila in cursor.fetchall()]


# ─────────────────────────────────────────
# PARTIDOS
# ─────────────────────────────────────────

def insertar_partido(id, grupo, jornada, local, visitante, fecha, hora, sede):
    """Inserta un partido. Si ya existe lo ignora."""
    with get_cursor() as cursor:
        cursor.execute("""
            INSERT OR IGNORE INTO partidos
            (id, grupo, jornada, local, visitante, fecha, hora, sede)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (id, grupo, jornada, local, visitante, fecha, hora, sede))


def obtener_partidos():
    """Devuelve todos los partidos ordenados por fecha y hora."""
    with get_cursor() as cursor:
        cursor.execute("SELECT * FROM partidos ORDER BY fecha, hora")
        return [dict(fila) for fila in cursor.fetchall()]


def obtener_partidos_por_grupo(grupo):
    """Devuelve los partidos de un grupo específico ordenados por jornada."""
    with get_cursor() as cursor:
        cursor.execute("""
            SELECT * FROM partidos WHERE grupo = ? ORDER BY jornada
        """, (grupo,))
        return [dict(fila) for fila in cursor.fetchall()]


def cargar_resultado(id_partido, goles_local, goles_visitante):
    """Carga el resultado de un partido existente."""
    with get_cursor() as cursor:
        cursor.execute("""
            UPDATE partidos
            SET goles_local = ?, goles_visitante = ?
            WHERE id = ?
        """, (goles_local, goles_visitante, id_partido))


# ─────────────────────────────────────────
# ESTADISTICAS
# ─────────────────────────────────────────

def registrar_estadistica(jugador, equipo, goles=0, asistencias=0):
    """
    Registra goles y asistencias de un jugador.
    Si el jugador ya existe suma los valores, si no lo crea.
    """
    with get_cursor() as cursor:
        cursor.execute("""
            SELECT id FROM estadisticas WHERE jugador = ? AND equipo = ?
        """, (jugador, equipo))
        existente = cursor.fetchone()

        if existente:
            cursor.execute("""
                UPDATE estadisticas
                SET goles = goles + ?, asistencias = asistencias + ?
                WHERE jugador = ? AND equipo = ?
            """, (goles, asistencias, jugador, equipo))
        else:
            cursor.execute("""
                INSERT INTO estadisticas (jugador, equipo, goles, asistencias)
                VALUES (?, ?, ?, ?)
            """, (jugador, equipo, goles, asistencias))


def obtener_goleadores():
    """Devuelve el ranking de goleadores ordenado de mayor a menor."""
    with get_cursor() as cursor:
        cursor.execute("""
            SELECT jugador, equipo, goles, asistencias
            FROM estadisticas
            WHERE goles > 0
            ORDER BY goles DESC
        """)
        return [dict(fila) for fila in cursor.fetchall()]


def obtener_asistidores():
    """Devuelve el ranking de asistidores ordenado de mayor a menor."""
    with get_cursor() as cursor:
        cursor.execute("""
            SELECT jugador, equipo, goles, asistencias
            FROM estadisticas
            WHERE asistencias > 0
            ORDER BY asistencias DESC
        """)
        return [dict(fila) for fila in cursor.fetchall()]
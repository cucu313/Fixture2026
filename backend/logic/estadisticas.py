# Gestión de goleadores y asistidores del torneo

from models import registrar_estadistica, obtener_goleadores, obtener_asistidores


def registrar_gol(jugador, equipo):
    """
    Registra un gol para un jugador.
    Si el jugador no existe en la base de datos lo crea.
    Si ya existe suma 1 a sus goles.
    """
    registrar_estadistica(jugador, equipo, goles=1, asistencias=0)


def registrar_asistencia(jugador, equipo):
    """
    Registra una asistencia para un jugador.
    Si el jugador no existe en la base de datos lo crea.
    Si ya existe suma 1 a sus asistencias.
    """
    registrar_estadistica(jugador, equipo, goles=0, asistencias=1)


def get_goleadores():
    """
    Devuelve el ranking completo de goleadores ordenado de mayor a menor.
    Cada elemento tiene: jugador, equipo, goles, asistencias.
    """
    return obtener_goleadores()


def get_asistidores():
    """
    Devuelve el ranking completo de asistidores ordenado de mayor a menor.
    Cada elemento tiene: jugador, equipo, goles, asistencias.
    """
    return obtener_asistidores()
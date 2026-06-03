# Clasificación de equipos y armado de llaves eliminatorias

from models import obtener_partidos_por_grupo
from logic.posiciones import calcular_tabla


# Los 12 grupos del Mundial 2026
GRUPOS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]


def obtener_todas_las_tablas():
    """
    Calcula y devuelve las tablas de posiciones de los 12 grupos.
    Retorna un diccionario donde la clave es la letra del grupo.
    Ejemplo: { "A": [...], "B": [...], ... }
    """
    return {grupo: calcular_tabla(grupo) for grupo in GRUPOS}


def obtener_clasificados():
    """
    Determina los 32 clasificados a la fase eliminatoria:
    - 24 clasificados directos: 1° y 2° de cada grupo
    - 8 mejores terceros de los 12 grupos

    Retorna un diccionario con tres listas: primeros, segundos, mejores_terceros.
    """
    tablas = obtener_todas_las_tablas()

    primeros  = []
    segundos  = []
    terceros  = []

    for grupo, tabla in tablas.items():
        if len(tabla) < 3:
            continue
        primeros.append({**tabla[0], "grupo": grupo})
        segundos.append({**tabla[1], "grupo": grupo})
        terceros.append({**tabla[2], "grupo": grupo})

    mejores_terceros = _ordenar_terceros(terceros)[:8]

    return {
        "primeros":         primeros,
        "segundos":         segundos,
        "mejores_terceros": mejores_terceros
    }


def crear_partido_playoff(id, ronda, equipo_a=None, equipo_b=None):
    """
    Crea y devuelve un partido de playoff vacío.
    Los campos de goles y ganador arrancan en None hasta que se cargue el resultado.

    Parámetros:
        id       — identificador único del partido (ej: "R32_1")
        ronda    — nombre de la ronda (ej: "Octavos de final")
        equipo_a — id del primer equipo (puede ser None si aún no se definió)
        equipo_b — id del segundo equipo (puede ser None si aún no se definió)
    """
    return {
        "id":          id,
        "ronda":       ronda,
        "equipo_a":    equipo_a,
        "equipo_b":    equipo_b,
        "goles_a":     None,
        "goles_b":     None,
        "ganador":     None,
        "definido_en": None  # "regular", "extratime" o "penales"
    }


def registrar_resultado_playoff(partido, goles_a, goles_b, definido_en="regular", ganador=None):
    """
    Registra el resultado de un partido eliminatorio y determina el ganador.

    En playoffs no puede haber empate en tiempo regular.
    Si se define en penales o extratime y el marcador quedó igualado,
    el ganador debe indicarse explícitamente con el parámetro 'ganador'.
    """
    partido["goles_a"]     = goles_a
    partido["goles_b"]     = goles_b
    partido["definido_en"] = definido_en

    if goles_a > goles_b:
        partido["ganador"] = partido["equipo_a"]
    elif goles_b > goles_a:
        partido["ganador"] = partido["equipo_b"]
    else:
        # Marcador igualado — el ganador se indica explícitamente (penales)
        partido["ganador"] = ganador

    return partido


# ─────────────────────────────────────────
# FUNCIONES INTERNAS
# ─────────────────────────────────────────

def _ordenar_terceros(terceros):
    """
    Ordena los terceros lugares por criterios FIFA:
    1° Puntos  2° Diferencia de goles  3° Goles a favor
    """
    return sorted(terceros, key=lambda e: (-e["PTS"], -e["DG"], -e["GF"]))
# Cálculo de tablas de posiciones con criterios de desempate FIFA


from models import obtener_equipos_por_grupo, obtener_partidos_por_grupo


def calcular_tabla(grupo):
    """
    Calcula y devuelve la tabla de posiciones de un grupo ordenada.
    Es el punto de entrada principal de este módulo.
    """
    equipos  = obtener_equipos_por_grupo(grupo)
    partidos = obtener_partidos_por_grupo(grupo)

    tabla = _inicializar_tabla(equipos)
    tabla = _procesar_partidos(tabla, partidos)
    tabla = _ordenar_tabla(tabla, partidos)

    return tabla


# ─────────────────────────────────────────
# FUNCIONES INTERNAS
# ─────────────────────────────────────────

def _inicializar_tabla(equipos):
    """
    Crea un diccionario con estadísticas en cero para cada equipo.
    La clave es el id del equipo (ej: 'ARG').
    """
    tabla = {}
    for equipo in equipos:
        tabla[equipo["id"]] = {
            "id":  equipo["id"],
            "PJ":  0,  # Partidos jugados
            "PG":  0,  # Partidos ganados
            "PE":  0,  # Partidos empatados
            "PP":  0,  # Partidos perdidos
            "GF":  0,  # Goles a favor
            "GC":  0,  # Goles en contra
            "DG":  0,  # Diferencia de goles
            "PTS": 0,  # Puntos
        }
    return tabla


def _procesar_partidos(tabla, partidos):
    """
    Recorre los partidos jugados y actualiza las estadísticas de cada equipo.
    Ignora los partidos sin resultado cargado.
    """
    for partido in partidos:
        goles_local     = partido["goles_local"]
        goles_visitante = partido["goles_visitante"]

        # Ignorar partidos sin resultado
        if goles_local is None or goles_visitante is None:
            continue

        local     = partido["local"]
        visitante = partido["visitante"]

        # Actualizar partidos jugados y goles
        tabla[local]["PJ"]     += 1
        tabla[visitante]["PJ"] += 1
        tabla[local]["GF"]     += goles_local
        tabla[local]["GC"]     += goles_visitante
        tabla[visitante]["GF"] += goles_visitante
        tabla[visitante]["GC"] += goles_local

        # Determinar resultado y asignar puntos
        if goles_local > goles_visitante:
            tabla[local]["PG"]      += 1
            tabla[local]["PTS"]     += 3
            tabla[visitante]["PP"]  += 1
        elif goles_local < goles_visitante:
            tabla[visitante]["PG"]  += 1
            tabla[visitante]["PTS"] += 3
            tabla[local]["PP"]      += 1
        else:
            tabla[local]["PE"]      += 1
            tabla[local]["PTS"]     += 1
            tabla[visitante]["PE"]  += 1
            tabla[visitante]["PTS"] += 1

    # Calcular diferencia de goles al final
    for equipo in tabla.values():
        equipo["DG"] = equipo["GF"] - equipo["GC"]

    return tabla


def _ordenar_tabla(tabla, partidos):
    """
    Convierte la tabla a lista y la ordena aplicando
    los 4 criterios de desempate FIFA en orden de prioridad.
    """
    lista = list(tabla.values())

    lista.sort(key=lambda a: (
        -a["PTS"],  # 1° Mayor puntos
        -a["DG"],   # 2° Mayor diferencia de goles
        -a["GF"],   # 3° Mayor goles a favor
    ))

    # Criterio 4: enfrentamiento directo (solo entre empatados en los 3 anteriores)
    lista = _aplicar_enfrentamiento_directo(lista, partidos)

    return lista


def _aplicar_enfrentamiento_directo(lista, partidos):
    """
    Revisa si hay equipos empatados en puntos, DG y GF.
    Si los hay, los ordena por el resultado de su enfrentamiento directo.
    """
    for i in range(len(lista) - 1):
        a = lista[i]
        b = lista[i + 1]

        # Solo aplicar si están empatados en los 3 primeros criterios
        if a["PTS"] == b["PTS"] and a["DG"] == b["DG"] and a["GF"] == b["GF"]:
            if _gano_enfrentamiento(b["id"], a["id"], partidos):
                lista[i], lista[i + 1] = lista[i + 1], lista[i]

    return lista


def _gano_enfrentamiento(idA, idB, partidos):
    """
    Devuelve True si el equipo A ganó el enfrentamiento directo contra B.
    """
    for partido in partidos:
        if partido["local"] == idA and partido["visitante"] == idB:
            if partido["goles_local"] is None:
                return False
            return partido["goles_local"] > partido["goles_visitante"]
        if partido["local"] == idB and partido["visitante"] == idA:
            if partido["goles_local"] is None:
                return False
            return partido["goles_visitante"] > partido["goles_local"]
    return False
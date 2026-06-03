# Punto de entrada de la aplicación Flask
# Define todas las rutas de la API REST

from flask import Flask, jsonify, request
from database import inicializar_db
from models import (
    insertar_equipo, insertar_partido,
    obtener_equipos, obtener_partidos,
    obtener_partidos_por_grupo, cargar_resultado
)
from logic.posiciones import calcular_tabla
from logic.estadisticas import registrar_gol, registrar_asistencia, get_goleadores, get_asistidores
from logic.playoffs import obtener_clasificados, crear_partido_playoff, registrar_resultado_playoff

app = Flask(__name__)


# ─────────────────────────────────────────
# INICIALIZACIÓN
# ─────────────────────────────────────────

@app.before_request
def setup():
    """
    Se ejecuta antes de la primera solicitud.
    Inicializa la base de datos y carga los datos si están vacíos.
    """
    inicializar_db()
    _cargar_datos_iniciales()


# ─────────────────────────────────────────
# RUTAS — EQUIPOS
# ─────────────────────────────────────────

@app.route("/api/equipos", methods=["GET"])
def get_equipos():
    """Devuelve todos los equipos del torneo."""
    return jsonify(obtener_equipos())


@app.route("/api/equipos/<grupo>", methods=["GET"])
def get_equipos_grupo(grupo):
    """Devuelve los equipos de un grupo específico."""
    from models import obtener_equipos_por_grupo
    return jsonify(obtener_equipos_por_grupo(grupo.upper()))


# ─────────────────────────────────────────
# RUTAS — PARTIDOS
# ─────────────────────────────────────────

@app.route("/api/partidos", methods=["GET"])
def get_partidos():
    """Devuelve todos los partidos ordenados por fecha."""
    return jsonify(obtener_partidos())


@app.route("/api/partidos/<grupo>", methods=["GET"])
def get_partidos_grupo(grupo):
    """Devuelve los partidos de un grupo específico."""
    return jsonify(obtener_partidos_por_grupo(grupo.upper()))


@app.route("/api/partidos/<id_partido>/resultado", methods=["POST"])
def post_resultado(id_partido):
    """
    Carga el resultado de un partido de fase de grupos.
    Espera un JSON con: goles_local, goles_visitante.
    Opcionalmente: goleadores y asistidores.

    Ejemplo de body:
    {
        "goles_local": 2,
        "goles_visitante": 1,
        "goleadores": [
            { "jugador": "Messi", "equipo": "ARG" }
        ],
        "asistidores": [
            { "jugador": "Di Maria", "equipo": "ARG" }
        ]
    }
    """
    datos = request.get_json()

    goles_local     = datos.get("goles_local")
    goles_visitante = datos.get("goles_visitante")

    # Validar que los goles sean números válidos
    if goles_local is None or goles_visitante is None:
        return jsonify({ "error": "Faltan goles_local o goles_visitante" }), 400

    if not isinstance(goles_local, int) or not isinstance(goles_visitante, int):
        return jsonify({ "error": "Los goles deben ser números enteros" }), 400

    if goles_local < 0 or goles_visitante < 0:
        return jsonify({ "error": "Los goles no pueden ser negativos" }), 400

    # Guardar resultado
    cargar_resultado(id_partido, goles_local, goles_visitante)

    # Registrar goleadores si se enviaron
    for gol in datos.get("goleadores", []):
        registrar_gol(gol["jugador"], gol["equipo"])

    # Registrar asistidores si se enviaron
    for asistencia in datos.get("asistidores", []):
        registrar_asistencia(asistencia["jugador"], asistencia["equipo"])

    return jsonify({ "mensaje": "Resultado cargado correctamente" }), 200


# ─────────────────────────────────────────
# RUTAS — POSICIONES
# ─────────────────────────────────────────

@app.route("/api/posiciones/<grupo>", methods=["GET"])
def get_posiciones(grupo):
    """Devuelve la tabla de posiciones de un grupo ordenada."""
    return jsonify(calcular_tabla(grupo.upper()))


# ─────────────────────────────────────────
# RUTAS — ESTADÍSTICAS
# ─────────────────────────────────────────

@app.route("/api/goleadores", methods=["GET"])
def get_goleadores():
    """Devuelve el ranking de goleadores del torneo."""
    return jsonify(get_goleadores())


@app.route("/api/asistidores", methods=["GET"])
def get_asistidores():
    """Devuelve el ranking de asistidores del torneo."""
    return jsonify(get_asistidores())


# ─────────────────────────────────────────
# RUTAS — PLAYOFFS
# ─────────────────────────────────────────

@app.route("/api/clasificados", methods=["GET"])
def get_clasificados():
    """Devuelve los 32 clasificados a la fase eliminatoria."""
    return jsonify(obtener_clasificados())


# ─────────────────────────────────────────
# DATOS INICIALES
# ─────────────────────────────────────────

def _cargar_datos_iniciales():
    """
    Carga los 48 equipos y 72 partidos en la base de datos.
    Usa INSERT OR IGNORE para no duplicar datos si ya existen.
    """
    equipos = [
        # GRUPO A
        ("MEX", "México",          "A", "🇲🇽"),
        ("KOR", "Corea del Sur",   "A", "🇰🇷"),
        ("RSA", "Sudáfrica",       "A", "🇿🇦"),
        ("CZE", "República Checa", "A", "🇨🇿"),
        # GRUPO B
        ("CAN", "Canadá",          "B", "🇨🇦"),
        ("SUI", "Suiza",           "B", "🇨🇭"),
        ("QAT", "Qatar",           "B", "🇶🇦"),
        ("BIH", "Bosnia y Herz.",  "B", "🇧🇦"),
        # GRUPO C
        ("BRA", "Brasil",          "C", "🇧🇷"),
        ("MAR", "Marruecos",       "C", "🇲🇦"),
        ("SCO", "Escocia",         "C", "SCO"),
        ("HAI", "Haití",           "C", "🇭🇹"),
        # GRUPO D
        ("USA", "Estados Unidos",  "D", "🇺🇸"),
        ("AUS", "Australia",       "D", "🇦🇺"),
        ("PAR", "Paraguay",        "D", "🇵🇾"),
        ("TUR", "Turquía",         "D", "🇹🇷"),
        # GRUPO E
        ("GER", "Alemania",        "E", "🇩🇪"),
        ("ECU", "Ecuador",         "E", "🇪🇨"),
        ("CIV", "Costa de Marfil", "E", "🇨🇮"),
        ("CUW", "Curazao",         "E", "🇨🇼"),
        # GRUPO F
        ("NED", "Países Bajos",    "F", "🇳🇱"),
        ("JPN", "Japón",           "F", "🇯🇵"),
        ("TUN", "Túnez",           "F", "🇹🇳"),
        ("SWE", "Suecia",          "F", "🇸🇪"),
        # GRUPO G
        ("BEL", "Bélgica",         "G", "🇧🇪"),
        ("IRN", "Irán",            "G", "🇮🇷"),
        ("EGY", "Egipto",          "G", "🇪🇬"),
        ("NZL", "Nueva Zelanda",   "G", "🇳🇿"),
        # GRUPO H
        ("ESP", "España",          "H", "🇪🇸"),
        ("URU", "Uruguay",         "H", "🇺🇾"),
        ("KSA", "Arabia Saudita",  "H", "🇸🇦"),
        ("CPV", "Cabo Verde",      "H", "🇨🇻"),
        # GRUPO I
        ("FRA", "Francia",         "I", "🇫🇷"),
        ("SEN", "Senegal",         "I", "🇸🇳"),
        ("NOR", "Noruega",         "I", "🇳🇴"),
        ("IRQ", "Irak",            "I", "🇮🇶"),
        # GRUPO J
        ("ARG", "Argentina",       "J", "🇦🇷"),
        ("AUT", "Austria",         "J", "🇦🇹"),
        ("ALG", "Argelia",         "J", "🇩🇿"),
        ("JOR", "Jordania",        "J", "🇯🇴"),
        # GRUPO K
        ("POR", "Portugal",        "K", "🇵🇹"),
        ("COL", "Colombia",        "K", "🇨🇴"),
        ("UZB", "Uzbekistán",      "K", "🇺🇿"),
        ("COD", "RD del Congo",    "K", "🇨🇩"),
        # GRUPO L
        ("ENG", "Inglaterra",      "L", "ENG"),
        ("CRO", "Croacia",         "L", "🇭🇷"),
        ("PAN", "Panamá",          "L", "🇵🇦"),
        ("GHA", "Ghana",           "L", "🇬🇭"),
    ]

    partidos = [
        # GRUPO A
        ("A1","A",1,"MEX","RSA","2026-06-11","16:00","Estadio Azteca, Ciudad de México"),
        ("A2","A",1,"KOR","CZE","2026-06-11","23:00","Estadio Akron, Guadalajara"),
        ("A3","A",2,"CZE","RSA","2026-06-18","15:00","Mercedes-Benz Stadium, Atlanta"),
        ("A4","A",2,"MEX","KOR","2026-06-19","00:00","Estadio Akron, Guadalajara"),
        ("A5","A",3,"CZE","MEX","2026-06-25","00:00","Estadio Azteca, Ciudad de México"),
        ("A6","A",3,"RSA","KOR","2026-06-25","00:00","Estadio BBVA, Monterrey"),
        # GRUPO B
        ("B1","B",1,"CAN","BIH","2026-06-12","18:00","BMO Field, Toronto"),
        ("B2","B",1,"QAT","SUI","2026-06-13","18:00","Levi's Stadium, San Francisco"),
        ("B3","B",2,"SUI","BIH","2026-06-18","18:00","SoFi Stadium, Los Ángeles"),
        ("B4","B",2,"CAN","QAT","2026-06-18","21:00","BC Place, Vancouver"),
        ("B5","B",3,"SUI","CAN","2026-06-24","18:00","BC Place, Vancouver"),
        ("B6","B",3,"BIH","QAT","2026-06-24","18:00","Lumen Field, Seattle"),
        # GRUPO C
        ("C1","C",1,"BRA","MAR","2026-06-13","21:00","MetLife Stadium, Nueva Jersey"),
        ("C2","C",1,"HAI","SCO","2026-06-14","00:00","Gillette Stadium, Boston"),
        ("C3","C",2,"BRA","HAI","2026-06-19","21:00","Gillette Stadium, Boston"),
        ("C4","C",2,"SCO","MAR","2026-06-20","00:00","Lincoln Financial Field, Filadelfia"),
        ("C5","C",3,"SCO","BRA","2026-06-25","21:00","Hard Rock Stadium, Miami"),
        ("C6","C",3,"MAR","HAI","2026-06-25","21:00","Mercedes-Benz Stadium, Atlanta"),
        # GRUPO D
        ("D1","D",1,"USA","PAR","2026-06-13","00:00","SoFi Stadium, Los Ángeles"),
        ("D2","D",1,"AUS","TUR","2026-06-13","03:00","BC Place, Vancouver"),
        ("D3","D",2,"TUR","PAR","2026-06-19","03:00","Levi's Stadium, San Francisco"),
        ("D4","D",2,"USA","AUS","2026-06-19","18:00","Lumen Field, Seattle"),
        ("D5","D",3,"TUR","USA","2026-06-26","01:00","SoFi Stadium, Los Ángeles"),
        ("D6","D",3,"PAR","AUS","2026-06-26","01:00","Levi's Stadium, San Francisco"),
        # GRUPO E
        ("E1","E",1,"GER","CUW","2026-06-14","16:00","NRG Stadium, Houston"),
        ("E2","E",1,"CIV","ECU","2026-06-14","22:00","Lincoln Financial Field, Filadelfia"),
        ("E3","E",2,"GER","CIV","2026-06-20","21:00","BMO Field, Toronto"),
        ("E4","E",2,"ECU","CUW","2026-06-20","23:00","Arrowhead Stadium, Kansas City"),
        ("E5","E",3,"ECU","GER","2026-06-26","21:00","MetLife Stadium, Nueva Jersey"),
        ("E6","E",3,"CUW","CIV","2026-06-26","21:00","Lincoln Financial Field, Filadelfia"),
        # GRUPO F
        ("F1","F",1,"NED","JPN","2026-06-14","19:00","AT&T Stadium, Dallas"),
        ("F2","F",1,"TUN","SWE","2026-06-15","01:00","Arrowhead Stadium, Kansas City"),
        ("F3","F",2,"NED","TUN","2026-06-20","18:00","SoFi Stadium, Los Ángeles"),
        ("F4","F",2,"SWE","JPN","2026-06-21","00:00","Lumen Field, Seattle"),
        ("F5","F",3,"SWE","NED","2026-06-25","18:00","BC Place, Vancouver"),
        ("F6","F",3,"JPN","TUN","2026-06-25","18:00","AT&T Stadium, Dallas"),
        # GRUPO G
        ("G1","G",1,"BEL","IRN","2026-06-15","16:00","AT&T Stadium, Dallas"),
        ("G2","G",1,"EGY","NZL","2026-06-15","22:00","Arrowhead Stadium, Kansas City"),
        ("G3","G",2,"BEL","EGY","2026-06-21","18:00","NRG Stadium, Houston"),
        ("G4","G",2,"NZL","IRN","2026-06-21","21:00","MetLife Stadium, Nueva Jersey"),
        ("G5","G",3,"NZL","BEL","2026-06-26","18:00","AT&T Stadium, Dallas"),
        ("G6","G",3,"IRN","EGY","2026-06-26","18:00","Arrowhead Stadium, Kansas City"),
        # GRUPO H
        ("H1","H",1,"ESP","CPV","2026-06-15","15:00","Mercedes-Benz Stadium, Atlanta"),
        ("H2","H",1,"KSA","URU","2026-06-16","01:00","Hard Rock Stadium, Miami"),
        ("H3","H",2,"ESP","KSA","2026-06-21","15:00","Mercedes-Benz Stadium, Atlanta"),
        ("H4","H",2,"URU","CPV","2026-06-22","00:00","Gillette Stadium, Boston"),
        ("H5","H",3,"ESP","URU","2026-06-26","00:00","Estadio Akron, Guadalajara"),
        ("H6","H",3,"CPV","KSA","2026-06-26","00:00","Hard Rock Stadium, Miami"),
        # GRUPO I
        ("I1","I",1,"FRA","SEN","2026-06-16","16:00","MetLife Stadium, Nueva Jersey"),
        ("I2","I",1,"NOR","IRQ","2026-06-16","22:00","Lincoln Financial Field, Filadelfia"),
        ("I3","I",2,"FRA","NOR","2026-06-22","18:00","Gillette Stadium, Boston"),
        ("I4","I",2,"IRQ","SEN","2026-06-22","21:00","Hard Rock Stadium, Miami"),
        ("I5","I",3,"IRQ","FRA","2026-06-27","00:00","NRG Stadium, Houston"),
        ("I6","I",3,"SEN","NOR","2026-06-27","00:00","BMO Field, Toronto"),
        # GRUPO J
        ("J1","J",1,"ARG","ALG","2026-06-16","19:00","AT&T Stadium, Dallas"),
        ("J2","J",1,"AUT","JOR","2026-06-17","01:00","Arrowhead Stadium, Kansas City"),
        ("J3","J",2,"ARG","AUT","2026-06-22","22:00","NRG Stadium, Houston"),
        ("J4","J",2,"JOR","ALG","2026-06-23","01:00","SoFi Stadium, Los Ángeles"),
        ("J5","J",3,"JOR","ARG","2026-06-27","03:00","AT&T Stadium, Dallas"),
        ("J6","J",3,"ALG","AUT","2026-06-27","03:00","Arrowhead Stadium, Kansas City"),
        # GRUPO K
        ("K1","K",1,"POR","COD","2026-06-17","16:00","Levi's Stadium, San Francisco"),
        ("K2","K",1,"UZB","COL","2026-06-17","22:00","Estadio Azteca, Ciudad de México"),
        ("K3","K",2,"POR","UZB","2026-06-23","16:00","Lumen Field, Seattle"),
        ("K4","K",2,"COL","COD","2026-06-23","22:00","SoFi Stadium, Los Ángeles"),
        ("K5","K",3,"COL","POR","2026-06-27","21:00","BMO Field, Toronto"),
        ("K6","K",3,"COD","UZB","2026-06-27","21:00","Levi's Stadium, San Francisco"),
        # GRUPO L
        ("L1","L",1,"ENG","CRO","2026-06-17","19:00","MetLife Stadium, Nueva Jersey"),
        ("L2","L",1,"PAN","GHA","2026-06-18","01:00","Mercedes-Benz Stadium, Atlanta"),
        ("L3","L",2,"ENG","PAN","2026-06-23","19:00","Hard Rock Stadium, Miami"),
        ("L4","L",2,"GHA","CRO","2026-06-24","01:00","Lincoln Financial Field, Filadelfia"),
        ("L5","L",3,"GHA","ENG","2026-06-27","18:00","Gillette Stadium, Boston"),
        ("L6","L",3,"CRO","PAN","2026-06-27","18:00","BMO Field, Toronto"),
    ]

    for e in equipos:
        insertar_equipo(*e)

    for p in partidos:
        insertar_partido(*p)


# ─────────────────────────────────────────
# INICIO
# ─────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)
// Lógica del frontend — conecta la UI con la API de Flask

const API = "http://127.0.0.1:5000/api";

// ─────────────────────────────────────────
// NAVEGACIÓN
// ─────────────────────────────────────────

function mostrarSeccion(nombre) {
    // Ocultar todas las secciones
    document.querySelectorAll(".seccion").forEach(s => s.classList.remove("activa"));
    document.querySelectorAll(".btn-nav").forEach(b => b.classList.remove("activo"));

    // Mostrar la sección seleccionada
    document.getElementById(`seccion-${nombre}`).classList.add("activa");
    event.target.classList.add("activo");

    // Cargar los datos de la sección
    if (nombre === "grupos")       cargarGrupos();
    if (nombre === "fixture")      cargarFixture();
    if (nombre === "playoffs")     cargarPlayoffs();
    if (nombre === "estadisticas") cargarEstadisticas();
}

// ─────────────────────────────────────────
// GRUPOS — TABLAS DE POSICIONES
// ─────────────────────────────────────────

async function cargarGrupos() {
    const grupos = ["A","B","C","D","E","F","G","H","I","J","K","L"];
    const contenedor = document.getElementById("contenedor-grupos");
    contenedor.innerHTML = "";

    for (const grupo of grupos) {
        const tabla = await fetchJSON(`${API}/posiciones/${grupo}`);
        contenedor.appendChild(renderGrupo(grupo, tabla));
    }
}

function renderGrupo(grupo, tabla) {
    const card = document.createElement("div");
    card.className = "grupo-card";
    card.innerHTML = `
        <h3>Grupo ${grupo}</h3>
        <table class="tabla-posiciones">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Equipo</th>
                    <th>PJ</th>
                    <th>PG</th>
                    <th>PE</th>
                    <th>PP</th>
                    <th>GF</th>
                    <th>GC</th>
                    <th>DG</th>
                    <th>PTS</th>
                </tr>
            </thead>
            <tbody>
                ${tabla.map((equipo, index) => `
                    <tr class="${index < 2 ? 'clasificado' : index === 2 ? 'mejor-tercero' : ''}">
                        <td>${index + 1}</td>
                        <td>${equipo.id}</td>
                        <td>${equipo.PJ}</td>
                        <td>${equipo.PG}</td>
                        <td>${equipo.PE}</td>
                        <td>${equipo.PP}</td>
                        <td>${equipo.GF}</td>
                        <td>${equipo.GC}</td>
                        <td>${equipo.DG}</td>
                        <td><strong>${equipo.PTS}</strong></td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
    `;
    return card;
}

// ─────────────────────────────────────────
// FIXTURE — CARGA DE RESULTADOS
// ─────────────────────────────────────────

let todosLosPartidos = [];

async function cargarFixture() {
    todosLosPartidos = await fetchJSON(`${API}/partidos`);
    filtrarPartidos();
}

function filtrarPartidos() {
    const grupo = document.getElementById("filtro-grupo").value;
    const partidos = grupo === "todos"
        ? todosLosPartidos
        : todosLosPartidos.filter(p => p.grupo === grupo);

    const contenedor = document.getElementById("contenedor-fixture");
    contenedor.innerHTML = "";
    partidos.forEach(p => contenedor.appendChild(renderPartido(p)));
}

function renderPartido(partido) {
    const jugado = partido.goles_local !== null;
    const card = document.createElement("div");
    card.className = `partido-card ${jugado ? "jugado" : ""}`;

    card.innerHTML = `
        <div class="partido-info">
            <div>Grupo ${partido.grupo} — J${partido.jornada}</div>
            <div>${partido.fecha} ${partido.hora}</div>
            <div>${partido.sede}</div>
        </div>
        <div class="partido-equipos">
            <span class="equipo-nombre">${partido.local}</span>
            <span class="resultado">
                ${jugado ? `${partido.goles_local} - ${partido.goles_visitante}` : "vs"}
            </span>
            <span class="equipo-nombre">${partido.visitante}</span>
        </div>
        <div class="partido-acciones">
            ${jugado ? `
                <span style="color: var(--color-exito)">✓ Cargado</span>
                <button class="btn-guardar" onclick="editarResultado('${partido.id}')">Editar</button>
            ` : `
                <input class="input-goles" type="number" min="0" id="local-${partido.id}" placeholder="0">
                <span>-</span>
                <input class="input-goles" type="number" min="0" id="visit-${partido.id}" placeholder="0">
                <button class="btn-guardar" onclick="guardarResultado('${partido.id}')">Guardar</button>
            `}
        </div>
    `;
    return card;
}

async function guardarResultado(idPartido) {
    const golesLocal     = parseInt(document.getElementById(`local-${idPartido}`).value);
    const golesVisitante = parseInt(document.getElementById(`visit-${idPartido}`).value);

    if (isNaN(golesLocal) || isNaN(golesVisitante)) {
        alert("Ingresá los goles de ambos equipos.");
        return;
    }

    if (golesLocal < 0 || golesVisitante < 0) {
        alert("Los goles no pueden ser negativos.");
        return;
    }

    // Buscar el partido para saber los equipos
    const partido = todosLosPartidos.find(p => p.id === idPartido);

    // Mostrar modal para ingresar jugadores
    mostrarModalJugadores(idPartido, partido.local, partido.visitante, golesLocal, golesVisitante);
}

async function editarResultado(idPartido) {
    const confirmar = confirm("¿Querés borrar este resultado para volver a cargarlo?");
    if (!confirmar) return;

    await fetch(`${API}/partidos/${idPartido}/borrar-resultado`, {
        method: "POST",
        headers: { "Content-Type": "application/json" }
    });

    await cargarFixture();
    await cargarGrupos();
}

// ─────────────────────────────────────────
// PLAYOFFS — BRACKET VISUAL
// ─────────────────────────────────────────

async function cargarPlayoffs() {
    const contenedor = document.getElementById("contenedor-playoffs");
    contenedor.innerHTML = "<p style='color: var(--color-texto-suave)'>Cargando bracket...</p>";

    // Intentar generar bracket
    const respuesta = await fetch(`${API}/playoffs/generar`, { method: "POST" });
    const datos = await respuesta.json();

    // Si la fase de grupos no está completa mostrar mensaje
    if (respuesta.status === 400 && datos.error === "fase_incompleta") {
        contenedor.innerHTML = `
            <div style="text-align: center; padding: 3rem;">
                <p style="font-size: 2rem">⏳</p>
                <p style="font-size: 1.2rem; margin-top: 1rem">${datos.mensaje}</p>
                <p style="color: var(--color-texto-suave); margin-top: 0.5rem">
                    Completá todos los partidos de la fase de grupos para desbloquear los playoffs.
                </p>
            </div>
        `;
        return;
    }

    const partidos = await fetchJSON(`${API}/playoffs`);

    if (!partidos || partidos.length === 0) {
        contenedor.innerHTML = `<p style="color: var(--color-texto-suave)">Sin datos.</p>`;
        return;
    }

    const octavos = partidos.filter(p => p.ronda === "Octavos de final");
    const cuartos = partidos.filter(p => p.ronda === "Cuartos de final");
    const semis   = partidos.filter(p => p.ronda === "Semifinales");
    const final   = partidos.filter(p => p.ronda === "Final");

    contenedor.innerHTML = `
        <div class="bracket">
            <div class="bracket-ronda">
                <h3>Octavos de final</h3>
                ${octavos.map(p => renderPartidoPlayoff(p)).join("")}
            </div>
            <div class="bracket-ronda">
                <h3>Cuartos de final</h3>
                ${cuartos.map(p => renderPartidoPlayoff(p)).join("")}
            </div>
            <div class="bracket-ronda">
                <h3>Semifinales</h3>
                ${semis.map(p => renderPartidoPlayoff(p)).join("")}
            </div>
            <div class="bracket-ronda">
                <h3>Final</h3>
                ${final.map(p => renderPartidoPlayoff(p)).join("")}
            </div>
        </div>
    `;
}

function renderPartidoPlayoff(partido) {
    const jugado  = partido.goles_a !== null;
    const equipoA = partido.equipo_a || "Por definir";
    const equipoB = partido.equipo_b || "Por definir";

    return `
        <div class="playoff-card ${jugado ? "jugado" : ""}">
            <div class="playoff-equipo ${partido.ganador === partido.equipo_a ? "ganador" : ""}">
                ${equipoA}
                <span class="playoff-goles">${jugado ? partido.goles_a : "-"}</span>
            </div>
            <div class="playoff-equipo ${partido.ganador === partido.equipo_b ? "ganador" : ""}">
                ${equipoB}
                <span class="playoff-goles">${jugado ? partido.goles_b : "-"}</span>
            </div>
            ${!jugado && partido.equipo_a && partido.equipo_b ? `
                <button class="btn-playoff" onclick="cargarResultadoPlayoff('${partido.id}', '${partido.equipo_a}', '${partido.equipo_b}')">
                    Cargar resultado
                </button>
            ` : ""}
            ${jugado ? `<div class="playoff-definido">${partido.definido_en}</div>` : ""}
        </div>
    `;
}

function cargarResultadoPlayoff(idPartido, equipoA, equipoB) {
    const modalExistente = document.getElementById("modal-playoff");
    if (modalExistente) modalExistente.remove();

    const modal = document.createElement("div");
    modal.id = "modal-playoff";
    modal.innerHTML = `
        <div class="modal-overlay" onclick="cerrarModalPlayoff()"></div>
        <div class="modal-contenido">
            <h3>⚽ Resultado del partido</h3>
            <p class="modal-marcador">${equipoA} vs ${equipoB}</p>

            <div class="fila-gol">
                <span>${equipoA}</span>
                <input class="input-goles" type="number" min="0" id="playoff-goles-a" placeholder="0">
            </div>
            <div class="fila-gol">
                <span>${equipoB}</span>
                <input class="input-goles" type="number" min="0" id="playoff-goles-b" placeholder="0">
            </div>

            <div class="fila-gol" style="margin-top: 1rem">
                <span>Definido en:</span>
                <select id="playoff-definido" style="background: var(--color-primario); color: var(--color-texto); border: 1px solid var(--color-borde); padding: 0.3rem; border-radius: 4px;">
                    <option value="regular">Tiempo regular</option>
                    <option value="extratime">Tiempo extra</option>
                    <option value="penales">Penales</option>
                </select>
            </div>

            <div id="playoff-ganador-container" style="display:none; margin-top: 1rem">
                <p style="color: var(--color-texto-suave); margin-bottom: 0.5rem">¿Quién ganó en penales?</p>
                <div style="display: flex; gap: 1rem">
                    <button class="btn-guardar" onclick="setGanadorPenales('${equipoA}', '${idPartido}', '${equipoA}', '${equipoB}')">${equipoA}</button>
                    <button class="btn-guardar" onclick="setGanadorPenales('${equipoB}', '${idPartido}', '${equipoA}', '${equipoB}')">${equipoB}</button>
                </div>
            </div>

            <div class="modal-botones">
                <button class="btn-guardar" onclick="confirmarResultadoPlayoff('${idPartido}', '${equipoA}', '${equipoB}')">✅ Confirmar</button>
                <button class="btn-cancelar" onclick="cerrarModalPlayoff()">Cancelar</button>
            </div>
        </div>
    `;

    // Mostrar selector de ganador si se elige penales
    modal.querySelector("#playoff-definido").addEventListener("change", function() {
        const ganadorContainer = document.getElementById("playoff-ganador-container");
        ganadorContainer.style.display = this.value === "penales" ? "block" : "none";
    });

    document.body.appendChild(modal);
}

let ganadorPenales = null;

function setGanadorPenales(equipo, idPartido, equipoA, equipoB) {
    ganadorPenales = equipo;
    document.querySelectorAll("#modal-playoff .btn-guardar").forEach(b => b.style.opacity = "0.6");
    event.target.style.opacity = "1";
    event.target.style.outline = "2px solid white";
}

async function confirmarResultadoPlayoff(idPartido, equipoA, equipoB) {
    const golesA     = parseInt(document.getElementById("playoff-goles-a").value);
    const golesB     = parseInt(document.getElementById("playoff-goles-b").value);
    const definidoEn = document.getElementById("playoff-definido").value;

    if (isNaN(golesA) || isNaN(golesB)) {
        alert("Ingresá los goles de ambos equipos.");
        return;
    }

    let ganador = ganadorPenales;
    if (definidoEn !== "penales") {
        ganador = golesA > golesB ? equipoA : equipoB;
    }

    if (!ganador) {
        alert("Seleccioná el ganador en penales.");
        return;
    }

    await fetchPost(`${API}/playoffs/${idPartido}/resultado`, {
        goles_a:     golesA,
        goles_b:     golesB,
        definido_en: definidoEn,
        ganador:     ganador
    });

    ganadorPenales = null;
    cerrarModalPlayoff();
    await cargarPlayoffs();
}

function cerrarModalPlayoff() {
    const modal = document.getElementById("modal-playoff");
    if (modal) modal.remove();
    ganadorPenales = null;
}

window.cargarResultadoPlayoff  = cargarResultadoPlayoff;
window.confirmarResultadoPlayoff = confirmarResultadoPlayoff;
window.cerrarModalPlayoff      = cerrarModalPlayoff;
window.setGanadorPenales       = setGanadorPenales;

// ─────────────────────────────────────────
// ESTADÍSTICAS
// ─────────────────────────────────────────

async function cargarEstadisticas() {
    const goleadores  = await fetchJSON(`${API}/goleadores`);
    const asistidores = await fetchJSON(`${API}/asistidores`);

    document.getElementById("contenedor-goleadores").innerHTML = renderRanking(goleadores, "goles");
    document.getElementById("contenedor-asistidores").innerHTML = renderRanking(asistidores, "asistencias");
}

function renderRanking(jugadores, campo) {
    if (jugadores.length === 0) {
        return `<p style="color: var(--color-texto-suave)">Sin datos aún.</p>`;
    }

    return `
        <table class="ranking-tabla">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Jugador</th>
                    <th>Equipo</th>
                    <th>${campo === "goles" ? "Goles" : "Asistencias"}</th>
                </tr>
            </thead>
            <tbody>
                ${jugadores.map((j, i) => `
                    <tr>
                        <td>${i + 1}</td>
                        <td>${j.jugador}</td>
                        <td>${j.equipo}</td>
                        <td><strong>${j[campo]}</strong></td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
    `;
}

// ─────────────────────────────────────────
// UTILIDADES — fetch
// ─────────────────────────────────────────

async function fetchJSON(url) {
    const response = await fetch(url);
    return response.json();
}

async function fetchPost(url, datos) {
    return fetch(url, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify(datos)
    });
}
// ─────────────────────────────────────────
// MODAL — GOLEADORES Y ASISTIDORES
// ─────────────────────────────────────────

function mostrarModalJugadores(idPartido, local, visitante, golesLocal, golesVisitante) {
    // Eliminar modal anterior si existe
    const modalExistente = document.getElementById("modal-jugadores");
    if (modalExistente) modalExistente.remove();

    // Construir filas de goles del equipo local
    let filasLocal = "";
    for (let i = 1; i <= golesLocal; i++) {
        filasLocal += `
            <div class="fila-gol">
                <span>⚽ Gol ${i} (${local})</span>
                <input class="input-jugador" type="text" 
                    id="gol-local-${idPartido}-${i}" placeholder="Nombre del goleador">
                <input class="input-jugador" type="text" 
                    id="asist-local-${idPartido}-${i}" placeholder="Nombre del asistidor (opcional)">
            </div>
        `;
    }

    // Construir filas de goles del equipo visitante
    let filasVisitante = "";
    for (let i = 1; i <= golesVisitante; i++) {
        filasVisitante += `
            <div class="fila-gol">
                <span>⚽ Gol ${i} (${visitante})</span>
                <input class="input-jugador" type="text" 
                    id="gol-visit-${idPartido}-${i}" placeholder="Nombre del goleador">
                <input class="input-jugador" type="text" 
                    id="asist-visit-${idPartido}-${i}" placeholder="Nombre del asistidor (opcional)">
            </div>
        `;
    }

    // Crear el modal
    const modal = document.createElement("div");
    modal.id = "modal-jugadores";
    modal.innerHTML = `
        <div class="modal-overlay" onclick="cerrarModal()"></div>
        <div class="modal-contenido">
            <h3>📋 Detalles del partido</h3>
            <p class="modal-marcador">${local} ${golesLocal} - ${golesVisitante} ${visitante}</p>

            ${golesLocal > 0 ? `
                <h4>Goles de ${local}</h4>
                ${filasLocal}
            ` : ""}

            ${golesVisitante > 0 ? `
                <h4>Goles de ${visitante}</h4>
                ${filasVisitante}
            ` : ""}

            <div class="modal-botones">
                <button class="btn-guardar" 
                    onclick="confirmarResultado('${idPartido}', '${local}', '${visitante}', ${golesLocal}, ${golesVisitante})">
                    ✅ Confirmar
                </button>
                <button class="btn-cancelar" onclick="cerrarModal()">Cancelar</button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);
}

async function confirmarResultado(idPartido, local, visitante, golesLocal, golesVisitante) {
    const goleadores  = [];
    const asistidores = [];

    // Recolectar goleadores y asistidores del equipo local
    for (let i = 1; i <= golesLocal; i++) {
        const jugador   = document.getElementById(`gol-local-${idPartido}-${i}`)?.value.trim();
        const asistidor = document.getElementById(`asist-local-${idPartido}-${i}`)?.value.trim();

        if (jugador) goleadores.push({ jugador, equipo: local });
        if (asistidor) asistidores.push({ jugador: asistidor, equipo: local });
    }

    // Recolectar goleadores y asistidores del equipo visitante
    for (let i = 1; i <= golesVisitante; i++) {
        const jugador   = document.getElementById(`gol-visit-${idPartido}-${i}`)?.value.trim();
        const asistidor = document.getElementById(`asist-visit-${idPartido}-${i}`)?.value.trim();

        if (jugador) goleadores.push({ jugador, equipo: visitante });
        if (asistidor) asistidores.push({ jugador: asistidor, equipo: visitante });
    }

    await fetchPost(`${API}/partidos/${idPartido}/resultado`, {
        goles_local:     golesLocal,
        goles_visitante: golesVisitante,
        goleadores,
        asistidores
    });

    cerrarModal();
    await cargarFixture();
    await cargarGrupos();
}

function cerrarModal() {
    const modal = document.getElementById("modal-jugadores");
    if (modal) modal.remove();
}

// Exponer cerrarModal al HTML
window.cerrarModal         = cerrarModal;
window.confirmarResultado  = confirmarResultado;

// ─────────────────────────────────────────
// INICIO — cargar grupos al abrir la app
// ─────────────────────────────────────────

cargarGrupos();

// Exponer funciones al HTML
window.mostrarSeccion  = mostrarSeccion;
window.filtrarPartidos = filtrarPartidos;
window.guardarResultado = guardarResultado;
window.editarResultado  = editarResultado;
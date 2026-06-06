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
// PLAYOFFS
// ─────────────────────────────────────────

async function cargarPlayoffs() {
    const clasificados = await fetchJSON(`${API}/clasificados`);
    const contenedor = document.getElementById("contenedor-playoffs");

    contenedor.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 2rem;">
            <div>
                <h3 style="color: var(--color-acento); margin-bottom: 1rem">1° de cada grupo</h3>
                ${clasificados.primeros.map(e => `
                    <div style="padding: 0.5rem; border-bottom: 1px solid var(--color-borde)">
                        ${e.id} — Grupo ${e.grupo} (${e.PTS} pts)
                    </div>
                `).join("")}
            </div>
            <div>
                <h3 style="color: var(--color-acento); margin-bottom: 1rem">2° de cada grupo</h3>
                ${clasificados.segundos.map(e => `
                    <div style="padding: 0.5rem; border-bottom: 1px solid var(--color-borde)">
                        ${e.id} — Grupo ${e.grupo} (${e.PTS} pts)
                    </div>
                `).join("")}
            </div>
            <div>
                <h3 style="color: var(--color-acento); margin-bottom: 1rem">Mejores terceros</h3>
                ${clasificados.mejores_terceros.map(e => `
                    <div style="padding: 0.5rem; border-bottom: 1px solid var(--color-borde)">
                        ${e.id} — Grupo ${e.grupo} (${e.PTS} pts)
                    </div>
                `).join("")}
            </div>
        </div>
    `;
}

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
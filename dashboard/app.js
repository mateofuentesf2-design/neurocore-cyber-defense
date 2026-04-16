// ==============================
// 🔐 AUTH (JWT)
// ==============================

const token = localStorage.getItem("token");

if (!token) {
    alert("Not authenticated");
    window.location.href = "login.html";
}

// ==============================
// 📡 CONFIG
// ==============================

const API_URL = "http://127.0.0.1:8000/events";
const WS_URL = "ws://127.0.0.1:8000/ws";

const tbody = document.querySelector("#eventsTable tbody");

// ==============================
// 📊 ANALYTICS STATE
// ==============================

let eventsPerMinute = {};
let ipCounts = {};
let attackTypes = {};

let chart;

// ==============================
// 🧱 RENDER EVENT
// ==============================

function renderEvent(event, isLive = false) {
    const row = document.createElement("tr");

    const isAlert = event.raw.toLowerCase().includes("error");

    row.innerHTML = `
        <td>${isLive ? "LIVE" : event.id}</td>
        <td>${event.source}</td>
        <td class="${isAlert ? "alert" : ""}">
            ${event.raw}
        </td>
        <td>${isLive ? new Date().toLocaleTimeString() : event.created_at}</td>
    `;

    if (isLive) {
        tbody.prepend(row);
    } else {
        tbody.appendChild(row);
    }

    // 🔥 IMPORTANTE: analizar cada evento
    analyzeEvent(event);
}

// ==============================
// 📥 LOAD INITIAL DATA
// ==============================

async function loadEvents() {
    try {
        console.log("📥 Loading events...");

        const res = await fetch(API_URL, {
            headers: {
                "Authorization": "Bearer " + token
            }
        });

        if (!res.ok) throw new Error("Auth error");

        const data = await res.json();

        tbody.innerHTML = "";

        data.forEach(event => renderEvent(event));

        console.log("✅ Events loaded");

    } catch (err) {
        console.error("❌ Load error:", err);

        alert("Session expired");
        localStorage.removeItem("token");
        window.location.href = "login.html";
    }
}

// ==============================
// ⚡ WEBSOCKET REALTIME
// ==============================

let socket;

function connectWebSocket() {
    console.log("🔌 Connecting WebSocket...");

    socket = new WebSocket(WS_URL);

    socket.onopen = () => {
        console.log("✅ WebSocket connected");
    };

    socket.onmessage = (msg) => {
        try {
            const event = JSON.parse(msg.data);

            console.log("📡 LIVE EVENT:", event);

            renderEvent(event, true);

        } catch (err) {
            console.error("❌ WS parse error:", err);
        }
    };

    socket.onerror = (err) => {
        console.error("❌ WebSocket error:", err);
    };

    socket.onclose = () => {
        console.warn("⚠️ Reconnecting in 3s...");
        setTimeout(connectWebSocket, 3000);
    };
}

// ==============================
// 🧠 ANALYTICS ENGINE
// ==============================

function analyzeEvent(event) {
    const now = new Date();
    const minute = now.getHours() + ":" + now.getMinutes();

    // 📊 Eventos por minuto
    eventsPerMinute[minute] = (eventsPerMinute[minute] || 0) + 1;

    // 🌐 Extraer IP
    const ipMatch = event.raw.match(/\b\d{1,3}(\.\d{1,3}){3}\b/);
    if (ipMatch) {
        const ip = ipMatch[0];
        ipCounts[ip] = (ipCounts[ip] || 0) + 1;
    }

    // 🚨 Clasificación básica
    let type = "normal";

    const raw = event.raw.toLowerCase();

    if (raw.includes("failed")) type = "brute_force";
    else if (raw.includes("error")) type = "error";
    else if (raw.includes("sql")) type = "sql_injection";

    attackTypes[type] = (attackTypes[type] || 0) + 1;

    updateUI();
}

// ==============================
// 📈 CHART
// ==============================

function initChart() {
    const ctx = document.getElementById("eventsChart").getContext("2d");

    chart = new Chart(ctx, {
        type: "line",
        data: {
            labels: [],
            datasets: [{
                label: "Events per Minute",
                data: [],
                tension: 0.3
            }]
        },
        options: {
            responsive: true
        }
    });
}

function updateChart() {
    chart.data.labels = Object.keys(eventsPerMinute);
    chart.data.datasets[0].data = Object.values(eventsPerMinute);
    chart.update();
}

// ==============================
// 📋 LISTAS
// ==============================

function updateLists() {
    const ipList = document.getElementById("topIPs");
    const attackList = document.getElementById("attackTypes");

    ipList.innerHTML = "";
    attackList.innerHTML = "";

    Object.entries(ipCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .forEach(([ip, count]) => {
            const li = document.createElement("li");
            li.textContent = `${ip} (${count})`;
            ipList.appendChild(li);
        });

    Object.entries(attackTypes)
        .forEach(([type, count]) => {
            const li = document.createElement("li");
            li.textContent = `${type} (${count})`;
            attackList.appendChild(li);
        });
}

// ==============================
// 🔄 UPDATE UI
// ==============================

function updateUI() {
    updateChart();
    updateLists();
}

// ==============================
// 🚀 INIT
// ==============================

initChart();
loadEvents();
connectWebSocket();
/* SecNLP Frontend - Portal de Prevención del Ciberacoso */
const STATE = {
  total: 0, blocked: 0, allowed: 0,
  lastResult: null,
};

const LABELS = {
  hate_speech: "Odio", non_hate: "No Odio",
};

const COLORS = {
  hate_speech: "#ff1744", non_hate: "#00e676",
};

document.addEventListener("DOMContentLoaded", () => {
  const textInput = document.getElementById("textInput");
  const analyzeBtn = document.getElementById("analyzeBtn");
  const resultPanel = document.getElementById("resultPanel");
  const fpBtn = document.getElementById("fpBtn");
  const clearBtn = document.getElementById("clearResultBtn");

  // Smooth scroll for nav links
  document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener("click", e => {
      e.preventDefault();
      const target = document.querySelector(a.getAttribute("href"));
      if (target) target.scrollIntoView({ behavior: "smooth" });
    });
  });

  textInput.addEventListener("input", () => {
    document.getElementById("charCount").textContent = `${textInput.value.length} caracteres`;
  });

  analyzeBtn.addEventListener("click", analyze);
  clearBtn?.addEventListener("click", () => resultPanel.classList.add("hidden"));

  textInput.addEventListener("keydown", e => {
    if (e.key === "Enter" && e.ctrlKey) analyze();
  });

  document.querySelectorAll(".chip").forEach(btn => {
    btn.addEventListener("click", () => {
      textInput.value = btn.dataset.text;
      document.getElementById("charCount").textContent = `${textInput.value.length} caracteres`;
      textInput.focus();
    });
  });

  document.querySelectorAll(".analyzer-tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".analyzer-tab").forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      if (tab.dataset.mode === "batch") runBatch();
    });
  });

  fpBtn?.addEventListener("click", () => {
    if (!STATE.lastResult) return;
    const overlay = document.createElement("div");
    overlay.className = "modal-overlay";
    overlay.innerHTML = `
      <div class="modal-box">
        <h3>Reportar Falso Positivo</h3>
        <p>Si crees que este mensaje fue bloqueado incorrectamente o clasificado erróneamente, repórtalo para ayudarnos a mejorar.</p>
        <textarea id="fpComment" placeholder="Comentario opcional..."></textarea>
        <div class="modal-actions">
          <button class="btn-ghost" id="fpCancel">Cancelar</button>
          <button class="btn-primary" id="fpSubmit" style="padding:8px 20px">Enviar</button>
        </div>
      </div>`;
    document.body.appendChild(overlay);

    document.getElementById("fpCancel").onclick = () => overlay.remove();
    document.getElementById("fpSubmit").onclick = async () => {
      try {
        await fetch("/v1/feedback/false-positive", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            original_text: STATE.lastResult.sanitized || "unknown",
            action_taken: STATE.lastResult.action,
            is_false_positive: true,
            comment: document.getElementById("fpComment").value,
          }),
        });
        alert("✅ Reporte enviado. Gracias por contribuir.");
      } catch { alert("Error al enviar"); }
      overlay.remove();
    };
    overlay.addEventListener("click", e => { if (e.target === overlay) overlay.remove(); });
  });

  async function analyze() {
    const text = textInput.value.trim();
    if (!text) return;

    analyzeBtn.classList.add("loading");

    try {
      const res = await fetch("/v1/moderate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text }),
      });
      const data = await res.json();
      STATE.lastResult = data;
      displayResult(data);
      updateStats(data);
    } catch (err) {
      showError(err.message);
    } finally {
      analyzeBtn.classList.remove("loading");
    }
  }

  async function runBatch() {
    const samples = [
      "Eres una gran persona, gracias por tu ayuda",
      "Te voy a matar, ojalá te mueras",
      "Me encanta tu nuevo proyecto",
      "Odio a toda tu raza, deberían desaparecer",
      "Gracias por compartir tus conocimientos",
      "Eres un inútil que no sirve para nada",
      "Que tengas un excelente día",
      "Vete a la mierda y no vuelvas nunca",
      "Aprecio mucho tu trabajo en equipo",
      "Te romperé la cara estúpido",
    ];

    for (const text of samples) {
      textInput.value = text;
      document.getElementById("charCount").textContent = `${text.length} caracteres`;
      await analyze();
      await new Promise(r => setTimeout(r, 300));
    }
  }

  function displayResult(data) {
    resultPanel.classList.remove("hidden");
    const pct = Math.round(data.score * 100);
    const blocked = data.action === "BLOCK";

    const arc = document.getElementById("gaugeArc");
    const off = 314 - (pct / 100) * 314;
    arc.style.strokeDashoffset = off;
    arc.style.stroke = blocked ? "#ff1744" : pct > 30 ? "#ffab00" : "#00e676";
    document.getElementById("gaugeText").textContent = `${pct}%`;
    document.getElementById("gaugeText").style.fill = arc.style.stroke;

    const chip = document.getElementById("resultChip");
    chip.textContent = blocked ? "BLOQUEADO" : "PERMITIDO";
    chip.className = `result-chip ${blocked ? "block" : "allow"}`;

    const action = document.getElementById("resultAction");
    action.textContent = data.action;
    action.className = blocked ? "action-block" : "action-allow";

    document.getElementById("resultScore").textContent = `${data.score.toFixed(4)} (${pct}%)`;
    document.getElementById("resultLatency").textContent = `${data.latency_ms}ms`;
    document.getElementById("resultReason").textContent = data.reason || "—";

    const cats = document.getElementById("resultCategories");
    cats.innerHTML = "";
    if (data.categories) {
      Object.entries(data.categories).forEach(([k, v]) => {
        const t = document.createElement("span");
        const p = Math.round(v * 100);
        t.style.cssText = `font-size:11px;padding:3px 10px;border-radius:6px;font-weight:600;background:${p>50?'rgba(255,23,68,.15)':'rgba(0,230,118,.15)'};color:${p>50?'#ff1744':'#00e676'}`;
        t.textContent = `${LABELS[k]||k}: ${p}%`;
        cats.appendChild(t);
      });
    }

    resultPanel.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function updateStats(data) {
    STATE.total++;
    if (data.action === "BLOCK") STATE.blocked++;
    else STATE.allowed++;

    document.getElementById("statTotal").textContent = STATE.total;
    document.getElementById("statBlocked").textContent = STATE.blocked;
    document.getElementById("statAllowed").textContent = STATE.allowed;

    const rate = STATE.total > 0 ? ((STATE.blocked / STATE.total) * 100).toFixed(1) : "0.0";
    document.getElementById("statRate").textContent = `${rate}%`;
  }

  function showError(msg) {
    resultPanel.classList.remove("hidden");
    document.querySelector(".result-content").innerHTML =
      `<div style="grid-column:1/-1;text-align:center;padding:20px;color:var(--red)"><strong>Error:</strong> ${escHtml(msg)}</div>`;
  }

  function escHtml(s) {
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }
});

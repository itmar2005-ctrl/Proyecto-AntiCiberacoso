const CATEGORY_NAMES = {
    toxic: "Tóxico",
    severe_toxic: "Severamente Tóxico",
    obscene: "Obsceno",
    threat: "Amenaza",
    insult: "Insulto",
    identity_hate: "Discurso de Odio",
};

const CATEGORY_COLORS = {
    toxic: "#ff6b35",
    severe_toxic: "#e71d36",
    obscene: "#ff9f1c",
    threat: "#c70039",
    insult: "#ff5733",
    identity_hate: "#900c3f",
};

const EDUCATION_TIPS = {
    toxic: "El lenguaje tóxico normaliza la agresividad en línea. Intenta expresar tu desacuerdo sin atacar a la persona.",
    severe_toxic: "Este nivel de toxicidad puede tener consecuencias legales y psicológicas graves. Reflexiona antes de publicar.",
    obscene: "El lenguaje obsceno reduce la calidad del diálogo. Puedes comunicar tu punto sin recurrir a vulgaridades.",
    threat: "Las amenazas son delitos en la mayoría de jurisdicciones. Nunca es aceptable amenazar a otra persona, ni en broma.",
    insult: "Los insultos personales hieren y escalan conflictos. Critica ideas, no personas.",
    identity_hate: "El discurso de odio contra grupos protegidos es ilegal en muchos países y causa daño social profundo.",
};

const GENERAL_TIPS = [
    "Piensa antes de publicar: ¿lo dirías en persona?",
    "Si no tienes nada bueno que decir, es mejor no decir nada.",
    "El anonimato no es excusa para el maltrato.",
    "Reporta el ciberacoso: la mayoría de plataformas tienen herramientas para hacerlo.",
    "Apoya a las víctimas: a veces una palabra amable puede cambiar el día de alguien.",
];

document.addEventListener("DOMContentLoaded", () => {
    const textInput = document.getElementById("textInput");
    const charCount = document.getElementById("charCount");
    const wordCount = document.getElementById("wordCount");
    const analyzeBtn = document.getElementById("analyzeBtn");
    const resultsSection = document.getElementById("results");

    textInput.addEventListener("input", updateStats);

    document.querySelectorAll(".example-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            textInput.value = btn.dataset.text;
            updateStats();
            textInput.focus();
        });
    });

    analyzeBtn.addEventListener("click", analyzeText);

    textInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && e.ctrlKey) {
            analyzeText();
        }
    });

    function updateStats() {
        const text = textInput.value;
        charCount.textContent = `${text.length} caracteres`;
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        wordCount.textContent = `${words} palabras`;
    }

    async function analyzeText() {
        const text = textInput.value.trim();
        if (!text) {
            shakeElement(textInput);
            return;
        }

        analyzeBtn.classList.add("loading");
        resultsSection.classList.add("hidden");
        resultsSection.classList.remove("visible");

        try {
            const response = await fetch("/analyze", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text }),
            });

            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }

            const data = await response.json();
            displayResults(data);
        } catch (err) {
            showError(err.message);
        } finally {
            analyzeBtn.classList.remove("loading");
        }
    }

    function displayResults(data) {
        resultsSection.classList.remove("hidden");

        setTimeout(() => {
            resultsSection.classList.add("visible");
        }, 50);

        updateGauge(data.overall_toxicity);
        updateCategories(data.scores);
        updateSpans(data.highlighted_spans);
        updateEducation(data);
        scrollToResults();
    }

    function updateGauge(toxicity) {
        const percentage = Math.round(toxicity * 100);
        const circumference = 314;
        const offset = circumference - (percentage / 100) * circumference;

        const arc = document.getElementById("gaugeArc");
        const text = document.getElementById("gaugeText");
        const label = document.getElementById("toxicityLabel");
        const score = document.getElementById("overallScore");

        arc.style.strokeDashoffset = offset;
        text.textContent = `${percentage}%`;
        score.textContent = `${percentage}%`;

        let color, labelClass, labelText;
        if (toxicity < 0.3) {
            color = "#00e676";
            labelClass = "safe";
            labelText = "SEGURO";
        } else if (toxicity < 0.6) {
            color = "#ffab00";
            labelClass = "caution";
            labelText = "PRECAUCIÓN";
        } else {
            color = "#ff1744";
            labelClass = "danger";
            labelText = `${percentage}% TÓXICO`;
        }

        arc.style.stroke = color;
        text.style.fill = color;
        score.style.color = color;
        label.className = `toxicity-label ${labelClass}`;
        label.textContent = labelText;
    }

    function updateCategories(scores) {
        const list = document.getElementById("categoriesList");
        list.innerHTML = "";

        const sorted = Object.entries(scores).sort((a, b) => b[1] - a[1]);

        sorted.forEach(([key, value]) => {
            const percentage = Math.round(value * 100);
            const color = CATEGORY_COLORS[key] || "#ff6b35";
            const name = CATEGORY_NAMES[key] || key;

            const item = document.createElement("div");
            item.className = "category-item";
            item.innerHTML = `
                <div class="category-header">
                    <span class="category-name">${name}</span>
                    <span class="category-score" style="color: ${color}">${percentage}%</span>
                </div>
                <div class="category-bar">
                    <div class="category-fill" style="background: ${color}; width: ${percentage}%"></div>
                </div>
            `;
            list.appendChild(item);
        });
    }

    function updateSpans(spans) {
        const container = document.getElementById("highlightedSpans");
        container.innerHTML = "";

        if (!spans || spans.length === 0) {
            container.innerHTML =
                '<div style="color: var(--green); font-size: 13px;">No se detectaron palabras problemáticas</div>';
            return;
        }

        spans.forEach((span) => {
            const tag = document.createElement("div");
            tag.className = "span-tag";
            const pct = Math.round(span.score * 100);
            tag.innerHTML = `
                <span class="span-word">${escapeHtml(span.word)}</span>
                <span class="span-score">${pct}%</span>
            `;
            container.appendChild(tag);
        });
    }

    function updateEducation(data) {
        const container = document.getElementById("educationContent");
        container.innerHTML = "";

        if (!data.is_toxic) {
            const safeMsg = document.createElement("div");
            safeMsg.className = "edu-tip";
            safeMsg.style.borderLeftColor = "var(--green)";
            safeMsg.innerHTML = `
                <strong>&#10003; Mensaje seguro</strong>
                <p>Este texto no contiene lenguaje dañino detectable. Sigue así, usando un lenguaje respetuoso y constructivo.</p>
            `;
            container.appendChild(safeMsg);

            const tip =
                GENERAL_TIPS[Math.floor(Math.random() * GENERAL_TIPS.length)];
            const randomTip = document.createElement("div");
            randomTip.className = "edu-tip";
            randomTip.innerHTML = `
                <strong>&#128161; Consejo</strong>
                <p>${tip}</p>
            `;
            container.appendChild(randomTip);
            return;
        }

        const topCats = data.top_categories || [];
        topCats.forEach(([cat]) => {
            const tipText =
                EDUCATION_TIPS[cat] || "Este tipo de lenguaje puede ser dañino. Piensa antes de publicar.";
            const color = CATEGORY_COLORS[cat] || "var(--accent)";
            const name = CATEGORY_NAMES[cat] || cat;

            const tip = document.createElement("div");
            tip.className = "edu-tip";
            tip.style.borderLeftColor = color;
            tip.innerHTML = `
                <strong>${name}</strong>
                <p>${tipText}</p>
            `;
            container.appendChild(tip);
        });

        const helpTip = document.createElement("div");
        helpTip.className = "edu-tip";
        helpTip.style.borderLeftColor = "var(--purple)";
        helpTip.innerHTML = `
            <strong>&#128222; ¿Necesitas ayuda?</strong>
            <p>Si estás experimentando ciberacoso, habla con un adulto de confianza o contacta a una línea de ayuda. 
            En muchos países existen recursos como <strong>Linea de Ayuda contra el Ciberacoso</strong>.</p>
        `;
        container.appendChild(helpTip);
    }

    function showError(message) {
        resultsSection.classList.remove("hidden");
        resultsSection.classList.add("visible");
        resultsSection.innerHTML = `
            <div class="result-card" style="grid-column: 1 / -1; text-align: center; padding: 40px;">
                <div style="font-size: 48px; margin-bottom: 16px;">&#9888;&#65039;</div>
                <h3 style="color: var(--red); margin-bottom: 8px;">Error al analizar</h3>
                <p style="color: var(--text-secondary);">${escapeHtml(message)}</p>
                <button onclick="location.reload()" style="
                    margin-top: 16px; padding: 8px 24px; background: var(--accent);
                    border: none; border-radius: 8px; color: #fff; font-weight: 600;
                    cursor: pointer; font-family: inherit;
                ">Reintentar</button>
            </div>
        `;
    }

    function scrollToResults() {
        resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function shakeElement(el) {
        el.style.borderColor = "var(--red)";
        el.style.animation = "none";
        el.offsetHeight;
        el.style.animation = "shake 0.4s ease";
        setTimeout(() => {
            el.style.borderColor = "";
            el.style.animation = "";
        }, 500);
    }

    function escapeHtml(str) {
        const div = document.createElement("div");
        div.textContent = str;
        return div.innerHTML;
    }
});

const style = document.createElement("style");
style.textContent = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        20% { transform: translateX(-6px); }
        40% { transform: translateX(6px); }
        60% { transform: translateX(-4px); }
        80% { transform: translateX(4px); }
    }
`;
document.head.appendChild(style);

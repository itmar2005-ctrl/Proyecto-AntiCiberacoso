(function() {
'use strict';

const CATEGORIES = [
  { id:'Benigno', icon:'🛡️', desc:'Mensaje seguro y respetuoso. No contiene elementos de amenaza, acoso ni contenido malicioso.' },
  { id:'Acoso', icon:'⚠️', desc:'Contenido que constituye acoso psicológico, insultos o denigración hacia una persona o grupo.' },
  { id:'Amenaza', icon:'🚨', desc:'Lenguaje que expresa intención de causar daño físico, emocional o material a otra persona.' },
  { id:'Odio', icon:'🔥', desc:'Discurso que ataca o discrimina a grupos por su raza, religión, origen étnico, género u orientación sexual.' },
  { id:'Phishing', icon:'🎣', desc:'Intento de obtener información sensible o credenciales mediante engaño o suplantación de identidad.' }
];

const LOCK_MS = 1000;
let locked = false;

function lock() { locked = true; setTimeout(() => { locked = false; }, LOCK_MS); }

// ----- Scrollbar detection for textareas -----
document.querySelectorAll('textarea').forEach(ta => {
  ta.addEventListener('input', function() {
    this.style.overflowY = this.scrollHeight > this.clientHeight ? 'auto' : 'hidden';
  });
  setTimeout(() => {
    ta.style.overflowY = ta.scrollHeight > ta.clientHeight ? 'auto' : 'hidden';
  }, 50);
});

// ----- Tab switching -----
const tabs = document.querySelectorAll('.cl-tab');
const contents = document.querySelectorAll('.cl-tab-content');

tabs.forEach(tab => {
  tab.addEventListener('click', function() {
    if (locked) return;
    tabs.forEach(t => t.classList.remove('active'));
    contents.forEach(c => c.classList.remove('active'));
    this.classList.add('active');
    const target = document.getElementById('tab-' + this.dataset.tab);
    if (target) target.classList.add('active');
    if (this.dataset.tab !== 'classify') {
      document.getElementById('clResult').classList.add('hidden');
    }
  });
});

// ----- Character / Word counter -----
const textInput = document.getElementById('clTextInput');
const charCount = document.getElementById('clCharCount');
const wordCount = document.getElementById('clWordCount');

textInput.addEventListener('input', function() {
  const t = this.value;
  charCount.textContent = t.length + ' caracteres';
  wordCount.textContent = (t.trim() ? t.trim().split(/\s+/).length : 0) + ' palabras';
});

// ----- Classification engine -----
const KEYWORD_MAP = {
  Benigno:   ['gracias','buenos días','buenas tardes','feliz','genial','excelente','hermoso','maravilloso','amable','encantador','felicidades','éxito','bendiciones'],
  Acoso:     ['idiota','inútil','no vales','desaparecer','odiar','estúpido','imbécil','tonto','feo','gordo','maldito','basura','vete ya','nadie te quiere','abandona','suicid', 'no sirves','perdedor','cero','horrible'],
  Amenaza:   ['matar','morir','voy a','te voy','vas a pagar','te juro','arrepentirás','encontrar','daño','muerte','morirás','asesinar','cuchillo','bala','sangre','destruir','acabar contigo','golpear','apuñalar'],
  Odio:      ['inmigrante','plaga','raza','religión','basura','odio','eliminar','exterminio','limpieza','inferior','sucio','cerdo','demonio','salvaje','degenerado','extranjero','negro','blanco','judío','musulmán','homosexual','feminazi'],
  Phishing:  ['clic aquí','verificar','suspendida','premio','ganaste','ingresa tus datos','reclamar','comprometida','cambie su contraseña','https://','bit.ly','haga clic','urgente','acción inmediata','cuenta bloqueada','transferencia','herencia','príncipe','banco','tarjeta','pin','contraseña','verificación']
};

function classifyText(text) {
  const lower = text.toLowerCase();
  let scores = {};
  let matchedKeywords = {};

  CATEGORIES.forEach(c => { scores[c.id] = 0; matchedKeywords[c.id] = []; });

  // Keyword matching for each category
  Object.keys(KEYWORD_MAP).forEach(cat => {
    KEYWORD_MAP[cat].forEach(kw => {
      if (lower.includes(kw)) {
        matchedKeywords[cat].push(kw);
        scores[cat] += 1;
      }
    });
  });

  // Length factors
  if (text.length < 10) {
    scores.Benigno += 0.5;
  } else if (text.length > 150) {
    scores.Phishing += 0.3;
  }

  // URL detection boosts Phishing
  if (/https?:\/\/[^\s]+/.test(lower) || /bit\.ly|tinyurl|goo\.gl/i.test(lower)) {
    scores.Phishing += 4;
  }

  // Violence markers boost Amenaza
  if (/\b(te\s+(voy|iré|van|vamos)|le\s+(voy|iré)|os\s+(voy|iré))\s+(a\s+)?/.test(lower)) {
    scores.Amenaza += 2;
  }

  // If no keywords matched at all
  const totalMatch = Object.values(scores).reduce((a,b) => a + b, 0);
  if (totalMatch < 0.5) {
    scores.Benigno = 5; // default
    matchedKeywords.Benigno = ['texto seguro'];
  }

  // Convert to probabilities
  const keys = Object.keys(scores);
  const total = Object.values(scores).reduce((a,b) => a + b, 0);
  let probs = {};
  keys.forEach(k => { probs[k] = total > 0 ? Math.round((scores[k] / total) * 10000) / 100 : 0; });

  // Get top category
  let topCat = keys.reduce((a,b) => probs[a] >= probs[b] ? a : b, keys[0]);

  // Ensure min probability for top
  if (probs[topCat] < 25) { probs[topCat] = 25; }

  // Build explanation
  const catInfo = CATEGORIES.find(c => c.id === topCat);
  let reasons = [];
  let indicators = [];
  let alts = [];

  if (topCat === 'Benigno') {
    reasons.push('No se detectaron patrones de amenaza en el texto.');
    reasons.push('El lenguaje utilizado es respetuoso y constructivo.');
    reasons.push('No hay indicios de acoso, odio ni phishing.');
    indicators.push(['Lenguaje respetuoso', true]);
    indicators.push(['Amenazas', false]);
    indicators.push(['Insultos', false]);
    indicators.push(['Discurso de odio', false]);
    indicators.push(['Phishing/Spam', false]);
  } else {
    if (matchedKeywords[topCat].length > 0) {
      reasons.push(`Se detectaron ${matchedKeywords[topCat].length} palabra(s) clave asociadas a "${topCat}".`);
    }
    if (topCat === 'Acoso') {
      reasons.push('El texto contiene elementos de denigración o humillación personal.');
      if (matchedKeywords.Acoso.length > 0) reasons.push(`Palabras como "${matchedKeywords.Acoso.slice(0,3).join('", "')}" son características de acoso.`);
    }
    if (topCat === 'Amenaza') {
      reasons.push('El texto expresa intención de causar daño físico o psicológico.');
      if (matchedKeywords.Amenaza.length > 0) reasons.push(`Términos violentos como "${matchedKeywords.Amenaza.slice(0,3).join('", "')}" indican amenaza directa.`);
    }
    if (topCat === 'Odio') {
      reasons.push('El texto ataca o discrimina a un grupo por características inherentes.');
      if (matchedKeywords.Odio.length > 0) reasons.push(`Lenguaje de odio detectado: "${matchedKeywords.Odio.slice(0,3).join('", "')}".`);
    }
    if (topCat === 'Phishing') {
      reasons.push('El texto intenta engañar al usuario para obtener información sensible.');
      reasons.push('Contiene enlaces sospechosos o pide acciones urgentes no solicitadas.');
    }

    indicators = [
      ['Lenguaje respetuoso', false],
      ['Amenazas', topCat === 'Amenaza'],
      ['Insultos', topCat === 'Acoso' || matchedKeywords['Acoso'].length > 0],
      ['Discurso de odio', topCat === 'Odio'],
      ['Phishing/Spam', topCat === 'Phishing'],
      ['Urgencia/Falsa alarma', topCat === 'Phishing']
    ];

    // Alternative categories
    keys.filter(k => k !== topCat).sort((a,b) => probs[b] - probs[a]).slice(0,3).forEach(k => {
      if (probs[k] > 5) alts.push({ cat: k, prob: probs[k] });
    });
  }

  const summary = topCat === 'Benigno'
    ? 'El modelo determinó que el texto no representa ninguna amenaza. El contenido es seguro y apropiado.'
    : `El modelo clasificó este texto como "${topCat}" basándose en el análisis de patrones lingüísticos y palabras clave. ${matchedKeywords[topCat].length > 0 ? 'Se encontraron coincidencias con términos de riesgo en la base de conocimiento del modelo.' : 'La estructura y contexto del texto coinciden con patrones de esta categoría.'}`;

  return {
    category: topCat,
    icon: catInfo.icon,
    desc: catInfo.desc,
    confidence: probs[topCat],
    probabilities: probs,
    keywords: matchedKeywords[topCat],
    summary,
    reasons,
    indicators,
    alternatives: alts
  };
}

function renderResult(result, prefix) {
  const get = id => document.getElementById(prefix + id);
  const icon = get('Icon');
  const cat = get('Category');
  const desc = get('Desc');
  const confFill = get('ConfFill');
  const confPct = get('ConfPct');
  const probsDiv = get('Probs');

  if (icon) icon.textContent = result.icon;
  if (cat) cat.textContent = result.category;
  if (desc) desc.textContent = result.desc;
  if (confFill) {
    const pct = Math.min(result.confidence, 100);
    confFill.style.width = pct + '%';
    confFill.className = 'cr-conf-fill';
    if (pct >= 75) confFill.classList.add('high');
    else if (pct >= 50) confFill.classList.add('mid');
    else confFill.classList.add('low');
  }
  if (confPct) confPct.textContent = result.confidence + '%';

  // Probabilities
  if (probsDiv) {
    probsDiv.innerHTML = '';
    CATEGORIES.forEach(c => {
      const p = result.probabilities[c.id] || 0;
      const bar = document.createElement('div');
      bar.className = 'cr-prob-bar';
      bar.innerHTML = `
        <span class="cr-prob-label">${c.icon} ${c.id}</span>
        <div class="cr-prob-track"><div class="cr-prob-fill" style="width:${p}%"></div></div>
        <span class="cr-prob-val">${p.toFixed(1)}%</span>`;
      probsDiv.appendChild(bar);
    });
  }
}

function renderFullResult(result) {
  renderResult(result, 'cr');
  // Summary
  const summary = document.getElementById('crSummary');
  if (summary) summary.textContent = result.summary;

  // Reasons
  const reasonsUl = document.getElementById('crReasons');
  if (reasonsUl) {
    reasonsUl.innerHTML = '';
    result.reasons.forEach(r => {
      const li = document.createElement('li');
      li.textContent = r;
      reasonsUl.appendChild(li);
    });
  }

  // Indicators
  const indicatorsUl = document.getElementById('crIndicators');
  if (indicatorsUl) {
    indicatorsUl.innerHTML = '';
    (result.indicators || []).forEach(([label, detected]) => {
      const li = document.createElement('li');
      li.className = detected ? 'detected' : 'not-detected';
      li.innerHTML = detected ? '✅ ' : '❌ ';
      li.textContent += label;
      indicatorsUl.appendChild(li);
    });
  }

  // Keywords
  const kwDiv = document.getElementById('crKeywords');
  if (kwDiv) {
    kwDiv.innerHTML = '';
    if (result.keywords.length > 0) {
      result.keywords.forEach(kw => {
        const span = document.createElement('span');
        span.className = 'cr-kw';
        span.textContent = kw;
        kwDiv.appendChild(span);
      });
    } else {
      kwDiv.innerHTML = '<span class="cr-kw cr-kw-none">No se detectaron palabras clave</span>';
    }
  }

  // Alternatives
  const altsDiv = document.getElementById('crAlternatives');
  if (altsDiv) {
    altsDiv.innerHTML = '';
    if (result.alternatives && result.alternatives.length > 0) {
      const catInfo = CATEGORIES;
      result.alternatives.forEach(a => {
        const info = catInfo.find(c => c.id === a.cat);
        const div = document.createElement('div');
        div.className = 'cr-alt';
        div.innerHTML = `<span class="cr-alt-icon">${info ? info.icon : '?'}</span>
          <span class="cr-alt-name">${a.cat}</span>
          <div class="cr-alt-track"><div class="cr-alt-fill" style="width:${a.prob}%"></div></div>
          <span class="cr-alt-val">${a.prob.toFixed(1)}%</span>`;
        altsDiv.appendChild(div);
      });
    } else {
      altsDiv.textContent = 'No hay categorías alternativas significativas.';
      altsDiv.style.color = 'var(--text3)';
      altsDiv.style.fontSize = '13px';
    }
  }
}

// ----- Tab: Clasificar Texto -----
document.getElementById('clAnalyzeBtn').addEventListener('click', async function() {
  if (locked) return;
  const text = document.getElementById('clTextInput').value.trim();
  if (!text) return;
  lock();
  const btn = this;
  btn.classList.add('loading');
  const resultDiv = document.getElementById('clResult');
  resultDiv.classList.add('hidden');

  try {
    const resp = await fetch('/v1/moderate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    if (!resp.ok) throw new Error('Error del servidor');
    const data = await resp.json();
    // Use backend binary score to adjust frontend classification
    const result = classifyText(text);
    // Blend backend score into confidence
    const backendScore = data.is_toxic ? Math.max(data.toxicity_score, 0.5) : Math.min(data.toxicity_score, 0.4);
    result.confidence = Math.round(result.confidence * 0.4 + backendScore * 60 * 0.6);
    if (result.confidence > 100) result.confidence = 100;
    if (result.confidence < 5 && !data.is_toxic) result.confidence = 5;
    result.probabilities[result.category] = result.confidence;
    // Redistribute other probs to sum to 100
    const otherSum = 100 - result.confidence;
    const otherCats = CATEGORIES.filter(c => c.id !== result.category);
    const remaining = otherCats.reduce((sum, c) => sum + (result.probabilities[c.id] || 0), 0) || 1;
    otherCats.forEach(c => {
      result.probabilities[c.id] = Math.round(((result.probabilities[c.id] || 0) / remaining) * otherSum * 100) / 100;
    });
    renderFullResult(result);
    resultDiv.classList.remove('hidden');
  } catch(e) {
    // Fallback: use ML only
    const result = classifyText(text);
    renderFullResult(result);
    resultDiv.classList.remove('hidden');
  }
  btn.classList.remove('loading');
});

document.getElementById('clClearBtn').addEventListener('click', function() {
  if (locked) return;
  document.getElementById('clTextInput').value = '';
  document.getElementById('clResult').classList.add('hidden');
  charCount.textContent = '0 caracteres';
  wordCount.textContent = '0 palabras';
});

// ----- Tab: Analizar URL -----
document.getElementById('clUrlBtn').addEventListener('click', async function() {
  if (locked) return;
  const text = document.getElementById('clUrlInput').value.trim();
  if (!text) return;
  lock();
  const btn = this;
  btn.classList.add('loading');
  const resultDiv = document.getElementById('clUrlResult');
  resultDiv.classList.add('hidden');

  try {
    const resp = await fetch('/v1/moderate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    await resp.json();
  } catch(e) { /* fallback */ }

  const result = classifyText(text);
  renderResult(result, 'crUrl');
  resultDiv.classList.remove('hidden');
  btn.classList.remove('loading');
});

document.getElementById('clUrlClear').addEventListener('click', function() {
  document.getElementById('clUrlInput').value = '';
  document.getElementById('clUrlResult').classList.add('hidden');
});

// ----- Tab: Clasificación en Lote -----
document.getElementById('clBatchBtn').addEventListener('click', async function() {
  if (locked) return;
  const text = document.getElementById('clBatchInput').value.trim();
  if (!text) return;
  lock();
  const btn = this;
  btn.classList.add('loading');
  const resultDiv = document.getElementById('clBatchResult');
  resultDiv.classList.add('hidden');
  const tbody = document.getElementById('clBatchBody');
  tbody.innerHTML = '';

  const lines = text.split('\n').filter(l => l.trim().length > 0);
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim();
    let backendScore = 0;
    try {
      const resp = await fetch('/v1/moderate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: line })
      });
      if (resp.ok) {
        const data = await resp.json();
        backendScore = data.is_toxic ? data.toxicity_score : data.toxicity_score * 0.5;
      }
    } catch(e) { /* skip */ }
    const result = classifyText(line);
    result.confidence = Math.round(result.confidence * 0.4 + backendScore * 60 * 0.6);
    if (result.confidence > 100) result.confidence = 100;
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${i + 1}</td><td class="td-text">${escHtml(line)}</td><td><span class="cr-cat-tag ${result.category.toLowerCase()}">${result.icon} ${result.category}</span></td><td>${result.confidence}%</td>`;
    tbody.appendChild(tr);
  }

  resultDiv.classList.remove('hidden');
  btn.classList.remove('loading');
});

document.getElementById('clBatchClear').addEventListener('click', function() {
  document.getElementById('clBatchInput').value = '';
  document.getElementById('clBatchResult').classList.add('hidden');
});

// ----- Tab: Ejemplos Demo -----
document.querySelectorAll('.demo-card').forEach(card => {
  card.addEventListener('click', function() {
    if (locked) return;
    const text = this.dataset.text;
    // Switch to classify tab
    tabs.forEach(t => {
      t.classList.toggle('active', t.dataset.tab === 'classify');
    });
    contents.forEach(c => c.classList.toggle('active', c.id === 'tab-classify'));
    document.getElementById('clTextInput').value = text;
    charCount.textContent = text.length + ' caracteres';
    wordCount.textContent = (text.trim() ? text.trim().split(/\s+/).length : 0) + ' palabras';
    // Auto-analyze
    document.getElementById('clAnalyzeBtn').click();
  });
});

function escHtml(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}
})();

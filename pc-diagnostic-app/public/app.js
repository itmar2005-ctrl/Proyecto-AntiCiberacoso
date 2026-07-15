const state = {
  history: {
    cpu: [],
    ram: [],
    diskRead: [],
    diskWrite: [],
    netDown: [],
    netUp: []
  }
};

function $(selector) {
  return document.querySelector(selector);
}

function formatNumber(value, unit = '') {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return `N/D${unit}`;
  }
  return `${Number(value).toFixed(1)}${unit}`;
}

function formatRate(bytes) {
  return `${(bytes / 1024 / 1024).toFixed(2)} MB/s`;
}

function setGauge(element, value, color) {
  const safeValue = Math.max(0, Math.min(100, Number(value) || 0));
  element.style.setProperty('--angle', `${safeValue * 3.6}deg`);
  element.style.background = `conic-gradient(${color} 0deg ${safeValue * 3.6}deg, rgba(147, 164, 198, 0.14) ${safeValue * 3.6}deg 360deg)`;
  element.querySelector('span').textContent = `${safeValue.toFixed(0)}%`;
}

function pushMetric(key, value) {
  state.history[key].push(Number(value) || 0);
  if (state.history[key].length > 24) {
    state.history[key].shift();
  }
}

function drawLineChart(canvas, values, color) {
  const ctx = canvas.getContext('2d');
  const { width, height } = canvas;
  ctx.clearRect(0, 0, width, height);

  ctx.strokeStyle = 'rgba(147, 164, 198, 0.15)';
  ctx.beginPath();
  ctx.moveTo(0, height - 1);
  ctx.lineTo(width, height - 1);
  ctx.stroke();

  if (!values.length) {
    return;
  }

  const max = Math.max(...values, 1);
  ctx.strokeStyle = color;
  ctx.lineWidth = 2;
  ctx.beginPath();

  values.forEach((value, index) => {
    const x = (index / Math.max(values.length - 1, 1)) * width;
    const y = height - (value / max) * (height - 12) - 6;
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });

  ctx.stroke();
}

function renderLive(live) {
  $('#generatedAt').textContent = new Date(live.generatedAt).toLocaleString();
  setGauge($('#cpuGauge'), live.cpu.load, '#4cc9f0');
  setGauge($('#ramGauge'), live.ram.usedPercent, '#8b5cf6');

  $('#cpuMeta').textContent = `Temp ${formatNumber(live.cpu.temperature, ' C')}`;
  $('#ramMeta').textContent = `${formatNumber(live.ram.usedGb, ' GB')} / ${formatNumber(live.ram.totalGb, ' GB')}`;
  $('#diskRead').textContent = formatRate(live.disk.readBytesPerSec || 0);
  $('#diskWrite').textContent = formatRate(live.disk.writeBytesPerSec || 0);
  $('#netDown').textContent = formatRate(live.network.receivedBytesPerSec || 0);
  $('#netUp').textContent = formatRate(live.network.sentBytesPerSec || 0);

  pushMetric('cpu', live.cpu.load);
  pushMetric('ram', live.ram.usedPercent);
  pushMetric('diskRead', live.disk.readBytesPerSec || 0);
  pushMetric('diskWrite', live.disk.writeBytesPerSec || 0);
  pushMetric('netDown', live.network.receivedBytesPerSec || 0);
  pushMetric('netUp', live.network.sentBytesPerSec || 0);

  drawLineChart($('#cpuChart'), state.history.cpu, '#4cc9f0');
  drawLineChart($('#ramChart'), state.history.ram, '#8b5cf6');
  drawLineChart($('#diskChart'), state.history.diskWrite, '#22c55e');
  drawLineChart($('#netChart'), state.history.netDown, '#f59e0b');
}

function healthLabel(diagnostics) {
  if (diagnostics.some((item) => item.urgency === 'critico')) return ['Riesgo alto', 'bad'];
  if (diagnostics.some((item) => item.urgency === 'moderado')) return ['Atencion requerida', 'warn'];
  return ['Estable', 'good'];
}

function renderDefinitions(container, pairs) {
  container.innerHTML = pairs.map(([label, value]) => `
    <div>
      <small class="muted">${label}</small>
      <strong>${value}</strong>
    </div>
  `).join('');
}

function renderSnapshot(snapshot) {
  const [label, cls] = healthLabel(snapshot.diagnostics);
  const badge = $('#healthBadge');
  badge.textContent = label;
  badge.className = `pill ${cls}`;

  renderDefinitions($('#performanceSummary'), [
    ['CPU', `${snapshot.performance.cpu.brand}`],
    ['Uso CPU', `${snapshot.performance.cpu.load}%`],
    ['Temp CPU', `${snapshot.performance.cpu.temperature ?? 'N/D'} C`],
    ['RAM total', `${snapshot.performance.ram.totalGb} GB`],
    ['RAM usada', `${snapshot.performance.ram.usedGb} GB (${snapshot.performance.ram.usedPercent}%)`],
    ['GPU', `${snapshot.performance.gpu.name}`]
  ]);

  $('#topProcessesBody').innerHTML = snapshot.performance.ram.topProcesses.map((item) => `
    <tr><td>${item.name}</td><td>${item.pid}</td><td>${item.ramMb}</td><td>${item.cpu}</td></tr>
  `).join('');

  $('#baselinePanel').innerHTML = snapshot.baselineSummary ? `
    <div class="definition-grid">
      <div><small class="muted">Capturado</small><strong>${new Date(snapshot.baselineSummary.baselineAt).toLocaleString()}</strong></div>
      <div><small class="muted">CPU antes -> despues</small><strong>${snapshot.baselineSummary.cpuBefore}% -> ${snapshot.baselineSummary.cpuAfter}% (${snapshot.baselineSummary.cpuDelta} pts)</strong></div>
      <div><small class="muted">RAM antes -> despues</small><strong>${snapshot.baselineSummary.ramBefore}% -> ${snapshot.baselineSummary.ramAfter}% (${snapshot.baselineSummary.ramDelta} pts)</strong></div>
      <div><small class="muted">Lectura</small><strong>Vuelve a capturar tras aplicar comandos para comparar.</strong></div>
    </div>
  ` : 'Aun no has capturado una linea base.';

  $('#drivesGrid').innerHTML = snapshot.storage.drives.map((drive) => `
    <div class="drive-card">
      <small class="muted">${drive.mount} · ${drive.type}</small>
      <strong>${drive.usedPercent}% usado</strong>
      <div>${drive.usedGb} GB / ${drive.sizeGb} GB</div>
      <div class="muted">Disponible: ${drive.availableGb} GB</div>
    </div>
  `).join('');

  $('#fragmentationList').innerHTML = snapshot.storage.fragmentation.map((item) => `
    <div class="stack-item">
      <strong>${item.drive} (${item.type})</strong>
      <div class="muted">Fragmentacion: ${item.fragmentedPercent ?? 'N/D'}%</div>
      <div class="muted">${item.rawSummary}</div>
    </div>
  `).join('') || '<div class="stack-item muted">Sin datos de fragmentacion.</div>';

  $('#largeFilesBody').innerHTML = snapshot.storage.largeFiles.map((file) => `
    <tr><td>${file.path}</td><td>${file.sizeGb}</td></tr>
  `).join('') || '<tr><td colspan="2">No se detectaron archivos grandes en el alcance configurado.</td></tr>';

  renderDefinitions($('#securitySummary'), [
    ['Puertos abiertos', snapshot.security.openPorts.length],
    ['Conexiones activas', snapshot.security.connections.length],
    ['Antivirus', snapshot.security.antivirus.map((item) => item.name).join(', ') || 'No detectado'],
    ['Firewall', snapshot.security.firewall.map((item) => `${item.name}:${item.enabled ? 'On' : 'Off'}`).join(' | ')]
  ]);

  $('#suspiciousList').innerHTML = snapshot.security.suspiciousProcesses.map((item) => `
    <div class="stack-item">
      <strong>${item.name} (PID ${item.pid})</strong>
      <div class="muted">CPU ${item.cpu}% · RAM ${item.memoryMb} MB</div>
      <div class="muted">${item.reason}</div>
      <div class="muted">${item.path || 'Ruta no disponible'}</div>
    </div>
  `).join('') || '<div class="stack-item muted">No se detectaron procesos sospechosos con la heuristica actual.</div>';

  $('#connectionsBody').innerHTML = snapshot.security.connections.map((item) => `
    <tr><td>${item.localAddress}:${item.localPort}</td><td>${item.remoteAddress}:${item.remotePort}</td><td>${item.pid}</td></tr>
  `).join('');

  renderDefinitions($('#systemSummary'), [
    ['Sistema operativo', `${snapshot.system.os.platform} ${snapshot.system.os.release}`],
    ['Arquitectura', snapshot.system.os.arch],
    ['Host', snapshot.system.os.hostname],
    ['Placa base', `${snapshot.system.baseboard.manufacturer} ${snapshot.system.baseboard.model}`],
    ['BIOS', `${snapshot.system.bios.vendor} ${snapshot.system.bios.version}`],
    ['Uptime', snapshot.system.uptime.human]
  ]);

  $('#driversBody').innerHTML = snapshot.system.drivers.map((driver) => `
    <tr><td>${driver.deviceName || 'N/D'}</td><td>${driver.version || 'N/D'}</td><td>${driver.date || 'N/D'}</td><td>${driver.ageYears ?? 'N/D'} anos</td></tr>
  `).join('');

  $('#diagnosticsList').innerHTML = snapshot.diagnostics.map((item) => `
    <article class="diagnostic-card ${item.urgency}">
      <div class="section-header">
        <h3>${item.title}</h3>
        <span class="pill ${item.urgency === 'critico' ? 'bad' : item.urgency === 'moderado' ? 'warn' : 'info'}">${item.urgency}</span>
      </div>
      <p>${item.diagnosis}</p>
      <div><strong>Comando ${item.commandType}:</strong></div>
      <div class="command-box">${item.command}</div>
      <div><strong>Pasos:</strong></div>
      <ol>${item.steps.map((step) => `<li>${step}</li>`).join('')}</ol>
      <div class="muted"><strong>Por que:</strong> ${item.rationale}</div>
    </article>
  `).join('');

  renderHistory(snapshot.history);
}

function renderHistory(history) {
  $('#historyBody').innerHTML = history.map((entry) => `
    <tr><td>${new Date(entry.at).toLocaleString()}</td><td>${entry.category}</td><td>${entry.urgency}</td><td>${entry.note}</td></tr>
  `).join('') || '<tr><td colspan="4">Sin historial registrado.</td></tr>';
}

async function refreshSnapshot() {
  const response = await fetch('/api/snapshot');
  const snapshot = await response.json();
  renderSnapshot(snapshot);
}

async function captureBaseline() {
  await fetch('/api/baseline/capture', { method: 'POST' });
  await refreshSnapshot();
}

async function submitHistory(event) {
  event.preventDefault();
  const form = event.currentTarget;
  const formData = new FormData(form);
  const payload = Object.fromEntries(formData.entries());
  await fetch('/api/history', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  form.reset();
  await refreshSnapshot();
}

function initSocket() {
  const protocol = location.protocol === 'https:' ? 'wss' : 'ws';
  const socket = new WebSocket(`${protocol}://${location.host}`);

  socket.addEventListener('open', () => {
    $('#wsStatus').textContent = 'Tiempo real activo';
    $('#wsStatus').className = 'pill good';
  });

  socket.addEventListener('close', () => {
    $('#wsStatus').textContent = 'Tiempo real desconectado';
    $('#wsStatus').className = 'pill bad';
    setTimeout(initSocket, 2500);
  });

  socket.addEventListener('message', (event) => {
    const message = JSON.parse(event.data);
    if (message.type === 'live') {
      renderLive(message.payload);
    }
  });
}

window.addEventListener('DOMContentLoaded', async () => {
  $('#refreshSnapshotBtn').addEventListener('click', refreshSnapshot);
  $('#captureBaselineBtn').addEventListener('click', captureBaseline);
  $('#printPdfBtn').addEventListener('click', () => window.print());
  $('#historyForm').addEventListener('submit', submitHistory);

  initSocket();
  await refreshSnapshot();
});

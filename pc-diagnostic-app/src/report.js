function esc(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function buildReportHtml(snapshot) {
  const diagnosticsHtml = snapshot.diagnostics.map((item) => `
    <article class="card urgency-${esc(item.urgency)}">
      <h3>${esc(item.title)}</h3>
      <p><strong>Diagnostico:</strong> ${esc(item.diagnosis)}</p>
      <p><strong>Urgencia:</strong> ${esc(item.urgency)}</p>
      <p><strong>Comando (${esc(item.commandType)}):</strong></p>
      <pre>${esc(item.command)}</pre>
      <p><strong>Pasos:</strong></p>
      <ol>${item.steps.map((step) => `<li>${esc(step)}</li>`).join('')}</ol>
      <p><strong>Motivo:</strong> ${esc(item.rationale)}</p>
    </article>
  `).join('');

  const historyHtml = snapshot.history.map((entry) => `
    <tr>
      <td>${esc(entry.at)}</td>
      <td>${esc(entry.category)}</td>
      <td>${esc(entry.urgency)}</td>
      <td>${esc(entry.note)}</td>
      <td><code>${esc(entry.command)}</code></td>
    </tr>
  `).join('');

  return `<!DOCTYPE html>
  <html lang="es">
  <head>
    <meta charset="utf-8" />
    <title>Reporte de diagnostico de PC</title>
    <style>
      body { background: #0b1020; color: #e8ecff; font-family: Arial, sans-serif; margin: 0; padding: 24px; }
      h1, h2, h3 { margin: 0 0 12px; }
      .grid { display: grid; gap: 16px; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); }
      .card { background: #151c33; border: 1px solid #25304f; border-radius: 16px; padding: 16px; }
      .urgency-critico { border-color: #ef4444; }
      .urgency-moderado { border-color: #f59e0b; }
      .urgency-informativo { border-color: #38bdf8; }
      code, pre { background: #0f172a; color: #c8d7ff; border-radius: 12px; padding: 12px; overflow: auto; }
      table { width: 100%; border-collapse: collapse; }
      th, td { border-bottom: 1px solid #25304f; padding: 10px; text-align: left; vertical-align: top; }
      .meta { margin-bottom: 20px; color: #b2bfdc; }
      @media print { body { background: #fff; color: #111; } .card, code, pre { border: 1px solid #ccc; background: #fff; color: #111; } }
    </style>
  </head>
  <body>
    <h1>Reporte de diagnostico integral</h1>
    <p class="meta">Generado: ${esc(snapshot.generatedAt)}</p>
    <section class="grid">
      <div class="card">
        <h2>Sistema</h2>
        <p><strong>SO:</strong> ${esc(snapshot.system.os.platform)} ${esc(snapshot.system.os.release)}</p>
        <p><strong>Arquitectura:</strong> ${esc(snapshot.system.os.arch)}</p>
        <p><strong>Uptime:</strong> ${esc(snapshot.system.uptime.human)}</p>
      </div>
      <div class="card">
        <h2>CPU y RAM</h2>
        <p><strong>CPU:</strong> ${esc(snapshot.performance.cpu.load)}%</p>
        <p><strong>CPU Temp:</strong> ${esc(snapshot.performance.cpu.temperature ?? 'N/D')} C</p>
        <p><strong>RAM:</strong> ${esc(snapshot.performance.ram.usedPercent)}%</p>
      </div>
      <div class="card">
        <h2>Seguridad</h2>
        <p><strong>Procesos sospechosos:</strong> ${esc(snapshot.security.suspiciousProcesses.length)}</p>
        <p><strong>Puertos abiertos:</strong> ${esc(snapshot.security.openPorts.length)}</p>
        <p><strong>Conexiones activas:</strong> ${esc(snapshot.security.connections.length)}</p>
      </div>
    </section>
    <h2>Diagnosticos y comandos</h2>
    ${diagnosticsHtml}
    <h2>Historial</h2>
    <table>
      <thead>
        <tr><th>Fecha</th><th>Categoria</th><th>Urgencia</th><th>Nota</th><th>Comando</th></tr>
      </thead>
      <tbody>${historyHtml}</tbody>
    </table>
  </body>
  </html>`;
}

module.exports = { buildReportHtml };

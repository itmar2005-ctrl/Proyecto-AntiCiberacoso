const express = require('express');
const http = require('http');
const path = require('path');
const { WebSocketServer } = require('ws');
const { collectFullSnapshot, collectLiveMetrics, loadHistory, appendHistory } = require('./src/system');
const { buildReportHtml } = require('./src/report');

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({ server });
const PORT = process.env.PORT || 3030;

let baselineSnapshot = null;
let latestFullSnapshot = null;

app.use(express.json({ limit: '2mb' }));
app.use(express.static(path.join(__dirname, 'public')));

app.get('/api/health', (_req, res) => {
  res.json({ ok: true, app: 'pc-diagnostic-app' });
});

app.get('/api/live', async (_req, res) => {
  const live = await collectLiveMetrics();
  res.json(live);
});

app.get('/api/snapshot', async (_req, res) => {
  latestFullSnapshot = await collectFullSnapshot(baselineSnapshot);
  res.json(latestFullSnapshot);
});

app.post('/api/baseline/capture', async (_req, res) => {
  baselineSnapshot = await collectFullSnapshot(null);
  res.json({ ok: true, capturedAt: baselineSnapshot.generatedAt, baseline: baselineSnapshot.baselineSummary });
});

app.post('/api/history', async (req, res) => {
  const { note, command, category, urgency } = req.body || {};
  const entry = appendHistory({
    note: note || 'Cambio manual registrado por el usuario',
    command: command || 'N/A',
    category: category || 'manual',
    urgency: urgency || 'informativo'
  });
  res.json({ ok: true, entry });
});

app.get('/api/history', (_req, res) => {
  res.json(loadHistory());
});

app.get('/api/export/report.html', async (_req, res) => {
  const snapshot = latestFullSnapshot || await collectFullSnapshot(baselineSnapshot);
  res.setHeader('Content-Type', 'text/html; charset=utf-8');
  res.setHeader('Content-Disposition', 'attachment; filename="pc-diagnostic-report.html"');
  res.send(buildReportHtml(snapshot));
});

wss.on('connection', (socket) => {
  let timer = null;

  const sendUpdate = async () => {
    if (socket.readyState !== 1) {
      return;
    }
    const live = await collectLiveMetrics();
    socket.send(JSON.stringify({ type: 'live', payload: live }));
  };

  sendUpdate();
  timer = setInterval(sendUpdate, 3000);

  socket.on('close', () => {
    if (timer) {
      clearInterval(timer);
    }
  });
});

server.listen(PORT, () => {
  console.log(`PC Diagnostic App disponible en http://localhost:${PORT}`);
});

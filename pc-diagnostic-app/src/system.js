const fs = require('fs');
const path = require('path');
const os = require('os');
const { exec } = require('child_process');
const si = require('systeminformation');
const { analyzeSnapshot, summarizeBaseline, toFixedNumber } = require('./diagnostics');

const historyFile = path.join(__dirname, '..', 'data', 'history.json');

function ensureHistoryFile() {
  if (!fs.existsSync(historyFile)) {
    fs.writeFileSync(historyFile, '[]', 'utf8');
  }
}

function loadHistory() {
  ensureHistoryFile();
  try {
    return JSON.parse(fs.readFileSync(historyFile, 'utf8'));
  } catch (_error) {
    return [];
  }
}

function appendHistory(entry) {
  const history = loadHistory();
  const fullEntry = {
    id: `hist-${Date.now()}`,
    at: new Date().toISOString(),
    ...entry
  };
  history.unshift(fullEntry);
  fs.writeFileSync(historyFile, JSON.stringify(history.slice(0, 100), null, 2), 'utf8');
  return fullEntry;
}

function runPowerShell(command) {
  return new Promise((resolve) => {
    exec(`powershell -NoProfile -ExecutionPolicy Bypass -Command "${command}"`, { timeout: 20000, windowsHide: true }, (error, stdout) => {
      if (error) {
        resolve([]);
        return;
      }
      try {
        const parsed = JSON.parse(stdout.trim() || '[]');
        resolve(Array.isArray(parsed) ? parsed : [parsed]);
      } catch (_parseError) {
        resolve([]);
      }
    });
  });
}

async function collectSecurityData() {
  const [openPorts, connections, firewall, antivirus] = await Promise.all([
    runPowerShell("Get-NetTCPConnection -State Listen | Select-Object LocalAddress,LocalPort,OwningProcess,CreationTime | ConvertTo-Json"),
    runPowerShell("Get-NetTCPConnection -State Established | Select-Object LocalAddress,LocalPort,RemoteAddress,RemotePort,OwningProcess | ConvertTo-Json"),
    runPowerShell("Get-NetFirewallProfile | Select-Object @{Name='name';Expression={$_.Name}},@{Name='enabled';Expression={[bool]$_.Enabled}},DefaultInboundAction,DefaultOutboundAction | ConvertTo-Json"),
    runPowerShell("Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntivirusProduct | Select-Object displayName,productState,pathToSignedProductExe | ConvertTo-Json")
  ]);

  return {
    openPorts: openPorts.map((item) => ({
      localAddress: item.LocalAddress,
      localPort: item.LocalPort,
      pid: item.OwningProcess
    })),
    connections: connections.map((item) => ({
      localAddress: item.LocalAddress,
      localPort: item.LocalPort,
      remoteAddress: item.RemoteAddress,
      remotePort: item.RemotePort,
      pid: item.OwningProcess
    })),
    firewall: firewall.map((item) => ({
      name: item.name,
      enabled: item.enabled,
      inbound: item.DefaultInboundAction,
      outbound: item.DefaultOutboundAction
    })),
    antivirus: antivirus.map((item) => ({
      name: item.displayName,
      productState: item.productState,
      executable: item.pathToSignedProductExe
    }))
  };
}

async function collectDriverData() {
  const drivers = await runPowerShell("Get-CimInstance Win32_PnPSignedDriver | Select-Object DeviceName,DriverVersion,DriverDate | Sort-Object DriverDate | Select-Object -First 15 | ConvertTo-Json");
  const now = Date.now();

  return drivers.map((item) => {
    const dateValue = item.DriverDate ? new Date(item.DriverDate) : null;
    const ageYears = dateValue && !Number.isNaN(dateValue.getTime())
      ? toFixedNumber((now - dateValue.getTime()) / (1000 * 60 * 60 * 24 * 365), 1)
      : null;

    return {
      deviceName: item.DeviceName,
      version: item.DriverVersion,
      date: item.DriverDate,
      ageYears
    };
  });
}

async function collectLargeFiles() {
  const targets = ['Desktop', 'Documents', 'Downloads', 'Videos']
    .map((folder) => path.join(os.homedir(), folder))
    .filter((folder) => fs.existsSync(folder));

  const files = [];

  function walk(currentPath, depth = 0) {
    if (depth > 2) {
      return;
    }
    let entries = [];
    try {
      entries = fs.readdirSync(currentPath, { withFileTypes: true });
    } catch (_error) {
      return;
    }
    for (const entry of entries) {
      const fullPath = path.join(currentPath, entry.name);
      if (entry.isDirectory()) {
        walk(fullPath, depth + 1);
        continue;
      }
      try {
        const stats = fs.statSync(fullPath);
        if (stats.size >= 250 * 1024 * 1024) {
          files.push({
            path: fullPath,
            sizeGb: toFixedNumber(stats.size / 1024 / 1024 / 1024, 2)
          });
        }
      } catch (_error) {
        continue;
      }
    }
  }

  for (const target of targets) {
    walk(target);
  }

  return files.sort((a, b) => b.sizeGb - a.sizeGb).slice(0, 12);
}

async function collectFragmentation(disks) {
  const results = [];

  for (const drive of disks.slice(0, 3)) {
    if (!drive.mount || !/^[A-Z]:$/i.test(drive.mount)) {
      continue;
    }

    const output = await new Promise((resolve) => {
      exec(`defrag ${drive.mount} /A`, { timeout: 20000, windowsHide: true }, (_error, stdout) => {
        resolve(stdout || 'No fue posible obtener el analisis de fragmentacion.');
      });
    });

    const fragmentationMatch = output.match(/(\d+)% fragmented/i);
    results.push({
      drive: drive.mount,
      type: drive.type,
      fragmentedPercent: fragmentationMatch ? Number(fragmentationMatch[1]) : null,
      rawSummary: output.split(/\r?\n/).map((line) => line.trim()).filter(Boolean).slice(0, 8).join(' | ')
    });
  }

  return results;
}

function formatBytes(value) {
  return toFixedNumber(value / 1024 / 1024 / 1024, 2);
}

function humanizeUptime(seconds) {
  const days = Math.floor(seconds / 86400);
  const hours = Math.floor((seconds % 86400) / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  return `${days}d ${hours}h ${minutes}m`;
}

function detectSuspiciousProcesses(processes) {
  const suspiciousNames = [/miner/i, /crypt/i, /hack/i, /inject/i, /payload/i, /\brat\b/i];
  const ignoredNames = new Set(['System Idle Process', 'System']);
  return processes.list
    .filter((process) => {
      if (ignoredNames.has(process.name) || process.pid === 0) {
        return false;
      }
      const reasons = [];
      if (process.cpu > 60) reasons.push('alto consumo de CPU');
      if (process.memRss > 1.5 * 1024 * 1024 * 1024) reasons.push('alto consumo de memoria');
      if (suspiciousNames.some((pattern) => pattern.test(process.name || ''))) reasons.push('nombre anomalo');
      if (process.path && /temp|appdata\\local\\temp/i.test(process.path)) reasons.push('ejecucion desde ruta temporal');
      process.reason = reasons.join(', ');
      return reasons.length > 0;
    })
    .slice(0, 8)
    .map((process) => ({
      pid: process.pid,
      name: process.name,
      cpu: toFixedNumber(process.cpu),
      memoryMb: toFixedNumber(process.memRss / 1024 / 1024),
      path: process.path,
      reason: process.reason
    }));
}

async function collectLiveMetrics() {
  const [load, memory, fsStats, networkStats, cpuTemp, graphics, cpuSpeed] = await Promise.all([
    si.currentLoad(),
    si.mem(),
    si.fsStats(),
    si.networkStats(),
    si.cpuTemperature(),
    si.graphics(),
    si.cpuCurrentSpeed()
  ]);

  const gpu = graphics.controllers?.[0] || {};
  const network = networkStats?.[0] || {};

  return {
    generatedAt: new Date().toISOString(),
    cpu: {
      load: toFixedNumber(load.currentLoad),
      temperature: toFixedNumber(cpuTemp.main),
      speedGHz: toFixedNumber(cpuSpeed.avg)
    },
    ram: {
      totalGb: formatBytes(memory.total),
      usedGb: formatBytes(memory.used),
      freeGb: formatBytes(memory.available),
      usedPercent: toFixedNumber((memory.used / memory.total) * 100)
    },
    disk: {
      readBytesPerSec: fsStats?.rx_sec || 0,
      writeBytesPerSec: fsStats?.wx_sec || 0
    },
    network: {
      receivedBytesPerSec: network.rx_sec || 0,
      sentBytesPerSec: network.tx_sec || 0
    },
    gpu: {
      name: gpu.model || 'No detectada',
      temperature: toFixedNumber(gpu.temperatureGpu),
      memoryUsedMb: toFixedNumber(gpu.memoryUsed),
      memoryTotalMb: toFixedNumber(gpu.memoryTotal),
      utilizationGpu: toFixedNumber(gpu.utilizationGpu)
    }
  };
}

async function collectFullSnapshot(baselineSnapshot) {
  const [cpu, load, memory, processes, graphics, disks, diskLayout, osInfo, system, baseboard, bios, time, live, security, drivers, largeFiles] = await Promise.all([
    si.cpu(),
    si.currentLoad(),
    si.mem(),
    si.processes(),
    si.graphics(),
    si.fsSize(),
    si.diskLayout(),
    si.osInfo(),
    si.system(),
    si.baseboard(),
    si.bios(),
    si.time(),
    collectLiveMetrics(),
    collectSecurityData(),
    collectDriverData(),
    collectLargeFiles()
  ]);

  const gpu = graphics.controllers?.[0] || {};
  const driveMap = new Map(diskLayout.map((disk) => [disk.name, disk]));
  const storageDrives = disks.map((drive) => {
    const matchingLayout = [...driveMap.values()].find((item) => item.name && drive.fs && item.name.includes(drive.fs));
    return {
      mount: drive.mount,
      fs: drive.fs,
      type: matchingLayout?.type || drive.type || 'Desconocido',
      sizeGb: formatBytes(drive.size),
      usedGb: formatBytes(drive.used),
      availableGb: formatBytes(drive.available),
      usedPercent: toFixedNumber(drive.use)
    };
  });

  const fragmentation = await collectFragmentation(storageDrives);

  const snapshot = {
    generatedAt: new Date().toISOString(),
    performance: {
      cpu: {
        manufacturer: cpu.manufacturer,
        brand: cpu.brand,
        cores: cpu.cores,
        physicalCores: cpu.physicalCores,
        speedGHz: toFixedNumber(cpu.speed),
        speedMaxGHz: toFixedNumber(cpu.speedMax),
        load: toFixedNumber(load.currentLoad),
        temperature: live.cpu.temperature
      },
      ram: {
        totalGb: formatBytes(memory.total),
        availableGb: formatBytes(memory.available),
        usedGb: formatBytes(memory.used),
        usedPercent: toFixedNumber((memory.used / memory.total) * 100),
        topProcesses: processes.list
          .sort((a, b) => b.memRss - a.memRss)
          .slice(0, 10)
          .map((process) => ({
            name: process.name,
            pid: process.pid,
            ramMb: toFixedNumber(process.memRss / 1024 / 1024),
            cpu: toFixedNumber(process.cpu),
            path: process.path || 'N/D'
          }))
      },
      gpu: {
        name: gpu.model || 'No detectada',
        vendor: gpu.vendor || 'N/D',
        memoryUsedMb: toFixedNumber(gpu.memoryUsed),
        memoryTotalMb: toFixedNumber(gpu.memoryTotal),
        temperature: toFixedNumber(gpu.temperatureGpu),
        utilizationGpu: toFixedNumber(gpu.utilizationGpu)
      },
      live
    },
    storage: {
      drives: storageDrives,
      largeFiles,
      fragmentation
    },
    security: {
      suspiciousProcesses: detectSuspiciousProcesses(processes),
      openPorts: security.openPorts,
      connections: security.connections.slice(0, 20),
      firewall: security.firewall,
      antivirus: security.antivirus
    },
    system: {
      os: {
        platform: osInfo.distro,
        release: osInfo.release,
        build: osInfo.build,
        arch: osInfo.arch,
        hostname: osInfo.hostname
      },
      hardware: {
        manufacturer: system.manufacturer,
        model: system.model,
        serial: system.serial || 'N/D'
      },
      baseboard: {
        manufacturer: baseboard.manufacturer,
        model: baseboard.model,
        serial: baseboard.serial || 'N/D'
      },
      bios: {
        vendor: bios.vendor,
        version: bios.version,
        releaseDate: bios.releaseDate
      },
      uptime: {
        seconds: time.uptime,
        human: humanizeUptime(time.uptime)
      },
      drivers
    },
    history: loadHistory()
  };

  snapshot.diagnostics = analyzeSnapshot(snapshot);
  snapshot.baselineSummary = summarizeBaseline(snapshot, baselineSnapshot);
  return snapshot;
}

module.exports = {
  collectFullSnapshot,
  collectLiveMetrics,
  loadHistory,
  appendHistory
};

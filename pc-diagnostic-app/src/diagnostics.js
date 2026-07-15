function toFixedNumber(value, decimals = 1) {
  const number = Number(value);
  if (!Number.isFinite(number)) {
    return null;
  }
  return Number(number.toFixed(decimals));
}

function createRecommendation({ id, title, diagnosis, urgency, commandType, command, steps, rationale }) {
  return { id, title, diagnosis, urgency, commandType, command, steps, rationale };
}

function buildStorageCommands(letter) {
  return [
    createRecommendation({
      id: `cleanup-${letter}`,
      title: `Liberar espacio en ${letter}`,
      diagnosis: `La unidad ${letter} presenta poco espacio libre.`,
      urgency: 'moderado',
      commandType: 'PowerShell',
      command: `Start-Process cleanmgr.exe -ArgumentList '/d ${letter.replace(':', '')}' -Verb RunAs`,
      steps: [
        'Abre PowerShell como administrador.',
        'Ejecuta el comando para abrir Liberador de espacio en la unidad indicada.',
        'Marca temporales, miniaturas y elementos que no necesites.',
        'Aplica la limpieza y vuelve a capturar una linea base.'
      ],
      rationale: 'Reduce archivos temporales y mejora la disponibilidad de espacio.'
    }),
    createRecommendation({
      id: `defrag-${letter}`,
      title: `Analizar fragmentacion en ${letter}`,
      diagnosis: `Conviene validar el nivel de fragmentacion antes de optimizar la unidad.`,
      urgency: 'informativo',
      commandType: 'CMD',
      command: `defrag ${letter} /A /V`,
      steps: [
        'Abre CMD como administrador.',
        'Ejecuta el analisis con el comando indicado.',
        'Si el disco es HDD y el nivel es alto, usa luego defrag con /O.',
        'Si es SSD, Windows aplicara optimizacion TRIM cuando corresponda.'
      ],
      rationale: 'Permite distinguir si el disco necesita optimizacion o solo verificacion.'
    })
  ];
}

function analyzeSnapshot(snapshot) {
  const diagnostics = [];
  const cpuLoad = snapshot.performance.cpu.load ?? 0;
  const cpuTemp = snapshot.performance.cpu.temperature;
  const ramUsage = snapshot.performance.ram.usedPercent ?? 0;
  const disks = snapshot.storage.drives || [];
  const suspiciousProcesses = snapshot.security.suspiciousProcesses || [];
  const openPorts = snapshot.security.openPorts || [];
  const firewallDisabled = (snapshot.security.firewall || []).filter((profile) => profile.enabled === false);
  const oldDrivers = (snapshot.system.drivers || []).filter((driver) => driver.ageYears !== null && driver.ageYears >= 3);

  if (cpuLoad >= 85) {
    diagnostics.push(createRecommendation({
      id: 'cpu-load-high',
      title: 'Uso de CPU elevado',
      diagnosis: `La CPU esta en ${cpuLoad}% de uso, lo cual puede degradar la respuesta general del sistema.`,
      urgency: 'critico',
      commandType: 'PowerShell',
      command: 'Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 Name,Id,CPU,WS',
      steps: [
        'Abre PowerShell.',
        'Ejecuta el comando para identificar los procesos con mayor consumo acumulado.',
        'Verifica si alguno no pertenece a software confiable o si esta fuera de control.',
        'Si confirmas que un proceso es prescindible, cierralo desde el Administrador de tareas o con Stop-Process -Id <PID>.'
      ],
      rationale: 'Localiza el origen del consumo anormal antes de finalizar procesos.'
    }));
  }

  if (cpuTemp !== null && cpuTemp >= 85) {
    diagnostics.push(createRecommendation({
      id: 'cpu-temp-high',
      title: 'Temperatura de CPU alta',
      diagnosis: `La temperatura reportada de la CPU es ${cpuTemp} C y entra en una zona de riesgo termico.`,
      urgency: 'critico',
      commandType: 'PowerShell',
      command: 'powercfg /SETACTIVE SCHEME_BALANCED',
      steps: [
        'Abre PowerShell o CMD como administrador.',
        'Ejecuta el comando para volver temporalmente al plan de energia balanceado.',
        'Reduce cargas intensivas y verifica limpieza fisica, ventiladores y pasta termica.',
        'Vuelve a revisar la temperatura desde el panel en tiempo real.'
      ],
      rationale: 'Bajar la agresividad energetica ayuda a contener la temperatura mientras se corrige la causa fisica.'
    }));
  }

  if (ramUsage >= 90) {
    diagnostics.push(createRecommendation({
      id: 'ram-high',
      title: 'Memoria RAM casi agotada',
      diagnosis: `La RAM esta en ${ramUsage}% de uso y puede provocar paginacion intensa.`,
      urgency: 'critico',
      commandType: 'PowerShell',
      command: 'Get-Process | Sort-Object WorkingSet -Descending | Select-Object -First 10 Name,Id,@{Name="RAM_MB";Expression={[math]::Round($_.WorkingSet / 1MB, 1)}}',
      steps: [
        'Abre PowerShell.',
        'Ejecuta el comando para identificar los procesos que mas memoria consumen.',
        'Cierra aplicaciones pesadas que no necesites o reinicia las que tengan fugas de memoria.',
        'Captura nuevamente una linea base cuando el uso baje.'
      ],
      rationale: 'Reduce la presion de memoria y mejora la estabilidad.'
    }));
  }

  for (const drive of disks) {
    if ((drive.usedPercent ?? 0) >= 90) {
      diagnostics.push(...buildStorageCommands(drive.mount));
    }
  }

  if (suspiciousProcesses.length > 0) {
    const process = suspiciousProcesses[0];
    diagnostics.push(createRecommendation({
      id: 'suspicious-process',
      title: 'Proceso potencialmente sospechoso',
      diagnosis: `Se detecto el proceso ${process.name} con heuristicas de riesgo (${process.reason}).`,
      urgency: 'critico',
      commandType: 'PowerShell',
      command: `Get-Process -Id ${process.pid} | Format-List *; Stop-Process -Id ${process.pid} -WhatIf`,
      steps: [
        'Abre PowerShell como administrador.',
        'Ejecuta el primer comando para inspeccionar el proceso completo.',
        'Ejecuta la parte con -WhatIf para simular su detencion sin cerrarlo.',
        'Si confirmas que es malicioso o innecesario, repite el comando quitando -WhatIf y luego corre un analisis antivirus completo.'
      ],
      rationale: 'Obliga a validar el proceso antes de terminarlo de forma real.'
    }));
  }

  if (openPorts.length >= 12) {
    diagnostics.push(createRecommendation({
      id: 'many-open-ports',
      title: 'Cantidad elevada de puertos en escucha',
      diagnosis: `Se encontraron ${openPorts.length} puertos en escucha. Conviene revisar si todos son necesarios.`,
      urgency: 'moderado',
      commandType: 'PowerShell',
      command: 'Get-NetTCPConnection -State Listen | Sort-Object LocalPort | Select-Object LocalAddress,LocalPort,OwningProcess',
      steps: [
        'Abre PowerShell como administrador.',
        'Ejecuta el comando para listar todos los puertos en escucha.',
        'Relaciona cada PID con su proceso usando Get-Process -Id <PID>.',
        'Deshabilita o desinstala servicios no requeridos.'
      ],
      rationale: 'Reduce la superficie de ataque de servicios expuestos innecesariamente.'
    }));
  }

  if (firewallDisabled.length > 0) {
    diagnostics.push(createRecommendation({
      id: 'firewall-disabled',
      title: 'Firewall deshabilitado',
      diagnosis: `Uno o mas perfiles del firewall estan deshabilitados: ${firewallDisabled.map((item) => item.name).join(', ')}.`,
      urgency: 'critico',
      commandType: 'PowerShell',
      command: 'Set-NetFirewallProfile -Profile Domain,Public,Private -Enabled True',
      steps: [
        'Abre PowerShell como administrador.',
        'Ejecuta el comando para habilitar todos los perfiles del firewall.',
        'Verifica el estado con Get-NetFirewallProfile.',
        'Revisa luego si alguna aplicacion necesita una regla especifica en lugar de desactivar el firewall.'
      ],
      rationale: 'Restablece una capa base de proteccion de red en Windows.'
    }));
  }

  if (oldDrivers.length > 0) {
    diagnostics.push(createRecommendation({
      id: 'old-drivers',
      title: 'Drivers posiblemente desactualizados',
      diagnosis: `Se detectaron ${oldDrivers.length} controladores con varios anos de antiguedad.`,
      urgency: 'moderado',
      commandType: 'PowerShell',
      command: 'pnputil /enum-drivers',
      steps: [
        'Abre PowerShell o CMD como administrador.',
        'Ejecuta el comando para enumerar los controladores instalados.',
        'Cruza los dispositivos criticos con Windows Update o con el fabricante.',
        'Actualiza primero chipset, GPU, red y almacenamiento.'
      ],
      rationale: 'No confirma obsolescencia, pero prioriza componentes de mayor impacto.'
    }));
  }

  if (diagnostics.length === 0) {
    diagnostics.push(createRecommendation({
      id: 'healthy',
      title: 'Sin alertas criticas inmediatas',
      diagnosis: 'No se detectaron problemas graves con los umbrales actuales. Aun asi conviene revisar almacenamiento, drivers y seguridad de forma periodica.',
      urgency: 'informativo',
      commandType: 'PowerShell',
      command: 'Get-ComputerInfo | Select-Object WindowsProductName,WindowsVersion,OsHardwareAbstractionLayer',
      steps: [
        'Abre PowerShell.',
        'Ejecuta el comando para registrar la configuracion actual del sistema.',
        'Guarda un reporte HTML desde la aplicacion como referencia de estado saludable.'
      ],
      rationale: 'Sirve como evidencia y punto de comparacion futuro.'
    }));
  }

  return diagnostics;
}

function summarizeBaseline(snapshot, baselineSnapshot) {
  if (!baselineSnapshot) {
    return null;
  }

  const currentCpu = snapshot.performance.cpu.load ?? 0;
  const previousCpu = baselineSnapshot.performance.cpu.load ?? 0;
  const currentRam = snapshot.performance.ram.usedPercent ?? 0;
  const previousRam = baselineSnapshot.performance.ram.usedPercent ?? 0;

  return {
    baselineAt: baselineSnapshot.generatedAt,
    cpuDelta: toFixedNumber(currentCpu - previousCpu),
    ramDelta: toFixedNumber(currentRam - previousRam),
    cpuBefore: toFixedNumber(previousCpu),
    cpuAfter: toFixedNumber(currentCpu),
    ramBefore: toFixedNumber(previousRam),
    ramAfter: toFixedNumber(currentRam)
  };
}

module.exports = {
  analyzeSnapshot,
  summarizeBaseline,
  toFixedNumber
};

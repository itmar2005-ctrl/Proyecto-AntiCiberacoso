# PC Diagnostic App

Aplicacion web local para diagnostico integral de un PC con dashboard en tiempo real, analisis de almacenamiento, seguridad, informacion general del sistema, recomendaciones y comandos de remediacion.

## Tecnologia usada

- Frontend: HTML, CSS y JavaScript vanilla
- Backend: Node.js con `Express`
- Tiempo real: `WebSocket` con `ws`
- Recoleccion de metricas: `systeminformation`
- Integracion con Windows: comandos PowerShell y `defrag` ejecutados desde el backend

## Como interactua con el sistema operativo

La aplicacion es local. El backend ejecuta dos tipos de lectura:

1. Metricas de hardware y sistema mediante `systeminformation`.
2. Consultas especificas de Windows mediante PowerShell, por ejemplo:
   - `Get-NetTCPConnection`
   - `Get-NetFirewallProfile`
   - `Get-CimInstance root/SecurityCenter2:AntivirusProduct`
   - `Get-CimInstance Win32_PnPSignedDriver`
   - `defrag <unidad> /A`

No modifica la configuracion del sistema por si sola. Solo muestra diagnosticos y los comandos exactos para que el usuario decida ejecutarlos manualmente.

## Instalacion

1. Abre una terminal en `pc-diagnostic-app`.
2. Instala dependencias:

```powershell
npm install
```

3. Inicia la aplicacion:

```powershell
npm start
```

4. Abre `http://localhost:3030` en tu navegador.

## Permisos requeridos

- Ejecucion normal:
  - Permite ver dashboard, CPU, RAM, GPU, discos, procesos, historial y parte de red.
- Administrador recomendado:
  - Para obtener mejor visibilidad de firewall, conexiones, puertos, antivirus y fragmentacion.
  - Para ejecutar los comandos correctivos sugeridos desde PowerShell o CMD.

## Exportacion de informes

- HTML: boton `Exportar HTML`
- PDF: boton `Exportar PDF`, que usa la impresion del navegador para guardar como PDF

## Alcance y notas

- La deteccion de malware es heuristica y no reemplaza un EDR o antivirus profesional.
- El analisis de drivers marca controladores potencialmente antiguos por fecha; no valida automaticamente la ultima version del fabricante.
- La busqueda de archivos grandes se limita a carpetas del perfil del usuario y a poca profundidad para evitar escaneos demasiado pesados.
- La temperatura de CPU y GPU depende de sensores y drivers disponibles.

## Estructura

```text
pc-diagnostic-app/
  data/history.json
  public/
    app.js
    index.html
    styles.css
  src/
    diagnostics.js
    report.js
    system.js
  package.json
  server.js
```

// =============================================
// SCRIPT 2: PROTECCIÓN CONTRA CLICKJACKING
// Educativo - Previene que tu sitio sea embebido en iframes maliciosos
// =============================================

class ClickjackProtector {
    constructor() {
        this.protectionEnabled = true;
        this.allowedDomains = [];
        this.detectionLog = [];
    }

    // Protección principal: configurar headers CSP y X-Frame-Options
    enableFrameProtection() {
        // Para páginas served via HTTP headers (configurar en servidor)
        // X-Frame-Options: DENY (niega cualquier embebido)
        // X-Frame-Options: SAMEORIGIN (solo permite mismo dominio)
        
        // Protección JavaScript (capa adicional)
        if (self !== top) {
            const currentDomain = window.location.hostname;
            const parentDomain = document.referrer ? 
                new URL(document.referrer).hostname : 'desconocido';
            
            // Verificar si el frame padre está permitido
            if (!this.isAllowedDomain(parentDomain)) {
                this.logThreat('FRAME_BUST', {
                    parent: parentDomain,
                    child: currentDomain,
                    reason: 'Dominio no permitido intenta embeber la página'
                });
                
                // Opción 1: Romper el frame (más agresivo)
                // top.location.href = self.location.href;
                
                // Opción 2: Mostrar advertencia y permitir continuar
                this.showFrameWarning(parentDomain);
            }
        }
        
        // Detectar cambios de visibility
        this.monitorVisibility();
        
        // Proteger contra drag-and-drop de contenido
        this.protectDragDrop();
        
        console.log('🛡️ Clickjack Protector activo');
    }

    // Agregar dominio permitido para framing legítimo
    allowDomain(domain) {
        if (!this.allowedDomains.includes(domain)) {
            this.allowedDomains.push(domain);
            console.log(`✅ Dominio permitido: ${domain}`);
        }
    }

    isAllowedDomain(domain) {
        if (this.allowedDomains.length === 0) return false;
        return this.allowedDomains.some(
            allowed => domain === allowed || domain.endsWith('.' + allowed)
        );
    }

    showFrameWarning(parentDomain) {
        // Crear overlay de advertencia
        const overlay = document.createElement('div');
        overlay.id = 'clickjack-warning';
        overlay.style.cssText = `
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0,0,0,0.95);
            color: white;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 999999;
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 20px;
        `;
        
        overlay.innerHTML = `
            <div style="font-size: 64px; margin-bottom: 20px;">⚠️</div>
            <h1 style="color: #ff6b6b; margin-bottom: 20px;">
                ⚠️ INTENTO DE CLICKJACKING BLOQUEADO
            </h1>
            <p style="font-size: 18px; max-width: 500px; line-height: 1.6;">
                Esta página está siendo embebida en un sitio externo 
                (<strong>${this.escapeHtml(parentDomain)}</strong>).
            </p>
            <p style="font-size: 14px; color: #888; margin-top: 20px;">
                Si confías en este sitio, haz clic abajo para continuar.
            </p>
            <div style="margin-top: 30px;">
                <button id="allow-iframe" style="
                    padding: 15px 30px;
                    font-size: 16px;
                    background: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    margin: 5px;
                ">Permitir (no recomendado)</button>
                <button id="exit-iframe" style="
                    padding: 15px 30px;
                    font-size: 16px;
                    background: #f44336;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    margin: 5px;
                ">Salir del frame</button>
            </div>
            <p style="font-size: 12px; color: #666; margin-top: 30px;">
                Este es un mecanismo de protección contra ataques de clickjacking.
                <br>Los atacantes pueden usar iframes para engañarte y hacer que hagas clic en botones ocultos.
            </p>
        `;
        
        document.body.appendChild(overlay);
        
        // Acciones de los botones
        document.getElementById('allow-iframe').onclick = () => {
            overlay.remove();
            this.logThreat('ALLOWED', { parent: parentDomain });
        };
        
        document.getElementById('exit-iframe').onclick = () => {
            top.location.href = self.location.href;
        };
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    monitorVisibility() {
        // Detectar si la página está oculta (posible ataque)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.logThreat('VISIBILITY_HIDDEN', {
                    timestamp: new Date().toISOString()
                });
            }
        });
        
        // Detectar blur (pérdida de foco)
        window.addEventListener('blur', () => {
            // Solo alertar si estamos en un frame
            if (self !== top) {
                this.logThreat('WINDOW_BLUR_IN_FRAME', {});
            }
        });
    }

    protectDragDrop() {
        ['dragenter', 'dragover', 'drop'].forEach(eventName => {
            document.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            }, false);
        });
        
        // Prevenir que elementos sean arrastados fuera
        document.addEventListener('dragstart', (e) => {
            // Permitir drag normal pero monitorear
            this.logThreat('DRAG_ATTEMPT', {
                target: e.target.tagName,
                dataType: e.dataTransfer.types
            });
        });
    }

    logThreat(type, details) {
        const entry = {
            type,
            timestamp: new Date().toISOString(),
            url: window.location.href,
            ...details
        };
        
        this.detectionLog.push(entry);
        
        // También log en consola
        console.group('🚨 Clickjack Threat Detected');
        console.log('Type:', type);
        console.log('Details:', details);
        console.log('Full log:', this.detectionLog);
        console.groupEnd();
        
        // Enviar a servidor si existe función
        if (typeof reportSecurityEvent === 'function') {
            reportSecurityEvent(entry);
        }
    }

    // Generar headers de seguridad recomendados
    static getRecommendedHeaders() {
        return {
            'X-Frame-Options': 'DENY',
            'X-Frame-Options': 'SAMEORIGIN',
            'X-Content-Type-Options': 'nosniff',
            'X-XSS-Protection': '1; mode=block',
            'Content-Security-Policy': "frame-ancestors 'none'",
            'Content-Security-Policy': "frame-ancestors 'self'"
        };
    }

    // Middleware para servidor Express (Node.js)
    static expressMiddleware() {
        return (req, res, next) => {
            res.set({
                'X-Frame-Options': 'DENY',
                'X-Content-Type-Options': 'nosniff',
                'X-XSS-Protection': '1; mode=block',
                'Content-Security-Policy': "frame-ancestors 'none'"
            });
            next();
        };
    }
}

// Auto-inicializar
const clickjackProtector = new ClickjackProtector();

// Verificar en diferentes momentos
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        clickjackProtector.enableFrameProtection();
    });
} else {
    clickjackProtector.enableFrameProtection();
}

// Exportar
window.ClickjackProtector = ClickjackProtector;
window.clickjackProtector = clickjackProtector;

console.log('🛡️ Clickjack Protector - Protegiendo contra embebido malicioso');
console.log('📋 Dominios permitidos:', clickjackProtector.allowedDomains);

// =============================================
// SCRIPT 3: PROTECCIÓN CONTRA CSP (Content Security Policy) Y SEGURIDAD DE RED
// Educativo - Implementa políticas de seguridad y protección de comunicaciones
// =============================================

class SecurityHeadersManager {
    constructor() {
        this.policies = {};
        this.violations = [];
        this.networkMonitor = new NetworkMonitor();
    }

    // Definir política CSP completa
    setCSPPolicy() {
        const directives = {
            'default-src': ["'self'"],
            'script-src': ["'self'", "'strict-dynamic'"],
            'style-src': ["'self'", "'unsafe-inline'"],
            'img-src': ["'self'", 'data:', 'https:'],
            'font-src': ["'self'"],
            'connect-src': ["'self'"],
            'frame-ancestors': ["'none'"],
            'form-action': ["'self'"],
            'base-uri': ["'self'"],
            'object-src': ["'none'"],
            'upgrade-insecure-requests': []
        };

        let csp = Object.entries(directives)
            .map(([key, values]) => `${key} ${values.join(' ')}`)
            .join('; ');

        this.policies['Content-Security-Policy'] = csp;
        
        // Aplicar meta tag si no hay headers del servidor
        this.applyCSPMeta(csp);
        
        // Monitorear violaciones
        this.monitorCSPViolations();
        
        return csp;
    }

    // CSP más permisiva para desarrollo
    setCSPDevelopment() {
        const csp = `
            default-src 'self' 'unsafe-inline' 'unsafe-eval';
            script-src 'self' 'unsafe-inline' 'unsafe-eval' blob:;
            style-src 'self' 'unsafe-inline';
            img-src 'self' data: blob: http: https:;
            connect-src 'self' ws: wss: http: https:;
            frame-ancestors 'self' localhost:*
        `.replace(/\s+/g, ' ').trim();

        this.applyCSPMeta(csp);
        return csp;
    }

    applyCSPMeta(csp) {
        // Verificar si ya existe
        let meta = document.querySelector(
            'meta[http-equiv="Content-Security-Policy"]'
        );
        
        if (!meta) {
            meta = document.createElement('meta');
            meta.httpEquiv = 'Content-Security-Policy';
            document.head.appendChild(meta);
        }
        
        meta.content = csp;
        console.log('🛡️ CSP aplicado:', csp.substring(0, 100) + '...');
    }

    monitorCSPViolations() {
        document.addEventListener('securitypolicyviolation', (event) => {
            const violation = {
                blockedURI: event.blockedURI,
                violatedDirective: event.violatedDirective,
                originalPolicy: event.originalPolicy,
                timestamp: new Date().toISOString()
            };
            
            this.violations.push(violation);
            
            console.group('🚨 CSP Violation Detected');
            console.log('Bloqueado:', event.blockedURI);
            console.log('Directiva violada:', event.violatedDirective);
            console.log('Política:', event.originalPolicy);
            console.groupEnd();
            
            // Mostrar notificación visual
            this.showViolationNotification(violation);
        });
    }

    showViolationNotification(violation) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            background: linear-gradient(135deg, #ff6b6b, #ee5a5a);
            color: white;
            padding: 15px 20px;
            border-radius: 8px;
            font-family: Arial, sans-serif;
            font-size: 14px;
            z-index: 999999;
            box-shadow: 0 4px 15px rgba(255,0,0,0.3);
            max-width: 350px;
            animation: slideIn 0.3s ease-out;
        `;
        
        notification.innerHTML = `
            <div style="font-weight: bold; margin-bottom: 8px; font-size: 16px;">
                🚨 Bloqueo de Seguridad
            </div>
            <div style="font-size: 12px; opacity: 0.9;">
                <strong>Recurso bloqueado:</strong><br>
                <code style="word-break: break-all;">${violation.blockedURI}</code>
            </div>
            <div style="font-size: 11px; margin-top: 8px; opacity: 0.8;">
                CSP: ${violation.violatedDirective}
            </div>
            <button onclick="this.parentElement.remove()" style="
                position: absolute;
                top: 5px;
                right: 10px;
                background: none;
                border: none;
                color: white;
                cursor: pointer;
                font-size: 18px;
            ">×</button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
}

class NetworkMonitor {
    constructor() {
        this.requests = [];
        this.blockedDomains = [
            'malware-domain.com',
            'tracker-evil.net',
            'ads-malicious.com'
        ];
        this.initialized = false;
    }

    init() {
        if (this.initialized) return;
        
        // Interceptar fetch
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const url = typeof args[0] === 'string' ? args[0] : args[0].url;
            this.logRequest('fetch', url);
            this.checkForThreats('fetch', url);
            return originalFetch.apply(window, args);
        };
        
        // Interceptar XMLHttpRequest
        const originalXHROpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url, ...rest) {
            NetworkMonitor.prototype.logRequest.call(
                networkMonitor, 'xhr', url
            );
            NetworkMonitor.prototype.checkForThreats.call(
                networkMonitor, 'xhr', url
            );
            return originalXHROpen.call(this, method, url, ...rest);
        };
        
        // Interceptar creación de WebSocket
        const OriginalWebSocket = window.WebSocket;
        window.WebSocket = function(url, protocols) {
            networkMonitor.logRequest('websocket', url);
            networkMonitor.checkForThreats('websocket', url);
            return new OriginalWebSocket(url, protocols);
        };
        
        this.initialized = true;
        console.log('🛡️ Network Monitor activo - Monitoreando peticiones');
    }

    logRequest(type, url) {
        try {
            const entry = {
                type,
                url,
                timestamp: new Date().toISOString(),
                tab: window.location.hostname
            };
            this.requests.push(entry);
        } catch (e) {
            console.warn('Error logging request:', e);
        }
    }

    checkForThreats(type, url) {
        try {
            const urlObj = new URL(url, window.location.origin);
            const hostname = urlObj.hostname;
            
            // Verificar dominios bloqueados
            for (const blocked of this.blockedDomains) {
                if (hostname.includes(blocked) || hostname === blocked) {
                    console.error(`🚨 Intentando conectar a dominio bloqueado: ${hostname}`);
                    return false;
                }
            }
            
            // Verificar URLs no-HTTPS en producción
            if (urlObj.protocol === 'http:' && 
                window.location.protocol === 'https:') {
                console.warn(`⚠️ Request HTTP desde HTTPS: ${url}`);
            }
            
            return true;
        } catch (e) {
            return true;
        }
    }

    getRequests() {
        return this.requests;
    }

    clearLog() {
        this.requests = [];
    }
}

// Instancia global
const networkMonitor = new NetworkMonitor();

// Auto-inicializar cuando el DOM esté listo
function initSecurity() {
    // Inicializar monitor de red
    networkMonitor.init();
    
    // Inicializar CSP
    const headersManager = new SecurityHeadersManager();
    const csp = headersManager.setCSPPolicy();
    
    // Proteger cookies
    protectCookies();
    
    // Proteger localStorage/sessionStorage
    protectStorage();
    
    // Deshabilitar funcionalidades peligrosas
    disableDangerousFeatures();
    
    console.log('🛡️ Suite de seguridad completamente cargada');
    console.log('📊 Violaciones CSP:', headersManager.violations.length);
    console.log('📊 Requests monitorizados:', networkMonitor.requests.length);
}

function protectCookies() {
    // Configurar cookies seguras
    Object.defineProperty(document, 'cookie', {
        set: function(value) {
            // Agregar flags de seguridad automáticamente
            if (!value.includes('Secure')) {
                value += '; Secure';
            }
            if (!value.includes('HttpOnly') === false) {
                // HttpOnly solo funciona desde servidor, 
                // pero podemos añadir SameSite
                if (!value.includes('SameSite')) {
                    value += '; SameSite=Strict';
                }
            }
            
            // Verificar que no se envíe a terceros
            if (value.includes('Domain=')) {
                console.warn('⚠️ Cookie con Domain configurado - posible tracking');
            }
            
            // Usar setter original
            setCookie.call(this, value);
        },
        get: function() {
            return getCookie.call(this);
        }
    });
    
    function setCookie(value) {
        Object.getOwnPropertyDescriptor(
            Document.prototype, 'cookie'
        ).set.call(document, value);
    }
    
    function getCookie() {
        return Object.getOwnPropertyDescriptor(
            Document.prototype, 'cookie'
        ).get.call(document);
    }
}

function protectStorage() {
    // Monitorear acceso a localStorage
    const originalSetItem = Storage.prototype.setItem;
    const originalRemoveItem = Storage.prototype.removeItem;
    
    Storage.prototype.setItem = function(key, value) {
        console.log('📝 Storage: Intentando guardar', key);
        
        // No almacenar datos sensibles en localStorage
        const sensitivePatterns = [
            /password/i, /token/i, /secret/i, 
            /key/i, /credential/i, /auth/i
        ];
        
        for (const pattern of sensitivePatterns) {
            if (pattern.test(key)) {
                console.warn(`⚠️ Almacenando dato sensible en localStorage: ${key}`);
                console.warn('   Se recomienda usar sessionStorage o HttpOnly cookies');
            }
        }
        
        return originalSetItem.call(this, key, value);
    };
}

function disableDangerousFeatures() {
    // Deshabilitar autocomplete en formularios sensibles
    document.querySelectorAll('input[type="password"], input[name*="password"]')
        .forEach(input => {
            input.setAttribute('autocomplete', 'off');
        });
    
    // Prevenir que se abra como ventana nueva con opener
    if (window.opener && window.opener !== window) {
        window.opener = null;
    }
    
    // Deshabilitar webkitmessagechannel (puede ser usado para tracking
    if (window.webkitMessageChannel) {
        console.warn('⚠️ webkitMessageChannel detectado - monitoreando');
    }
}

// Agregar estilos para animaciones
const styleSheet = document.createElement('style');
styleSheet.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(styleSheet);

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initSecurity);
} else {
    initSecurity();
}

// Exportar
window.SecurityHeadersManager = SecurityHeadersManager;
window.NetworkMonitor = NetworkMonitor;
window.networkMonitor = networkMonitor;

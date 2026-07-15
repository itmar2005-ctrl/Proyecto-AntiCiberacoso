// =============================================
// SCRIPT 1: PROTECCIÓN CONTRA XSS (Cross-Site Scripting)
// Educativo - Demuestra cómo sanitizar entradas y prevenir inyección de scripts
// =============================================

class XSSProtector {
    constructor() {
        this.dangerousPatterns = [
            /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
            /javascript:/gi,
            /on\w+\s*=/gi,
            /<iframe/gi,
            /<object/gi,
            /<embed/gi,
            /<link/gi,
            /<import/gi
        ];
        
        this.xssPayloads = [
            '<script>alert("XSS")</script>',
            '<img src=x onerror="alert(1)">',
            'javascript:alert("XSS")',
            '<svg onload="alert(1)">',
            '<iframe src="javascript:alert(1)">'
        ];
    }

    // Sanitizar HTML eliminando etiquetas y eventos peligrosos
    sanitize(input) {
        if (typeof input !== 'string') return input;
        
        let sanitized = input;
        
        // Eliminar etiquetas script
        sanitized = sanitized.replace(/<\/?script[^>]*>/gi, '');
        
        // Eliminar atributos on* (onclick, onerror, etc)
        sanitized = sanitized.replace(/\s*on\w+\s*=\s*["'][^"']*["']/gi, '');
        sanitized = sanitized.replace(/\s*on\w+\s*=\s*[^\s>]+/gi, '');
        
        // Eliminar javascript:
        sanitized = sanitized.replace(/javascript:/gi, '');
        
        // Eliminar data: URLs peligrosas
        sanitized = sanitized.replace(/data:text\/html/gi, '');
        
        // Reemplazar < y > por entidades HTML
        sanitized = sanitized
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#x27;');
        
        return sanitized;
    }

    // Validar que el input no contenga patrones peligrosos
    validate(input) {
        for (const pattern of this.dangerousPatterns) {
            if (pattern.test(input)) {
                return { 
                    safe: false, 
                    threat: 'Patrón peligroso detectado',
                    pattern: pattern.toString()
                };
            }
        }
        return { safe: true };
    }

    // Escapar HTML para顯示 segura
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    // Proteger todos los formularios de la página
    protectForms() {
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', (e) => {
                const inputs = form.querySelectorAll('input, textarea');
                inputs.forEach(input => {
                    const validation = this.validate(input.value);
                    if (!validation.safe) {
                        e.preventDefault();
                        alert('⚠️ Entrada peligrosa bloqueada:\n' + validation.threat);
                        input.value = this.sanitize(input.value);
                    }
                });
            });
        });
        
        // Proteger elementos con innerHTML
        const originalInnerHTML = Object.getOwnPropertyDescriptor(
            Element.prototype, 'innerHTML'
        );
        
        Object.defineProperty(Element.prototype, 'innerHTML', {
            set: function(value) {
                const sanitized = XSSProtector.sanitizeStatic(value);
                originalInnerHTML.set.call(this, sanitized);
            },
            get: originalInnerHTML
        });
    }

    static sanitizeStatic(value) {
        if (typeof value !== 'string') return value;
        
        // Eliminar patrones XSS conocidos
        const patterns = [
            /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
            /on\w+\s*=\s*["'][^"']*["']/gi,
            /javascript:/gi
        ];
        
        let result = value;
        patterns.forEach(pattern => {
            result = result.replace(pattern, '');
        });
        
        return result;
    }

    // Detectar y registrar intentos de XSS
    monitorDOM() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach(node => {
                        if (node.nodeType === 1) { // Element node
                            const html = node.innerHTML || node.outerHTML || '';
                            const validation = this.validate(html);
                            if (!validation.safe) {
                                console.warn('🚨 XSS bloqueado:', {
                                    node: node.tagName,
                                    threat: validation.threat,
                                    content: html.substring(0, 100)
                                });
                                node.remove();
                            }
                        }
                    });
                }
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
}

// Inicializar protección
const protector = new XSSProtector();

// Proteger formularios al cargar DOM
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        protector.protectForms();
        protector.monitorDOM();
    });
} else {
    protector.protectForms();
    protector.monitorDOM();
}

// Exportar para uso educativo
window.XSSProtector = XSSProtector;
console.log('🛡️ XSS Protector cargado - Protegiendo contra ataques de inyección');

import json
import os
import random
from typing import Dict, List, Optional, Any
from pathlib import Path

from ..core.config import config
from ..core.logger import logger


class ChatbotEngine:
    def __init__(self):
        self._name = config.get("chatbot.name", "Purple Team AI")
        self._version = config.get("chatbot.version", "2.0.0")
        self._provider = config.get("chatbot.provider", "local")
        self._conversation_history: List[Dict[str, str]] = []
        self._knowledge_base = self._load_knowledge()

        self._intents = {
            "scan": ["scan", "escanear", "scannear", "analizar", "vulnerabilidad"],
            "block": ["block", "bloquear", "ban", "denegar"],
            "monitor": ["monitor", "trafico", "red", "network", "packet"],
            "status": ["status", "estado", "health", "alive", "funcionando"],
            "help": ["help", "ayuda", "comandos", "helpme", "que puedes hacer"],
            "alert": ["alert", "alerta", "notificacion", "alarma"],
            "report": ["report", "reporte", "informe", "resumen"],
            "waf": ["waf", "firewall", "cloudflare", "protection"],
            "agent": ["agent", "agente", "victima", "payload"],
        }

        self._responses = {
            "scan": self._handle_scan,
            "block": self._handle_block,
            "monitor": self._handle_monitor,
            "status": self._handle_status,
            "help": self._handle_help,
            "alert": self._handle_alert,
            "report": self._handle_report,
            "waf": self._handle_waf,
            "agent": self._handle_agent,
        }

    @staticmethod
    def _load_knowledge() -> Dict[str, Any]:
        kb_path = Path(__file__).parent.parent.parent / "data" / "knowledge.json"
        if kb_path.exists():
            with open(kb_path) as f:
                return json.load(f)
        return {
            "waf": {
                "description": "Web Application Firewall - protege aplicaciones web contra ataques",
                "types": ["Cloudflare WAF", "ModSecurity", "AWS WAF", "Azure WAF"],
                "common_attacks": ["SQLi", "XSS", "CSRF", "LFI", "RCE", "SSRF"],
            },
            "purple_team": {
                "description": "Equipo de seguridad que combina red team (ataque) y blue team (defensa)",
                "tools": ["ntopng", "Wireshark", "Metasploit", "Burp Suite", "Nmap"],
            },
            "commands": {
                "scan <ip>": "Escanea una IP/puertos",
                "block <ip>": "Bloquea una IP en el WAF",
                "monitor": "Muestra estadisticas de trafico",
                "status": "Estado del sistema",
                "report": "Genera un reporte de seguridad",
                "waf list": "Lista reglas del WAF",
                "agent list": "Lista agentes conectados",
            },
        }

    def _classify_intent(self, message: str) -> Optional[str]:
        msg_lower = message.lower()
        for intent, keywords in self._intents.items():
            for kw in keywords:
                if kw in msg_lower:
                    return intent
        return None

    def chat(self, message: str) -> str:
        if not message or not message.strip():
            return "Por favor, escribe un mensaje."

        self._conversation_history.append({"role": "user", "content": message})
        intent = self._classify_intent(message)

        if intent and intent in self._responses:
            try:
                response = self._responses[intent](message)
            except Exception as e:
                response = f"Error al procesar '{intent}': {e}"
                logger.error(f"Chatbot error: {e}")
        else:
            response = self._fallback_response(message)

        self._conversation_history.append({"role": "assistant", "content": response})

        if len(self._conversation_history) > 50:
            self._conversation_history = self._conversation_history[-50:]

        return response

    def _handle_scan(self, message: str) -> str:
        import re
        ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", message)
        domains = re.findall(
            r"\b(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}\b", message
        )

        targets = ips + domains
        if targets:
            from ..agent.scanner import Scanner
            scanner = Scanner()
            results = []
            for target in targets[:3]:
                scan_result = scanner.scan(target, "1-1024")
                results.append(f"  **{target}**: {len(scan_result)} puertos abiertos")
            return (
                f"**Escaneo completado**\n" + "\n".join(results)
                if results
                else "No se encontraron puertos abiertos"
            )
        return (
            "Para escanear usa: `scan <IP>` o `escanear <dominio>`\n"
            "Ejemplo: `scan 192.168.1.1`"
        )

    def _handle_block(self, message: str) -> str:
        import re
        ips = re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", message)
        if ips:
            from ..waf.manager import waf_manager
            results = []
            for ip in ips[:5]:
                waf_manager.block_ip("", ip)
                results.append(f"  IP {ip} bloqueada")
            return "**Bloqueo completado**\n" + "\n".join(results)
        return "Especifica una IP para bloquear: `block 192.168.1.100`"

    def _handle_monitor(self, message: str) -> str:
        from ..monitor.sniffer import network_monitor
        stats = network_monitor.get_dashboard_data()
        s = stats.get("stats", {})
        return (
            f"**Monitor de Red**\n"
            f"  Bytes totales: {s.get('total_bytes', 0)}\n"
            f"  Paquetes: {s.get('total_packets', 0)}\n"
            f"  Conexiones activas: {s.get('active_connections', 0)}\n"
            f"  Flujos: {s.get('flows', 0)}\n"
        )

    def _handle_status(self, message: str) -> str:
        from ..c2.server import c2_server
        stats = c2_server.get_stats()
        return (
            f"**Estado del Sistema**\n"
            f"  Agentes online: {stats.get('agents_online', 0)}/{stats.get('agents_total', 0)}\n"
            f"  Alertas criticas: {stats.get('alerts_critical', 0)}\n"
            f"  Comandos pendientes: {stats.get('commands_pending', 0)}\n"
            f"  Flujos de red: {stats.get('flows_total', 0)}"
        )

    def _handle_help(self, message: str) -> str:
        cmds = self._knowledge_base.get("commands", {})
        return "**Comandos disponibles**\n" + "\n".join(
            f"  `{cmd}` - {desc}" for cmd, desc in cmds.items()
        )

    def _handle_alert(self, message: str) -> str:
        from ..core.database import db
        alerts = db.list_alerts(limit=10)
        if not alerts:
            return "No hay alertas registradas"
        lines = ["**Alertas Recientes**"]
        for a in alerts:
            lines.append(
                f"  [{a.get('severity', 'info').upper()}] {a.get('title', '')}"
            )
        return "\n".join(lines)

    def _handle_report(self, message: str) -> str:
        from ..core.database import db
        stats = db.get_stats()
        return (
            f"**Reporte de Seguridad**\n"
            f"  Agentes monitoreados: {stats.get('agents_total', 0)}\n"
            f"  Alertas activas: {stats.get('alerts_critical', 0)}\n"
            f"  Flujos analizados: {stats.get('flows_total', 0)}\n"
            f"  Comandos ejecutados: {stats.get('commands_pending', 0)} pendientes"
        )

    def _handle_waf(self, message: str) -> str:
        msg = message.lower()
        if "list" in msg or "regla" in msg:
            from ..waf.manager import waf_manager
            rules = waf_manager.list_rules("")
            if rules:
                return "Reglas WAF:\n" + "\n".join(
                    f"  [{r.get('action', '?')}] {r.get('expression', '')}"
                    for r in rules[:10]
                )
            return "No hay reglas WAF configuradas"
        return (
            "Comandos WAF:\n"
            "  `waf list` - Lista reglas\n"
            "  `block <IP>` - Bloquea IP\n"
        )

    def _handle_agent(self, message: str) -> str:
        msg = message.lower()
        if "list" in msg:
            from ..c2.server import c2_server
            agents = c2_server.list_agents()
            if agents:
                lines = ["**Agentes Conectados**"]
                for a in agents:
                    lines.append(
                        f"  [{a.get('status', '?')}] {a.get('agent_id', '?')} - "
                        f"{a.get('hostname', '?')}@{a.get('ip', '?')}"
                    )
                return "\n".join(lines)
            return "No hay agentes conectados"
        return "Usa `agent list` para ver agentes conectados"

    def _fallback_response(self, message: str) -> str:
        msg_lower = message.lower()
        knowledge = self._knowledge_base

        if any(word in msg_lower for word in ["hola", "buenas", "hey", "hi"]):
            greetings = [
                f"Hola! Soy {self._name}. ¿En que puedo ayudarte?",
                f"Bienvenido al sistema Purple Team. Puedes pedirme ayuda con `help`",
            ]
            return random.choice(greetings)

        if "gracias" in msg_lower or "thanks" in msg_lower:
            return "¡De nada! Estoy aqui para ayudar con la seguridad."

        if any(word in msg_lower for word in knowledge.get("waf", {}).get("common_attacks", [])):
            attack = next(
                (w for w in knowledge["waf"]["common_attacks"] if w.lower() in msg_lower),
                None,
            )
            if attack:
                return (
                    f"**{attack}** es un ataque web común. El WAF de Cloudflare "
                    f"puede mitigarlo con reglas personalizadas."
                )

        return (
            f"No entendí tu mensaje. Usa `help` para ver los comandos disponibles "
            f"o pregunta sobre seguridad, WAF, o monitoreo de red."
        )

    def reset_conversation(self) -> str:
        self._conversation_history.clear()
        return "Conversación reiniciada."

    @property
    def name(self) -> str:
        return self._name

    @property
    def version(self) -> str:
        return self._version

    def get_status(self) -> str:
        return f"{self._name} v{self._version} | Modo: {self._provider.title()}"

    def get_conversation_history(self) -> List[Dict[str, str]]:
        return self._conversation_history[-20:]


chatbot = ChatbotEngine()

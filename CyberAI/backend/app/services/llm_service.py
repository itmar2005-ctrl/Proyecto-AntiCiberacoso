import time
import json
import httpx
from groq import Groq
from app.config import settings

groq_client = Groq(api_key=settings.groq_api_key)

CALL_START_PROMPT = """Eres CyberAI, una asistente de ciberseguridad experta y profesional. 
Tienes una personalidad amable pero técnica. 
Respondes en español de forma clara y precisa.
Saluda al usuario y pregúntale en qué puedes ayudarle con ciberseguridad.
Mantén tus respuestas CONCISAS (máximo 3 párrafos) a menos que te pidan detalles.
"""

SYSTEM_PROMPT = """Eres CyberAI, un asistente experto en ciberseguridad, hacking ético, redes, Linux, Windows, Wazuh, Suricata, pfSense.

Reglas:
- Responde en español
- Usa Markdown para código, tablas y listas
- Sé técnicamente preciso pero didáctico
- Promueve prácticas éticas y legales
- Si no sabes algo, dilo honestamente

Contexto de documentos:
{context}

Historial:
{history}
"""

class LLMService:
    def __init__(self):
        self.model = settings.groq_model
        self.use_ollama = settings.use_ollama

    def generate(self, message: str, context: str = "", history: list = None, system_override: str = None) -> tuple:
        if history is None:
            history = []

        system = system_override or SYSTEM_PROMPT
        system = system.format(
            context=context or "No hay documentos relevantes.",
            history="\n".join([f"{m['role']}: {m['content']}" for m in history[-6:]])
        )

        messages = [{"role": "system", "content": system}]
        for m in history[-10:]:
            messages.append({"role": m["role"], "content": m["content"]})
        messages.append({"role": "user", "content": message})

        start = time.time()

        if self.use_ollama:
            reply, tokens = self._call_ollama(messages)
        else:
            reply, tokens = self._call_groq(messages)

        elapsed = time.time() - start
        return reply, tokens, elapsed

    def _call_groq(self, messages: list) -> tuple:
        response = groq_client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
        )
        reply = response.choices[0].message.content
        tokens = response.usage.total_tokens if response.usage else 0
        return reply, tokens

    def _call_ollama(self, messages: list) -> tuple:
        try:
            resp = httpx.post(
                f"{settings.ollama_base_url}/api/chat",
                json={"model": settings.ollama_model, "messages": messages, "stream": False},
                timeout=120
            )
            data = resp.json()
            return data.get("message", {}).get("content", ""), data.get("total_tokens", 0)
        except Exception as e:
            return f"[Error Ollama: {e}]", 0

    def generate_call_start(self) -> tuple:
        reply, tokens, elapsed = self.generate(
            "Inicia la conversación con un saludo profesional",
            system_override=CALL_START_PROMPT
        )
        return reply, tokens, elapsed

    def switch_model(self, model: str):
        self.model = model

    def list_models(self) -> list:
        models = [
            {"id": "llama-3.1-8b-instant", "name": "Groq Llama 3.1 8B Instant", "provider": "groq"},
            {"id": "llama-3.3-70b-versatile", "name": "Groq Llama 3.3 70B", "provider": "groq"},
            {"id": "mixtral-8x7b-32768", "name": "Groq Mixtral 8x7B", "provider": "groq"},
            {"id": "gemma2-9b-it", "name": "Groq Gemma 2 9B", "provider": "groq"},
        ]
        if self.use_ollama:
            models.append({"id": settings.ollama_model, "name": f"Ollama {settings.ollama_model}", "provider": "ollama"})
        return models

import base64
import os
import tempfile
from groq import Groq
from app.config import settings

client = Groq(api_key=settings.groq_api_key)

class VoiceService:
    async def speech_to_text(self, audio_bytes: bytes) -> str:
        whisper_available = False
        try:
            import whisper
            whisper_available = True
        except ImportError:
            pass

        if whisper_available:
            import whisper
            model = whisper.load_model(settings.whisper_model)
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
            try:
                result = model.transcribe(tmp_path, language="es")
                return result["text"].strip()
            finally:
                os.unlink(tmp_path)

        with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name
        try:
            with open(tmp_path, "rb") as f:
                transcription = client.audio.transcriptions.create(
                    file=(tmp_path, f),
                    model="whisper-large-v3",
                    language="es",
                    response_format="text"
                )
            return transcription.strip()
        except Exception as e:
            return f"[Error de transcripción: {e}]"
        finally:
            os.unlink(tmp_path)

    def text_to_speech(self, text: str, voice: str = "shimmer") -> bytes:
        try:
            response = client.audio.speech.create(
                model="playai-tts",
                voice=voice,
                input=text,
                response_format="wav",
            )
            return response.content
        except Exception:
            return b""

    def get_audio_base64(self, text: str, voice: str = "shimmer") -> str:
        audio_bytes = self.text_to_speech(text, voice)
        return base64.b64encode(audio_bytes).decode("utf-8")

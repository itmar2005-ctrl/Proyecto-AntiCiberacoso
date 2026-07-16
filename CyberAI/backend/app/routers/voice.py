from fastapi import APIRouter, UploadFile, File
from app.services.voice_service import VoiceService

router = APIRouter(prefix="/api/voice", tags=["Voice"])
voice = VoiceService()

@router.post("/stt")
async def speech_to_text(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    text = await voice.speech_to_text(audio_bytes)
    return {"text": text}

@router.post("/tts")
async def text_to_speech(text: str, voice: str = "shimmer"):
    audio_b64 = voice.get_audio_base64(text, voice)
    return {"audio": audio_b64, "format": "wav"}

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "CyberAI Assistant"
    version: str = "2.0.0"
    debug: bool = True

    groq_api_key: str = ""
    groq_model: str = "llama-3.1-8b-instant"
    groq_tts_model: str = "playai-tts"

    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.3"
    use_ollama: bool = False

    chroma_dir: str = "database/chroma"
    upload_dir: str = "documents/uploads"
    history_dir: str = "database/history"

    whisper_model: str = "base"
    max_tokens: int = 4096
    temperature: float = 0.7

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()

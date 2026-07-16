# CyberAI Assistant

Asistente de ciberseguridad con IA, voz, avatar 3D y base de conocimiento RAG.

## Stack

- **Frontend:** React + Vite + Tailwind CSS + Three.js + Framer Motion
- **Backend:** FastAPI + Groq API (Llama 3 70B)
- **Base Vectorial:** ChromaDB (RAG)
- **Voz:** Whisper (STT) + Groq TTS
- **Avatar:** Three.js 3D animado

## Requisitos

- Python 3.10+
- Node.js 18+
- Groq API Key (incluida)
- Whisper (opcional, para STT local)

## Instalación

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker-compose up --build
```

## Endpoints API

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/chat` | Enviar mensaje |
| GET | `/api/chat/history` | Listar conversaciones |
| GET | `/api/chat/history/{id}` | Ver conversación |
| DELETE | `/api/chat/history/{id}` | Eliminar conversación |
| POST | `/api/documents/upload` | Subir documento |
| POST | `/api/documents/upload-url` | Indexar URL |
| GET | `/api/documents` | Listar documentos |
| DELETE | `/api/documents/{id}` | Eliminar documento |
| POST | `/api/voice/stt` | Voz a texto |
| POST | `/api/voice/tts` | Texto a voz |
| GET | `/api/health` | Health check |

## Estructura

```
CyberAI/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── routers/
│   │   ├── services/
│   │   └── models/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Chat/
│   │   │   ├── Avatar/
│   │   │   ├── Background/
│   │   │   ├── Sidebar/
│   │   │   └── StatsPanel/
│   │   ├── services/
│   │   ├── store/
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── database/
├── documents/
└── docker-compose.yml
```

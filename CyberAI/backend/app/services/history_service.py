import json
import os
import uuid
from datetime import datetime
from typing import List, Optional
from app.models.schemas import Conversation, Message
from app.config import settings

class HistoryService:
    def __init__(self):
        os.makedirs(settings.history_dir, exist_ok=True)

    def _path(self, cid: str) -> str:
        return os.path.join(settings.history_dir, f"{cid}.json")

    def create(self, title: str = "Nueva conversación") -> Conversation:
        cid = str(uuid.uuid4())
        conv = Conversation(id=cid, title=title, messages=[])
        self._save(conv)
        return conv

    def _save(self, conv: Conversation):
        with open(self._path(conv.id), "w", encoding="utf-8") as f:
            data = conv.model_dump()
            data["created_at"] = data["created_at"].isoformat()
            data["updated_at"] = data["updated_at"].isoformat()
            for m in data["messages"]:
                if m.get("timestamp"):
                    m["timestamp"] = m["timestamp"].isoformat()
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, cid: str) -> Optional[Conversation]:
        path = self._path(cid)
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return Conversation(**data)

    def add_message(self, cid: str, role: str, content: str):
        conv = self.load(cid) or self.create()
        conv.messages.append(Message(role=role, content=content, timestamp=datetime.now()))
        conv.updated_at = datetime.now()
        if len(conv.messages) == 1:
            conv.title = content[:50] + ("..." if len(content) > 50 else "")
        self._save(conv)

    def list_conversations(self) -> List[dict]:
        convs = []
        for fname in os.listdir(settings.history_dir):
            if fname.endswith(".json"):
                path = os.path.join(settings.history_dir, fname)
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                convs.append({"id": data["id"], "title": data["title"], "updated_at": data["updated_at"], "message_count": len(data["messages"])})
        convs.sort(key=lambda c: c["updated_at"], reverse=True)
        return convs

    def delete(self, cid: str):
        path = self._path(cid)
        if os.path.exists(path):
            os.remove(path)

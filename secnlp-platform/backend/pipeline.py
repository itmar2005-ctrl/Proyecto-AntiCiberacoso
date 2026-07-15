"""
Pipeline de moderación de lenguaje natural.
Capas: Sanitización anti-evasión -> Análisis Transformer -> Decisión
"""
import re
import unicodedata
import logging
import hashlib
import time

import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

from backend.config import MODEL_NAME, LEET_DICT, HOMOGLYPHS, TOXICITY_THRESHOLD, MAX_TEXT_LENGTH

logger = logging.getLogger(__name__)


class ModerationPipeline:
    def __init__(self):
        logger.info("[+] Cargando modelo: %s", MODEL_NAME)
        self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        self.model.eval()
        self.cache = {}
        logger.info("[+] Modelo cargado exitosamente")

    def sanitize(self, text: str) -> str:
        """CAPA 1: Sanitización contra evasión adversarial."""
        if not text:
            return ""

        text = unicodedata.normalize("NFKC", text).lower()

        for old, new in HOMOGLYPHS.items():
            text = text.replace(old, new)

        for old, new in LEET_DICT.items():
            text = text.replace(old, new)

        text = re.sub(r"https?://\S+", "[URL]", text)
        text = re.sub(r"@\w+", "[@usuario]", text)

        chars = []
        for i, c in enumerate(text):
            if i < 2 or not (c == text[i - 1] == text[i - 2]):
                chars.append(c)
        text = "".join(chars)

        text = re.sub(r"\s+", " ", text).strip()
        return text[:MAX_TEXT_LENGTH]

    def get_text_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    def analyze(self, text: str) -> dict:
        """CAPA 2: Análisis semántico completo."""
        start = time.time()
        sanitized = self.sanitize(text)

        if not sanitized:
            return {
                "action": "ALLOW",
                "score": 0.0,
                "reason": "Texto vacío tras sanitización",
                "sanitized": "",
                "latency_ms": round((time.time() - start) * 1000, 2),
                "categories": {},
            }

        text_hash = self.get_text_hash(sanitized)
        if text_hash in self.cache:
            result = self.cache[text_hash].copy()
            result["cached"] = True
            result["latency_ms"] = round((time.time() - start) * 1000, 2)
            return result

        inputs = self.tokenizer(
            sanitized,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1).flatten()

        hate_score = float(probs[1].item())
        categories = {
            "hate_speech": round(hate_score, 4),
            "non_hate": round(float(probs[0].item()), 4),
        }

        if hate_score >= TOXICITY_THRESHOLD:
            result = {
                "action": "BLOCK",
                "score": round(hate_score, 4),
                "reason": "Discurso malicioso / ciberacoso detectado",
                "sanitized": sanitized,
                "categories": categories,
                "cached": False,
                "latency_ms": round((time.time() - start) * 1000, 2),
            }
        else:
            result = {
                "action": "ALLOW",
                "score": round(hate_score, 4),
                "reason": "Texto benigno verificado",
                "sanitized": sanitized,
                "categories": categories,
                "cached": False,
                "latency_ms": round((time.time() - start) * 1000, 2),
            }

        self.cache[text_hash] = result
        if len(self.cache) > 10000:
            self.cache.clear()

        return result

    def analyze_batch(self, texts: list[str]) -> list[dict]:
        return [self.analyze(t) for t in texts]

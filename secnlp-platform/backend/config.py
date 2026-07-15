"""
SecNLP Platform - Configuración central
"""
import os

MODEL_NAME = os.getenv("SECNLP_MODEL", "Hate-speech-CNERG/dehatebert-mono-spanish")
TOXICITY_THRESHOLD = float(os.getenv("SECNLP_THRESHOLD", "0.70"))
MAX_TEXT_LENGTH = int(os.getenv("SECNLP_MAX_LENGTH", "1000"))
CACHE_ENABLED = os.getenv("SECNLP_CACHE", "true").lower() == "true"
REDIS_URL = os.getenv("SECNLP_REDIS", "redis://localhost:6379")

LEET_DICT = {
    "4": "a", "@": "a", "3": "e", "1": "i", "!": "i",
    "0": "o", "7": "t", "5": "s", "$": "s", "9": "g",
    "6": "b", "8": "b", "2": "z", "*": "",
}

HOMOGLYPHS = {
    "а": "a", "е": "e", "о": "o", "р": "p", "с": "c",
    "у": "y", "х": "x", "і": "i", "ј": "j",
}

CATEGORY_LABELS = {0: "No_Odio", 1: "Odio"}

import logging
from typing import Dict, List
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_NAME = "unitary/toxic-bert"

LABELS = [
    "toxic",
    "severe_toxic",
    "obscene",
    "threat",
    "insult",
    "identity_hate",
]

LABEL_DESCRIPTIONS = {
    "toxic": "Contenido dañino o malintencionado en general",
    "severe_toxic": "Contenido extremadamente dañino o agresivo",
    "obscene": "Lenguaje obsceno, vulgar o inapropiado",
    "threat": "Amenazas directas o indirectas hacia alguien",
    "insult": "Insultos personales o ataques verbales",
    "identity_hate": "Discurso de odio basado en identidad (raza, género, religión, etc.)",
}

LABEL_COLORS = {
    "toxic": "#ff6b35",
    "severe_toxic": "#e71d36",
    "obscene": "#ff9f1c",
    "threat": "#c70039",
    "insult": "#ff5733",
    "identity_hate": "#900c3f",
}


class ToxicityDetector:
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._load_model()

    def _load_model(self):
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification

            logger.info(f"Cargando modelo {MODEL_NAME}...")
            self.tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
            self.model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
            self.model.eval()
            logger.info("Modelo cargado exitosamente")
        except Exception as e:
            logger.error(f"Error al cargar el modelo: {e}")
            raise

    def predict(self, text: str) -> Dict:
        if not text or not text.strip():
            return {"error": "Texto vacío", "scores": {}, "overall_toxicity": 0.0}

        import torch

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512,
        )

        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.sigmoid(outputs.logits).squeeze().tolist()

        if isinstance(probabilities, float):
            probabilities = [probabilities]

        scores = {}
        for label, prob in zip(LABELS, probabilities):
            scores[label] = round(prob, 4)

        overall_toxicity = round(max(scores.values()), 4)

        highlighted_spans = self._get_highlighted_spans(text, scores)

        top_categories = sorted(
            [(l, s) for l, s in scores.items() if s > 0.3],
            key=lambda x: x[1],
            reverse=True,
        )

        return {
            "scores": scores,
            "overall_toxicity": overall_toxicity,
            "highlighted_spans": highlighted_spans,
            "top_categories": top_categories,
            "is_toxic": overall_toxicity > 0.5,
            "label_descriptions": {
                l: LABEL_DESCRIPTIONS.get(l, "") for l, _ in top_categories
            },
        }

    def _get_highlighted_spans(self, text: str, scores: Dict) -> List[Dict]:
        toxic_words = []
        word_toxicity = {}

        for word in text.split():
            clean_word = word.strip(".,!?;:()[]\"'")
            if len(clean_word) < 2:
                continue

            word_inputs = self.tokenizer(
                clean_word,
                return_tensors="pt",
                truncation=True,
                padding=True,
                max_length=512,
            )

            import torch

            with torch.no_grad():
                word_outputs = self.model(**word_inputs)
                word_probs = (
                    torch.sigmoid(word_outputs.logits).squeeze().tolist()
                )

            if isinstance(word_probs, float):
                word_probs = [word_probs]

            word_max_toxicity = max(word_probs)
            if word_max_toxicity > 0.4:
                word_toxicity[word] = word_max_toxicity

        total_score = sum(word_toxicity.values())
        if total_score == 0 or not word_toxicity:
            words_list = list(scores.keys())
            word_toxicity = {w: scores[w] for w in words_list[:2] if scores[w] > 0.3}

        return [
            {"word": word, "score": round(score, 4)}
            for word, score in sorted(
                word_toxicity.items(), key=lambda x: x[1], reverse=True
            )[:10]
        ]

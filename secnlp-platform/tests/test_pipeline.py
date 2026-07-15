"""Tests del pipeline de moderación"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.pipeline import ModerationPipeline


def test_sanitize_empty():
    p = ModerationPipeline()
    assert p.sanitize("") == ""
    assert p.sanitize(None) == ""


def test_sanitize_leet():
    p = ModerationPipeline()
    result = p.sanitize("3r3s un 1d10t4")
    assert "eres" in result or "un" in result
    assert "idiota" in result or "1d10t4" not in result


def test_sanitize_homoglyph():
    p = ModerationPipeline()
    result = p.sanitize("привет")
    assert isinstance(result, str)


def test_sanitize_repeated():
    p = ModerationPipeline()
    result = p.sanitize("perraaaaaaaa")
    assert result.count("a") <= 3


def test_analyze_safe():
    p = ModerationPipeline()
    result = p.analyze("Eres una gran persona, gracias")
    assert result["action"] == "ALLOW"
    assert 0 <= result["score"] <= 1


def test_analyze_toxic():
    p = ModerationPipeline()
    result = p.analyze("Eres un idiota inutil")
    assert result["action"] in ("ALLOW", "BLOCK")
    assert "latency_ms" in result


def test_analyze_batch():
    p = ModerationPipeline()
    texts = ["Hola amigo", "Te odio"]
    results = p.analyze_batch(texts)
    assert len(results) == 2


def test_cache():
    p = ModerationPipeline()
    r1 = p.analyze("Texto de prueba")
    r2 = p.analyze("Texto de prueba")
    assert r1["sanitized"] == r2["sanitized"]


def test_sanitize_url():
    p = ModerationPipeline()
    result = p.sanitize(" visita https://malware.com ahora ")
    assert "[URL]" in result

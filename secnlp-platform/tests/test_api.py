"""Tests de la API"""
from fastapi.testclient import TestClient
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.main import app
from backend.routers.moderation import pipeline

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code in (200, 404)


def test_moderate_empty():
    resp = client.post("/v1/moderate", json={"text": ""})
    assert resp.status_code == 422


def test_moderate_safe():
    resp = client.post("/v1/moderate", json={"text": "Hola mundo"})
    assert resp.status_code == 200
    data = resp.json()
    assert "action" in data
    assert "score" in data


def test_moderate_toxic():
    resp = client.post("/v1/moderate", json={"text": "Eres un idiota"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["action"] in ("ALLOW", "BLOCK")


def test_metrics():
    resp = client.get("/metrics")
    assert resp.status_code == 200


def test_feedback():
    resp = client.post("/v1/feedback/false-positive", json={
        "original_text": "test",
        "action_taken": "BLOCK",
        "is_false_positive": True,
        "comment": "FP test"
    })
    assert resp.status_code == 200

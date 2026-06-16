from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_chat_basic() -> None:
    response = client.post(
        "/chat",
        json={"prompt": "hello", "max_tokens": 64},
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data["text"], str) #tests Open AI Model for now.
    assert len(data["text"]) > 0
    assert data["input_tokens"] > 0
    assert data["output_tokens"] > 0
    assert isinstance(data["model"], str)


def test_embed_basic() -> None:
    response = client.post(
        "/embed",
        json={"texts": ["abc", "defg"]},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["vectors"]) == 2
    assert data["dim"] > 0
    assert isinstance(data["model"], str)
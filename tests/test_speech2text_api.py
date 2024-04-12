import os

from fastapi.testclient import TestClient
from loguru import logger

from speech2text.application.app import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {'message': 'Hello Speech2Text!'}


def test_speech2text():
    with open("tests/dataset/en/en-1.wav", "rb") as f:
        response = client.post("/rest/speech2text", files={"file": ("filename", f, "audio/x-wav")})
        logger.debug(response.text)
    assert response.status_code == 200


def test_fr():
    for filename in sorted(os.listdir('tests/dataset/fr'), key=lambda x: int(x.replace('.wav', ''))):
        with open(f"tests/dataset/fr/{filename}", "rb") as f:
            response = client.post("/rest/speech2text/fr", files={"file": ("filename", f, "audio/x-wav")})
            logger.debug(f"{filename} = {response.text}")
    assert response.status_code == 200

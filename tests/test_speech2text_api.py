from fastapi.testclient import TestClient
from speech2text.application.app import app

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() ==  {'message': 'Hello Speech2Text!'}
    
def test_speech2text():
    with open("tests/dataset/en/1.wav", "rb") as f:
        response = client.post("/speech2text", files={"file": ("filename", f, "audio/x-wav")})
  
    assert response.status_code == 200 
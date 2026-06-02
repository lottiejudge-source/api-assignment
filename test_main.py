from fastapi.testclient import TestClient
from main import app,  connection
client=TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "Hello, Taybah!" in response.text

def test_database_connection():
    assert connection is not None
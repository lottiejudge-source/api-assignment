from fastapi.testclient import TestClient
from main import app,  connection
client=TestClient(app)

# def test_read_main():
#     response = client.get("/")
#     assert response.status_code == 200
#     assert "Hello, Taybah!" in response.text

# def test_database_connection():
#     assert connection is not None

def test_for_coin():
    response = client.get("/coins")
    assert response.status_code == 200

    coins = response.json()

    assert type(coins) == list
    assert len(coins) > 0
    

def test_for_coin():
    response = client.get("/coins")

    assert response.status_code == 200

    coins = response.json()
    print(coins)

    assert [1, "Assemble"] in coins

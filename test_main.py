from fastapi.testclient import TestClient
from main import app,  connection, insert_coin
client=TestClient(app)

# testing adding a coin

def test_for_coin():
    response = client.get("/coins")
    assert response.status_code == 200

    coins = response.json()

    assert type(coins) == list
    assert len(coins) > 0
    
# testing assemble exists 
def test_for_coin_assemble():
    response = client.get("/coins")
    assert response.status_code == 200

    coins = response.json()

    print(coins)
    assert [1, "Assemble"] in coins

# def test_for_adding_coin():
#     response = client.post("/coins")
#     assert response.status_code == 201
    
#     coins = response.json()
#     print(coins)

#     # assert new coin is in the database 
#     assert [14, "Biscuit"] in coins


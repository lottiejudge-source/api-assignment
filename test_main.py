from fastapi.testclient import TestClient
from main import app
from database import db, Coins, Duties, JoinCoinsAndDuties
client=TestClient(app)

db.connect(reuse_if_open=True)
JoinCoinsAndDuties.delete().execute()
Coins.delete().execute()
Duties.delete().execute()
db.close()
# testing adding a coin
def test_for_coin():
    response = client.get("/coins")
    assert response.status_code == 200
    coins = response.json()
    assert isinstance(coins, list)
    

def test_for_adding_coins():
    db.connect(reuse_if_open=True)
    test_duty = Duties.create(
        duty_name="Duty 8",
        duty_description="Evolve and define architecture, utilising the knowledge and experience of the team to design in an optimal user experience, scalability, security, high availability and optimal performance."
        )
    
    db.close()

    coin_to_add = {
        "coin_name": "Assemble",
        "coin_complete": False,
        "duty_ids": [str(test_duty.duty_id)]
    }

    response = client.post("/coins", json=coin_to_add )

    assert response.status_code == 201
    assert "coin_name" in response.json()

def test_for_no_duplicate_coins():
    test_coin = {
          "coin_name": "Assemble",
        "coin_complete": False,
        "duty_ids": []
    }

    response = client.post("/coins", json=test_coin )

    assert response.status_code == 400


def test_for_updating_coin():
    db.connect(reuse_if_open=True)
    coin = Coins.create(coin_name="Assemble", coin_complete=False)
    db.close()

    update_coin = {
        "coin_name": "General Assemble",
        "coin_complete": True,
        "duty_ids": []
    }

    response = client.put(f"/coins/{coin.coin_id}", json=update_coin)

    assert response.status_code == 200


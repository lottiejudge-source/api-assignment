import pytest
from fastapi.testclient import TestClient
from main import app
from peewee import SqliteDatabase
from database import db, Coins, Duties, JoinCoinsAndDuties, init_db
from seed import seed_data

test_db = SqliteDatabase(':memory:')

@pytest.fixture(autouse=True)
def set_up():
    db.initialize(test_db)
    init_db()
    with db:
        JoinCoinsAndDuties.delete().execute()
        Coins.delete().execute()
        Duties.delete().execute()
  
client=TestClient(app)

def test_for_root():   
    response = client.get("/")
    assert response.status_code == 200
    assert "The Coins" in response.text

    
# testing adding a coin
def test_for_coin():
    response = client.get("/coins")
    assert response.status_code == 200
    coins = response.json()
    assert isinstance(coins, list)
    

def test_for_adding_coins():
    with db:
        test_duty = Duties.create(
            duty_name="Duty 8",
            duty_description="Evolve and define architecture, utilising the knowledge and experience of the team to design in an optimal user experience, scalability, security, high availability and optimal performance."
            )
            
    coin_to_add = {
        "coin_name": "Assemble",
        "coin_complete": False,
        "duty_ids": [str(test_duty.duty_id)]
    }

    response = client.post("/coins", json=coin_to_add )
    assert response.status_code == 201

    data = response.json()
    assert data["coin_name"] == "Assemble"

def test_for_no_duplicate_coins():
    with db:
        Coins.create(coin_name="Assemble", coin_complete=False)
    
    test_coin = {
        "coin_name": "Assemble",
        "coin_complete": False,
        "duty_ids": []
    }

    response = client.post("/coins", json=test_coin )
    assert response.status_code == 400

    data = response.json()
    assert "Coin name already exists" in data["detail"]


def test_for_updating_coin():
    with db:
        coin = Coins.create(coin_name="Assemble", coin_complete=False)
        coin_id = coin.coin_id

    update_coin = {
            "coin_name": "General Assemble",
            "coin_complete": True,
            "duty_ids": []
        }

    response = client.put(f"/coins/{coin_id}", json=update_coin)
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "coin updated successfully"

def test_seeds_data_successfully():
    seed_data()
    with db:
        assert Coins.select().count() > 0
        assert Duties.select().count() > 0

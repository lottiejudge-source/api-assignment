from fastapi.testclient import TestClient
from main import app
from peewee import SqliteDatabase
from database import db, Coins, Duties, JoinCoinsAndDuties
from seed import seed_data

test_db = SqliteDatabase(':memory:')
db.initialize(test_db)

client=TestClient(app)


def setup_module():
    with db:
        db.create_tables([Coins, Duties, JoinCoinsAndDuties], safe=True)
    
# wrapping the test set up in a function so I can call it at the top of the test suite for it to run everytime, otherwise I get the following error - failed: server closed the connection unexpectedly 
def set_up():
    with db:
        JoinCoinsAndDuties.delete().execute()
        Coins.delete().execute()
        Duties.delete().execute()

def test_for_hello():
    set_up()
    response = client.get("/")
    assert response.status_code == 200
    assert "The Coins" in response.text

    
# testing adding a coin
def test_for_coin():
    # calling test set up here 
    set_up()
    response = client.get("/coins")
    assert response.status_code == 200
    coins = response.json()
    assert isinstance(coins, list)
    

def test_for_adding_coins():
    set_up()
    with db:
        test_duty = Duties.create(
            duty_name="Duty 8",
            duty_description="Evolve and define architecture, utilising the knowledge and experience of the team to design in an optimal user experience, scalability, security, high availability and optimal performance."
            )
        

    coin_to_add = {
        "coin_name": "Test Coin",
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
    set_up()
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

def test_seeds_data_successfully():
    set_up()
    try:
        seed_data()
        seed_successful = True
    except Exception as error:
        seed_successful = False 
        print(f"seed failed wither error: {error}")

    assert seed_successful == True

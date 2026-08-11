import datetime
import pytest
import uuid
from fastapi.testclient import TestClient
from main import JWT_ALGORITHM, JWT_SECRET, app
from peewee import SqliteDatabase
from database import db, Coins, Duties, JoinCoinsAndDuties, Users, AuditLog, init_db
from seed import seed_data
import jwt

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
def get_admin_headers():
    """Generates a valid JWT bearer header for admin endpoints."""
    token_payload = {
        "user_id": "test-admin-id",
        "user_name": "admin_tester",
        "role": "admin",
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
    }
    token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return {"Authorization": f"Bearer {token}"}

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

    response = client.post("/coins", json=coin_to_add, headers=get_admin_headers())
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

    response = client.post("/coins", json=test_coin, headers=get_admin_headers())
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

    response = client.put(f"/coins/{coin_id}", json=update_coin, headers=get_admin_headers())
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "coin updated successfully"

def test_seeds_data_successfully():
    seed_data()
    with db:
        assert Coins.select().count() > 0
        assert Duties.select().count() > 0

def test_create_user():
    unique_name = f"Test User {uuid.uuid4().hex[:6]}"
    with db: 
        new_user = Users.create(
            user_name = unique_name,
            user_password = "hashed_very_secure_password",
            role = "admin"
        )

        added_user = Users.get(Users.user_name == unique_name)

        assert added_user.user_name == unique_name
        assert added_user.role == "admin"

def test_register_user():
    with db: 
        Users.delete().where(Users.user_name == "lottie_test").execute()

    payload = {
        "user_name": "lottie_test",
        "user_password": "not12345!",
        "role": "authorised"
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "User registered successfully"
    assert "user_id" in data

    with db:
        saved_user = Users.get(Users.user_name == "lottie_test")
        assert saved_user.user_password != "not12345!"


def test_create_HTTP_log():
    with db: 
        AuditLog.delete().execute()

    response = client.get("/")
    assert response.status_code == 200

    with db:
        latest_log = AuditLog.select().order_by(AuditLog.timestamp.desc()).first()

        assert latest_log is not None 
        assert latest_log.method == "GET"
        assert latest_log.path == "/"
        assert latest_log.status_code == 200 

# ensureing the login sends a JSON web token - safe way to pass info between user and server (loogin in basically)

def test_login_user_success():
    with db:
        Users.delete().where(Users.user_name == "login_tester").execute()

    client.post("/auth/register", json={    
        "user_name": "login_tester",
        "user_password": "SecurePassword123!",
        "role": "admin"
    })

    login_payload = {
        "user_name": "login_tester",
        "user_password": "SecurePassword123!"
    }
    response = client.post("/auth/login", json=login_payload)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    decoded = jwt.decode(data["access_token"], options={"verify_signature": False})
    assert decoded["user_name"] == "login_tester"
    assert decoded["role"] == "admin"

def test_login_user_invalid_credentials():
    login_payload = {
        "user_name": "login_tester",
        "user_password": "WrongPassword123!"
    }
    response = client.post("/auth/login", json=login_payload)
    assert response.status_code == 401
    # not telling users which is incorrect - safer code
    assert response.json()["detail"] == "Invalid username or password"


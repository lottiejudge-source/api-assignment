from database import db, init_db, AuditLog, Coins, Duties, JoinCoinsAndDuties, Users 
import bcrypt
import os
from schemas import CoinCreate, UserCreate
from fastapi import FastAPI, HTTPException, Response, Request
from fastapi.templating import Jinja2Templates
from uuid import UUID
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    os.getenv("ORIGIN_LOCAL_ONE"),  
    os.getenv("ORIGIN_LOCAL_TWO"),
    os.getenv("ADD FRONT END HERE")
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin for origin in origins if origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()

@app.middleware("http")
async def audit_logger(request: Request, call_next):
    response = await call_next(request)
    db.connect(reuse_if_open = True)
    try: 
        AuditLog.create(
            method = request.method,
            path = request.url.path,
            status_code = response.status_code
        )
    finally: 
        db.close()
    return response


@app.get("/")
def get_hello():
    data = """<!DOCTYPE html>
    <html>
    <h1>
        The Coins 
    </h1> 
    </html>"""
    return Response(content=data, media_type="text/html")

# decorator
@app.get("/coins")
# method
def get_coins():
    db.connect(reuse_if_open=True)

    coins_as_list=[]
    for coin in Coins.select():

        joins = JoinCoinsAndDuties.select().where(JoinCoinsAndDuties.coin == coin)
        
        duties_for_coin = []
        for join in joins:
            duty_info = {
                "duty_id": join.duty.duty_id,
                "duty_name": join.duty.duty_name,
                "duty_description": join.duty.duty_description
            }
            duties_for_coin.append(duty_info)

        coin_info = {
            "coin_id": coin.coin_id,
            "coin_name": coin.coin_name,
            "coin_complete": coin.coin_complete,
            "duties": duties_for_coin
        }
        coins_as_list.append(coin_info)
    db.close()
    return coins_as_list

@app.post("/coins", status_code=201)
def create_coin(payload: CoinCreate):
    db.connect(reuse_if_open=True)

# validation demonstraton 
    duplication_check = Coins.select().where(Coins.coin_name == payload.coin_name).exists()
    if duplication_check == True:
        db.close()
        raise HTTPException(status_code=400, detail="Coin name already exists")
    
    new_coin = Coins.create(
        coin_name = payload.coin_name, 
        coin_complete = payload.coin_complete
    )

    for duty_id in payload.duty_ids:
        duty = Duties.get(Duties.duty_id == duty_id)

        JoinCoinsAndDuties.create(coin=new_coin, duty=duty_id)

    db.close()
    return{"message": "Coin ceated successfully", "coin_id": new_coin.coin_id, "coin_name": new_coin.coin_name}

@app.put("/coins/{coin_id}")
def update_coin(coin_id: UUID, payload: CoinCreate):
    db.connect(reuse_if_open=True)

    coin = Coins.get(Coins.coin_id == coin_id)

    coin.coin_name = payload.coin_name
    coin.coin_complete = payload.coin_complete
    coin.save()

    remove_duties = JoinCoinsAndDuties.delete().where(JoinCoinsAndDuties.coin == coin)
    remove_duties.execute()

    for duty_id in payload.duty_ids: 
        JoinCoinsAndDuties.create(coin = coin, duty =duty_id )

    db.close()
    return {"message": "coin updated successfully"}

# decorator > method
@app.delete("/coins/{coin_id}")
def delete_coin(coin_id: UUID):
    db.connect(reuse_if_open=True)

    coin = Coins.get(Coins.coin_id == coin_id)

    remove_duties = JoinCoinsAndDuties.delete().where(JoinCoinsAndDuties.coin == coin)
    remove_duties.execute()

    coin.delete_instance()

    db.close()
    return {"message": "coin deleted successfully"}

@app.get("/coins/{coin_id}")
def get_coin_by_id(coin_id: UUID):
    db.connect(reuse_if_open=True)
    coin = Coins.get(Coins.coin_id == coin_id)

    joins = JoinCoinsAndDuties.select().where(JoinCoinsAndDuties.coin == coin)
        
    duties_for_coin = [
            {
            "duty_id": join.duty.duty_id,
            "duty_name": join.duty.duty_name,
            "duty_description": join.duty.duty_description
            } for join in joins
        ]
    db.close()
    return {
            "coin_id": coin.coin_id,
            "coin_name": coin.coin_name,
            "coin_complete": coin.coin_complete,
            "duties": duties_for_coin
    }

@app.post("/auth/register", status_code =201)
def register_user(payload: UserCreate):
    db.connect(reuse_if_open =True)
    try: 
        # dupe check - pen testing 
        if Users.select().where(Users.user_name == payload.user_name).exists():
            raise HTTPException(status_code=400, detail="Username already exists")
        password_bytes = payload.user_password.encode('utf-8')
        # 12 is industry standard to encryopt the password
        salt = bcrypt.gensalt(rounds=12) 
        hashed_password = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        new_user = Users.create(
            user_name=payload.user_name,
            user_password=hashed_password,
            role=payload.role
        )

        return {
            "message": "User registered successfully",
            "user_id": new_user.user_id
        }
    finally:
        db.close()
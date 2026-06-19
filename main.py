from database import db, init_db, Coins, Duties, JoinCoinsAndDuties
from schemas import CoinCreate
from typing import List
from fastapi import FastAPI, HTTPException, status
from uuid import UUID

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()


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
    return {"message": "coin update successfully"}

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
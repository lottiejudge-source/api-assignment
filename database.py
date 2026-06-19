from peewee import *
import os 
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()

db = PostgresqlDatabase(
    os.getenv("DB_NAME"),
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT", "5432")
)

class BaseModel(Model):
    class Meta:
        database = db
        schema = "coins"

class Coins(BaseModel):
    coin_id = UUIDField(primary_key=True, default=uuid4)
    coin_name = TextField()
    coin_complete = BooleanField(default=False)


class Duties(BaseModel):
    duty_id = UUIDField(primary_key=True, default=uuid4)
    duty_name = TextField()
    duty_description = TextField()

class JoinCoinsAndDuties(BaseModel):
    coin = ForeignKeyField(Coins)
    duty = ForeignKeyField(Duties)

def init_db():
    with db:
        db.create_tables([Coins, Duties, JoinCoinsAndDuties], safe=True)
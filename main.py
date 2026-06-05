from peewee import *
import os 
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI
from uuid import uuid4

app = FastAPI()
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

db.connect()

# @Dom - best practice is to remove the below, otherwise everytime a dev runs the app it'll remake everything
# but am leaving in commented to show my working 
# db.drop_tables([
#     JoinCoinsAndDuties,
#     Coins,
#     Duties
# ])

db.create_tables([
    Coins,
    Duties,
    JoinCoinsAndDuties
], safe=True)

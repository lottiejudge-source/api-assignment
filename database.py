from peewee import *
import os 
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()

db = Proxy()

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

class Users(BaseModel):
    user_id = UUIDField(primary_key=True, default=uuid4)
    user_name = TextField(unique=True)
    user_password = TextField()
    role = TextField()

class AuditLog(BaseModel):
    log_id = UUIDField(primary_key=True, default=uuid4)
    method = TextField()
    path = TextField()
    status_code = IntegerField()
    timestamp = DateTimeField(constraints =[SQL("DEFAULT CURRENT_TIMESTAMP")])
    
def init_db():
    real_db = PostgresqlDatabase(
        os.getenv("DB_NAME"),
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", "5432"))
    db.initialize(real_db)

    with db:
        db.execute_sql("CREATE SCHEMA IF NOT EXISTS coins;")
        db.create_tables([Coins, Duties, JoinCoinsAndDuties, Users, AuditLog], safe=True)
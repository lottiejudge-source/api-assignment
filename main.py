from database import db, init_db, AuditLog, Coins, Duties, JoinCoinsAndDuties, Users 
import bcrypt, datetime, jwt, os
from schemas import CoinCreate, UserCreate, UserLogin
from fastapi import Depends, FastAPI, HTTPException, Header, Response, Request
from fastapi.templating import Jinja2Templates
from uuid import UUID
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")

JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-key-change-in-prod")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

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

# adding in a least responsibility route for security here 
def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorisation header")

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(allowed_roles: list):
    """Role-based Access Control (RBAC) Dependency Factory."""
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(status_code=403, detail="Forbidden: Insufficient privileges")
        return current_user
    return role_checker

require_admin = require_role(["admin"])
require_authenticated = require_role(["authorised", "admin"])


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


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    coins = list(Coins.select())
    user = request.cookies.get("user") 
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={
            "title": "Lottie's Coins", 
            "coins": coins, 
            "user": user
        }
    )

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

@app.post("/coins", status_code=201, dependencies=[Depends(require_admin)])
def create_coin(payload: CoinCreate):
    db.connect(reuse_if_open=True)
    try:
        duplication_check = Coins.select().where(Coins.coin_name == payload.coin_name).exists()
        if duplication_check:
            raise HTTPException(status_code=400, detail="Coin name already exists")
        
        new_coin = Coins.create(
            coin_name=payload.coin_name, 
            coin_complete=payload.coin_complete
        )

        for duty_id in payload.duty_ids:
            JoinCoinsAndDuties.create(coin=new_coin, duty=duty_id)

        return {"message": "Coin created successfully", "coin_id": new_coin.coin_id, "coin_name": new_coin.coin_name}
    finally:
        db.close()

@app.put("/coins/{coin_id}", dependencies=[Depends(require_admin)])
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
@app.delete("/coins/{coin_id}", dependencies=[Depends(require_admin)])
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

# logging in etc 
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


# user logging in 
@app.post("/auth/login")
def login_user(payload: UserLogin):
    user_name = payload.user_name
    user_password = payload.user_password

    if not user_name or not user_password:
        raise HTTPException(status_code=400, detail="Username and password are required")

    db.connect(reuse_if_open=True)
    try:
        try:
            user = Users.get(Users.user_name == user_name)
        except Users.DoesNotExist:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        password_bytes = user_password.encode('utf-8')
        hashed_bytes = user.user_password.encode('utf-8')

        if not bcrypt.checkpw(password_bytes, hashed_bytes):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        token_payload = {
            "user_id": str(user.user_id),
            "user_name": user.user_name,
            "role": user.role,
            "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }

        token = jwt.encode(token_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        return {
            "access_token": token,
            "token_type": "bearer",
            "role": user.role
        }
    finally:
        db.close()

# admin logs route
@app.get("/admin/logs", dependencies=[Depends(require_admin)])
def get_admin_logs():
    db.connect(reuse_if_open=True)
    try:
        logs = AuditLog.select().order_by(AuditLog.timestamp.desc()).limit(100)
        return [
            {
                "id": log.id,
                "method": log.method,
                "path": log.path,
                "status_code": log.status_code,
                "timestamp": log.timestamp
            }
            for log in logs
        ]
    finally:
        db.close()
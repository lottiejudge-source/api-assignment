import os
import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

load_dotenv()

connection = psycopg.connect(
    host=os.getenv("DB_HOST"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT", "5432")
)

app = FastAPI()
templates=Jinja2Templates(directory="templates")

@app.get("/")
def read_root():
    return RedirectResponse("/welcome")

@app.get("/welcome", response_class=HTMLResponse)
def read_items(request: Request, name: str = "Taybah"):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"name": name}
    )

@app.get("/coins")
def get_coins():
    with connection.cursor() as cursor:
        cursor.execute("SELECT * from coins.coins")
        coins = cursor.fetchall()
        return coins
from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

connection=None 

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

@app.get("/dog", response_class=HTMLResponse)
def get_dogs():
    external_Url = "https://dog.ceo/api/breeds/image/random"
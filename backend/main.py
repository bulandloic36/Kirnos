from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI()

@app.get("/test")
def test():
    return {"kirnos": "ok"}

# chemins
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

# page accueil
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# page connexion
@app.get("/connect")
async def connect(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


# login
@app.post("/login")
async def login(username: str = Form(...)):
    return RedirectResponse("/dashboard", status_code=303)


# dashboard
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# logs live
@app.get("/live", response_class=PlainTextResponse)
def live():
    try:
        with open("data/live_logs.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "No logs"
    
    from fastapi import Form

users = {}

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    
    if username not in users:
        users[username] = password

    return RedirectResponse("/dashboard", status_code=303)


from fastapi.staticfiles import StaticFiles

app.mount("/", StaticFiles(directory=".", html=True), name="static")
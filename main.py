from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="kirnos")

# ===== FILES =====
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ===== DATA =====
bot_running = False

# ===== HOME =====
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ===== LOGIN FAKE =====
@app.get("/login/tiktok")
def login(request: Request):
    request.session["user"] = "user"
    return RedirectResponse("/dashboard")

# ===== LOGOUT =====
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")

# ===== DASHBOARD =====
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/login/tiktok")

    return templates.TemplateResponse("dashboard.html", {"request": request})

# ===== DOCUMENTATION =====
@app.get("/documentation", response_class=HTMLResponse)
def documentation(request: Request):
    return templates.TemplateResponse("docs.html", {"request": request})

# ===== FAQ =====
@app.get("/faq", response_class=HTMLResponse)
def faq(request: Request):
    return templates.TemplateResponse("faq.html", {"request": request})

# ===== SUPPORT =====
@app.get("/support", response_class=HTMLResponse)
def support(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})

# ===== BOT =====
@app.get("/bot/start")
def start():
    global bot_running
    bot_running = True
    return {"status": "on"}

@app.get("/bot/stop")
def stop():
    global bot_running
    bot_running = False
    return {"status": "off"}

@app.get("/bot/status")
def status():
    return {"running": bot_running}

# ===== LOGS =====
@app.get("/live", response_class=PlainTextResponse)
def live():
    try:
        with open("data/live_logs.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Aucun live"
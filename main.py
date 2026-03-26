from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import httpx
import subprocess
import os

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="kirnos")

# ===== CONFIG =====
CLIENT_KEY = "TA_CLIENT_KEY"
CLIENT_SECRET = "TA_SECRET"
DOMAIN = "http://127.0.0.1:8000"

# ===== FILES =====
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ===== DATA =====
processes = {}

# ===== HOME =====
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ===== LOGIN TIKTOK =====
@app.get("/login/tiktok")
def login_tiktok():
    url = (
        f"https://www.tiktok.com/v2/auth/authorize/"
        f"?client_key={CLIENT_KEY}"
        f"&response_type=code"
        f"&scope=user.info.basic"
        f"&redirect_uri={DOMAIN}/callback"
    )
    return RedirectResponse(url)

# ===== CALLBACK =====
@app.get("/callback")
async def callback(request: Request):

    code = request.query_params.get("code")

    async with httpx.AsyncClient() as client:

        token_res = await client.post(
            "https://open.tiktokapis.com/v2/oauth/token/",
            data={
                "client_key": CLIENT_KEY,
                "client_secret": CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": DOMAIN + "/callback"
            }
        )

        token_data = token_res.json()
        access_token = token_data.get("access_token")

        user_res = await client.get(
            "https://open.tiktokapis.com/v2/user/info/",
            headers={"Authorization": f"Bearer {access_token}"}
        )

        user_data = user_res.json()
        user = user_data["data"]["user"]

        request.session["user"] = user["display_name"]
        request.session["avatar"] = user["avatar_url"]

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

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": request.session.get("user"),
        "avatar": request.session.get("avatar")
    })

# ===== PAGES =====
@app.get("/documentation", response_class=HTMLResponse)
def documentation(request: Request):
    return templates.TemplateResponse("docs.html", {"request": request})

@app.get("/faq", response_class=HTMLResponse)
def faq(request: Request):
    return templates.TemplateResponse("faq.html", {"request": request})

@app.get("/support", response_class=HTMLResponse)
def support(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})

# ===== BOT CONTROL (PROCESS) =====
@app.get("/bot/start")
def start_bot(request: Request):

    user = request.session.get("user")

    if not user:
        return {"status": "error"}

    if user in processes:
        return {"status": "already_running"}

    # 🔥 lance bot.py avec le pseudo
    p = subprocess.Popen(["python", "bot.py"])
    processes[user] = p

    return {"status": "started"}

@app.get("/bot/stop")
def stop_bot(request: Request):

    user = request.session.get("user")

    if user in processes:
        processes[user].terminate()
        del processes[user]

    return {"status": "stopped"}

@app.get("/bot/status")
def status_bot(request: Request):

    user = request.session.get("user")

    if user in processes:
        return {"running": True}

    return {"running": False}

# ===== LOGS =====
@app.get("/live", response_class=PlainTextResponse)
def live():
    try:
        with open("data/live_logs.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Aucun live"
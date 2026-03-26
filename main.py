from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import httpx


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
    


import httpx

CLIENT_KEY = "TA_CLIENT_KEY"
CLIENT_SECRET = "TA_SECRET"

# LOGIN TIKTOK
@app.get("/login/tiktok")
def login():
    url = f"https://www.tiktok.com/v2/auth/authorize/?client_key={CLIENT_KEY}&response_type=code&scope=user.info.basic&redirect_uri={DOMAIN}/callback"
    return RedirectResponse(url)

# CALLBACK
@app.get("/callback")
async def callback(request: Request):

    code = request.query_params.get("code")

    async with httpx.AsyncClient() as client:
        token_res = await client.post("https://open.tiktokapis.com/v2/oauth/token/", data={
            "client_key": CLIENT_KEY,
            "client_secret": CLIENT_SECRET,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": DOMAIN + "/callback"
        })

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
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import stripe
import os

app = FastAPI()

# ==============================
# CONFIG GLOBAL
# ==============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_DIR = os.path.join(BASE_DIR, "data")
LOG_FILE = os.path.join(DATA_DIR, "live_logs.txt")

os.makedirs(DATA_DIR, exist_ok=True)

if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        f.write("[SYSTEM] Bot prêt...\n")

# ==============================
# SESSION
# ==============================
app.add_middleware(SessionMiddleware, secret_key="kirnos_secret")

# ==============================
# STRIPE
# ==============================
stripe.api_key = "sk_test_xxxxx"
DOMAIN = "http://127.0.0.1:8000"

# ==============================
# DATA
# ==============================
premium_users = {}
bot_status = {}
banned_users = []

# ==============================
# TEMPLATES & STATIC
# ==============================
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# ==============================
# HOME
# ==============================
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ==============================
# LOGIN
# ==============================
@app.get("/login/tiktok")
def login(request: Request):
    request.session["user"] = "user123"
    return RedirectResponse("/dashboard")

# ==============================
# LOGOUT
# ==============================
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")

# ==============================
# DASHBOARD
# ==============================
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    if "user" not in request.session:
        return RedirectResponse("/login/tiktok")

    user = request.session["user"]
    is_premium = premium_users.get(user, False)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "premium": is_premium
    })

# ==============================
# STRIPE PAIEMENT
# ==============================
@app.get("/buy/{plan}")
def buy(plan: str):

    prices = {
        "1m": 1000,
        "3m": 3000,
        "6m": 5000
    }

    if plan not in prices:
        return RedirectResponse("/dashboard")

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": f"Kirnos Premium {plan}"
                },
                "unit_amount": prices[plan],
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=DOMAIN + "/success",
        cancel_url=DOMAIN,
    )

    return RedirectResponse(session.url)

# ==============================
# SUCCESS
# ==============================
@app.get("/success")
def success(request: Request):
    user = request.session.get("user")

    if user:
        premium_users[user] = True

    return RedirectResponse("/dashboard")

# ==============================
# PAGES
# ==============================
@app.get("/documentation", response_class=HTMLResponse)
def docs_page(request: Request):
    return templates.TemplateResponse("docs.html", {"request": request})

@app.get("/faq", response_class=HTMLResponse)
def faq_page(request: Request):
    return templates.TemplateResponse("faq.html", {"request": request})

@app.get("/support", response_class=HTMLResponse)
def support_page(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})

# ==============================
# BOT CONTROL
# ==============================
@app.get("/bot/start")
def start_bot(request: Request):
    user = request.session.get("user")

    if not user:
        return JSONResponse({"error": "not logged"}, status_code=401)

    bot_status[user] = True
    return {"status": "started"}

@app.get("/bot/stop")
def stop_bot(request: Request):
    user = request.session.get("user")

    if not user:
        return JSONResponse({"error": "not logged"}, status_code=401)

    bot_status[user] = False
    return {"status": "stopped"}

@app.get("/bot/status")
def get_status(request: Request):
    user = request.session.get("user")

    if not user:
        return {"running": False}

    return {"running": bot_status.get(user, False)}

# ==============================
# BAN SYSTEM
# ==============================
@app.get("/ban/{username}")
def ban_user(username: str):

    if username not in banned_users:
        banned_users.append(username)

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[BAN] {username} a été banni\n")

    return {"status": "banned", "user": username}

# ==============================
# LIVE LOGS
# ==============================
@app.get("/live", response_class=PlainTextResponse)
def live():
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Erreur lecture logs"
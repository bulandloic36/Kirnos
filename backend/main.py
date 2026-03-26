from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import stripe
import os

app = FastAPI()

# ===== SESSION =====
app.add_middleware(SessionMiddleware, secret_key="kirnos_secret")

# ===== STRIPE =====
stripe.api_key = "sk_test_TA_CLE"
DOMAIN = "https://kirnos.onrender.com"  # 🔥 TON VRAI SITE

# ===== DATA =====
premium_users = {}
bot_status = {}
banned_users = []

# ===== PATH =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

# ===== HOME =====
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ===== LOGIN =====
@app.get("/login/tiktok")
def login(request: Request):
    request.session["user"] = "user123"
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

    user = request.session["user"]
    is_premium = premium_users.get(user, False)

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "premium": is_premium
    })

# ===== STRIPE =====
@app.get("/create-checkout-session/{plan}")
def create_checkout_session(plan: str):

    prices = {
        "1m": (1000, "Kirnos Premium - 1 mois"),
        "3m": (3000, "Kirnos Premium - 3 mois"),
        "6m": (5000, "Kirnos Premium - 6 mois")
    }

    if plan not in prices:
        return JSONResponse({"error": "plan invalide"})

    amount, name = prices[plan]

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {"name": name},
                "unit_amount": amount,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=DOMAIN + "/success",
        cancel_url=DOMAIN,
    )

    return JSONResponse({"url": session.url})

# ===== SUCCESS =====
@app.get("/success")
def success(request: Request):
    user = request.session.get("user")

    if user:
        premium_users[user] = True

    return RedirectResponse("/dashboard")

# ===== PAGES =====
@app.get("/documentation", response_class=HTMLResponse)
def docs_page(request: Request):
    return templates.TemplateResponse("docs.html", {"request": request})

@app.get("/faq", response_class=HTMLResponse)
def faq_page(request: Request):
    return templates.TemplateResponse("faq.html", {"request": request})

@app.get("/support", response_class=HTMLResponse)
def support_page(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})

# ===== BOT CONTROL =====
@app.get("/bot/start")
def start_bot(request: Request):
    user = request.session.get("user")

    if not user:
        return {"status": "error"}

    bot_status[user] = True
    return {"status": "started"}

@app.get("/bot/stop")
def stop_bot(request: Request):
    user = request.session.get("user")

    if not user:
        return {"status": "error"}

    bot_status[user] = False
    return {"status": "stopped"}

@app.get("/bot/status")
def get_status(request: Request):
    user = request.session.get("user")

    if not user:
        return {"status": "error"}

    return {"running": bot_status.get(user, False)}

# ===== BAN =====
@app.get("/ban/{username}")
def ban_user(username: str):
    banned_users.append(username)
    return {"status": "banned", "user": username}

# ===== LIVE LOGS =====
@app.get("/live", response_class=PlainTextResponse)
def live():
    try:
        with open("data/live_logs.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "Aucun live"
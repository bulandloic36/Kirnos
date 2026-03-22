from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import stripe

app = FastAPI()

# ===== SESSION =====
app.add_middleware(SessionMiddleware, secret_key="kirnos_secret")

# ===== STRIPE =====
stripe.api_key = "sk_test_TA_CLE"
DOMAIN = "http://127.0.0.1:8000"

# ===== DATA =====
premium_users = {}

# ===== TEMPLATES =====
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ===== HOME =====
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ===== LOGIN TIKTOK (FAKE) =====
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
@app.get("/buy/{plan}")
def buy(request: Request, plan: str):

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
                "product_data": {"name": "Kirnos Premium"},
                "unit_amount": prices[plan],
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=DOMAIN + "/success",
        cancel_url=DOMAIN,
    )

    return RedirectResponse(session.url)

# ===== SUCCESS =====
@app.get("/success")
def success(request: Request):
    user = request.session.get("user")

    if user:
        premium_users[user] = True

    return RedirectResponse("/dashboard")

# ===== DOCUMENTATION =====
@app.get("/documentation", response_class=HTMLResponse)
def docs_page(request: Request):
    return templates.TemplateResponse("docs.html", {"request": request})

# ===== FAQ =====
@app.get("/faq", response_class=HTMLResponse)
def faq_page(request: Request):
    return templates.TemplateResponse("faq.html", {"request": request})

# ===== SUPPORT =====
@app.get("/support", response_class=HTMLResponse)
def support_page(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})

    # ===== BOT STATE =====
bot_status = {}

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
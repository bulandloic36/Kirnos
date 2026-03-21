from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import os
import requests
import stripe

app = FastAPI()

# ===== SESSION =====
app.add_middleware(SessionMiddleware, secret_key="kirnos_secret")

# ===== STRIPE CONFIG =====
stripe.api_key = "sk_test_TA_CLE_STRIPE"  # ⚠️ MET TA VRAIE CLÉ

YOUR_DOMAIN = "https://kirnos.onrender.com"

# ===== CONFIG TIKTOK =====
CLIENT_KEY = "awon9ygf81kxe6sx"
CLIENT_SECRET = "uThXUV0H8COoccFKqeGVnHNw9IuU3aDV"
REDIRECT_URI = "https://kirnos.onrender.com/auth/callback"

# ===== PATH =====
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

# ===== TEST =====
@app.get("/force")
def force():
    return {"ok": "YES"}

# ===== HOME =====
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ===== LOGIN PAGE =====
@app.get("/connect", response_class=HTMLResponse)
async def connect(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# ===== LOGIN LOCAL =====
users = {}

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    users[username] = password
    return RedirectResponse("/dashboard", status_code=303)

# ===== DASHBOARD (PROTECTION) =====
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):

    if "user" not in request.session:
        return RedirectResponse("/login/tiktok")

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": request.session["user"]
    })

# ===== LOGOUT =====
@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/")

# ===== LIVE LOGS =====
@app.get("/live", response_class=PlainTextResponse)
def live():
    try:
        with open("data/live_logs.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "No logs"

# ===== STRIPE PAIEMENT =====
@app.get("/create-checkout-session/{plan}")
async def create_checkout_session(plan: str):

    plans = {
        "1m": {"amount": 1000, "name": "Kirnos Premium - 1 mois"},
        "3m": {"amount": 3000, "name": "Kirnos Premium - 3 mois"},
        "6m": {"amount": 5000, "name": "Kirnos Premium - 6 mois"},
    }

    if plan not in plans:
        return {"error": "plan invalide"}

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "eur",
                "product_data": {
                    "name": plans[plan]["name"],
                },
                "unit_amount": plans[plan]["amount"],
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=YOUR_DOMAIN + "/dashboard?success=true",
        cancel_url=YOUR_DOMAIN + "?cancel=true",
    )

    return JSONResponse({"url": session.url})

# ===== LOGIN TIKTOK =====
@app.get("/login/tiktok")
def login_tiktok():
    state = "kirnos123"

    url = (
        f"https://www.tiktok.com/auth/authorize/"
        f"?client_key={CLIENT_KEY}"
        f"&response_type=code"
        f"&scope=user.info.basic"
        f"&redirect_uri={REDIRECT_URI}"
        f"&state={state}"
    )

    return RedirectResponse(url)

# ===== CALLBACK TIKTOK =====
@app.get("/auth/callback")
def tiktok_callback(request: Request, code: str):

    token_url = "https://open.tiktokapis.com/v2/oauth/token/"

    data = {
        "client_key": CLIENT_KEY,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": REDIRECT_URI
    }

    response = requests.post(token_url, data=data)
    token_data = response.json()

    # 🔥 SAUVE SESSION
    request.session["user"] = token_data

    return RedirectResponse("/dashboard")
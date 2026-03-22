from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import stripe

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="kirnos_secret")

# ===== STRIPE =====
stripe.api_key = "sk_test_TA_CLE"
DOMAIN = "http://127.0.0.1:8000"

# ===== DATA =====
premium_users = {}

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ===== HOME =====
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ===== LOGIN TIKTOK (FAKE POUR TEST) =====
@app.get("/login/tiktok")
def login(request: Request):
    request.session["user"] = "user123"
    return RedirectResponse("/dashboard")

# ===== DASHBOARD =====
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):

    if "user" not in request.session:
        return RedirectResponse("/login/tiktok")

    user = request.session["user"]

    if user not in premium_users:
        return templates.TemplateResponse("login.html", {"request": request})

    return templates.TemplateResponse("dashboard.html", {"request": request})

# ===== STRIPE =====
@app.get("/buy/{plan}")
def buy(request: Request, plan: str):

    prices = {"1m": 1000, "3m": 3000, "6m": 5000}

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
    premium_users[user] = True
    return RedirectResponse("/dashboard")

    # ===== DOCUMENTATION =====
@app.get("/documentation", response_class=HTMLResponse)
async def docs_page(request: Request):
    return templates.TemplateResponse("docs.html", {"request": request})

# ===== FAQ =====
@app.get("/faq", response_class=HTMLResponse)
async def faq_page(request: Request):
    return templates.TemplateResponse("faq.html", {"request": request})

@app.get("/support", response_class=HTMLResponse)
async def support(request: Request):
    return templates.TemplateResponse("support.html", {"request": request})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if "user" not in request.session:
        return RedirectResponse("/login/tiktok")
    return templates.TemplateResponse("dashboard.html", {"request": request})
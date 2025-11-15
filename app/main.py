import os

from fastapi import FastAPI, Request, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.api import bookings, listings
from app.auth import optional_user


# FastAPI APP SETUP

app = FastAPI(title="Remote Servers Marketplace", version="0.3")

FRONTEND_ORIGIN = "https://remote-servers-marketplace-test.onrender.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_ORIGIN,
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers

app.include_router(listings.router, prefix="/api/v1/listings", tags=["listings"])
app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["bookings"])


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}



# STATIC + TEMPLATES

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
templates_dir = os.path.join(BASE_DIR, "frontend", "templates")
static_dir = os.path.join(BASE_DIR, "frontend", "static")

templates = Jinja2Templates(directory=templates_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# AUTH SESSION STORAGE ENDPOINT
class StoreSession(BaseModel):
    token: str


@app.post("/auth/store-session")
async def store_session(payload: StoreSession, response: Response):
    """
    Stores the Supabase JWT in an HttpOnly cookie
    so Jinja2-rendered pages know the logged-in user.
    """
    response.set_cookie(
        key="access_token",
        value=payload.token,
        httponly=True,
        secure=False,  # set True when using HTTPS
        samesite="lax",
        path="/"
    )
    return {"status": "ok"}


# PAGE ROUTES (JINJA2)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, user=Depends(optional_user)):
    return templates.TemplateResponse("index.html", {"request": request, "user": user})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, user=Depends(optional_user)):
    if user:
        return RedirectResponse("/")
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request, user=Depends(optional_user)):
    if user:
        return RedirectResponse("/")
    return templates.TemplateResponse("signup.html", {"request": request})


@app.get("/listings", response_class=HTMLResponse)
async def listings_page(request: Request, user=Depends(optional_user)):
    return templates.TemplateResponse("listings.html", {"request": request, "user": user})


@app.get("/bookings", response_class=HTMLResponse)
async def bookings_page(request: Request, user=Depends(optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("bookings.html", {"request": request, "user": user})


@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, user=Depends(optional_user)):
    if not user:
        return RedirectResponse("/login")
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user})


# LOGOUT (Clears Cookie)
@app.get("/logout")
async def logout():
    response = RedirectResponse("/")
    response.delete_cookie("access_token")
    return response
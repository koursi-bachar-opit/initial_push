from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.api import bookings, listings

# Main FastAPI application entrypoint
app = FastAPI(title="Remote Servers Marketplace", version="0.2")

# CORS (adjust when deploying full production frontend)
FRONTEND_ORIGIN = "https://remote-servers-marketplace-test.onrender.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_ORIGIN,
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ],
    #allow_origins=[FRONTEND_ORIGIN],    # hosted Render site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routers
app.include_router(listings.router, prefix="/api/v1/listings", tags=["listings"])
app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["bookings"])

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


# STATIC FRONTEND (MVP + scalable)

# Absolute path to /frontend directory
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")

# Serve entire frontend at root (/) — best for MVP & future development
app.mount(
    "/", 
    StaticFiles(directory=frontend_dir, html=True), 
    name="frontend"
)

# Note:
# html=True means:
#   - visiting "/" returns index.html
#   - unknown paths under "/" also return index.html (good for future SPA routing)


# from fastapi import FastAPI
# from app.api import bookings, listings
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse
# import os

# # Main FastAPI application entrypoint
# app = FastAPI(title="Remote Servers Marketplace", version="0.2")

# FRONTEND_ORIGIN = "https://remote-servers-marketplace-test.onrender.com"    #change to real site

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[FRONTEND_ORIGIN],   # allow Render site
#     allow_credentials=True,
#     allow_methods=["*"],               # allow all HTTP methods
#     allow_headers=["*"],               # allow all headers
# )

# # Include routers for modular endpoints
# app.include_router(listings.router, prefix="/api/v1/listings", tags=["listings"])
# app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["bookings"])

# @app.get("/api/v1/health")
# def health():
#     """Simple health-check endpoint used by CI/CD and uptime monitors."""
#     return {"status": "ok"}

# # Static Frontend Serving
# frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")

# # Serve the static folder (JS, CSS, images)
# app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# # Serve index.html when visiting root or unknown routes
# @app.get("/", include_in_schema=False)
# async def serve_index():
#     index_path = os.path.join(frontend_dir, "index.html")
#     return FileResponse(index_path)
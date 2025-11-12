from fastapi import FastAPI
from app.api import listings
from app.api import bookings

# Main FastAPI application entrypoint
app = FastAPI(title="Remote Servers Marketplace", version="0.2")

# Include routers for modular endpoints
app.include_router(listings.router, prefix="/api/v1/listings", tags=["listings"])
app.include_router(bookings.router, prefix="/api/v1/bookings", tags=["bookings"])

@app.get("/api/v1/health")
def health():
    """Simple health-check endpoint used by CI/CD and uptime monitors."""
    return {"status": "ok"}
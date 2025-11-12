from datetime import datetime, timedelta, timezone
from app.database import SessionLocal
from app import models

def run_seed():
    """
    Seed the database with initial demo data.
    This is safe to run locally or in CI (not for production).
    """
    db = SessionLocal()
    try:
        # Clean old data
        db.query(models.Booking).delete()
        db.query(models.Listing).delete()

        # Create demo listings
        listings = [
            models.Listing(title="High-Performance VPS - 8 Cores, 32GB RAM, Global Access", price=40),
            models.Listing(title="Budget Remote Server — Fast, Secure, Always On", price=25),
            models.Listing(title="GPU Server for AI & Rendering — Ready to Deploy", price=30),
        ]
        db.add_all(listings)
        db.commit()

        # Add a sample booking (3-hour confirmed session)
        start = datetime.now(timezone.utc)
        end = start + timedelta(hours=3)
        duration_hours = (end - start).total_seconds() / 3600
        price_per_hour = listings[0].price

        booking = models.Booking(
            listing_id=listings[0].id,
            buyer_name="demo_user",
            start_time=start,
            end_time=end,
            total_price_estimate=duration_hours * price_per_hour,
            status=models.BookingStatus.CONFIRMED,
        )

        db.add(booking)
        db.commit()
        print("Database seeded successfully!")
    except Exception as e:
        print("Seed failed:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
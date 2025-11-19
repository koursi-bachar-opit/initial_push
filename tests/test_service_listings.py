from app.services import listings_service
from app import schemas


def test_listings_service_delegates_to_repository(db_session):
    #create via service
    payload = schemas.ListingCreate(title="Service-level listing", price=7.5)
    created = listings_service.create_listing(db_session, payload)

    assert created.id is not None
    assert created.title == "Service-level listing"

    #list via service
    listings = listings_service.list_listings(db_session)
    assert any(l.id == created.id for l in listings)
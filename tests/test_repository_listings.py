from app.repositories import listing_repository
from app import schemas


def test_listing_repository_create_and_get(db_session):
    create_payload = schemas.ListingCreate(title="Repo GPU", price=9.5)
    created = listing_repository.create_listing(db_session, create_payload)

    assert created.id is not None
    assert created.title == "Repo GPU"
    assert created.price == 9.5

    #get_listing_by_id()
    fetched = listing_repository.get_listing_by_id(db_session, created.id)
    assert fetched is not None
    assert fetched.id == created.id

    #get_listings() should include
    all_listings = listing_repository.get_listings(db_session)
    ids = [l.id for l in all_listings]
    assert created.id in ids
from .service import ListingsService, get_listings_service

from fastapi import Depends
from typing import Protocol


class ListingsPublic(Protocol):
    """
    Public interface for interacting with the Listings domain.
    Other domains should use this instead of directly depending on
    listings.service or listings.repository.
    """
    def create_listing(self, provider_id, payload):
        ...

    def get_listing_by_id(self, listing_id):
        ...

    def search_listings_by_name(self, name: str):
        ...

    def list_listings(self):
        ...    

class ListingsPublicImpl:
    def __init__(self, service: ListingsService):
        self.service = service

    def create_listing(self, provider_id, payload):
        return self.service.create_listing(provider_id, payload)

    def get_listing_by_id(self, listing_id):
        return self.service.get_listing_by_id(listing_id)
    
    def search_listings_by_name(self, name: str):
        return self.service.search_listings_by_name(name)  #consider: customer search with metrics injected

    def list_listings(self):
        return self.service.list_listings()
    

def get_listings_public(
    service: ListingsService = Depends(get_listings_service),
) -> ListingsPublic:
    return ListingsPublicImpl(service)
def test_create_listing_as_provider(client):
    headers = {"Authorization": "Bearer provider:alice@example.com"}
    resp = client.post(
        "/api/v1/listings/",
        json={"title": "API GPU", "price": 12.5},
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "API GPU"
    assert body["price"] == 12.5


def test_list_listings_public(client):
    headers = {"Authorization": "Bearer provider:alice@example.com"}
    #ensure at least one
    client.post(
        "/api/v1/listings/",
        json={"title": "Public GPU", "price": 9},
        headers=headers,
    )

    resp = client.get("/api/v1/listings/")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(l["title"] == "Public GPU" for l in data)
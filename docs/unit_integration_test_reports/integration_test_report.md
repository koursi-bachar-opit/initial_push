# Integration Testing Report

## Overview
This integration testing report documents the comprehensive test suite for the remote servers marketplace. The tests validate the interaction between different modules and services, ensuring that the system components work together correctly as a whole. All integration tests were executed in a controlled test environment with isolated database transactions and mocked authentication.

## Testing Architecture

### Test Fixtures and Modularization
The integration testing suite employs a modular architecture using Pytest fixtures to manage test dependencies and ensure proper isolation:

- **Database Fixture**: Each test runs within an isolated database transaction using a session-scoped fixture that applies Alembic migrations and rolls back changes after each test, preventing test contamination.

- **Client Fixture**: A FastAPI TestClient fixture overrides the database dependency to use the test session, enabling HTTP request testing without affecting production data.

- **Factory Pattern**: Test data creation is abstracted through factory functions that generate consistent test objects (users, machines, listings, bookings) with minimal boilerplate.

### Factory Method Implementation
The test suite utilizes a factory pattern for test data creation, which provides several benefits:

1. **Consistency**: Factory functions like `create_machine`, `create_listing`, and `create_booking` generate valid test data with sensible defaults.

2. **Reusability**: Factories can be reused across multiple test files, reducing code duplication.

3. **Configuration Awareness**: Factory functions leverage centralized test configuration (`TestConfig`) for standardized test credentials and data.

4. **Dependency Management**: Factories handle the creation of dependent objects (e.g., creating a provider profile before creating a machine).

## Integration Test Categories

### 1. Authentication and Authorization Integration
Tests verify that the authentication system properly integrates with protected endpoints:

- **Role-Based Access Control**: Tests validate that different user roles (admin, provider, buyer) have appropriate access to endpoints.

- **Token Validation**: Integration between JWT token parsing and endpoint authorization is tested.

- **Cross-Role Protection**: Tests ensure providers cannot access other providers' resources
```python
def test_provider_cannot_access_other_providers_machine(client, db_session):
    """
    Provider cannot access machines belonging to other providers.
    """
    #Create machine with one provider
    machine = create_machine(client, db_session, provider_role="provider")
    
    #Try to access with a different provider
    from factories.users import create_user, auth_headers_for
    other_provider = create_user(db_session, "other@example.com", "provider")
    
    resp = client.get(
        f"/api/v1/machines/{machine['id']}/",
        headers=auth_headers_for("other@example.com", "provider")
    )
    assert_forbidden(resp)
```

---

### 2. Booking Lifecycle Integration
Tests validate the complete booking workflow across multiple system components:

- **State Transitions**: Tests verify the sequence of booking states from request to completion
```python
def test_full_booking_lifecycle_confirm_cancel(client, db_session):
    """
    Full booking lifecycle: request -> confirm -> cancel
    """
    api = ApiClient(client)

    #For this test we need the booking to be cancellable after confirmation.
    now = datetime.now(timezone.utc)
    start = now + timedelta(hours=2)
    end = start + timedelta(hours=1)

    booking = create_booking(
        client,
        db_session,
        start_time=start.isoformat(),
        end_time=end.isoformat(),
    )

    #Confirm booking
    response = api.put_booking_action(booking['id'], 'confirm', 'admin')
    assert_status_code(response, 200)
    assert_booking_status(response, 'confirmed')

    #Cancel booking  
    response = api.put_booking_action(booking['id'], 'cancel', 'admin')
    assert_status_code(response, 200)
    assert_booking_status(response, 'cancelled')
```

---

- **Usage Sessions**: Integration between booking management and session tracking is validated
```python
def test_booking_usage_session_start_and_end(client, db_session):
    """
    confirm -> start -> end
    """
    api = ApiClient(client)

    #For this test, we need to be able to start the session immediately.
    now = datetime.now(timezone.utc)
    start = now - timedelta(minutes=5)
    end = now + timedelta(hours=1)

    booking = create_booking(
        client,
        db_session,
        start_time=start.isoformat(),
        end_time=end.isoformat(),
    )

    #Confirm booking
    response = api.put_booking_action(booking['id'], 'confirm', 'admin')
    assert_status_code(response, 200)

    #Start session
    response = api.put_booking_action(booking['id'], 'start', 'provider')
    assert_booking_lifecycle_state(response, 'active', has_active_session=True)

    #End session
    response = api.put_booking_action(booking['id'], 'end', 'provider')
    assert_status_code(response, 200)
    assert_booking_status(response, 'completed')
    assert_response_contains(response, 'usage_seconds')
    assert_response_contains(response, 'actual_price_charged')
```

---

- **Cross-User Visibility**: Tests ensure buyers see their own bookings while providers see bookings for their machines.
```python
def test_request_booking_and_list_for_buyer_and_provider(client, db_session):
    """
    A buyer sees the bookings they made.
    A provider sees bookings for their machines.
    """
    api = ApiClient(client)
    booking = create_booking(client, db_session)

    #Buyer sees their booking
    response = api.get_bookings("buyer")
    assert_status_code(response, 200)
    assert_any_item_contains(response, "id", booking["id"])

    #Provider sees booking for their machine
    response = api.get_bookings("provider")
    assert_status_code(response, 200)
    assert_any_item_contains(response, "id", booking["id"])
```

### 3. Cross-Domain Integration (Payments & Compliance)
Tests validate interactions between bookings and other system domains:

- **Payment Integration**: Tests verify that booking actions trigger appropriate payment events.
```python
def test_escrow_created_on_booking_request(client, db_session):
    booking = create_booking(client, db_session)
    payments = _list_payments_for_booking(client, booking["id"], role="buyer")

    assert len(payments) == 1

    p = payments[0]
    assert p["type"] == "escrow"
    assert p["status"] == "authorized"
    assert str(p["booking_id"]) == booking["id"]
```

---

- **Compliance Integration**: Tests validate that booking completion triggers compliance requirements.
```python
def test_booking_completion_auto_generates_wipe_attestation(client, db_session):
    """Uses helper to ensure machine + listing + provider verification"""
    booking, listing, machine = create_booking_with_machine_and_listing(client, db_session)

    machine_id = machine["id"]
    api = ApiClient(client)

    # lifecycle
    api.put_booking_action(booking["id"], "confirm", role="admin")
    api.put_booking_action(booking["id"], "start", role="admin")

    # complete → triggers auto-wipe
    end_resp = api.put_booking_action(booking["id"], "end", role="admin")
    assert_status_code(end_resp, 200)

    # check wipe
    provider_headers = auth_headers_by_role("provider")
    atts_resp = client.get(
        f"{COMPLIANCE_BASE_URL}/machines/{machine_id}/attestations",
        headers=provider_headers,
    )
    assert_status_code(atts_resp, 200)

    items = atts_resp.json()
    assert len(items) >= 1
    assert items[0]["booking_id"] == booking["id"]
```

---

- **Provider Actions**: Tests verify providers can submit compliance attestations for their machines.
```python
def test_provider_can_submit_wipe_attestation_for_own_machine(client, db_session):
    booking, listing, machine = create_booking_with_machine_and_listing(client, db_session)

    machine_id = machine["id"]
    provider_headers = auth_headers_by_role("provider")
    payload = _create_wipe_attestation_payload(booking["id"], machine_id)

    # submit attestation
    resp = client.post(
        f"{COMPLIANCE_BASE_URL}/attestations",
        json=payload,
        headers=provider_headers,
    )
    assert_status_code(resp, 200)
    att = resp.json()

    assert att["booking_id"] == booking["id"]
    assert att["machine_id"] == machine_id
    assert att["method"] == payload["method"]

    # verify listing
    resp_list = client.get(
        f"{COMPLIANCE_BASE_URL}/machines/{machine_id}/attestations",
        headers=provider_headers,
    )
    assert_status_code(resp_list, 200)
    assert any(a["id"] == att["id"] for a in resp_list.json())
```

### 4. Resource Management Integration
Tests validate the integration between users, machines, and listings:

- **Provider-Verification Integration**: Tests ensure machine creation requires verified provider profiles.

- **Listing Creation Flow**: Tests validate the integration between provider authentication and listing creation.
```python
def test_create_listing_as_provider(client, db_session):
    """
    A provider can create a listing.
    """
    listing = create_listing(client, db_session, provider_role="provider")
    
    assert listing["title"] == TestConfig.DEFAULT_LISTING_TITLE
    assert listing["hourly_price"] == TestConfig.DEFAULT_LISTING_PRICE
```

---

- **Public Access**: Tests verify that public endpoints properly display available listings.
```python
def test_list_listings_public(client, db_session):
    """
    The public show listings endpoint works.
    """
    api = ApiClient(client)
    create_listing(client, db_session)

    resp = client.get("/api/v1/listings/")
    assert_status_code(resp, 200)
    assert_is_list(resp)

    data = resp.json()
    assert any(item.get('listing', {}).get('title') == TestConfig.DEFAULT_LISTING_TITLE 
               for item in data), \
        f"No listing found with title = {TestConfig.DEFAULT_LISTING_TITLE}"
```

### 5. API Client Integration
Tests validate the custom API client wrapper integration:

- **Endpoint Consistency**: The `ApiClient` class provides consistent URL construction and authentication.

- **Common Operations**: Wrapper methods simplify common test operations like booking actions.

## Test Examples

### Cross-Domain Workflow Integration
```python
def test_booking_can_complete_after_wipe_attestation_exists(client, db_session):
    """Uses helper to guarantee valid machine/listing + verified provider"""
    booking, listing, machine = create_booking_with_machine_and_listing(client, db_session)

    machine_id = machine["id"]
    api = ApiClient(client)

    api.put_booking_action(booking["id"], "confirm", role="admin")
    api.put_booking_action(booking["id"], "start", role="admin")

    provider_headers = auth_headers_by_role("provider")

    payload = {
        "booking_id": booking["id"],
        "machine_id": machine_id,
        "method": "secure-erase",
        "evidence_uri": "mock://manual/att.log",
        "notes": "Provider submitted manually",
    }
    att_resp = client.post(
        f"{COMPLIANCE_BASE_URL}/attestations",
        json=payload,
        headers=provider_headers,
    )
    assert_status_code(att_resp, 200)

    end_resp = api.put_booking_action(booking["id"], "end", role="admin")
    assert_status_code(end_resp, 200)

    final = end_resp.json()
    assert final["status"].lower() in ("completed", "complete")
```
- Validates the workflow integration between compliance submissions and booking completion.

---

### Health Check Integration
```python
def test_health_endpoint(client):
    """
    This test ensures that the API health endpoint
    responds with an okay status.
    """
    resp = client.get("/api/v1/health/")
    assert_status_code(resp, 200)
    body = resp.json()
    assert body.get("status") == "ok"
```
- Validates that the system health endpoint properly reports operational status.

---

### Administrative Integration
```python
def test_admin_create_booking_endpoint(client, db_session):
    """
    An admin member can manually create a booking with buyer_user_id.
    """
    api = ApiClient(client)
    
    #Create users using config-based helpers
    admin = create_user_by_role(db_session, "admin")
    buyer = create_user_by_role(db_session, "buyer")
    
    listing = create_listing(client, db_session)

    payload = booking_payload(listing_id=listing["id"], buyer_user_id=str(buyer.id))

    resp = client.post(
        "/api/v1/bookings/",
        json=payload,
        headers=auth_headers_by_role("admin"),
    )
    assert_status_code(resp, 201)
```
- Validates that administrative functions can create bookings on behalf of users.

---

### Error Condition Integration
```python
def test_get_nonexistent_machine_returns_404(client, db_session):
    """
    Getting a non-existent machine returns a 404 error.
    """
    resp = client.get(
        "/api/v1/machines/999999/",  #This machine ID doesn't exist
        headers=auth_headers_by_role("provider")
    )
    assert_status_code(resp, 404)
```
- Validates proper error handling for non-existent resources.

---

### Authentication Flow Integration
```python
def test_auth_blocks_missing_token_on_protected_endpoint(client, db_session):
    payload = valid_listing_payload(client, db_session)
    resp = client.post("/api/v1/listings/", json=payload)
    assert_unauthorized(resp)
```
- Validates that authentication properly blocks unauthorized access.

---

## Test Results Summary

### Execution Statistics
- **Test Coverage**: Cross-domain integration across bookings, payments, compliance, users, machines, and listings
- **Success Rate**: 100% of tests pass in isolated test environment

### Key Findings
1. **Positive Results**: All core integration points function correctly with proper data flow between domains.

2. **State Management**: Booking state transitions properly trigger corresponding actions in payment and compliance domains.

3. **Access Control**: Role-based authentication integrates correctly with resource ownership validation.

4. **Error Handling**: Integration points properly propagate and handle error conditions.

## Recommendations

### For Development
1. **Expand Test Coverage**: Add integration tests for edge cases in payment processing and compliance workflows.

2. **Performance Testing**: Consider adding integration tests for concurrent booking requests.

3. **Monitoring Integration**: Add tests for integration with logging and monitoring systems.

### For Deployment
1. **Environment Validation**: Ensure test configuration matches production environment variables.

2. **Database Migration Testing**: Add integration tests for backward-compatible schema changes.

3. **Third-Party Service Integration**: Expand tests for external payment gateway and compliance service integrations.

## Conclusion
The integration test suite successfully validates the critical integration points between system components. The modular test architecture using fixtures and factories provides maintainable, reliable tests that can evolve with the application. All core business workflows have been validated through integration testing, ensuring that the system functions correctly as a cohesive whole.
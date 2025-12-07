# User Stories – Remote Servers Marketplace (Refined for MVP Simulation)

## Overview
This document contains **user stories** for the Remote Servers Marketplace project.
The stories are based on the findings from stakeholder interviews and aim to describe system behavior in terms of user needs and expected outcomes.
**Note:** As this is an MVP simulation, "provisioning," "wiping," and "metrics" refer to the logic and database state transitions, not physical hardware manipulation.

---

## Functional User Stories

### Buyer Stories

1.  **Search and Filtering**
    *   As a Buyer, I want to search for servers by title and see their current activity metrics so that I can find machines that match my workload.
    *   **Acceptance Criteria:**
        *   The `/api/v1/listings/search/{name}` endpoint returns a JSON list of listings matching the title.
        *   Each listing result includes a `latest_metrics` object containing `cpu_util` and `gpu_util` (simulated/ingested data).
        *   The frontend "Listings" tab updates the grid dynamically without a page reload when a search term is entered.

2.  **Benchmark Transparency**
    *   As a Buyer, I want to see published benchmark results for each server so that I can compare performance before booking.
    *   **Acceptance Criteria:**
        *   The `/api/v1/benchmarks/machines/{id}` endpoint returns a list of `MachineBenchmark` objects (e.g., "Geekbench", "Score: 9000").
        *   Clicking "View Details" on a listing card opens a modal that displays these benchmark scores if available.

3.  **Booking and Access (Credentials)**
    *   As a Buyer, I want to receive SSH key and VPN configuration details when my session starts so that I can simulate accessing the machine.
    *   **Acceptance Criteria:**
        *   When a booking transitions to the `ACTIVE` state (via `PUT /bookings/{id}/start`), the system automatically creates an `AccessCredential` record.
        *   The `AccessCredential` contains a generated mock `vpn_config_uri` (e.g., `s3://mock-agent/...`) and an `ssh_public_key_fingerprint`.
        *   The Buyer Dashboard displays a "Download VPN" link or button for Active bookings, which is hidden for Requested or Completed bookings.

4.  **Data Security (Simulated Wiping)**
    *   As a Buyer, I want assurance that servers are "wiped" after each booking so that my data remains private.
    *   **Acceptance Criteria:**
        *   When a booking transitions to `COMPLETED` (via `PUT /bookings/{id}/end`), the system triggers `ComplianceService.simulate_wipe_for_booking`.
        *   A `WipeAttestation` record is created in the database linked to that booking ID.
        *   Admins can view this attestation via the `/api/v1/compliance/attestations` endpoint to verify the cleanup "occurred."

5.  **Institutional Purchasing**
    *   As a University or Research Center Buyer, I want an invoice generated for my organization's usage so that I can process payment.
    *   **Acceptance Criteria:**
        *   The `InvoiceService` can generate an invoice for a specific `organization_id` and date range.
        *   The invoice total is calculated by aggregating the `actual_price_charged` of all `COMPLETED` bookings for that organization within the period.
        *   The generated invoice status starts as `PENDING` and can be finalized by an Admin.

---

### Provider Stories

6.  **Server Listing**
    *   As a Provider, I want to list my machines with pricing so that buyers can book them.
    *   **Acceptance Criteria:**
        *   The "Create Listing" modal is only accessible if the user has created at least one Machine.
        *   Submitting the form POSTs to `/api/v1/listings/` and creates a `Listing` record linked to the selected `machine_id`.
        *   The listing immediately appears in the "My Listings" tab on the dashboard.

7.  **Onboarding and Verification**
    *   As a Provider, I want to complete a verification process so that I am allowed to create listings.
    *   **Acceptance Criteria:**
        *   A new Provider user has a `ProviderProfile` with `verification_status="pending"`.
        *   The `/api/v1/listings/` creation endpoint rejects requests (HTTP 403) if the status is not `verified`.
        *   An Admin can use the Dashboard "Provider Management" tab to click "Verify," which updates the status to `verified` via the API.

8.  **Metrics and Monitoring**
    *   As a Provider, I want my servers to report uptime and GPU usage so that buyers can trust reliability.
    *   **Acceptance Criteria:**
        *   The system accepts POST requests to `/api/v1/metrics/machines/{id}/ingest` (simulating an on-premise agent).
        *   These metric samples are persisted in the `metric_samples` table.
        *   The API validates that the authenticated user actually owns the machine before accepting metrics.

9.  **Payments and Payouts**
    *   As a Provider, I want guaranteed payment authorization before a session starts so that I have financial security.
    *   **Acceptance Criteria:**
        *   When a booking is created (`REQUESTED`), a `Payment` record of type `ESCROW` is created with status `AUTHORIZED` (mocked Stripe intent).
        *   When a booking is `COMPLETED`, the system triggers `capture_for_booking`, updating the payment status to `CAPTURED`.

---

### Admin Stories

10. **Provider Verification**
    *   As an Admin, I want to view a list of pending providers and approve/reject them so that the platform maintains trust.
    *   **Acceptance Criteria:**
        *   The Admin Dashboard renders a list of providers fetched from `/api/v1/providers/admin/providers`.
        *   Clicking "Verify" sends a request to `/api/v1/providers/verification/{id}/review`, updating the provider's ability to create listings.

11. **Dispute Resolution**
    *   As an Admin, I want tools to resolve disputes between buyers and providers so that platform integrity is maintained.
    *   **Acceptance Criteria:**
        *   Admins can view disputes with status `OPEN` or `IN_REVIEW`.
        *   Admins can POST to `/api/v1/disputes/{id}/resolve` with a decision (`refund` or `deny`).
        *   A `refund` decision automatically triggers a refund transaction in the `PaymentService`.

---

## Non-Functional User Stories

15. **Security (Role-Based Access Control)**
    *   As a System, I want to ensure users can only access their own data so that privacy is enforced.
    *   **Acceptance Criteria:**
        *   API endpoints use dependency injection (`get_current_user`) to validate the JWT token.
        *   A Provider cannot view bookings for machines they do not own (HTTP 403).
        *   A Buyer cannot view credentials for a booking that belongs to another user (HTTP 403).

16. **Reliability (Database Integrity)**
    *   As a Developer, I want the system to prevent invalid state transitions so that data remains consistent.
    *   **Acceptance Criteria:**
        *   A booking cannot be moved to `ACTIVE` unless it is currently `CONFIRMED`.
        *   A listing cannot be created for a machine ID that does not exist (Foreign Key constraint or Service check).

17. **Usability**
    *   As a User, I want the interface to provide visual feedback so that I know the status of my actions.
    *   **Acceptance Criteria:**
        *   Status badges (e.g., "Confirmed", "Active", "Completed") are color-coded in the Bookings Dashboard.
        *   Forms (Login, Signup, Create Listing) display error messages returned by the API (e.g., "Invalid credentials", "Provider not verified") directly on the UI.
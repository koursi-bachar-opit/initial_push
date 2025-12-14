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
    *   **Acceptance Criteria:** Buyers can see a list of server listings with attached activity metrics like CPU and GPU utilization.

2.  **Benchmark Transparency**
    *   As a Buyer, I want to see published benchmark results for each server so that I can compare performance before booking.
    *   **Acceptance Criteria:** Clicking the "Benchmarks" badge or "View Details" on a listing displays the associated benchmark scores.

3.  **Booking and Access (Credentials)**
    *   As a Buyer, I want to receive SSH key and VPN configuration details when my session starts so that I can simulate accessing the machine.
    *   **Acceptance Criteria:** Buyers can see a "Download VPN" link and view VPN/SSH key credentials attached to their active bookings in their dashboard.

4.  **Data Security (Simulated Wiping)**
    *   As a Buyer, I want assurance that servers are "wiped" after each booking so that my data remains private.
    *   **Acceptance Criteria:** A wipe attestation record is created upon booking completion, and buyers can see a verification that the wipe occurred.

5.  **Institutional Purchasing**
    *   As a University or Research Center Buyer, I want an invoice generated for my organization's usage so that I can process payment.
    *   **Acceptance Criteria:** Buyers belonging to an organization can see invoices generated for the completed bookings made under that organization.

---

### Provider Stories

6.  **Server Listing**
    *   As a Provider, I want to list my machines with pricing so that buyers can book them.
    *   **Acceptance Criteria:** Providers can publish listings with pricing, and these listings are displayed on the marketplace.

7.  **Onboarding and Verification**
    *   As a Provider, I want to complete a verification process so that I am allowed to create listings.
    *   **Acceptance Criteria:** Providers can apply for verification after creating an account, which is required before creating listings.

8.  **Metrics and Monitoring**
    *   As a Provider, I want my servers to report uptime and GPU usage so that buyers can trust reliability.
    *   **Acceptance Criteria:** Providers can have their machines report metrics, which are ingested and stored by the system.

9.  **Payments and Payouts**
    *   As a Provider, I want guaranteed payment authorization before a session starts so that I have financial security.
    *   **Acceptance Criteria:** A payment must be successfully authorized before a booking request can be created.

---

### Admin Stories

10. **Provider Verification**
    *   As an Admin, I want to view a list of pending providers and approve/reject them so that the platform maintains trust.
    *   **Acceptance Criteria:** Admins see a list of provider verification requests in the dashboard and can approve or deny them.

11. **Dispute Resolution**
    *   As an Admin, I want tools to resolve disputes between buyers and providers so that platform integrity is maintained.
    *   **Acceptance Criteria:** Admins can see a list of open disputes and resolve them directly from the admin dashboard.

---

## Non-Functional User Stories

15. **Security (Role-Based Access Control)**
    *   As a System, I want to ensure users can only access their own data so that privacy is enforced.
    *   **Acceptance Criteria:** Authorization is enforced at all API endpoints and reinforced in the service layer logic.

16. **Reliability (Database Integrity)**
    *   As a Developer, I want the system to prevent invalid state transitions so that data remains consistent.
    *   **Acceptance Criteria:** All booking and payment state transitions are strictly enforced according to defined business rules.

17. **Usability**
    *   As a User, I want the interface to provide visual feedback so that I know the status of my actions.
    *   **Acceptance Criteria:** UI elements are interactive, provide clear feedback, and are intuitive for users.
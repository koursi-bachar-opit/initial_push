# User Acceptance Test Cases – Remote Servers Marketplace

**Stakeholder:** Stakeholders Team, Group 4  
**Week:** Final Week – Testing and Deployment  
**Scope:** UAT test cases with all functionalities confirmed

| Test Case ID | Title | Steps | Expected Result | Status |
|--------------|-------|-------|------------------|--------|
| UAT-001 | Buyer Registration for Machine | 1. Open home page <br> 2. Navigate to “Listings” <br> 3. Click “Apply” on one listing <br> 4. Enter personal details <br> 5. Submit application | Application is sent, user receives confirmation link or status | ☑️ |
| UAT-002 | Provider Applies for Verification | 1. Log in as provider <br> 2. Go to “Profile” <br> 3. Click “Request Verification” <br> 4. Fill necessary info <br> 5. Submit request | Verification request submitted, status shown | ☑️ |
| UAT-003 | Admin Approves Provider | 1. Log in as admin <br> 2. Navigate to “Verification Requests” <br> 3. Click “Approve” on pending provider <br> 4. Confirm action | Provider is verified, reflected in their profile | ☑️ |
| UAT-004 | Booking a Machine | 1. Browse listings <br> 2. Select a machine <br> 3. Choose duration and specs <br> 4. Click “Book Now” <br> 5. Proceed to payment | Booking confirmation shown, backend receives request | ☑️ |
| UAT-005 | Payment Integration via Stripe | 1. Book a machine <br> 2. Redirected to payment <br> 3. Enter Stripe test card info <br> 4. Submit payment | Success message shown, mock Stripe adapter logs transaction | ☑️ |
| UAT-006 | Cancel Booking via Link | 1. Open email with cancel link <br> 2. Click on link <br> 3. Confirm cancellation | Booking is cancelled, status is updated in database | ☑️ |
| UAT-007 | Dashboard Overview for Admin | 1. Open Dashboard <br> 2. View all current bookings, users, machines <br> 3. Filter by date/type | All data loads properly, filters apply | ☑️ |
| UAT-008 | Provider Adds a New Machine | 1. Log in as provider <br> 2. Go to “My Machines” <br> 3. Click “Add Machine” <br> 4. Fill form, attach specs <br> 5. Submit | Machine is listed and pending approval | ☑️ |
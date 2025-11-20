# User Acceptance Testing (UAT) Report
_Remote Servers Marketplace – Core Feature Validation (Part 3)_

This report documents the User Acceptance Testing (UAT) performed on the remote servers marketplace application as part of Part 3 of the Intro to Software Engineering project. The goal of UAT is to validate that implemented core features function as intended, meet user and business requirements, and support the essential marketplace workflows for providers and buyers.

---

## 1. Scope of Testing
User acceptance testing focused exclusively on the **core functionality implemented**, as defined in the project requirements and confirmed through stakeholder feedback:

### Provider Features
- Create an account
- Add a machine
- Create a listing
- Publish a listing
- Log out

### Buyer Features
- Log in
- Browse published server listings
- Book a server
- View current bookings
- Cancel a booking

> Source for validated features:
> [Stakeholder Feedback](stakeholder-feedback.md)

---

## 2. UAT Methodology
The following approach was used:

### 2.1 Test Environment
- Local development environment running the marketplace application
- Fresh account created for provider functions
- Previously registered account used for buyer functions
- Browser-based manual UAT with visual verification via screenshots

### 2.2 Testing Technique
- **Scenario‑based testing** using real workflows
- **Positive and negative path testing**, including error handling (e.g., wrong credentials)
- **State validation** before and after user actions (e.g., booking creation and cancellation)

### 2.3 Acceptance Criteria
A feature was marked as Pass if:
- It performed the required action end‑to‑end
- It enforced expected validations and error messages
- The system entered a correct and consistent state
- It matched user and business requirements

---

## 3. Test Scenarios and Results
Each scenario below includes the test purpose, expected result, actual result, and pass/fail status.

### 3.1 Provider Registration
**Purpose:** Ensure a provider can successfully create a new account.
- **Expected Result:** Valid account is created and redirected to provider dashboard.
- **Actual Result:** Successful registration; dashboard displays provider options.
- **Status:** Pass

**Negative Path:** Attempt registration with an existing account.
- **Expected Result:** Error message indicating user already registered.
- **Actual Result:** Clear red-text error, form blocked.
- **Status:** Pass

---

### 3.2 Add Machine
**Purpose:** Validate that providers can register a machine in the system.
- **Expected Result:** Machine form accepts inputs. The new machine appears in provider dashboard.
- **Actual Result:** Machine added successfully, confirmation is displayed.
- **Status:** Pass

---

### 3.3 Create and Publish Listing
**Purpose:** Ensure providers can access created machines in listings forms and publish them.
- **Expected Result:** Listing accepts title, price, and machine selection, then appears in marketplace.
- **Actual Result:** Listing created and published; buyers can view it.
- **Status:** Pass

---

### 3.4 Provider Logout
**Purpose:** Validate session termination and redirection.
- **Expected Result:** Provider session ends and user returns to homepage.
- **Actual Result:** Logout works as expected.
- **Status:** Pass

---

### 3.5 Buyer Login
**Negative Path Test:** Incorrect credentials.
- **Expected Result:** Login blocked, error message displayed.
- **Actual Result:** "Invalid login credentials" shown.
- **Status:** Pass

**Positive Path Test:** Valid credentials.
- **Expected Result:** Redirect to homepage or dashboard.
- **Actual Result:** Successful login.
- **Status:** Pass

---

### 3.6 Browse Listings
**Purpose:** Ensure buyers can access all published listings.
- **Expected Result:** Listings appear with accurate details.
- **Actual Result:** Listings display correctly.
- **Status:** Pass

---

### 3.7 Book a Server
**Purpose:** Validate booking functionality.
- **Expected Result:** Booking successfully recorded and visible in buyer dashboard.
- **Actual Result:** Booking request processed; confirmation dialog displayed.
- **Status:** Pass

---

### 3.8 View Current Booking
**Purpose:** Verify that buyers can track their active bookings.
- **Expected Result:** Booking appears with status and listing details.
- **Actual Result:** Booking shows correctly under pending bookings.
- **Status:** Pass

---

### 3.9 Cancel Booking
**Purpose:** Validate that buyers can cancel bookings and that the system updates state.
- **Expected Result:** System prompts confirmation and marks booking as cancelled.
- **Actual Result:** Cancellation confirmed; booking shows status "cancelled".
- **Status:** Pass

---

## 4. Issues Discovered
Although all core features met acceptance requirements, the following issues and improvement opportunities were identified during UAT:

### 4.1 UI Feedback and Confirmation Mechanisms
**Observation:** Several actions rely on basic JavaScript alert dialogs.
**Impact:** Alerts provide minimal UX clarity and do not match modern UI expectations.
**Recommendation:** Replace alerts with styled modal components to improve clarity and visual consistency.

### 4.2 Listing Search and Filtering
**Observation:** Buyers must manually scan all listings.
**Impact:** Decreases efficiency as listing volume grows.
**Recommendation:** Add search, filter, and sort capabilities.

### 4.3 Provider Dashboard Enhancements
**Observation:** Dashboard displays core controls but lacks operational analytics.
**Recommendation:** Add indicators such as listing status, availability, booking history, or performance metrics.

### 4.4 Validation and Form UX Improvements
**Observation:** While validation is functional, some fields could show inline feedback.
**Recommendation:** Include real-time validation messages, especially for pricing, title, and email inputs.

---

## 5. Summary of UAT Outcomes
All core features implemented in Part 3 successfully passed UAT and meet the essential business requirements for the marketplace:
- Provider listing workflow functions end‑to‑end
- Buyer booking workflow completes reliably
- Error-handling is predictable and informative
- System state updates correctly for all key operations

These results validate the readiness of the core system and provide a strong foundation for the advanced features and refinements planned for Part 4.

---

## 6. Approval
Based on the testing conducted and the successful results, the core feature implementation for Part 3 is **accepted** pending enhancement work scheduled for the next development phase.
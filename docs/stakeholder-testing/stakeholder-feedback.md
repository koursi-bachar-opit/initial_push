# Stakeholder Feedback Report
_Remote Servers Marketplace – Part 3 (Core Features)_

This document summarizes the stakeholder feedback on the implemented core features of the remote servers marketplace. As Part 3 focuses on core functionality, each section below addresses whether the implemented features meet user needs and business requirements. Each feedback section references the testing steps and includes screenshots as visual aids.

---

## 1. Overview of Core Features Evaluated
Stakeholders tested the following implemented features:
- **Provider functions:** Sign up, create a machine, create a listing, publish listing, logout.
- **Buyer functions:** Log in, browse listings, book a server, view booking, cancel booking.

These features represent the essential workflow of the marketplace and were validated through guided interaction steps.

---

## 2. Testing Steps & Visual Evidence
Below is a step-by-step breakdown with space for screenshots.

### 2.1 Go to Homepage
- Stakeholder navigates to the landing page.
- Page loads correctly, displays company information, and provides navigation text for sign‑up and login.

**Screenshot:**
```
![Homepage](images/homepage.png)
```

---

### 2.2 Sign Up With Existing Provider Account (Error Expected)
- Attempting to create an account with the credentials of an already-registered provider triggers error handling.
- Error message was visible with a "User already registered" red text display and prevented duplicate accounts.

**Screenshot:**
```
![Signup Existing Error](images/signup-existing-error.png)
```

---

### 2.3 Sign Up With New Provider Account
- New account creation succeeded.
- Form validation worked as expected.
- Account type selection accepted an input.

**Screenshot:**
```
![Signup New Provider](images/signup-new-1.png)
![Signup New Provider - Successful](images/signup-new-2.png)
```

---

### 2.4 Navigate to Provider Dashboard
- Successful redirect after sign‑up.
- Dashboard clearly lists foundational booking statistics.
- Clearly labeled provider action buttons are displayed.

**Screenshot:**
```
![Provider Dashboard](images/provider-dashboard.png)
```

---

### 2.5 Add Machine
- Stakeholder was able to add a machine resource.
- Hostname input requirement accepted.

**Screenshot:**
```
![Add Machine](images/add-machine-1.png)
![Add Machine - Confirmation](images/add-machine-2.png)
```

---

### 2.6 Create Listing
- Listing form "Machine" field successfully loaded previously added machine.
- Title and price fields were accepted.

**Screenshot:**
```
![Create Listing](images/create-listing.png)
```

---

### 2.7 Publish / List the Listing
- JavaScript dialog box confirms successful listing.
- Publishing workflow is intuitive.

**Screenshot:**
```
![Publish Listing](images/publish-listing.png)
```

---

### 2.8 Provider Logout
- Logout successfully invalidates session and redirects back to homepage.

**Screenshot:**
```
![Provider Logout](images/provider-logout.png)
```

---

### 2.9 Buyer Login With Wrong Credentials (Error Expected)
- Incorrect login attempt returned an "Invalid login credentials" error in red text.
- Messaging was clear and user‑friendly.

**Screenshot:**
```
![Buyer Login Error](images/buyer-login-error.png)
```

---

### 2.10 Buyer Login With Correct Credentials
- Buyer successfully logged in.
- Redirects back to the home page.

**Screenshot:**
```
![Buyer Login Success](images/buyer-login-success-1.png)
![Buyer Login Success - Successful](images/buyer-login-success-2.png)
```

---

### 2.11 Browse Server Listings
- Listings created by different providers appeared correctly.
- Buyer can view the details of a listing.

**Screenshot:**
```
![Browse Listings](images/browse-listings.png)
```

---

### 2.12 Book a Server
- Request booking completes without errors.
- JavaScript dialog box displays "Booking request sent!"

**Screenshot:**
```
![Book Server](images/book-server.png)
```

---

### 2.13 View Current Booking (Buyer Dashboard)
- Request booking appears under pending bookings.
- Details (listing name, user email, time block, status) are accurate.

**Screenshot:**
```
![View Booking](images/view-booking.png)
```

---

### 2.14 Cancel Server Booking
- Cancel booking button is displayed under bookings.
- Cancel booking prompts the confirmation "Are you sure you want to cancel this booking?"

**Screenshot:**
```
![Cancel Booking](images/cancel-booking-1.png)
![Cancel Booking - Confirmation](images/cancel-booking-2.png)
```

---

### 2.15 Confirm Booking Cancellation
- System state updates as expected.
- Booking is now listed as cancelled.

**Screenshot:**
```
![Booking Cancelled](images/booking-cancelled.png)
```

---

## 3. Stakeholder Feedback Summary
### Strengths
- **Clear, linear user flows** for both provider and buyer.
- **Error handling** is consistent and visible.
- **Listings and booking system** function reliably.
- **Dashboard layouts** for both user roles are specialized.

### Areas for Improvement
- Some UI elements could provide **stronger visual feedback** (for example, bookings and cancellations).
- For confirmations, replace JavaScript dialog boxes with **interactive and visually appealing modals**.
- Consider adding **search or filter functionality** to the listings page.
- Provider dashboards may benefit from **advanced settings and analytics**.

---

## 4. Alignment With Business Requirements
The core system successfully supports the foundational marketplace interactions:
- Providers can list available resources.
- Buyers can discover and book resources.
- Both sides can manage their accounts and view relevant data.
- Error prevention ensures valid sign‑ups and logins.

Part 3 requirements implementing and validating core functionality are met.

---

## 5. Conclusion
Stakeholders confirm that the current implementation satisfies the baseline expectations for Part 3. While additional enhancements will be introduced in Part 4 (usability improvements, extended roles, aesthetics), the core marketplace functions are stable and meet the intended design.
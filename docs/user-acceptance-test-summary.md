# User Acceptance Testing Report – Remote Servers Marketplace

**Stakeholder:** Stakeholders Team, Group 4  
**Week:** Final Week – Testing, Deployment and Maintenance  
**Report Date:** 3-12-2025

---

## Summary

User Acceptance Testing (UAT) was conducted to verify that the application meets business and user requirements from a stakeholder perspective. All major functionalities were tested through simulated user scenarios across buyer, provider, and admin roles.

A total of **8 core test cases** were executed based on realistic user workflows. All scenarios passed successfully, indicating that the system is ready for end-user deployment.

---

## Test Execution Overview

| Test Case ID | Title | Result | Notes |
|--------------|-------|--------|-------|
| UAT-001 | Buyer Registration for Machine | ✅ Pass | Application submitted successfully, data received on backend |
| UAT-002 | Provider Applies for Verification | ✅ Pass | Verification request flow functional; status reflected in UI |
| UAT-003 | Admin Approves Provider | ✅ Pass | Admin can approve; state changes reflected instantly |
| UAT-004 | Booking a Machine | ✅ Pass | Booking and availability confirmed; routing works |
| UAT-005 | Payment Integration via Stripe | ✅ Pass | Mock Stripe adapter processed payment flow successfully |
| UAT-006 | Cancel Booking via Link | ✅ Pass | Cancellation link works and updates status properly |
| UAT-007 | Dashboard Overview for Admin | ✅ Pass | Admin dashboard loaded full data and filters work |
| UAT-008 | Provider Adds a New Machine | ✅ Pass | New machine submitted and appears in provider's list |

---

## Observations and Suggestions

- All tested features worked as intended from an end-user perspective.
- User interface was intuitive and all core flows (booking, payment, approval) were responsive.
- Minor UI suggestions (like confirmation tooltips or loading spinners) could further enhance UX.
- Stripe integration with mock adapter is successful; real deployment can be validated further post-launch.

---

## Next Steps

- Prepare for post-deployment monitoring and logging.
- Ensure real Stripe credentials are securely injected in production.
- Collect user feedback after initial public access.
- Track logs to identify any hidden edge-case issues.

---

**Conclusion:**  
All UAT test cases passed successfully. The application is ready for deployment, pending any final peer reviews or last-minute UI polishing.
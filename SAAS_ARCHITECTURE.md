# CampoPawa Enterprise SaaS Architecture

This document serves as the true north for the CampoPawa backend architecture following the **Multi-Vertical Enterprise Pivot**.

## 🏗️ 1. The Multi-App Topography
Instead of building a massive, tightly coupled monolith, the SaaS platform is segregated into loosely coupled, highly secure Django applications based on vertical workflows.

### A. The Core Monolith (`vendors`, `customers`, `billing`)
- **Tier:** MSME Retail / Standard
- **Price:** KES 700 / month (Retail Pro)
- **Workflow:** 
  - Frictionless "2-Tap Numpad" Quick Sale logging.
  - Complete "Zero Data-Entry" Auto-CRM generated directly from M-Pesa C2B Payloads.
  - Basic analytics, customer loyalty SMS blasts, and stock management.

### B. The NGO Enterprise Portal (`ngo_portal`)
- **Tier:** Development Agencies / NGOs
- **Price:** KES 3,500 / month (Enterprise)
- **Routing:** Handled gracefully by `vendors/views.py` `root_redirect` intercepting `business_type == 'ngo'`.
- **Workflow:**
  - Built strictly around **USAID AMELP** compliance.
  - PII (Personally Identifiable Information) strictly divorced from data tables.
  - **Models:** `Beneficiary` (generates automated UUIDs, tracks demographics/vulnerability markers), `Intervention` (tracks specific field activities against programs).
  - **Core Utility:** `export_donor_audit` generates an instant, 1-Click CSV stripping names and outputting pure statistical compliance frameworks for grant reporting.

### C. The Resort PMS & POS (`resort_portal`)
- **Tier:** Hospitality Operations
- **Price:** KES 3,500 / month (Enterprise)
- **Routing:** Intercepted natively for `business_type == 'resort'`.
- **Workflow:**
  - Uses professional hospitality software logic built on a **Master Folio** structure.
  - **Models:**
    - `Room` (Tracks Status: Clean, Dirty, Occupied).
    - `Folio` (The Master guest bill connecting a stay).
    - `FolioCharge` (The Point-of-Sale tracker mapping a single drink to a specific `Department` and a specific `Folio` instantly).
  - **Core Utility:** "Smart Insights Engine". The dashboard recalculates live data constantly, presenting Occupancy Rates, Daily Revenue split strictly by Department Yield, Housekeeping Alerts, and VIP "Churn Radars".

---

## 🔐 2. Gatekeeper Enterprise Security
To prevent Tier 1 (KES 700) users from accessing Tier 2 (KES 3500) isolated systems, the codebase relies on rigorous custom decorators:
- `@ngo_enterprise_required` (Raises `PermissionDenied` if MSMEs hit `/ngo/`)
- `@resort_enterprise_required`
- The `vendors/views.py` dashboard view acts as a universal router holding the traffic cop logic.

---

## 💰 3. Dynamic Billing & The "Great Mode" Admin
The `billing/models.py` natively separates `premium_retail` from `enterprise_ngo`. 

### The `/saas-admin/` Core
Located securely in the `admin_dashboard` app and protected by `@user_passes_test(lambda u: u.is_superuser)`.
- Calculates live platform Monthly Recurring Revenue (MRR).
- Segregates the vendor demographics into a KPI grid.
- Powers the **Churn Radar**, a hyper-intelligent table that flags "At Risk" accounts where subscriptions are either expiring in < 3 days OR the vendor has failed to log in for > 14 days, granting the Super-Admin instantly actionable WhatsApp messaging logic to recover the user.

---
## Standard Operating Procedure (SOP) for Scaling
If CampoPawa decides to target a 4th vertical (e.g. `logistics_portal`), do not build it into `vendors`!
1. Scaffold `python manage.py startapp logistics_portal`.
2. Build isolated database schema for the logistics workflow.
3. Add `logistics_enterprise_required` decorators.
4. Add the intercept router to `vendors.views.dashboard` to route them instantly to `logistics_portal/dashboard.html`.

# CampoPawa Unified SaaS Ecosystem

A high-performance, multi-tenant enterprise operating system designed for **MSMEs (Retail Pro)**, **NGOs (Impact Ops)**, and **Resorts (Hospitality OS)**.

## 🚀 Core Verticals

- **MSME Retail Pro**: Intelligent sales logging, auto-CRM, and customer engagement.
- **NGO Impact Ops**: USAID AMELP-compliant beneficiary tracking and statistical reporting.
- **Resort Hospitality OS**: Professional Property Management System (PMS) with folio tracking and department-based yield analysis.

## 🛠️ Internal Tech Stack

- **Backend**: Django 5.x / Python 3.12
- **Frontend**: Vanilla HTML5, TailwindCSS, Inter & Outfit Typography
- **UI Architecture**: Glassmorphic "Boxed" UI with premium dark-themed accents.
- **Database**: PostgreSQL (Production) / SQLite (Local)
- **Deployment**: Fly.io (Platform) / Supabase (Database)

## 🏗️ Quick Start (Local Development)

1. **Activate Virtual Environment**
   ```powershell
   & ./venv/Scripts/Activate.ps1
   ```

2. **Run Migrations**
   ```powershell
   python manage.py migrate
   ```

3. **Seed System Archetypes**
   ```powershell
   python scripts/seed_sample_data.py
   ```
   *Creates superuser and base vertical profiles.*

4. **Launch Platform**
   ```powershell
   python manage.py runserver
   ```
   *Access at http://127.0.0.1:8000/*

---

## 🔐 Security & Permissions

All enterprise features are gated by vertical-specific decorators (`@ngo_enterprise_required`, `@resort_enterprise_required`) and tier-based billing logic.

## 💰 Billing Structure

- **Standard (Free)**: 20 Customer Seats, Basic Analytics.
- **Retail Pro (KES 700/mo)**: Unlimited CRM, Marketing Automations.
- **Enterprise (KES 3,500/mo)**: Multi-tenant Portals, Advanced Reporting, Priority Support.

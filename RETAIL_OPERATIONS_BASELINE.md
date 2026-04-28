# 🛡️ RETAIL OPERATIONS BASELINE (GROUND TRUTH)

**Last Updated**: 2026-04-23
**Vertical**: Retail Pro
**Primary Objective**: "At a Glance" Operational Efficiency

---

## 1. UI Architecture (The "Wow" Standard)
All future changes to the Retail vertical MUST adhere to these design primitives to maintain visual parity with the operational baseline:

### Core Tokens
- **Label Density**: Always use `text-[8px]` or `text-[9px]` for metadata labels and uppercase tracking (`tracking-widest`).
- **Inner Padding**: Standard container padding is `p-6`. Component gaps are `gap-3` or `gap-4`.
- **Corner Radius**: Use `rounded-3xl` for main cards and `rounded-2xl` for action buttons.
- **Color Palette**: 
  - Background: `bg-stone-950` / `bg-deep` (`#0c0a09`)
  - Accent (Active): `text-emerald-500` / `bg-emerald-500`
  - Brand: `text-brand` / `bg-brand` (`#C5A059`)

## 2. Component Blueprint

### KPI Hub (Metric Ingestion)
- **Geometry**: 2-Row grid, strictly non-scrolling on mobile viewports (375px).
- **Behavior**: Real-time revenue variance (▲/▼) must be calculated against the previous day's aggregate.

### Quick Actions execution hub
- **Hierarchy**: Primary "Hero" action (Add Customer) is full-width.
- **Utility Grid**: Secondary actions (Promo, Note, Reports) are in a triple-column grid for high-speed access.

### My Notes (Strategic Records)
- **Entity Identity**: Always referred to as "My Notes," never technical jargon like "Log" or "Database."
- **Input Logic**: Quick-add via glassmorphic modal is mandatory to prevent context switching.

## 3. Technical Source of Truth
- **Main View**: `vendors.views.dashboard`
- **Main Template**: `templates/dashboard/overview.html`
- **Logic Imports**: `customers.models` (Customer, Purchase, Service, BusinessNote), `notes.models` (Note).

---

> [!CAUTION]
> **PROTECTED STATE**: This file represents the final approved state of the Retail Dashboard. Any AI or manual modification that breaks the "At a Glance" density or "Fitted" logic is a regression.

---
*CampoPawa Retail Pro — Precision Engineering for MSMEs.*

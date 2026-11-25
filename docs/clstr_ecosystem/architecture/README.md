# CLSTR Ecosystem — Unified Knowledge Base & Architecture Documentation

> **Complete, definitive architectural, technical, operational, and expansion guide for the Clstr student network ecosystem.**  
> *Confidential — Internal Documentation & Engineering Hub*

---

## 🧭 Ecosystem Overview: The Three Layers

The **Clstr Ecosystem** solves the fundamental fragmentation of student life in India. In every Indian city, higher education institutions operate as isolated islands: students are locked behind campus gates, placement cells compete, and social networks are restricted to volatile WhatsApp groups that dissolve upon graduation.

Clstr unites students across an entire metropolitan area into a singular, high-trust, persistent digital and physical campus:
> **“Your college gets you a degree. Clstr gets you a city.”**

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                               CLSTR ECOSYSTEM TRINITY                                  │
├──────────────────────────┬──────────────────────────────┬──────────────────────────────┤
│  Layer 1: Digital Core   │  Layer 2: Beachhead Community│  Layer 3: Expansion Engine   │
│  clstr.in (Platform)     │  vizag.clstr.in (First City) │  Expansion (Cities → Country)│
├──────────────────────────┼──────────────────────────────┼──────────────────────────────┤
│ • Universal Trust Engine │ • Hyper-local Beachhead      │ • Algorithmic State Ranking  │
│ • Tier 1 (.edu) / Tier 2 │ • 19 Target Beachhead Campus │ • No-Edu College Database    │
│ • Campus Feeds & Collab  │ • Guilds (Tech) & Circles    │ • AP Coastal Corridor        │
│ • Realtime Chat & P2P    │ • Curfew & Transit Logistics │ • Tier 2 / Tier 3 Clusters   │
│ • Dynamic QR Ticketing   │ • Campus Captains Flywheel   │ • Pan-India 36 State Roadmap │
│ • AI Career Assistant    │ • Local Brand Sponsorship    │ • Automated Onboarding DB    │
└──────────────────────────┴──────────────────────────────┴──────────────────────────────┘
```

---

## 📚 Documentation Index

This directory contains the exhaustive, unabridged documentation for the entire ecosystem. Navigate to the relevant module below:

| File | Title | Description | Primary Code Repositories |
| :--- | :--- | :--- | :--- |
| **[`01_ECOSYSTEM_MASTER_ARCHITECTURE.md`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/all_about_clstr_ecosystem/01_ECOSYSTEM_MASTER_ARCHITECTURE.md)** | **Master System Architecture** | High-level topology, monorepo breakdown, inter-service data flows, shared database design, and deployment topology. | All 4 Repositories |
| **[`02_CLSTR_NETWORK_PLATFORM_SPEC.md`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/all_about_clstr_ecosystem/02_CLSTR_NETWORK_PLATFORM_SPEC.md)** | **clstr.in Platform Specification** | Complete functional breakdown of all 15 core features, Dual-Tier Auth (.edu vs non-edu OTP), Spectator Mode, and Deno Edge Functions. | `clstr.network` |
| **[`03_TICKET_PLATFORM_AND_ADMIN_SPEC.md`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/all_about_clstr_ecosystem/03_TICKET_PLATFORM_AND_ADMIN_SPEC.md)** | **Ticketing & Admin Platforms** | Architecture of TanStack Start ticketing system, cryptographic QR check-in, batch PDF certificates, and the `clstr.admin` control panel. | `Ticket-Platform`<br/>`clstr.admin` |
| **[`04_VIZAG_COMMUNITY_PLAYBOOK.md`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/all_about_clstr_ecosystem/04_VIZAG_COMMUNITY_PLAYBOOK.md)** | **Vizag Beachhead Community Playbook** | Vizag community operations, 19 beachhead colleges profile, Guilds vs Circles, curfew/hostel logistics, and Ambassador program. | `vizag.clstr-website` |
| **[`05_NATIONWIDE_EXPANSION_ENGINE.md`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/all_about_clstr_ecosystem/05_NATIONWIDE_EXPANSION_ENGINE.md)** | **Nationwide Expansion Engine** | Algorithmic city/state opportunity scoring, AP Coastal Tech corridor, non-institutional email research, and multi-phase national rollout. | `clstr.network/data/expansion/` |
| **[`06_BEHAVIORAL_ECONOMICS_AND_INVESTOR_PLAYBOOK.md`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/all_about_clstr_ecosystem/06_BEHAVIORAL_ECONOMICS_AND_INVESTOR_PLAYBOOK.md)** | **Behavioral Strategy & Investor Playbook** | VC interrogation rebuttal, BJ Fogg habit formation, dopamine loops, campus clout mechanics, and unit economics defensibility against WhatsApp. | Cross-Platform Strategy |
| **[`07_DEVELOPER_SETUP_AND_OPERATIONS_GUIDE.md`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/all_about_clstr_ecosystem/07_DEVELOPER_SETUP_AND_OPERATIONS_GUIDE.md)** | **Engineering Setup & Runbooks** | Step-by-step developer setup for all 4 repos, environment variables, Supabase local migrations, RLS test scripts, and deployment instructions. | Engineering Runbooks |
| **[`08_MARKETING_GROWTH_AND_CAMPUS_ACQUISITION_PLAYBOOK.md`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/all_about_clstr_ecosystem/08_MARKETING_GROWTH_AND_CAMPUS_ACQUISITION_PLAYBOOK.md)** | **Marketing, Growth & Acquisition** | Anti-Instagram positioning, the 6-week campus cycle, activation gates, club-first flywheel, 40-poster design system, and multi-channel calendar. | Growth & Marketing Skills |
| **[`09_CAMPUS_AMBASSADORS_AND_PARTNERSHIPS_EXECUTION.md`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/all_about_clstr_ecosystem/09_CAMPUS_AMBASSADORS_AND_PARTNERSHIPS_EXECUTION.md)** | **Campus Ambassadors & College MOUs** | Real student tactics from applicant filings, 4-week outreach sprint (0-200 users), 48-hour ripple effect, objection handling, and institutional partnerships. | Operations & Ambassador DB |
| **[`10_VIZAG_12_MONTH_EVENT_CALENDAR_AND_COMMUNITY_OPS.md`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/all_about_clstr_ecosystem/10_VIZAG_12_MONTH_EVENT_CALENDAR_AND_COMMUNITY_OPS.md)** | **Vizag 12-Month Events & Ops** | Month-by-month reconciled event plan (v3), weekly continuous living cadence, venue rotation doctrine, core team structure, and risk register. | Vizag Master Playbook |
| **[`11_COUNCIL_OF_HIGH_INTELLIGENCE_GOVERNANCE.md`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/all_about_clstr_ecosystem/11_COUNCIL_OF_HIGH_INTELLIGENCE_GOVERNANCE.md)** | **Council Governance & Deliberation** | The 18-member multi-perspective cognitive council (Sun Tzu, Torvalds, Kahneman, Munger, Feynman, etc.) governing Clstr's strategy and execution. | Strategic Governance |
| **[`12_PRODUCTION_SAFETY_AND_AGENT_GUARDRAILS.md`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/all_about_clstr_ecosystem/12_PRODUCTION_SAFETY_AND_AGENT_GUARDRAILS.md)** | **Production Safety & Agent Guardrails** | Inviolable rules for touching live production code across all 4 repos, zero destructive DDL, minimum viable diff, and pre-commit checks. | Production Safety Doctrine |
| **[`clstr_seo_geo_engine/`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/clstr_seo_geo_engine/README.md)** | **SEO, GEO & AI Search Growth Engine** | 10-module operational suite for dominating Google, ChatGPT, Gemini, Perplexity, and Grok across `clstr.in`, `vizag.clstr.in`, and `spark.clstr.in`. | SEO, GEO & Growth Hub |

---

## 🛠️ Repository Mapping & Stack Summary

| Repository | Directory | Framework / Core Tech | Target URL / Role |
| :--- | :--- | :--- | :--- |
| **Core Social Platform** | [`clstr.network`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/clstr.network) | React 18, Vite (SWC), Tailwind CSS 3.4, Radix UI, TanStack Query v5, Supabase (PostgreSQL 17), Deno Edge Functions | `clstr.in`<br/>Main student social network, CollabHub, feeds & messaging |
| **Community Landing & Portal** | [`vizag.clstr-website`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/vizag.clstr-website) | TanStack Start (SSR), React 19, Tailwind CSS v4, Nitro, Cloudflare Workers / Wrangler | `vizag.clstr.in`<br/>Hyper-local community landing, ambassador portal, college directory |
| **Event & Ticket Engine** | [`Ticket-Platform`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/Ticket-Platform) | TanStack Start, React 19, Tailwind CSS v4, Supabase, QR/Canvas generator, PDF Worker | `tickets.clstr.in` / `clstr.in/events`<br/>Fest ticketing, gate check-in, certificates |
| **Internal Operations Admin** | [`clstr.admin`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/clstr.admin) | React 18, Vite, Tailwind CSS, Supabase JS, Algolia Search, PostHog Analytics | `admin.clstr.in`<br/>Domain approvals, college directory management, platform analytics |

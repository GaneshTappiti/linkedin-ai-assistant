# 07 — Developer Setup & Operations Guide

> **Engineering runbook, local environment configuration, database migration procedures, and deployment workflows across all Clstr ecosystem repositories.**

---

## 1. Prerequisites & Tooling Matrix

Ensure the following runtimes and tools are installed on your workstation:
* **Node.js**: `v20.x` or higher (LTS recommended)
* **Bun**: `v1.1.x` or higher (used for fast package installation and SSR tooling)
* **Git**: `2.40+`
* **Supabase CLI**: For local database orchestration and Edge Function testing (`v1.190+`)
* **Package Managers**: `npm` and `bun`

---

## 2. Repository Configuration & Local Development

### 2.1. `clstr.network` (Core Social Platform)
```bash
cd c:\Users\2005g\Downloads\clstr_ecosystem\clstr.network

# 1. Install dependencies
npm install

# 2. Configure environment variables (copy template)
cp .env.example .env

# 3. Start development server (Vite SPA)
npm run dev
# Running on http://localhost:5173
```

#### Key Scripts:
* `npm run build`: Compiles TypeScript and creates optimized production assets in `dist/`.
* `npm run lint`: Runs ESLint 9 across all components and API modules.
* `npm run test`: Executes unit and component tests with Vitest and Testing Library.
* `npm run security:invariants`: Verifies PostgreSQL Row Level Security (RLS) invariants.
* `npm run security:policy-drift`: Detects unauthorized schema changes against security snapshots.

---

### 2.2. `vizag.clstr-website` (Community SSR Portal)
```bash
cd c:\Users\2005g\Downloads\clstr_ecosystem\vizag.clstr-website

# 1. Install dependencies (Bun recommended)
bun install
# or: npm install

# 2. Start TanStack Start dev server
bun run dev
# or: npm run dev
# Running on http://localhost:3000
```

#### Key Scripts:
* `bun run build`: Prepares SSR serverless bundle via Nitro engine.
* `bun run preview`: Runs a local preview of the production SSR build.

---

### 2.3. `Ticket-Platform` (Ticketing & Gate Check-in)
```bash
cd c:\Users\2005g\Downloads\clstr_ecosystem\Ticket-Platform

# 1. Install dependencies
bun install
# or: npm install

# 2. Configure environment variables
cp .env.example .env.local

# 3. Verify Edge Secrets configuration
node scripts/verify-edge-secrets.mjs

# 4. Start full-stack dev server
bun run dev
# Running on http://localhost:3001
```

#### Key Scripts:
* `npm run test:unit`: Executes unit tests for QR and pass generation logic.
* `npm run test:e2e`: Runs Playwright end-to-end tests across registration and check-in flows.

---

### 2.4. `clstr.admin` (Internal Management Portal)
```bash
cd c:\Users\2005g\Downloads\clstr_ecosystem\clstr.admin

# 1. Install dependencies
npm install

# 2. Configure environment variables
cp .env.example .env

# 3. Start development server
npm run dev
# Running on http://localhost:5174
```

#### Key Scripts:
* `npm run lint`: Runs TypeScript validation (`tsc -p tsconfig.app.json --noEmit`).
* `npm run build`: Generates the production admin dashboard bundle.

---

## 3. Environment Variables Reference

Each repository requires dedicated configuration keys:

### `clstr.network` (`.env`)
```ini
# Supabase Configuration
VITE_SUPABASE_URL="https://your-project.supabase.co"
VITE_SUPABASE_ANON_KEY="your-anon-public-key"

# Production App URL
VITE_APP_URL="https://clstr.in"

# Resend Transactional Email (Used by Edge Functions)
RESEND_API_KEY="re_1234567890"

# OpenRouter AI Engine (Edge Functions)
OPENROUTER_API_KEY="sk-or-v1-..."

# Web Push VAPID Keys
VITE_VAPID_PUBLIC_KEY="BK..."
VAPID_PRIVATE_KEY="..."

# CRITICAL SECURITY RULE:
# NEVER enable VITE_ALLOW_BYPASS_AUTH in staging or production.
```

### `Ticket-Platform` (`.env.local`)
```ini
# Supabase Connection
VITE_SUPABASE_URL="https://your-project.supabase.co"
VITE_SUPABASE_ANON_KEY="your-anon-public-key"
SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"

# WhatsApp Business API
WHATSAPP_API_TOKEN="EA..."
WHATSAPP_PHONE_NUMBER_ID="..."

# Payment Gateway (Razorpay / Cashfree)
RAZORPAY_KEY_ID="rzp_live_..."
RAZORPAY_KEY_SECRET="..."
```

---

## 4. Database Migrations & Supabase Workflows

All database migrations reside in [`clstr.network/supabase/migrations/`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/clstr.network/supabase/migrations).

### 4.1. Migration Naming Convention
Migrations use ordered timestamp prefixes: `YYYYMMDDHHMMSS_XXX_descriptive_name.sql`.

Recent critical migrations:
* `20261001000000_200_tier2_verification.sql`: Adds non-academic-email tracking columns and atomic RPC `claim_tier2_profile()`.
* `20261001120000_203_expand_no_edu_colleges_nationwide.sql`: Seeds vetted institutions lacking student email domains across India.
* `20261001130000_204_fix_tier2_public_domain_trigger.sql`: Updates `block_public_domain_profile()` trigger to permit personal emails for students from verified Tier 2 institutions.

### 4.2. Applying Migrations
```bash
# Push migrations to connected Supabase Cloud project
cd clstr.network
npx supabase db push

# Reset local development database and run all migrations
npx supabase db reset
```

---

## 5. Security & Pre-Commit Quality Floor

Every commit across the ecosystem must comply with the strict **Pre-Commit Quality Floor**:

```bash
# In any repo before committing:
npx tsc --noEmit
npm run lint
npm run test
```

### Security Doctrine Checklist:
1. **Never commit `.env` or secret keys**: Verify `.env` is listed in `.gitignore`.
2. **Never hardcode club passcodes**: Club roles must be validated against `club_memberships` in PostgreSQL.
3. **Always verify RLS on new tables**: Every table created in PostgreSQL must explicitly run `ALTER TABLE public.<table_name> ENABLE ROW LEVEL SECURITY;` with accompanying `SELECT`, `INSERT`, `UPDATE`, and `DELETE` policies.
4. **Never allow client-side role escalation**: All administrative operations must be mediated by PostgreSQL Security Definer RPCs or Deno Edge Functions validating the caller's JWT role.

---

## 6. Production Deployment Runbook

```mermaid
flowchart TD
    DEV[Developer Commit to Git Main] --> CI[GitHub Actions CI Pipeline]
    
    subgraph QualityGates["Quality Gate Checks"]
        CI --> LINT[TypeScript & ESLint Check]
        CI --> TEST[Vitest & Playwright E2E Tests]
        CI --> SEC[RLS Policy Invariant Audit]
    end
    
    QualityGates --> DEPLOY{All Checks Passed?}
    
    DEPLOY -->|Yes| VERCEL_MAIN[Deploy clstr.network to Vercel (clstr.in)]
    DEPLOY -->|Yes| CF_VIZAG[Deploy vizag.clstr-website to Cloudflare (vizag.clstr.in)]
    DEPLOY -->|Yes| VERCEL_TICKETS[Deploy Ticket-Platform to Vercel (tickets.clstr.in)]
    DEPLOY -->|Yes| VERCEL_ADMIN[Deploy clstr.admin to Internal Edge (admin.clstr.in)]
    
    DEPLOY -->|No| FAIL[Halt Deployment & Send Alert]
```

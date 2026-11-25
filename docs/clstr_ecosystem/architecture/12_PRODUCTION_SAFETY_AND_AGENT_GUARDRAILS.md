# 12 — Production Safety Protocols & AI Agent Guardrails

> **The mandatory operational and security handbook for working with Clstr's live production repositories.**

---

## 1. Live Production Status & Reality

All four child applications within the `clstr_ecosystem` are currently deployed, accessible on the public internet, and handling active student traffic:

| Repository | Production Domain | Framework | Critical Live Capabilities |
| :--- | :--- | :--- | :--- |
| **`clstr.network/`** | **`clstr.in`** | React 18 + Vite | Active student sessions, real-time messaging, campus feeds, CollabHub team formations. |
| **`vizag.clstr-website/`** | **`vizag.clstr.in`** | TanStack Start (SSR) | Public community portal, 19-college directories, Campus Captain application intake. |
| **`Ticket-Platform/`** | **`spark.clstr.in`** | TanStack Start | Live fest ticketing, cryptographic QR passes, physical gate check-in scanners. |
| **`clstr.admin/`** | **Local only** | React 18 + Vite | Domain approvals, verification queue, platform-wide analytics. Not cloud-deployed. |

---

## 2. The 5 Cardinal Rules of Working on Live Code

### Rule 1: The Principle of Minimum Viable Diff
* Make only the precise changes necessary to fulfill the request.
* Refuse unrequested refactorings, directory restructuring, or stylistic rewrites.
* Three clean, focused lines of code are infinitely better than a "cleaner" 200-line rewrite that risks runtime regression.

### Rule 2: Database Inviolability (Zero Destructive Migrations)
* Destructive DDL commands (`DROP TABLE`, `DROP COLUMN`, `TRUNCATE`) are strictly banned.
* All schema changes must be non-breaking and additive.
* Never disable PostgreSQL Row Level Security (RLS) on any production table.

### Rule 3: Zero-Bypass Authentication Discipline
* Hardcoded credentials and debug bypass flags (`VITE_ALLOW_BYPASS_AUTH`, `club123`) must never exist in production code or environment files.
* Spectator Mode write restrictions must always be validated at the database layer via RLS policies.

### Rule 4: Framework & Dependency Isolation
* Maintain strict package boundaries between React 18 (`clstr.network`, `clstr.admin`) and React 19 / TanStack Start (`vizag.clstr-website`, `Ticket-Platform`). Never cross-copy components without reconciling dependency versions.

### Rule 5: Non-Negotiable Pre-Commit Quality Floor
Before any code change is merged, deployed, or committed, the following suite must be verified:
```bash
# 1. Type validation without emit
npx tsc --noEmit

# 2. Project linting
npm run lint

# 3. Unit & integration test execution
npm run test
```

---

## 3. Incident Response & Rollback Procedures

If an unexpected production bug or regression is detected on live environments:
1. **Immediate Rollback**: Revert the affected commit on GitHub; Vercel and Cloudflare will automatically trigger atomic rollbacks within 60 seconds.
2. **Database Reversion**: Ensure all database migrations have a documented down-migration or compensation script.
3. **Council Review**: Convene the `[Torvalds + Musashi + Taleb]` Council triad to perform a post-mortem, identify the root cause, and verify prevention tests before redeployment.

---

## 4. Persistent Memory Doctrine (`agentmemory-main`)

All AI agents and automated engineering workflows MUST enforce memory discipline via [`agentmemory-main`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/agentmemory-main) and the persistent store at [`.agentmemory/`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/.agentmemory):

* **Store Everything & Remember Everything**: No context should ever be lost across sessions.
* **Pre-Task Check**: Always query [`.agentmemory/lessons.json`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/.agentmemory/lessons.json) and [`.agentmemory/memories.json`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/.agentmemory/memories.json) before starting non-trivial tasks.
* **Settled Decisions**: Persist architecture, schema, and API contracts into `.agentmemory/memories.json` at the moment of resolution.
* **Confidence-Weighted Lessons**: Every bug, user correction, or discovered gotcha becomes a lesson in `.agentmemory/lessons.json` so mistakes are never repeated.
* **Session Recaps**: Record session progress in `.agentmemory/sessions.json`.


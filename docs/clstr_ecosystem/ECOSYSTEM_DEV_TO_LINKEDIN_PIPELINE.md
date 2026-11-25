# 🔄 CLSTR Ecosystem — Continuous Dev-to-LinkedIn Documentation & Content Pipeline

This pipeline establishes an automated, permanent bridge between Ganesh's active development workspace at `C:\Users\2005g\Downloads\clstr_ecosystem` and his founder personal brand / LinkedIn thought leadership engine.

---

## 🏗️ Monitored Ecosystem Topology

```
                  C:\Users\2005g\Downloads\clstr_ecosystem
                                     │
     ┌──────────────────┬────────────┴───────┬──────────────────┐
     ▼                  ▼                    ▼                  ▼
Ticket-Platform    clstr.network     vizag.clstr-website    clstr.admin
(spark.clstr.in)    (clstr.in)        (vizag.clstr.in)     (Local Only)
React 19 + TanStack React 18 + Vite   React 19 + Nitro     React 18 + Vite
Gate Check-in, QR   Social Network    City Community       Verification Queue
```

---

## ⚙️ Automated Tracking Engine (`scripts/ecosystem_tracker.py`)

Run the scanner anytime to ingest the latest commits, test runs, and architectural shifts:

```powershell
python scripts/ecosystem_tracker.py
```

### What it automatically tracks:
1. **Git Commit Velocity:** Extracts recent commits across all 4 production repositories.
2. **Test Suites & Quality Reports:** Monitors `test-results/.last-run.json` and `TEST_REPORT.md` (e.g., unit test passes, Playwright gate tests).
3. **Architectural Guardrails & Migrations:** Detects database changes, auth hardening (e.g., removing `VITE_ALLOW_BYPASS_AUTH`), and gate scanner HMAC updates.
4. **Programmatic Content Generation:** Formulates 4+ high-signal LinkedIn post angles directly grounded in the code diffs.

---

## 📝 Canonical Artifacts Generated

1. **`docs/clstr_ecosystem/ECOSYSTEM_LIVE_ACTIVITY_LOG.md`:** Living markdown changelog detailing repo statuses, recent commits, and test outcomes.
2. **`data-tracking/ecosystem_activity.json`:** Machine-readable data structure tracking cross-repo activity.
3. **`memory/draft_posts/`:** Verified, human-scored post drafts (e.g. `2026-11-12_boxoffice_resilience.txt` scoring **84.2 PASS** on `detect.py`).

---

## 🎯 Dev-to-Post Conversion Framework (How Code Becomes Content)

Every major engineering milestone maps to a specific founder narrative pillar:

| Live Dev Signal in `clstr_ecosystem` | Technical Implementation | Founder LinkedIn Post Angle |
| :--- | :--- | :--- |
| **Commit `4516050`:** `feat(boxoffice): walk-in cash issuance` | Local HMAC QR token generation + batch Supabase sync | *"Why online ticketing fails at college gates: building offline cash box office for 500-student crowds."* |
| **Commit `08f184c`:** `feat(blog): 54 campus event blogs` | Programmatic SEO schema markup & GEO crawlability | *"How we ranked 54 college fest events on Google and Perplexity in one sprint."* |
| **Commit `b45e8ae`:** `feat(ambassador): editorial redesign` | Eliminated CSS preload chunk lag on 2G campus networks | *"Redesigning student forms: why corporate UX drops conversion by 60% on campus Wi-Fi."* |
| **Commit `d52f576`:** `feat: pre-commit test resilience` | Playwright test suites for physical gate scanners | *"When your app checks in 400 students for a 24h hackathon, your gate scanner cannot crash."* |


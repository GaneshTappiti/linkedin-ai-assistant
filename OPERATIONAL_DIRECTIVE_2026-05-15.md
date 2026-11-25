# Operational Directive — May 15, 2026

> **Status**: ACTIVE  
> **Effective**: 2026-05-15  
> **Review Date**: 2026-05-29 (14 days)  
> **Phase**: Calibration — NO new infrastructure

---

## System Maturity Assessment

The outreach system has crossed from **automation tooling** into **operational lifecycle infrastructure**.

| Capability              | Status |
| ----------------------- | ------ |
| Persistent memory       | ✅ SQLite-backed via `outreach_db.py` |
| Lifecycle timing        | ✅ Cadence-based via `followup_scheduler.py` |
| Safety governance       | ✅ `SafetyGovernor` + daily limits |
| Crash recovery          | ✅ Deterministic state restoration |
| Follow-up orchestration | ✅ Queue → Review → Send pipeline |
| Observability           | ✅ `outreach_dashboard.py` anomaly engine |
| Relationship aging      | ✅ Pipeline stage progression |
| Pipeline progression    | ✅ `opener_sent` → follow-up stages |

This is more mature than most open-source agent systems.

---

## Core Architectural Principle

```
scheduler → queue → review → send
```

**Scheduling, execution, and governance must remain separated.**

Even if human review is eventually reduced, queue-based orchestration is non-negotiable.

---

## 14-Day Calibration Period (May 15 – May 29)

### What To Do

| Task | Goal | Cadence |
|------|------|---------|
| Run dashboard daily | Observe anomalies, surface operational truth | Daily |
| Backfill scheduling | Activate cadence system for all `opener_sent` | Day 1-2 |
| Tune follow-up delays | Humanize pipeline timing | Week 1 |
| Watch reply patterns | Gather real behavioral data | Continuous |
| Fix JOIN cosmetic issue | Clean observability display | Week 1 |
| Log negative outcomes | Improve validators and tone | Continuous |

### What NOT To Do

- ❌ Add new automation features
- ❌ Build new agents
- ❌ Create new infrastructure
- ❌ Optimize for volume/speed
- ❌ Build React/FastAPI command center (yet)

### What To Observe

- Where prospects stall
- Where follow-ups feel robotic
- Where reply timing matters
- Where crashes happen
- Where cadence feels unnatural

---

## Post-Calibration Upgrade Path (After May 29)

### Phase 1: Relationship Scoring

The strongest upgrade will NOT be bigger models or more agents.

It will be **relationship scoring**:

| Score | Description |
|-------|-------------|
| Warmth score | How receptive is this prospect? |
| Responsiveness | Reply speed and engagement level |
| Conversion probability | Likelihood of ambassador signup |
| Conversation quality | Depth and authenticity of exchanges |
| Engagement momentum | Trending up or decaying? |

This transforms the system from **workflow automation** into **decision intelligence**.

### Phase 2: React + FastAPI Command Center

Build ONLY after real usage data reveals:
- What metrics actually matter
- What workflows deserve a UI
- What's noise vs. signal
- What operational patterns repeat

---

## The Hidden Asset

The SQLite database is the most powerful asset in this system.

Over time it becomes:
- **Relationship history** — who, when, what, how
- **Timing intelligence** — optimal engagement windows
- **Behavioral analytics** — what messages work
- **Outreach learning data** — pattern recognition
- **Pipeline intelligence** — conversion path mapping

This compounds massively over months. This is the advantage of **fully local persistent systems**.

---

## The "0% Reply Rate" Insight

The current 0% reply rate is **not a failure** — it's the system exposing **operational truth**.

Most builders optimize for `messages sent`.  
The real KPI is `relationship progression`.

The dashboard now forces that visibility. That's healthy.

---

## Philosophy Guardrails

The system must remain:

- **Local-first** — no cloud dependencies for core ops
- **Operational-first** — optimize for real outcomes, not activity metrics
- **Deterministic** — predictable, reproducible behavior
- **Memory-centric** — everything persists, nothing is forgotten
- **Governance-aware** — safety > speed, always

---

## Known Issues (Low Priority)

| Issue | Severity | Notes |
|-------|----------|-------|
| JOIN display showing `?` for migrated names | Cosmetic | Migration inconsistency, not data corruption |
| Follow-up cadence needs real-world tuning | Operational | Requires behavioral data from calibration period |

---

> **Next review**: 2026-05-29  
> **Decision point**: Begin relationship scoring implementation or extend calibration.

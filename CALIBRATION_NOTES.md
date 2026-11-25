# Calibration Notes — Outreach OS

> **Period**: 2026-05-15 → 2026-05-29 (14 days)  
> **Philosophy**: Optimize for consistency, observability, and learning. NOT scale, speed, or autonomy.  
> **Directive**: [OPERATIONAL_DIRECTIVE_2026-05-15.md](./OPERATIONAL_DIRECTIVE_2026-05-15.md)

---

## Daily Tracking Template

Copy this block for each day:

```
### Day N — YYYY-MM-DD

**Sent**: X follow-ups / Y new openers
**Replies received**: 
**Reply sentiment**: 
**Time-to-reply**: 
**Profile quality observations**: 
**Follow-up response delta**: (did follow-up perform better/worse than opener?)
**Negative reactions**: (ignored, blocked, reported?)
**Dashboard anomalies**: 
**Manual observations**: 
**Cadence feel**: (natural / robotic / too fast / too slow)
**System issues**: 
```

---

## Calibration Metrics

| Metric | Why It Matters | Target |
|--------|---------------|--------|
| Reply sentiment | Quality signal — warm vs. cold vs. hostile | Mostly neutral-to-warm |
| Time-to-reply | Cadence signal — how fast do they respond? | Baseline collection |
| Profile quality | Targeting signal — are we reaching right people? | Current students, tech-active |
| Follow-up response delta | Sequencing signal — does follow-up help? | Positive delta over opener |
| Negative reactions | Safety signal — are we annoying people? | Zero blocks/reports |
| Manual observations | Hidden insights the dashboard can't capture | Daily entries |

---

## Day 1 — 2026-05-15

**Sent**: 0 follow-ups / 0 new openers (system calibration day)
**Repairs completed**:
- Fixed 8 NULL prospect names (migration-era records)
- Backfilled follow-up dates for all 8 opener_sent prospects
- All 8 now marked OVERDUE (11 days since May 4 openers)

**Dashboard state**:
- 51 prospects total (37 new, 8 opener_sent, 1 deferred, 5 dead)
- 0% reply rate (0/8) — statistically meaningless, not actionable yet
- Safety budget: 100% remaining (0/15)
- Risk alerts: 0% reply rate, 11 days inactive

**System health**: 
- Name display bug fixed across all dashboard sections
- Cadence system activated — all 8 prospects now have scheduled follow-ups
- Unscheduled follow-up alert resolved

**Calibration observations**:
- All 8 opener messages start with "Hey there" — need to verify actual first-name personalization when sending follow-ups
- **5 dead prospects** (Ananya Dhiman, Niveditha .K.K, Muskan Kumari, Susmitha Eluri, Vijay kumar Tholeti):
  - All have `followup_count=0`, `last_stage=NULL`, `sentiment=NULL`
  - This means they were **pre-filtered** during migration — never actually engaged
  - Likely a targeting quality issue, not a message quality issue
  - Worth investigating: were these wrong audience (non-students? wrong geography?)
- **1 deferred** (Raj Raut, id=44):
  - `college=NULL`, `headline=NULL`, `followup_count=0`, `next_followup_at=NULL`
  - No context on why deferred — needs manual profile check before re-engagement
  - Not in the follow-up queue (no scheduled date)
- **Lead scores**: All 8 queued prospects have `score=NULL` — no lead scoring yet (expected, this is a future upgrade)
- **No enrichment data**: college, headline, sentiment all NULL for queue prospects — the migration only captured URLs and messages

**Day 1 decision**: System repair only. No sends. Controlled restart begins Day 2.

---

## Day 2 — 2026-05-16

**Plan**: 
- Review all 8 in queue via `python followup_scheduler.py review`
- Send 2–3 follow-ups maximum (controlled restart, not pipeline shock)
- Observe for 24h before sending more
- Log outcomes below

**Sent**: 
**Replies received**: 
**Reply sentiment**: 
**Time-to-reply**: 
**Profile quality observations**: 
**Follow-up response delta**: 
**Negative reactions**: 
**Dashboard anomalies**: 
**Manual observations**: 
**Cadence feel**: 
**System issues**: 

---

## Controlled Restart Protocol

> ⚠ **DO NOT batch-advance all 8 simultaneously.**

After 11 inactive days, sudden reactivation creates:
- Behavioral spikes (robotic pattern)
- Reduced calibration quality (too many variables)
- Potential LinkedIn detection risk

**Restart cadence**:

| Day | Action | Volume |
|-----|--------|--------|
| Day 1 (May 15) | System repair, no sends | 0 |
| Day 2 (May 16) | First controlled follow-ups | 2–3 |
| Day 3 (May 17) | Observe Day 2 results, send 2–3 more if safe | 2–3 |
| Day 4-7 | Gradual ramp based on behavioral data | 3–5 |
| Day 8-14 | Stable operational cadence | Per dashboard |

---

## Anti-Patterns (DO NOT)

- ❌ Change message prompts daily
- ❌ Redesign architecture during calibration
- ❌ Add new agents or automation
- ❌ Increase outreach volume before gathering baseline data
- ❌ Optimize for metrics before having statistically meaningful sample size
- ❌ Make multiple changes at once (can't identify causality)

## Correct Patterns (DO)

- ✅ One variable at a time
- ✅ Log every observation, even "nothing happened"
- ✅ Run dashboard daily
- ✅ Track time-to-reply as primary engagement signal
- ✅ Keep system stable for consistent measurement
- ✅ Review message quality manually before each send

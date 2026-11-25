# clstr.in LinkedIn Outreach — Agent Rules & Constraints

> **MANDATORY**: Any AI agent, browser agent, or automation script touching LinkedIn
> on behalf of clstr.in MUST read and follow every rule in this document BEFORE taking any action.
> No exceptions. No improvisation.

---

## WHO WE ARE / WHAT WE ARE DOING

**clstr.in** is a verified campus social network built by Ganesh Tappiti. It connects
students with batchmates, alumni, mentors, and real opportunities — all within their college.

We are recruiting 3 types of team members via LinkedIn:
1. **Campus Ambassador** — represents clstr.in at their college, runs activations
2. **Core Team (Designing & Marketing)** — owns branding, campaigns, growth
3. **Founding Team** — fully dedicated, skilled, builds the product

The outreach tool is `clstr_browseruse_outreach.py` (browser-use + Ollama agent).
The inbox reply tool is `clstr_browseruse_inbox.py`.
Legacy Selenium script: `clstr_direct_outreach_legacy.py` (deprecated).

Run the browser-use scripts. Don't improvise around them.

---

## SYSTEM ARCHITECTURE (v2)

### Data Layer — SQLite
All outreach data is stored in **`data-tracking/outreach.db`** (SQLite).
Legacy JSON files have been migrated and backed up as `.json.bak`.

**Tables:**
- `prospects` — every person we've encountered (dedup, identity tracking)
- `messages` — every message sent or received (full conversation history)
- `pipeline` — follow-up stage per prospect (new → opener_sent → replied → interested → converted)
- `sessions` — agent run tracking with crash recovery
- `checkpoints` — resume capability after crashes
- `approvals` — human-in-the-loop approval queue

### Safety Layer — Safety Governor (`safety_governor.py`)
Centralized enforcement of all safety limits:
- **15 messages/day** (cross-session, persisted in SQLite)
- **10 messages/round** (per-session cap)
- **2-hour cooldown** between sessions
- **10% random stop** after each message (anti-pattern detection)
- **3 consecutive failures** = automatic session stop

### Approval Layer — Human-in-the-Loop (`approval_mode.py`)
Before any message is sent, the operator can review:
- `--approve` (DEFAULT): Human reviews each draft → Send/Edit/Skip/Quit
- `--auto`: Send automatically (no review)
- `--dry-run`: Generate drafts, save to DB, send nothing

### Identity Validation — Layered Resolution
Names are validated through 5 layers before any message is generated:
1. Explicit DOM selector extraction
2. Profile heading parsing
3. URL slug parsing
4. AI fallback extraction
5. **HARD FAIL** — if name is "there", "LinkedIn Member", empty, or invalid → REJECT

---

## HARD RULES — NEVER BREAK THESE

### Volume & Pacing
- ✅ **15 messages MAX per day** — enforced cross-session via SQLite
- ✅ **10 messages MAX per round** — stop after 10 in a single session
- ✅ **ONE profile at a time** — finish one completely before moving to the next
- ✅ **25-45 second random delay** between each message (with occasional longer pauses)
- ✅ **2-hour cooldown** between sessions of the same type
- ✅ **Sequential only** — never parallel, never batch, never rush
- ❌ **Never send 2 messages to the same person in one round**

### Profile Verification (must pass ALL before messaging)
- ✅ Name must be extractable (real person's name, not "there" or "LinkedIn Member")
- ✅ College must be extractable (actual institution, not "You both studied at...")
- ✅ Profile must be a real person, not a company page
- ❌ Skip if name OR college cannot be confirmed from the profile
- ❌ **HARD FAIL**: If extracted name is in the rejected names list, message is BLOCKED

### Deduplication
- ✅ Always check SQLite `prospects` table before messaging
- ✅ Never message anyone already in the database with an outbound message
- ✅ Save every new prospect and message to SQLite immediately after send
- ❌ Never reset or overwrite the database

### Detection Prevention
- ✅ Type messages character-by-character (30-80ms per character)
- ✅ Use human-like random delays between all actions
- ✅ Always use persistent Chrome profile from `data-tracking/chrome-profile/`
- ✅ Anti-automation flags must be set (see script)
- ✅ 10% random early stop per message (anti-pattern)
- ❌ Never paste messages all at once
- ❌ Never run headless Chrome
- ❌ Never use LinkedIn API / unofficial APIs
- ❌ Never do more than 15 messages in a day

---

## MESSAGE RULES — TONE & CONTENT

### Ganesh's Real Voice (non-negotiable)
Learned from real WhatsApp conversations. Messages must sound like this:

**✅ DO:**
- Short — 2 sentences maximum
- Casual, peer-to-peer — "bro", first name, direct
- Reference something SPECIFIC from their profile
- End with ONE genuine question
- Sound like a 21-year-old founder, not a recruiter

**❌ NEVER:**
- No corporate language ("I would like to explore", "exciting opportunity")
- No emoji overload
- No paragraphs or walls of text
- No pitching clstr.in in the first message
- No sharing the form link in the first message
- No sharing phone number in the first message
- No asking them to WhatsApp you first message

### Role-Aware Messaging
Detect the person's strongest signal and match the message to it:

| Signal Detected | Role Fit | Message Angle |
|---|---|---|
| Campus ambassador, TEDx, student council, event organizer, club president | Campus Ambassador | Campus community / engagement questions |
| Graphic design, UI/UX, Figma, marketing lead, content creator | Core Team | Creative / growth ownership angle |
| Startup cell, E-cell | Founding Team | Builder / shipping angle |
| No clear signal | Campus Ambassador (default) | General campus leadership angle |

### First Message Template Reference
See `clstr_browseruse_outreach.py` → `TEMPLATES` dict. Use those exactly.
Never write your own templates unless adding to that dict and committing.

---

## INBOX REPLY RULES — READ BEFORE REPLYING

### ❗ MANDATORY: Read Full Conversation Before Replying
**Never reply based on the last message alone. Always read the entire conversation thread first.**

- ✅ **Scroll to the top** of each conversation — read every message exchanged
- ✅ **Understand the arc** — what was asked, what was said, what stage is this conversation at
- ✅ **Match the reply to where the conversation actually is** — not where you assume it is
- ✅ **If you already sent a message and they haven't replied** — do NOT send another message, skip that conversation
- ✅ **If they gave a detailed answer** — acknowledge specific things they said, don't give a generic response
- ❌ **Never blindly fire a template reply** without reading context first
- ❌ **Never send a follow-up if the last message in thread is yours** (that's double-messaging)
- ❌ **Never reply to sponsored/LinkedIn system messages** — only to real human replies

### Context → Reply Mapping (based on full thread reading)

| Situation (from full thread) | What to do |
|---|---|
| They replied with details about their campus role | Acknowledge the specific detail, then ask one follow-up |
| They asked about stipend / pay | Honest answer: early stage, no pay yet, ownership + experience |
| They mentioned exams / vacation / not studying | Acknowledge, no pressure, "I'll follow up later" |
| They said they're not a student / not studying | Gracefully note it's college-student focused, keep door open |
| They gave detailed info about their skills | Pick ONE specific skill and connect it to clstr role |
| They asked what clstr is | Explain in 2 lines max, end with a campus-specific question |
| They said something positive / interested | Share form link + WhatsApp number |
| Their last reply was YOUR message | **Do not reply again. Skip this conversation.** |

---

## REPLY / CONVERSION FLOW

Only share the form and phone number when someone **replies positively**:

**They say:** "interested", "want to join", "yes", "sounds good", "sure", "okay"
**You reply:**
```
Perfect! Fill this quick form and we'll take it from there: https://forms.gle/2NYjiunqeUk3WUDh9

Should take 2 mins. We'll reach out within 48 hours. Ping me on WhatsApp (9441467303) if you have any questions.
```

**They say:** "what is clstr", "tell me more"
**You reply:**
```
clstr.in is a verified campus network — connects students to real opportunities, batchmates, and alumni within their college. We're onboarding campus leaders to shape how it rolls out. What does your typical week on campus look like?
```

**They say:** "busy", "exams", "not now"
**You reply:**
```
All good — makes total sense. I'll follow up in a couple weeks. Good luck with the exams!
```

---

## WHAT TO RUN

### Pre-session setup (run once per boot)
```powershell
.\scripts\ollama_config.ps1
```

### Outreach (new candidates) — with human approval (DEFAULT)
```powershell
cd c:\Users\2005g\Downloads\tappits-linkedin-agents
.venv\Scripts\python.exe clstr_browseruse_outreach.py --approve
```

### Outreach (auto mode — no review)
```powershell
.venv\Scripts\python.exe clstr_browseruse_outreach.py --auto
```

### Outreach (dry run — drafts only, no sending)
```powershell
.venv\Scripts\python.exe clstr_browseruse_outreach.py --dry-run
```

### Inbox replies
```powershell
cd c:\Users\2005g\Downloads\tappits-linkedin-agents
.venv\Scripts\python.exe clstr_browseruse_inbox.py
```

Both scripts are powered by **browser-use + Ollama (qwen2.5:7b) + SQLite**.
They handle everything:
1. Pre-session safety check (daily limit, cooldown)
2. Crash recovery (marks crashed sessions, resumes state)
3. Loads dedup from SQLite database
4. Searches LinkedIn / checks inbox
5. Extracts and verifies each profile (hard-fail on bad names)
6. Generates role-aware message in Ganesh's tone
7. Human approval gate (in --approve mode)
8. Types messages character-by-character at human speed
9. Records everything to SQLite (prospect, message, pipeline stage, checkpoint)
10. Random stop check after each message (anti-detection)

**Do not bypass the scripts. Do not improvise. Run the scripts.**

> Legacy Selenium script: `clstr_direct_outreach_legacy.py` (deprecated, kept for reference).

---

## DATA FILES

### Primary (SQLite)
- `data-tracking/outreach.db` — all prospects, messages, pipeline, sessions, approvals

### Legacy (backed up)
- `data-tracking/messaged_profiles.json.bak` — migrated to SQLite
- `data-tracking/outreach_log.json.bak` — migrated to SQLite
- `data-tracking/sent_candidates.json.bak` — migrated to SQLite

---

## WHAT LINKEDIN BANS FOR

Avoid all of the following:
- Sending identical messages to many people quickly
- Pasting text (no copy-paste, type it)
- Using automation-detected browser fingerprints
- Sending more than ~10-20 DMs per day
- Scraping at high speed
- Using headless browsers

The script is already designed to avoid all of the above. **Follow the script.**

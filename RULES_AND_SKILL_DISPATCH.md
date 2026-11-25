# 📜 Repository Operating Rules, Regulations & Skill Dispatch Matrix
## tappits-linkedin-agents — Autonomous Founder Brand & Intelligence Architecture

This document defines the binding rules, regulations, and skill routing procedures for all agents operating in this repository.

---

## 🏛️ The 7 Non-Negotiable Operational Laws

### 1. Mandatory Pre-Task Memory Load
Before generating plans or running scripts, every agent must load the 5 normalized memory assets in strict sequence:
1. `memory/normalized_2026-04-26/linkedin_master_export_deduped.json`
2. `memory/normalized_2026-04-26/goals_vision_building_focus.json`
3. `memory/normalized_2026-04-26/profile_comprehensive_analysis.json`
4. `memory/normalized_2026-04-26/normalization_summary_report.json`
5. `memory/normalized_2026-04-26/PERSONAL_SYNTHESIS_GANESH.md`

### 2. Ground-Truth Data Invariance
Never hallucinate or exaggerate traction metrics. All recommendations, posts, and pitches must anchor to verified ground truth:
- **LinkedIn Profile:** **2,021 followers**, **500+ connections**, **310 profile viewers**, **1,300 weekly impressions**.
- **Clstr Scale:** ~600 verified students across 7 Vizag colleges (Raghu, ANITS, Vignan, NSRIT, MVGR, GITAM, AU).
- **Garba Night Economics:** 88 registrations, 81 paid @ ₹349, ~₹33k gross, ₹45k total costs, ₹12k loss on Konfhub, 0 refunds.
- **Top LinkedIn Viral Milestone:** Clstr Vizag team meetup at **5,663 impressions and 142 reactions**.

### 3. Human-Final-Action Posting Policy
Antigravity agents research, formulate hooks, draft copy, generate images, test humanization, and copy text to clipboard. **The agent NEVER clicks the final "Post" button.** Ganesh reviews and posts manually in his own browser or schedules natively on LinkedIn.

### 4. Slop-Free Voice & Detection Gate
Every single post, comment, and document written in Ganesh's name must:
- Match his authentic voice in `.claude/linkedin/voice.md` and `ganesh_real_tone_reference.md` (direct, short sentences, contractions, numbers, 0 corporate fluff).
- Pass `python skills/li-human/detect.py "<file>"` scoring **$\ge 80$** (PASS) with **0 slop words**.
- Rotate across Ganesh's 6 builder facets (AI Generative builder, Product Designer, Full-Stack Dev, Startup Founder, Campus Ecosystem Builder, Contrarian Tech Commentator). **Never force every post to mention Clstr.**

### 5. Ethical & Institutional Guardrails
- **Zero Anonymity:** Never build anonymous feeds or confessions (banned by Raghu MOU v5; breaks college trust).
- **Safety First:** Never display hostel/dorm blocks in social proof counters due to female student safety and curfew realities.
- **Free Spark for Campus Clubs:** Clstr Spark ticketing is permanently free (0% platform cut) for student clubs. Revenue comes from paid flagship experiences and commercial event ticketing.

### 6. Persistent Browser & Profile Integrity
- Always use `data-tracking/chrome-profile/` for LinkedIn automation. Never run clean or incognito browser profiles.
- Always terminate existing Chrome processes (`taskkill /F /IM chrome.exe`) before starting a Playwright session to prevent profile lock collisions.
- Use keyboard `PageDown` or `mouse.wheel` to hydrate all 17 virtualized profile sections.
- Always capture visual `.png` screenshots in `data-tracking/` as undeniable evidence.

### 7. Instant Memory Mutation
Whenever a browser crawl or user session discovers new live metrics, post engagement changes, or MOU updates, the agent must immediately update:
- `memory/normalized_2026-04-26/` (JSON and markdown summaries)
- `.agentmemory/memories.json` (Tagging appropriate concepts)
- Conversation artifacts in `<appDataDir>/brain/<conversation-id>/`

---

## 🧭 Complete Skill Dispatch Matrix

When executing any task, agents must select and execute the designated specialized skill from this matrix:

```
                                 [INCOMING TASK]
                                        │
      ┌────────────────┬────────────────┼────────────────┬────────────────┐
      ▼                ▼                ▼                ▼                ▼
[Research]       [Planning]       [Drafting]       [Quality Gate]   [Inspection]
      │                │                │                │                │
agent-reach       li-planner        li-post         li-human         Playwright
(Reddit/X/YT)   (Angle Bank)      (Voice MD)      (detect.py >=80)  (chrome-profile)
```

| Task Domain | Mandatory Skill / Tool | CLI / Execution Command | Primary Dependencies | Strict Completion Gate |
| :--- | :--- | :--- | :--- | :--- |
| **Ground Signal Discovery** | `skills/agent-reach/` | `python scripts/reach.py <channel> search "<query>"` | `r/Btechtards`, `r/developersIndia`, `r/visakhapatnam`, X | Real student quotes, placement pain points, or dev trends extracted |
| **Content Strategy & Angle Selection** | `skills/li-planner/` | `scripts/content_planner.py` | `memory/linkedin_post_writing_playbook.json`, `post_history.json` | Passes "Today Test"; 15-post dedup verified; 5 pillars rotated |
| **Hook Formulation** | `skills/li-hooks/` | `scripts/extract_hook.py` | `skills/li-hooks/hooks.json` (21 formulas) | Top 3 hook variants evaluated; thumb-stopping score verified |
| **Post Drafting** | `skills/li-post/` | `.claude/linkedin/voice.md` | `ganesh_real_tone_reference.md`, `MANUS_WORKFLOW.md` | 120–200 words; first person; 0 forced PR plugs; 1–3 hashtags |
| **Humanization & Anti-AI Audit** | `skills/li-human/` | `python skills/li-human/detect.py "<draft_file>"` | `memory/humanization_policy.json` (Sergebulaev v3 overlay) | **Score $\ge 80$** (PASS) + **0 slop words** |
| **Live Profile & Feed Inspection** | Playwright Browser Engine | `python scripts/dump_profile_text.py` & `scripts/inspect_feed.py` | `data-tracking/chrome-profile/` | Full DOM extracted; screenshot saved to `data-tracking/` |
| **Codebase Architecture & Design** | `skills/mattpocock-skills/` | `engineering/codebase-design` & `domain-modeling` | Specs, system interfaces, state boundaries | Decoupled architecture with typed domain models |
| **Implementation & Test-Driven Dev** | `skills/mattpocock-skills/` | `engineering/implement-spec` & `tdd` | Feature specs, unit/integration test suites | Red-Green-Refactor loop; 100% test pass gate |
| **Bug Diagnosis & System Triage** | `skills/mattpocock-skills/` | `engineering/diagnosing-bugs` & `triage` | Error traces, system logs, reproduction scripts | Systematic root cause confirmed before fixing |
| **Code Review & Pull Requests** | `skills/mattpocock-skills/` | `engineering/code-review` & `pr` | Git diff, commit conventions, safety checks | 0 regressions, clean PR description and changelog |
| **Requirements Grilling & Clarity** | `skills/mattpocock-skills/` | `productivity/grill-me` & `grill-with-docs` | Briefs, design contracts, edge cases | Ruthless Socratic interview to resolve ambiguity |
| **Campus Ambassador Outreach** | Outreach Automation Script | `python clstr_direct_outreach.py` | `OUTREACH_RULES.md`, `messaged_profiles.json` | 10 DMs/round max; 25-45s human typing delay; no pitch in opener |
| **Ecosystem Dev-to-Content Tracking** | Ecosystem Monitor | `python scripts/ecosystem_tracker.py` | `C:\Users\2005g\Downloads\clstr_ecosystem` | Ingests 4 repos, monitors tests, generates $\ge 80$ scored posts |
| **Product Specs & Ecosystem PRDs** | `skills/pm-skills/` | PM templates in `skills/pm-skills/` | `docs/clstr_ecosystem/` (13 specs, 74 playbooks) | Raghu MOU aligned; zero student data selling; cluster-id enforced |
| **Long-Term Memory Storage** | AgentMemory & `remember` | `.agentmemory/memories.json` | Stored concepts: `ganesh-identity`, `clstr-ecosystem`, `traction-metrics` | New durable discoveries tagged and committed to JSON |

---

## 📅 Daily Execution Rhythm for Personal Brand Management

| Phase | Time Window | Actions & Skills Used | Output Artifact |
| :--- | :--- | :--- | :--- |
| **Morning Radar** | 08:30 – 09:30 AM | Run `scripts/inspect_feed.py` to check feed engagement, 25 unread notifications, and profile viewers. Run `scripts/reach.py` for fresh Reddit/X signals. | Live feed snapshot + candidate topics |
| **Post Production** | 10:00 – 11:30 AM | 1. Select angle from `skills/li-planner/`.<br>2. Formulate 3 hooks via `skills/li-hooks/`.<br>3. Draft post using `.claude/linkedin/voice.md`.<br>4. Run `skills/li-human/detect.py` (ensure $\ge 80$). | Ready-to-publish copy + optional visual asset |
| **Human Publish** | 11:45 AM – 12:30 PM | Ganesh reviews the draft, adjusts any nuance, and clicks Post natively. | Live post published on LinkedIn |
| **Evening Review** | 06:00 – 07:00 PM | Check post engagement, reply to high-value comments in Ganesh's tone, and sync metrics into `memory/linkedin_post_history.json`. | Updated post history & network metrics |

[linkedin-agent-skill](directory;file:///c%3A/Users/2005g/Downloads/tappits-linkedin-agents/linkedin-agent-skill) [linkedin-ai-assistant](directory;file:///c%3A/Users/2005g/Downloads/tappits-linkedin-agents/linkedin-ai-assistant) [linkedin-llm-postgen](directory;file:///c%3A/Users/2005g/Downloads/tappits-linkedin-agents/linkedin-llm-postgen) [linkedin-post-generator-agent](directory;file:///c%3A/Users/2005g/Downloads/tappits-linkedin-agents/linkedin-post-generator-agent) [linkedin_post_agent](directory;file:///c%3A/Users/2005g/Downloads/tappits-linkedin-agents/linkedin-post-generator-agent/linkedin_post_agent) [LinkedInCraft-AI-Powered-LinkedIn-Post-Generator](directory;file:///c%3A/Users/2005g/Downloads/tappits-linkedin-agents/LinkedInCraft-AI-Powered-LinkedIn-Post-Generator) [linkedin-skills](directory;file:///c%3A/Users/2005g/Downloads/tappits-linkedin-agents/linkedin-skills) 

use all the required , respective skills when every required
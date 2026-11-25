# Agent Runtime Rules for tappits-linkedin-agents

These rules apply to all agents in this repository.

## Mandatory Pre-Task Memory Load

Before planning or executing any task, agents must read the following files in order:

1. `memory/normalized_2026-04-26/linkedin_master_export_deduped.json`
2. `memory/normalized_2026-04-26/goals_vision_building_focus.json`
3. `memory/normalized_2026-04-26/profile_comprehensive_analysis.json`
4. `memory/normalized_2026-04-26/normalization_summary_report.json`
5. `memory/normalized_2026-04-26/PERSONAL_SYNTHESIS_GANESH.md`

If any of the above files are missing, fall back to:

1. `memory/linkedin_master_export.json`
2. `memory/linkedin_profile_snapshot.json`
3. `memory/linkedin_recent_posts.json`
4. `memory/linkedin_comparison_report.json`
5. `memory/linkedin_prompts.json`

## Working Contract

- Use the loaded memory as first-class context for all outputs.
- Keep recommendations aligned with active focus: Scollab, Buildtrix, Clstr, and current execution priorities.
- Avoid generic answers when memory provides project-specific context.
- When new durable insights are discovered, append them to repository memory assets before task completion.

## Repository Organization Sources

- High-level map: `REPO_MAP.md`
- Machine-readable index: `.qodo/workflows/repo_inventory.json`

## Shared Content Humanization Policy

- Policy file: `memory/humanization_policy.json`
- For any LinkedIn/content generation task, load this JSON policy and apply its rules.
- If `enabled` is false, skip the humanization rewrite pass.
- Respect `constraints.project_name_whitelist` when mentioning project names in generated content.

## Hard Enforcement Guard

- Workspace hooks are enabled via `.github/hooks/memory-guard.json`.
- Session bootstrap script: `scripts/hooks/bootstrap_memory_guard.ps1`.
- Blocking pre-tool guard: `scripts/hooks/pretool_memory_guard.ps1`.
- Enforcement behavior: tool operations are denied if the normalized memory bundle is not loaded successfully.

## LinkedIn Outreach Tasks — Additional Mandatory Reads

If the task involves LinkedIn outreach, messaging, or recruitment for clstr.in, you MUST
also read these files BEFORE taking any browser or script action:

1. `OUTREACH_RULES.md` — hard rules, tone, anti-detection, volume limits, role mapping
2. `memory/normalized_2026-04-26/ganesh_real_tone_reference.md` — Ganesh's actual voice and message patterns
3. `data-tracking/messaged_profiles.json` — who has already been messaged (dedup check)
4. `memory/normalized_2026-04-26/clstr_ambassador_program.json` — full program details, benefits, outcomes, eligibility (sourced from live clstr.in/campus-ambassadors page)

### Outreach Hard Constraints (summary — full detail in OUTREACH_RULES.md)

- **Run the script**: always execute `python clstr_direct_outreach.py` — never improvise your own flow
- **10 per round max**: stop after 10 DMs regardless of anything else
- **One at a time**: complete one profile fully before starting the next — no parallel work
- **25-45s delay**: mandatory human-speed wait between every message
- **Verify name + college**: skip any profile where either cannot be confirmed
- **No dedup bypass**: never message a URL already in `data-tracking/messaged_profiles.json`
- **Tone is non-negotiable**: 2 sentences max, casual, first name, specific signal, one question
- **First message = no pitch**: no form link, no phone number, no clstr.in description in opener
- **Form + phone only on positive reply**: share `https://forms.gle/2NYjiunqeUk3WUDh9` and `9441467303` only when they express interest
- **Human typing**: character-by-character, 30-80ms per char — never paste
- **Persistent Chrome profile**: always use `data-tracking/chrome-profile/` — never fresh/incognito
- **Anti-detection**: `--disable-blink-features=AutomationControlled` must be set, `navigator.webdriver` must be removed

## LinkedIn Original Daily Post Tasks — Additional Mandatory Reads

If the task involves creating a native LinkedIn post (daily viral data post), you MUST
also read these files and run the checker script BEFORE taking any action:

1. `LINKEDIN_ORIGINAL_POST_RULES.md` — complete pipeline rules, Antigravity tool chain, voice, image template, dedup logic
2. `memory/normalized_2026-04-26/ganesh_real_tone_reference.md` — Ganesh's actual voice patterns
3. `memory/linkedin_post_history.json` — dedup check (never repeat recent topics or hook types)
4. `memory/linkedin_post_writing_playbook.json` — hook formulas, algorithm rules, content pillars
5. Run the live checker: ALWAYS run `python check_linkedin_posts.py` first to sync state.

### Original Post Hard Constraints (summary — full detail in LINKEDIN_ORIGINAL_POST_RULES.md v10.0)

- **Run checker first**: ALWAYS run `python check_linkedin_posts.py` before generating or planning a post to sync with actual LinkedIn state.
- **Use Antigravity tools**: use `search_web` + `generate_image` + `run_command` — never use python browser-use library
- **Human-final-action posting (v10.0)**: agent prepares everything (text, image, clipboard) but does NOT click Post. Ganesh publishes manually in his own browser, or uses LinkedIn's native scheduling. See Section 9.
- **Once per day max**: never post more than one time per day from this pipeline
- **Weekdays only**: Mon–Fri per Section 5's calendar — never post on weekends
- **Research first**: always `search_web` for fresh trends before writing — no evergreen-only posts. Apply the "Today Test" (Section 15).
- **Context fingerprint dedup**: generate a 5-8 word `context_fingerprint` for every post. HARD BLOCK if same insight appeared in last 15 posts — even if format/style changed. See Section 12.
- **"Teach Something New" gate**: before writing, answer: "What NEW thing will the reader learn that they couldn't learn from ANY of my last 15 posts?" If you can't answer clearly → pick a different angle from the Angle Bank.
- **Angle Bank**: pick angles from the 56-angle registry. Mark used angles. Never rehash the same underlying insight.
- **Pillar rotation (v10.0 merged taxonomy)**: no pillar more than 2× in any 5 consecutive posts. Use the 5 Pillars + 3 Cross-Cutting Modifiers system (Section 3) — old "Topic Families" are merged into this.
- **Builder's Log**: every Wednesday morning, publish a "Builder's Log — Week N" entry (Section 8)
- **Dedup check**: read post_history.json — 15-post lookback for topic, context fingerprint, hook, pillar, framework (Section 12)
- **120-200 words**: hard cap on post length (Track B); 1-10 words for meme/humor (Track A)
- **Format variety**: not every post needs an image. Use text-only for hot takes, questions, stories. Use PDF carousels weekly.
- **Writing framework rotation**: never use same framework (PASS/SLAY/Herubel) more than 3 times in 5 posts
- **quote_card removed (v10.0)**: this post type is fully retired. Use `relatable_meme` or text-only instead.
- **Ganesh voice only**: check every sentence against on-voice examples in ganesh_real_tone_reference.md
- **No links in body**: external links go in first comment, never in post text. Edit Method for high-stakes posts (Section 10).
- **Hashtags: 1-3, default 2**: at the very end of the post only
- **End with a question**: always close with a genuine, specific engagement question — never a generic CTA like "Follow/Repost/Save"
- **Log everything**: update linkedin_post_history.json (including context_fingerprint + pillar + modifier) AND data-tracking/post_native_log.json after every run
- **V3 humanization overlay**: `memory/humanization_policy.json` v1.1.0+ includes `sergebulaev_v3_overlay` — vocab density list, em-dash cap 1/100w, reveal-bridge blacklist, pass-2 rhythm rules, pass-4 over-correction guard. All generated content must respect the project_name_whitelist gate for "clstr.in".

## Founder Visibility & Continuous Intelligence Layer (Agent-Reach + LinkedIn Agent Skill)

Always execute founder visibility and content intelligence workflows with these two unified toolkits:

1. **Agent Reach (`skills/agent-reach/` & `agent-reach/`)**:
   - Primary research engine for real-time ground signals across external platforms:
     - **Reddit**: Deep search on `r/Btechtards`, `r/developersIndia`, `r/visakhapatnam`, and `r/Indian_Academia` for genuine student pain points, placement realities, and campus sentiment.
     - **X / Twitter**: Track Indian tech founder discourse, hackathon announcements, and engineering student debates.
     - **YouTube**: Extract video transcripts and key takeaways from founder interviews and higher-ed discussions.
     - **GitHub**: Search student repositories and open-source tools.
   - Run via `python scripts/reach.py <channel> <action>` or `python -m agent_reach.cli <channel> <action>`.

2. **LinkedIn Agent Skill (`linkedin-agent-skill/` & `.claude/linkedin/voice.md`)**:
   - Every post, comment, and profile revision must follow Ganesh's configured voice in `.claude/linkedin/voice.md`.
   - Post generation must draw from the 21 hook formulas (`skills/li-hooks/`).
   - Every draft must pass the humanizer and detection engine (`skills/li-human/detect.py`) scoring $\ge 80$ with 0 slop words before presentation.

---

## 🧭 Mandatory Skill Dispatch Matrix (Task-to-Skill Routing)

Every agent MUST route tasks to the corresponding specialized skill before executing work:

| Task Domain | Primary Skill / Engine | Execution Mechanism | Key Inputs & Policy | Quality & Completion Gate |
| :--- | :--- | :--- | :--- | :--- |
| **External Signal & Trend Discovery** | `skills/agent-reach/` | `python scripts/reach.py <channel> search "<query>"` | Reddit (`r/Btechtards`, `r/developersIndia`, `r/visakhapatnam`), X, YouTube, GitHub | Real-world student pain points or founder discussions sourced |
| **Content Strategy & Calendar Planning** | `skills/li-planner/` | `scripts/content_planner.py` | `memory/linkedin_post_writing_playbook.json`, `memory/linkedin_post_history.json` | Passes the "Today Test"; 15-post dedup check; pillar rotation satisfied |
| **Hook Formulation** | `skills/li-hooks/` | `scripts/extract_hook.py` | `skills/li-hooks/hooks.json` (21 verified formulas) | Top 3 hook variants evaluated; thumb-stopping score verified |
| **Post Drafting & Tone Formatting** | `skills/li-post/` | `.claude/linkedin/voice.md` & `ganesh_real_tone_reference.md` | `MANUS_WORKFLOW.md` (6 builder facets) | 120–200 words; first person; 0 forced corporate plugs; 1–3 hashtags |
| **Anti-AI Detection & Humanization** | `skills/li-human/` | `python skills/li-human/detect.py "<draft_file>"` | `memory/humanization_policy.json` (Sergebulaev v3 overlay) | **Score $\ge 80$** (PASS) + **0 slop words** |
| **Live Browser Crawling & Feed Audit** | Playwright + Persistent Chrome Profile | `python scripts/dump_profile_text.py` & `python scripts/inspect_feed.py` | Profile at `data-tracking/chrome-profile/` | Full DOM extraction + visual screenshot saved to `data-tracking/` |
| **Product Specs & Ecosystem GTM** | `skills/pm-skills/` | PM playbooks in `skills/pm-skills/` | `docs/clstr_ecosystem/` (13 architecture specs, 74 playbooks) | Grounded in Raghu MOU v5, zero student data selling, 0% fee on campus clubs |
| **Instagram Content & Reels Engine** | `skills/ig-*/` | `python skills/ig-reel/hookscore.py` & `python skills/ig-human/detect.py` | `.claude/instagram/voice.md` & `skills/ig-*/` | 13 Instagram skills (Reels, Captions, Stories, Humanizer, Carousels, Viral Swipe) |
| **Long-Term Memory Preservation** | `remember` & AgentMemory | `.agentmemory/memories.json` + `memory/normalized_2026-04-26/` | Durable metrics, newly scraped profile stats, viral benchmarks | Normalized JSON files and concept tags immediately updated |

---

## 🛡️ Browser & Profile Safety Operating Rules

1. **Persistent Session Protection**:
   - Always use `data-tracking/chrome-profile/`. Never launch a raw, unauthenticated, or incognito browser for LinkedIn tasks.
   - Always check for and terminate orphan Chrome processes (`taskkill /F /IM chrome.exe`) before starting a Playwright session to avoid SQLite profile lock collisions.
2. **Keyboard Navigation & DOM Hydration**:
   - LinkedIn uses aggressive virtualized rendering. All scrapers must use keyboard `PageDown` or `page.mouse.wheel()` loops to ensure all 17 profile sections and feed posts hydrate.
3. **Visual Ground-Truth Mandate**:
   - Every browser inspection must capture high-resolution `.png` screenshots to `data-tracking/` and mirror them to the conversation artifact directory for auditability.
4. **Immediate Memory Synchronization**:
   - Any live metric change (e.g. followers, connections, impressions, unread messages) must immediately be committed to `memory/normalized_2026-04-26/` and `.agentmemory/memories.json`. Never leave live discoveries in transient context.





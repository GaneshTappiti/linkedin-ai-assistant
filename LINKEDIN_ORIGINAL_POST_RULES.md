# LinkedIn Growth System v10.0 — Consolidated & Reconciled
## Ganesh Tappiti / clstr.in — Single Source of Truth

> **This file replaces v5.0 through v9.0.** Every rule below has been checked against
> every other rule for contradictions. Where two old sections disagreed, this file states
> which one won and why. Nothing in this document needs cross-referencing against an older
> version — if it's not here, it's retired.
>
> **One change from prior versions that actually matters for safety, not just cleanup:**
> the posting mechanism in Section 9 now has a human performing the final publish action.
> Everything else — research, writing, image generation, dedup — stays automated. See
> Section 9 for why, and the companion audit report for the reasoning in full.

---

# 1. WHO THIS IS FOR

**Ganesh Tappiti** — 21, CSM student at Raghu Engineering College, Vizag. Founder/solo technical lead of **clstr.in**, a verified campus operating system for Indian colleges, currently live at 4 colleges with 14 production features. Also building Buildtrix (AI MVP validator, submitted to YUKTI) and Scollab (AI academic hub, YC target). Leads a 16-member design team. Stack: React, Supabase, Firebase, Node.js, Figma, AI/LLM/RAG.

**Current state (update these numbers each review cycle):**
- Followers: 1,557 → target 5,000 by Sept 2026
- Avg impressions/post: 1,592 → target 50,000+
- Avg comments/post: 0.5 → this is the #1 thing every rule below is designed to fix
- Top post ever: 3,492 impressions (CIC I3 Conclave, community/ecosystem content)

**Who Ganesh is NOT:** not an influencer, not a motivational poster, not a marketer. A builder who documents what he's actually shipping.

---

# 2. THE ALGORITHM — WHAT'S TRUE IN 2026 (unchanged from v9.0, verified)

| Signal | Weight | What triggers it |
|---|---|---|
| **Saves** | Highest single signal | Data lists, frameworks, how-tos, tool recommendations — anything worth bookmarking |
| **Meaningful comments (15+ words)** | 2nd highest, several multiples above a like | Specific, debatable, easy-to-answer closing questions |
| **Dwell time** | Core ranking input | Carousels (swipe resets the clock), structured long reads, anything that earns a real read, not a glance |
| **Shares with commentary** | High | Contrarian takes, surprising data, quotable lines |
| **Comment reply depth (3+ exchanges)** | High, compounds distribution | Reply within 60 min with a follow-up question, not "Thanks!" |
| **Reactions (likes)** | Lowest — useful for early velocity only | Never optimize for this alone |

**Suppressed:** external links in post body (25–60% reach penalty), engagement bait ("comment YES if…"), AI-sounding generic phrasing, posts ignored in the first 90 minutes, coordinated/pod-style engagement (LinkedIn's 2026 detection is explicitly built to catch this).

**Amplified:** zero-link native content, consistent niche/topical authority, personal stories with a real takeaway, creators who reply to their own comments, document/PDF carousels (highest dwell time of any format).

---

# 3. CONTENT PILLARS + TOPIC FAMILIES (merged — this fixes the old dual-taxonomy bug)

There are **5 pillars** (what Ganesh's authority is built on) and **3 cross-cutting modifiers** (tone/format layers that can attach to any pillar). Old v9.0 had "8 Topic Families" running in parallel with no mapping — that's gone. Everything is one tree now.

### The 5 Pillars
| Pillar | Covers | Old "Topic Family" names this absorbs |
|---|---|---|
| **1. Build in Public** | clstr.in/Buildtrix/Scollab updates, metrics, architecture decisions, failures | Founder Journey, Validation/Research |
| **2. AI-Enabled Building** | How AI tools change building — practical, hands-on, with real prompts/configs | AI/Tech/Tools |
| **3. Campus Ecosystem** | Indian campus infrastructure problem, hiring/skills gap, ambassador growth | Campus/Hiring |
| **4. Founder Psychology** | The mental game — discipline, balance, leadership, doubt | Leadership/Team (when about Ganesh's own growth) |
| **5. Design × Engineering** | Product/design decisions, architecture, taste | Design/Product |

### The 3 Cross-Cutting Modifiers (attach to any pillar, tracked separately)
| Modifier | What it does | Rule |
|---|---|---|
| **Personal Life** | Grounds a pillar post in Ganesh's actual life (college, gym, family, friends) | At least 1 post per 5 must carry this modifier |
| **Dev Humor** | Memes/light format — can be its own post OR a tone layer on a pillar post | At least 1 post per 5 must carry this modifier |
| **Newsjack/Industry Commentary** | Reacting to a current event/launch | Capped at 1 per 5 posts (was inconsistently 20%/2-per-10/1-per-5 across old sections — 1-per-5 is now the single number) |

**Rotation rule:** no pillar more than 2× in any 5 consecutive posts (tightened per v8.0's intent, now the only number — old doc had "2 in 5" in one place and "3 in 5" in another).

---

# 4. POST TYPES (13 total — quote_card removed)

`quote_card` is fully retired. It was marked deprecated in the old Section 16 but kept alive in five other places — that inconsistency is fixed by deleting it everywhere. Its slot in any calendar or rotation defaults to `relatable_meme` or a text-only post instead.

| # | Type | Goal | Primary signal | Frequency |
|---|---|---|---|---|
| 1 | `research_data` | Reach via data | Saves + dwell time | 2×/week |
| 2 | `hot_take` | Debate | Comments + shares | 1×/week |
| 3 | `personal_story` | Trust | Dwell time + saves | 1×/week |
| 4 | `build_in_public` | Credibility | Comments + saves | 1×/week |
| 5 | `educational_howto` | Authority | Saves (highest) | 1× per 2 weeks |
| 6 | `industry_commentary` | Timeliness | Shares + comments | capped — see Section 3 |
| 7 | `question_engagement` | Community | Comments (highest) | 1× per 2 weeks |
| 8 | `resource_recommendation` | Trust | Saves + shares | 1× per 2 weeks |
| 9 | `win_milestone` | Social proof | Reactions + comments | 1×/month |
| 10 | `behind_the_scenes` | Authenticity | Dwell time + comments | 1× per 2 weeks |
| 11 | `relatable_meme` | Follower acquisition | Shares + reactions | 2–3×/week |
| 12 | `pdf_carousel` | Max dwell + saves | Saves + dwell time | 1×/week |
| 13 | `tool_discovery` | Saves + credibility | Saves + shares | 1×/week |
| 14 | `framework_mental_model` | Authority | Saves + dwell time | 1× per 2 weeks |

---

# 5. THE WEEKLY CALENDAR (one cadence — replaces both old "Double-Tap" and old "v7.0 quality" tables)

The old doc had three overlapping cadence systems (Sections 6, 22, and 35) that disagreed with each other on Thursday/Friday specifically. This is the one calendar. It absorbs Section 39's minimums (1 text-only/week, 1 video/10, 1 meme/week, 1 personal/week) as built-in slots rather than bolt-on rules layered over a different table.

| Day | Slot | Category | Type | Format |
|---|---|---|---|---|
| Monday | AM (10–11:30 IST) | Insight | `research_data` or `educational_howto` | PDF carousel |
| Monday | PM (7–8:30 IST) | Viral | `question_engagement` | Text-only |
| Tuesday | AM | Viral | `relatable_meme` | Single image |
| Tuesday | PM | Opinion | `question_engagement` or skip | Text-only |
| Wednesday | AM | **Builder's Log (fixed weekly slot — see Section 8)** | `behind_the_scenes` | Text-only or multi-image |
| Wednesday | PM | Viral | `question_engagement` | Text-only |
| Thursday | AM | Opinion | `hot_take` | Text-only, no image |
| Thursday | PM | — | REST | — |
| Friday | AM | Story | `build_in_public` | Multi-image (real screenshots) |
| Friday | PM | Viral | `relatable_meme` | Single image |

**Hard floors per week (these were scattered across 3 old sections — now in one place):**
- 7–10 posts/week max, skip a slot rather than post something mediocre
- Minimum 2 text-only posts/week
- Minimum 1 meme/week (already covered by the calendar above — Tue + Fri AM)
- Minimum 1 personal-modifier post/week
- Maximum 2 `research_data`/week, maximum 1 `industry_commentary` per 5 posts
- At least 1 video post per 10 posts (no fixed day — opportunistic, when there's a real demo/screen-recording worth showing)
- Minimum 4 hours between same-day posts if doubling up; never post on weekends

---

# 6. HOOK FORMULAS (21, consolidated — H1 through H21 kept, duplicates removed)

Rotation rule: never repeat the same hook formula in the last 3 posts. Never repeat the same *opener pattern* (e.g., "Everyone says X," "🚨 breaking," "I scanned X") more than 2× in any 10 posts — this was Ghadeer's biggest weakness per the competitor audit (Section 13 below) and is now a hard cap, not a suggestion.

| # | Formula | Best for | Example |
|---|---|---|---|
| H1 | "I scanned [N] [sources] in [timeframe]." | research_data | "I scanned 280 student founder stacks." |
| H2 | "[Bold contrarian statement]." | hot_take | "CGPA still matters. Just not how you think." |
| H3 | "[N] months ago, [tension]." | personal_story | "8 months ago, clstr.in was a Notion doc." |
| H4 | "Nobody talks about [uncomfortable truth]." | hot_take, commentary | "Nobody talks about how unpaid most student internships are." |
| H5 | "[Company] just [did X]. Here's what it means." | industry_commentary | "Google just shipped agents to 1B phones." |
| H6 | "I built [X] in [timeframe]. Here's what worked." | build_in_public | "I built 14 features with ₹0 funding." |
| H7 | "[Specific provocative question]?" | question_engagement | "Would you hire a 6.5 CGPA with 4 GitHub projects?" |
| H8 | "Here's how I [outcome] without [expected thing]." | educational_howto | "Here's how I learned system design without paid courses." |
| H9 | "We just hit [milestone]. Full breakdown." | win_milestone | "500 students on clstr.in. Here's the breakdown." |
| H10 | "Behind every [polished thing] is [messy reality]." | behind_the_scenes | "Behind every demo day is 3 failed pitches." |
| H11 | "I [unexpected action]. [Surprising result]." | personal_story | "I deleted our whole stack. Signups went up." |
| H12 | "[Tool] changed how I [do X]." | resource_recommendation | "Cursor + Supabase changed how I ship." |
| H13 | "[1–3 word trigger]" | relatable_meme | "Every. Single. Time. 😅" |
| H14 | "[N] months ago, [before]. Today, [after]." | personal_story, win_milestone | "7 months ago: Notion doc. Today: 500 students." |
| H15 | "Swipe → to see [value]" | pdf_carousel | "Swipe → what Indian startups pay AI engineers." |
| H16 | "[Relatable struggle] 😅" | relatable_meme | "Explaining clstr.in to my parents 😅" |
| H17 | "Everyone says [X]. The opposite happened." | hot_take, research_data | "Everyone said AI would replace devs. Opposite happened." |
| H18 | "A [company] engineer just shipped [X]." | tool_discovery | "A Netflix engineer just cut token usage 60-95%." |
| H19 | "[Ironic 1-liner] 😂" | relatable_meme | "Trusted ChatGPT. Then it trusted me back. 😶" |
| H20 | "[Bold claim + number]. [Pivot]." | research_data, commentary | "AI labs pay $750K+. Stanford teaches it free." |
| H21 | "🚨 [Breaking discovery]" | tool_discovery, commentary | "🚨 You can run any LLM on Codex now." |

---

# 7. POST FORMATTING — THE 11 RULES (from competitor pattern analysis, unchanged from v9.0)

These were genuinely good and are kept as-is:

1. **Arrow lists (→) over dashes/bullets.**
2. **One sentence per line.** Mobile shows ~40 chars/line — short lines earn more "see more" clicks.
3. **1–2 emojis max, used as punctuation** (😂 at the end of a joke), never as decoration (🚀🔥💡✨🎯 stacked).
4. **Links: see Section 10 below** (this replaces the old contradictory Sections 13 and 38).
5. **Hashtags: 1–3, default 2.** (Was inconsistently "3" in templates and "2-3" in rules — 2 is now the default, 3 the ceiling, 1 acceptable for high-authority posts.)
6. **No generic CTA footers.** Banned: "Follow for more," "Repost to help others," "Save for later," "Comment YES," "Tag someone." Every closing line must be a specific, answerable question.
7. **The "would you scroll past?" test** — if the first 2 lines don't create curiosity or emotion in ~8 words, rewrite before doing anything else.
8. **At least 1 text-only post per 7** (folded into Section 5's weekly floors).
9. **At least 1 video post per 10** (folded into Section 5).
10. **One concept per post.** Never mix two ideas in one post — dilutes the takeaway and the save-worthiness.
11. **Opener pattern cap: max 2× per 10 posts** for any single hook *family* (not just formula — "Everyone says X" and "Everyone said X" count as the same family).

---

# 8. BUILDER'S LOG — THE SIGNATURE WEEKLY SERIES

Every **Wednesday AM** (fixed slot in Section 5's calendar — this is the one post type exempt from the "don't repeat post_type 2 days running" rule, since it's a recognized recurring series):

```
📋 Builder's Log — Week [N]

This week at clstr.in:

✅ Shipped: [1–2 specific things]
🔧 Building: [what's in progress]
❌ Broke: [what went wrong — be honest, this section is non-negotiable]
💡 Learned: [one specific insight]

[One specific question to other builders]

#BuildInPublic #StudentFounders
```

Max 120 words. `behind_the_scenes` type, H10 hook. Alternate Track A/B caption length weekly. This is your habit-forming anchor — readers should come to expect it.

---

# 9. POSTING MECHANISM — THE ONE REAL CHANGE FROM v9.0

**What changes:** the agent stops being the thing that clicks "Post." A human does that part. Everything upstream of it stays exactly as automated as it was.

**Why:** LinkedIn's own published policy (not a third-party guess) prohibits browser plug-ins, extensions, or bots that "automate activity" on the site — full stop, independent of how human-like the timing looks. Section 17 of the old doc (remote-debugging Chrome, scripted clicks/paste/type, anti-detection flags like disabling `navigator.webdriver`) is precisely the mechanism that policy names. The fact that the old doc needed anti-detection measures at all is the tell — if the activity needed to evade detection, it was the kind of activity detection exists to catch. The risk isn't hypothetical: account restrictions for this exact category of tool are documented and recoverable-but-disruptive at best, permanent at worst, and clstr.in's whole growth thesis depends on this one account staying alive.

**What the agent still does, fully unattended:**
- Research (web search for fresh data, GitHub trending, industry news)
- Dedup checks against post history (Sections 12–14)
- Writing the full post text
- Generating the image (carousel slides, charts, memes — all of Section 11's styles)
- Preparing the image file and copying it to clipboard
- Updating the post-history log after publishing

**What now requires you, manually, in your own normal browser session (not the debug-port Chrome):**
- Opening LinkedIn, clicking "Start a post"
- Pasting the prepared image (Ctrl+V — the agent already put it on your clipboard)
- Pasting the prepared text
- Clicking "Post"
- This is genuinely ~60 seconds of your time per post, not a meaningful workflow tax

**Alternative if you want zero manual steps for non-time-sensitive posts:** LinkedIn has its own native post-scheduling feature. The agent can hand you the finished post+image and you schedule it natively a few times a week in one sitting, rather than per-post same-day action. This is explicitly allowed because it's LinkedIn's first-party tool, not injected automation.

**Comment replies:** same logic. The agent can draft replies for the first-hour engagement window (Section 2's "reply within 60 min" rule still applies and still matters), but you send them yourself. A drafted-reply queue you approve with one tap is the right shape here, not auto-posting.

---

# 10. LINK STRATEGY (unified — replaces the old Section 13 vs. Section 38 contradiction)

**Default rule:** links go in the first comment, never in the post body. This is what the highest-performing reference profile (eordax) does consistently, and it's the standard 2026 workaround.

**When to use the more conservative Edit Method instead** (post with zero links anywhere → wait 30–60 min for initial engagement → edit the post to add a link only if truly necessary): use this for anything you'd be upset to lose reach on if LinkedIn's comment-link detection tightens further — i.e., your highest-stakes launch posts, not routine `tool_discovery` posts. For routine tool/repo shares, first-comment is fine and is now the single default.

**Never:** link in the post body itself. No exceptions, no "but it's worth it this once."

---

# 11. IMAGE STYLES — 6-STYLE ROTATION SYSTEM

**NEVER repeat the same style two posts in a row.** Always check `linkedin_post_history.json` for the last used `image_style` and pick the next in the cycle.

### ROTATION CYCLE (1 → 2 → 3 → 4 → 5 → 6 → 1 → ...)
- **Style 1: Dark Brand Slide** — #080808 black, clstr logo, white bold title, tool diagram/mockup
- **Style 2: Light Editorial Card** — cream white, bold black serif, pastel accent color, flat vector
- **Style 3: Data / Stats Visual** — big numbers, bar/pie chart, data journalism aesthetic (dark or light)
- **Style 4: Relatable Meme / Comic** — Flork/flat vector comic, 10-word punchline, builder humor
- **Style 5: Notebook / Sketch Card** — off-white paper, pen-stroke aesthetic, hand-drawn, warm
- **Style 6: Bold Quote Card** — full-bleed color, single quote ≤10 words, magazine typographic

**Log the style used** in every `linkedin_post_history.json` entry under `"image_style"`.

---

### Style 1 — Dark Brand Slide (Pillow Hybrid Required)
**Best for:** Tool discoveries, build-in-public updates, industry commentary, hot takes.

| Element | Spec |
|---|---|
| Canvas | 1080×1080px, `#080808` |
| Header divider | `#1a1a1a`, y=108px |
| Header text | Courier New mono, 16px, white 80% |
| clstr logo | 3 white circles + 2 lines, top-left (52, 128) |
| Page number | Omit for single posts; carousels only |
| Headline | Arial Bold, 48–56px, white, center-aligned |
| Cards | Rounded rect, `#0066FF` stroke, `#0D0D0D` fill, 12px radius |
| Arrows | `#0066FF`, 2px, 8px arrowhead polygon |
| Watermark | `@ganeshtappiti`, Arial 14px, white 30%, bottom-right |
| **Logos** | **ALWAYS fetch official favicon/PNG — never AI-generated** |

---

### Style 2 — Light Editorial Card
**Best for:** Personal stories, campus/student posts, opinion pieces, reflective founder posts.

| Element | Spec |
|---|---|
| Background | Warm cream `#FAFAF7` |
| Headline | Bold serif, black, large, left-aligned |
| Accent | Single pastel underline: coral `#FF6B6B`, sage `#6BCB77`, or sky blue `#4DABF7` |
| Illustration | Flat vector scene (NOT photorealistic) |
| clstr logo | 3 black circles, top-left |
| Watermark | Muted gray, bottom-right |

---

### Style 3 — Data / Stats Visual
**Best for:** "X% of devs..." hooks, comparison posts, metrics, research-backed posts.

| Element | Spec |
|---|---|
| Theme | Alternate dark (`#111111`) and light (`#FFFFFF`) each time |
| Chart type | Bar, pie, or stat comparison panel — not decorative |
| Numbers | Min 36px visible at thumbnail size |
| clstr logo | Top-left |
| Watermark | Bottom-right |
| Note | Use Pillow if chart needs exact pixel precision |

---

### Style 4 — Relatable Meme / Comic
**Best for:** Relatable dev/founder/student humor, cultural tie-ins, engagement-bait.

| Element | Spec |
|---|---|
| Art style | Flork-style flat vector comic or two-panel editorial |
| Punchline | ≤10 words, bold sans-serif caption |
| Watermark | `@ganeshtappiti`, bottom-right, small gray |
| Rules | NOT for serious commentary; keep humor to founder/builder culture |

---

### Style 5 — Notebook / Sketch Card
**Best for:** Wednesday Builder's Log (mandatory), framework/mental model posts, behind-the-scenes.

| Element | Spec |
|---|---|
| Background | Off-white paper texture `#FAF7F0` |
| Lines | Rough pen-stroke ruled lines |
| Diagram | Clean hand-drawn sketch: loops, arrows, phases |
| Fonts | Handwriting-style: bold headers black, notes in dark gray |
| Signature | `@ganeshtappiti` stamped in ink blue, bottom-right |

---

### Style 6 — Bold Quote Card
**Best for:** Hot take posts, single punchy insight, opinion post with one strong sentence.

| Element | Spec |
|---|---|
| Background | Full-bleed accent: indigo `#1A1A6E`, teal `#0B4F6C`, or amber `#B45309` |
| Quote | ≤10 words, white bold sans-serif, large centered |
| Attribution | `— @ganeshtappiti`, white 60% opacity, below divider |
| clstr logo | White, top-left |
| Watermark | Not needed (attribution inside suffices) |

---

### Post Type → Style Default Mapping

| Post Type | Default Style | Fallback |
|---|---|---|
| `tool_discovery` | Style 1 — Dark Brand Slide | Style 3 — Data |
| `hot_take` | Style 6 — Bold Quote Card | Style 1 or text-only |
| `personal_story` | Style 2 — Light Editorial | Style 5 — Notebook |
| `build_in_public` | Style 1 or Style 3 | Real screenshots |
| `educational_howto` | Style 3 or PDF carousel | Style 5 |
| `industry_commentary` | Style 1 or Style 6 | text-only |
| `question_engagement` | Style 4 — Meme or Style 2 | text-only |
| `resource_recommendation` | Style 1 or Style 2 | Style 3 |
| `win_milestone` | Style 2 or Style 6 | Style 3 |
| `behind_the_scenes` | Style 5 — Notebook | Style 2 |
| `relatable_meme` | Style 4 — Meme | Style 6 |
| `pdf_carousel` | Style 1 (cover slide) | Style 3 |
| `framework_mental_model` | Style 5 — Notebook | Style 3 |
| `research_data` | Style 3 — Data | Style 1 |

---

### Rotation Hard Rules
1. **Never repeat the same style in consecutive posts.**
2. **At least 4 distinct styles in any rolling 5-post window.**
3. **Style 5 (Notebook) is mandatory for every Wednesday Builder's Log post.**
4. **Style 4 (Meme) max once per 5 posts** — don't over-meme the feed.
5. **Check `image_style` field in last 3 entries in `linkedin_post_history.json` before picking.**

---

### Programmatic Slide Composing Protocol (Strict Quality Guard)
For any post needing crisp typography, exact padding, official logos, or diagram elements:

1. **AI Base Generation:** Use `generate_image` to generate only the central background, scene, or mockup visual. Never use it to render logos, brand names, or data labels.
2. **Official Logo Extraction:** Fetch official transparent PNGs from `favicon.ico` at the brand's domain or from `unpkg.com` CDN packages. Save to `scratch/logos/`.
3. **Pillow Hybrid Composition:** Write a Python script using PIL (Pillow):
   - Canvas: 1080×1080px, pitch-black `#080808` for Style 1.
   - Crop the clean AI-generated visual from the background image.
   - Render all text, cards, arrows, logos, and layout elements programmatically.
   - Use system fonts: `C:/Windows/Fonts/arialbd.ttf` (bold) and `C:/Windows/Fonts/arial.ttf` (regular).
   - Save output PNG to `memory/post_images/[DATE]_[SLUG].png`.
4. **Staging:** Run clipboard PowerShell script (`scripts/copy_image.ps1`) to stage the final image for publication.

---

# 12. ANTI-REPETITION SYSTEM (kept fully intact — this was the best part of v9.0)

### Context Fingerprint (unchanged from old Section 36)
Every post gets a 5–8 word `context_fingerprint` capturing its *core insight*, not its topic or format. Compare against the last 15 fingerprints before writing. If a new fingerprint shares >50% of its meaning with an existing one — even in a totally different format — it's blocked. This is what catches "AI tools colleges don't teach" being reposted five times as a chart, then a hot take, then a carousel, then a meme.

### Teach-Something-New Gate (unchanged from old Section 37)
Before writing, answer: *"What will the reader learn here that they couldn't learn from any of my last 15 posts?"* Vague or overlapping answers block the post. The Angle Bank (56 pre-mapped angles across all 5 pillars, from old Section 37) stays exactly as-is — it's good work and didn't need fixing.

### The Pre-Generation Checklist (merged from old Sections 18 + 30 + 36, one list now instead of three)
- [ ] Different `post_type` from the last post
- [ ] Different `image_style` from the last 3 posts (or none, if text-only)
- [ ] Different `hook_formula` from the last 3 posts; different opener *pattern* from the last 10
- [ ] Different pillar from the last 2 posts; no pillar >2× in last 5
- [ ] Different `context_fingerprint` from the last 15 — checked for *meaning* overlap, not just literal topic
- [ ] Industry/newsjack cap respected (max 1 per 5)
- [ ] Personal-modifier and humor-modifier floors respected (≥1 per 5 each)
- [ ] "Teach Something New" answered concretely, not vaguely
- [ ] Writing framework (PASS/SLAY/Herubel) not used 3+ times in the last 5 posts

---

# 13. COMPETITOR PATTERN LIBRARY + ANTI-PATTERN BLOCKS (kept, unchanged from old Section 38/39)

The 6 proven high-engagement patterns (Tool Discovery, Contrarian Flip, Ultra-Short Humor, Data Escalation, Free Resource Reveal, Personal Milestone Reflection) and the explicit anti-pattern hard blocks for each reference creator (Ghadeer's single-niche/no-humor problem, Rishabh's hashtag bloat and lack of depth, eordax's volume and sponsored-content risk) all carry over unchanged from the old doc — this analysis was sound and specific, and nothing about it conflicted with anything else. Refer to the original Section 38/39 content; nothing here supersedes it.

One addition: the **opener-pattern cap** (max 2× per 10 posts for the same hook family) that was implicitly the lesson from Ghadeer's "6 of 11 posts start with 'Everyone says X'" weakness is now an explicit rule (Section 7, Rule 11) instead of just a cautionary note.

---

# 14. clstr.in PRODUCT DATA BANK (kept verbatim from old Section 31)

All 14 features, the architecture decisions, the student lifecycle map, and the 12 rotating post ideas from the old Section 31 are unchanged and still your factual source of truth for any `build_in_public` post. Never fabricate a metric not listed there — ask yourself for the current number if it's not in the bank, update the bank, then write the post.

---

# 15. RESEARCH PROTOCOL FOR FRESH CONTENT (kept, unchanged from old Section 40)

Before any post: web-search for something from the last 7 days (GitHub trending, industry reports, dev/HN discussion, campus/hiring news). Apply the "Today Test" — *why is this post relevant today and not any day in the last six months?* Rotate across at least 4 of the 6 source types per week (GitHub Trending, Industry Reports, Ganesh's Real Week, Dev Twitter/HN, Peer Founders, Campus/Hiring News). Never state a stat, benchmark, or star count without having verified it live in that research pass.

---

# 16. PRE-PUBLISH CHECKLIST (final, merged)

- [ ] Post history read, fingerprint + dedup checks (Section 12) all pass
- [ ] Fresh research completed for this week's "Today Test" (Section 15)
- [ ] Pillar + modifier selected, rotation rules respected (Section 3)
- [ ] Post type + hook formula selected, no repeats per Section 12's checklist
- [ ] Caption track and word count correct (Track A: 1–10 words for memes; Track B: 120–200 words for everything else)
- [ ] First 2 lines pass the "would you scroll past?" test
- [ ] No banned CTA footers, no engagement bait
- [ ] Links (if any) in first comment, never in body — Edit Method only for high-stakes posts
- [ ] 1–3 hashtags, default 2
- [ ] Image style selected and rotation-checked, or deliberately text-only
- [ ] Ganesh's real voice — on-voice examples match, off-voice phrases absent
- [ ] Post + image staged for **manual** publish (Section 9) — agent does not click Post
- [ ] Log updated after you confirm it's live

---

*Version 10.0.0 — Consolidated from v5.0–v9.0. All contradictions resolved per the companion audit report. Quote_card removed. One cadence, one taxonomy, one link policy, one version number. Posting mechanism changed to human-final-action per LinkedIn's published automation policy.*

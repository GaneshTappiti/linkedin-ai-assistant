# Manus Daily LinkedIn Viral Engine — Autonomous Pipeline Guide
## Powered by tappits-linkedin-agents

> **For Manus**: Whenever Ganesh asks you to generate today's LinkedIn post (or on a daily scheduled run), execute this pipeline step-by-step using the skills, rules, and memory files in this repository.

---

## 1. Mandatory Pre-Execution Reads
Before searching or drafting, read these core files to establish full context:

1. **Rules & Single Source of Truth**: [`LINKEDIN_ORIGINAL_POST_RULES.md`](LINKEDIN_ORIGINAL_POST_RULES.md)
2. **Ganesh's Real Voice Reference**: [`memory/normalized_2026-04-26/ganesh_real_tone_reference.md`](memory/normalized_2026-04-26/ganesh_real_tone_reference.md)
3. **Personal Synthesis & Projects**: [`memory/normalized_2026-04-26/PERSONAL_SYNTHESIS_GANESH.md`](memory/normalized_2026-04-26/PERSONAL_SYNTHESIS_GANESH.md)
4. **Post History (15-Post Dedup Lookback)**: [`memory/linkedin_post_history.json`](memory/linkedin_post_history.json)
5. **Humanization Policy (Sergebulaev v3 Overlay)**: [`memory/humanization_policy.json`](memory/humanization_policy.json)

---

## 2. Step 1: Real-Time Research & Topic Scoring ("Today Test")
Manus must search the live web for fresh data, releases, and trends from the **last 7 days**:

- **GitHub Trending & OSS AI**: New open-source models, agent sandboxes, dev tooling breakthroughs.
- **Indian Tech & AI Hiring Market**: Real JD shifts, skills demand percentages, salary comparisons.
- **Indian Campus & Builder Realities**: Engineering curriculum gap vs. actual industry stacks, placement data.
- **clstr.in Building Logs**: Real metrics, architecture decisions, and student founder experiences.
- **Developer Discussions**: Trending Hacker News, X/Dev Twitter discussions, and arXiv papers.

**The "Today Test" Gate**:
Every candidate topic must pass: *"Why is this topic urgently relevant today and not 6 months ago?"*

**Anti-Repetition & Context Fingerprint**:
Extract a 5–8 word `context_fingerprint` of the core insight. Compare against the last 15 posts in [`memory/linkedin_post_history.json`](memory/linkedin_post_history.json). If it shares >50% semantic overlap with a recent post, **discard and pick another angle**.

---

## 3. Ganesh's Creator & Builder Profile (Open Scope — NOT Clstr-Only)

> **CRITICAL CLARIFICATION FOR MANUS**: **Do NOT force every post to mention or plug Clstr.** Clstr is only one venture. Ganesh is a multifaceted builder, AI-native creator, and student founder. The topic can be **ANYTHING** high-signal in the tech, AI, dev, or builder world as long as it sounds like Ganesh.

### Ganesh's 6 Core Identity Facets (Rotate Freely Across Topics):
1. **AI Generative & Vibe Coder / AI-Native Builder**:
   - Vibe coding, prompt engineering, agentic workflows, Cursor/Claude/Copilot setups, local LLM quantization, benchmarking new open-source models, shipping software in hours instead of months.
2. **Product Designer & Frontend Architect (Design × Engineering)**:
   - UI/UX taste, typography, Figma-to-code execution, thumb-zone ergonomics, cognitive load reduction, tearing down broken designs.
3. **Full-Stack Developer & Hands-On Builder**:
   - Building real software (React, Flutter, Firebase, Supabase, Node.js), solving architecture bottlenecks, production bugs, developer tool discoveries.
4. **Entrepreneur & Startup Founder**:
   - Bootstrapping with ₹0, MVP validation, Mom Test principles, YC trends, startup hiring shifts, pitch decks, building traction without funding.
5. **Student & Campus Ecosystem Builder**:
   - Engineering college realities vs. market demand, student hackathons, cross-college networks, student builder culture.
6. **Contrarian Hot Takes & Developer Commentary**:
   - Calling out AI hype vs. real utility, tech salary realities, developer career shifts, honest builder struggles.

### The Voice Rule:
- Speak as a **curious, direct, 21-year-old builder** who is in the trenches actually testing tools and shipping things.
- Never write like a corporate marketing account or a paid PR promoter.
- If an AI model dropped, review its real coding output. If JDs are shifting, break down the numbers. If a dev tool is awesome, explain why you use it. Zero forced mentions.



---

## 4. Step 2: Activate Repository Skills

Chain the skills located in [`agents/skills/`](agents/skills/):

### A. Hook Creation — [`agents/skills/hook-generator/SKILL.md`](agents/skills/hook-generator/SKILL.md)
- Generate 6 hook variations using the formula: Line 1 (≤40 chars) + Line 2 bold contrast (≤40 chars).
- Must include digits, tension, or "How I" / "I scanned" statements.
- Pick the highest-performing hook matching today's format (e.g. H1 "I scanned X sources..." or contrarian reframe).

### B. Post Drafting — [`agents/skills/post-writer/SKILL.md`](agents/skills/post-writer/SKILL.md)
- Write in **Ganesh's voice** (21yo builder, direct, authentic, peer-to-peer, zero corporate jargon).
- Word Count: **120–200 words strictly** (Track B) or **1–10 words** for memes (Track A).
- **Zero links in post body** (prevents 25–60% LinkedIn algorithm penalty).
- 1–3 hashtags (default: 2) at the very bottom.
- Conclude with a **specific, polarizing debate question** to generate 15+ word comments (no generic CTAs like "Follow for more").

### C. Post Formatting — [`agents/skills/post-formatter/SKILL.md`](agents/skills/post-formatter/SKILL.md)
- 1 sentence per line (mobile ~40 chars/line) for maximum "see more" clicks.
- Arrow lists (`→`) over generic bullets.

### D. Quality & Algorithm Audit — [`agents/skills/post-scorer/SKILL.md`](agents/skills/post-scorer/SKILL.md)
Grade the draft against:
1. Hook strength (curiosity gap, mobile cutoff).
2. Dwell time potential (scannable lists, data numbers).
3. Humanization compliance: **Zero banned words** (`delve`, `showcase`, `utilize`, `leveraging`, `synergy`, `game-changing`, `disruptive`, `AI-first`).
4. Em-dash cap: Maximum 1 em-dash per 100 words.
- *If score < 85/100, rewrite before proceeding.*

### E. First Comment Drafting — [`agents/skills/pinned-comment/SKILL.md`](agents/skills/pinned-comment/SKILL.md)
- Draft the accompanying 1st comment containing the external URL, GitHub repo link, or data source.

---

## 5. Step 3: Senior Product Designer Visual System (The Anti-"AI Slop" Protocol)

> **CRITICAL DIRECTIVE FOR MANUS (Senior Product Designer + Frontend Architect Lens)**:  
> LinkedIn feeds are drowning in the **"AI Purple Problem"**: generic dark backgrounds, purple/indigo gradient halos, default Tailwind cards, glowing plastic 3D spheres, and robotic AI stock slop. **THIS IS HARD BANNED.**  
> Every post visual must be treated as a **production-grade editorial design or real engineering artifact** — visually distinctive, brand-driven, high-contrast, accessible, and impossible to mistake for generic AI output.

---

### 1. Audit & The "AI Purple Problem" Banlist ❌
- **Zero Purple/Indigo Glow**: Banned from using purple/indigo gradient halos, neon cyan glow, or generic dark-mode SaaS templates.
- **Zero Hallucinated AI Art**: No glowing digital brains, floating robot hands, abstract futuristic cubes, or synthetic stock humans.
- **Zero Gradient Spam**: No rainbow gradient borders or decorative noise that doesn't convey information.
- **Zero Uncanny Logos**: Never allow an image model to invent or draw a tech logo. Use authentic SVGs/PNGs sourced from official domains or `unpkg.com`.

---

### 2. The Clstr / Ganesh Brand Token System (Editorial Light Theme Default) 🎨
> **THEME DIRECTIVE**: **Light theme is the primary default.** While the rest of LinkedIn drowns in muddy dark-mode AI slop, a crisp, warm architectural light theme looks human, senior, and publication-grade (like Stripe Press, Linear docs, or the Financial Times).

```css
:root {
  /* Primary Theme: Editorial Warm Light (DEFAULT) */
  --color-bg: #FAFAF7;             /* Warm architectural gallery canvas (no harsh blinding white) */
  --color-surface: #FFFFFF;        /* Pure white structured component card */
  --color-border: #E2E4E9;         /* Crisp 1px hairline border */
  --color-subtle: #F1F3F5;         /* Subtle section fill / table alternate row */

  /* High-Contrast Typography */
  --color-text-primary: #0F172A;   /* Deep obsidian ink (WCAG AAA 14:1 contrast) */
  --color-text-secondary: #475569; /* Refined slate for metadata and captions */
  --color-text-muted: #94A3B8;     /* Footers and source timestamps */

  /* Disciplined Accent (Spend boldness in ONE place) */
  --color-primary: #0066FF;        /* Clstr Electric Blue (High authority, clean contrast) */
  --color-accent-green: #059669;   /* Crisp data success green */
  --color-accent-amber: #D97706;   /* Warning/callout amber */

  /* Code & Technical Blocks (GitHub Light / Linear style) */
  --color-code-bg: #F8FAFC;        /* Clean light-mode terminal / code surface */
  --color-code-border: #CBD5E1;    /* Defined boundary */
  --color-code-text: #0F172A;      /* Deep mono font */
}
```

---

### 3. Typography Architecture with Real Personality ✍️
- **Display / Headlines**: `Hanken Grotesk` or `Inter Display` — bold ink black (`#0F172A`), tight tracking (`letter-spacing: -0.02em`), confident editorial hierarchy.
- **Technical Data & Code Lines**: `Fragment Mono` or `SF Mono` / `Courier New` — gives immediate developer credibility to benchmark tables, numbers, and terminal snippets.
- **Structural Legibility**: Use numbering (`01 / 02 / 03`) ONLY if content is an actual sequence. Never decorate for the sake of decoration.

---

### 4. The 4 High-Craft Visual Formats (Light Editorial Aesthetics) 🖼️

1. **Real Production Artifacts & UI Teardowns (Light Frame)**:
   - Real, authentic screenshots: GitHub trending repo commits/stars, real terminal CLI benchmark logs (`fastfetch` / profiling traces), arXiv paper benchmark tables, or real UI component teardowns.
   - Framed on a warm `#FAFAF7` canvas with a clean `#FFFFFF` container and subtle 1px `#E2E4E9` border.

2. **System Architecture Blueprints & Component Schemas**:
   - Clean, technical system design flows (Linear / Figma / Stripe Press light canvas).
   - Shows real engineering reality: multi-tenant database routing, context-injection loops, agent tool-call sequences.
   - Clean directional connectors (`→`), deep ink labels, electric blue `#0066FF` active nodes.

3. **High-Density Technical Comparison & Cheat-Sheet Matrices**:
   - High-contrast tabular comparisons on clean white cards: *Tool A vs. Tool B*, *What Colleges Teach vs. What 2026 Startups Demand*, *The Solo Founder 2026 Stack*.
   - Alternating rows with `#F8FAFC`, deep black text, bold green/blue checks.
   - Information-dense layout that forces mobile users to pause, zoom in, and tap **Save** (triggering LinkedIn's highest-weighted algorithm boost).

4. **Stripe Press Style Editorial Data Cards**:
   - Stark, authoritative light editorial presentation: Single bold statistic (`Min 48px`, deep `#0F172A`), clean monospace data labels, and authentic vector logos.
   - Clean footer attribution: `clstr.in • @ganeshtappiti • Source: Scanned 215 JDs`.

---

### 5. Visual Engineering Growth Hacks 🚀
- **The Aspect Ratio Hack (1200×1500 / 4:5 Vertical)**:
  Square (1:1) and landscape (16:9) leave empty space on mobile screens. 4:5 vertical covers 25% more mobile feed real estate, forcing scrolling thumbs to stop and maximizing **dwell time**.
- **The "Save Test" (The #1 2026 Ranking Signal)**:
  The LinkedIn algorithm currently weights **Saves higher than comments and likes**. When a post contains a high-density reference graphic or comparison table, users bookmark it to revisit. Manus is instructed to design images specifically to pass this "Save Test."
- **The 3-Second Thumbnail Rule**:
  The main stat, comparison header, or takeaway must be 100% legible at 40% zoom on a smartphone screen without needing to click or expand the image.
- **Real Vector Logos Only**:
  Manus is instructed to fetch official SVG/PNG logos directly from CDNs/domains (e.g. `unpkg.com` or official site favicons) so all tech logos are 100% sharp, authentic, and accurate (never AI-hallucinated).
- **Light Mode Stands Out**:
  Over 90% of AI posts on LinkedIn use dark backgrounds with purple/indigo glows. An intentional, clean editorial light aesthetic immediately cuts through feed blindness.
- **The "Spend Boldness in One Place" Rule**:
  Make the central insight or technical data flow the undeniable hero. Keep everything around it quiet, disciplined, and minimal.
- **Source Citation & Authority Stamp**:
  Include small, clean attribution stamps (`Source: Scanned 215 JDs | @ganeshtappiti | clstr.in`) to establish authority.




---

## 6. Step 4: Daily Delivery Format to Ganesh

Manus outputs the final package in this clean copy-paste format:

```
══════════════════════════════════════════════════════════════════════════
📅 TODAY'S LINKEDIN POST PACKAGE
══════════════════════════════════════════════════════════════════════════

🎯 Strategic Metadata:
- Pillar: [Pillar Name: Build in Public | AI-Enabled Building | Campus Ecosystem | Founder Psychology | Design x Engineering]
- Post Type: [e.g. research_data / hot_take / build_in_public / relatable_meme]
- Context Fingerprint: [5-8 words summarizing core insight]
- "Today Test" Source: [Live trend/data source verified from last 7 days]
- Quality Score: [Score/100 via post-scorer]

──────────────────────────────────────────────────────────────────────────
📝 POST CAPTION (Copy & Paste to LinkedIn):
[Complete post text with 1 sentence per line, blank line breaks, hashtags, and ending debate question]
──────────────────────────────────────────────────────────────────────────

💬 FIRST COMMENT (Post this immediately after publishing):
[Reference URL, GitHub repo, or source link]

──────────────────────────────────────────────────────────────────────────
🖼️ VISUAL ASSET:
- Image Style: [Style Name]
- Visual File / Preview: [Attached or rendered image file]
- Exact Prompt (if re-generating): [Prompt text]
══════════════════════════════════════════════════════════════════════════
```

---

## 7. Step 5: Update Post History
After presenting the post, append the entry into [`memory/linkedin_post_history.json`](memory/linkedin_post_history.json) to update the 15-post lookback cache for tomorrow's run.

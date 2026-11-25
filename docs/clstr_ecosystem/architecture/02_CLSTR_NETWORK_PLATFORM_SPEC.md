# 02 — clstr.in Platform Specification

> **Comprehensive functional, architectural, and database specification for the primary social network platform (`clstr.in`).**

---

## 1. Product Overview & Core Philosophy

The `clstr.in` application (housed in [`clstr.network/`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/clstr.network)) is the digital anchor of the student ecosystem. It provides the persistent identity, cross-campus collaboration, and verified trust layer that traditional social networks (Instagram, LinkedIn) cannot offer Indian college students.

### The Trust Doctrine
Unlike open platforms where anyone can create arbitrary profiles, every interaction on Clstr is anchored to a student's verified college enrollment. This creates a high-trust, zero-bot, harassment-resistant ecosystem where students can safely share ideas, form teams, buy/sell campus items, and network with verified alumni.

---

## 2. Comprehensive Feature Breakdown (Step-by-Step)

### Feature 0: Verification & Identity Engine (The Root of Trust)
* **Objective**: Ensure 100% of active participants are authentic students or alumni of recognized Indian academic institutions.
* **Dual-Path Authentication Flow**:
  1. **Tier 1: Institutional Academic Email Path**
     * User inputs college email (e.g., `rollno@gvpce.ac.in`).
     * System checks the domain against local registry (`known_domains.json`) and database table `college_domains`.
     * System resolves domain aliases (e.g., ensuring both `@au.edu.in` and `@andhrauniversity.ac.in` map to Andhra University).
     * Validates that domain is not a public mail provider (Gmail, Outlook, Yahoo) via `block_public_domain_profile()`.
     * Supabase Auth sends an email OTP. Upon verification, `profiles.is_verified` becomes `true` with `verification_method = 'institutional_email'`.
  2. **Tier 2: Non-Institutional Email Path (No-Edu Colleges)**
     * Tailored for students attending colleges with no student email infrastructure.
     * Student inputs personal email and mobile number.
     * Receives SMS / Email OTP via Supabase Auth.
     * Selects their institution from the vetted `no_edu_colleges` registry (curated across 36 Indian states/UTs).
     * System executes the atomic PostgreSQL RPC `claim_tier2_profile(p_college_id, p_full_name, p_branch, p_year)`.
     * Upgrades profile with verified status while flagging `verification_method = 'manual_otp'`.
  3. **Spectator Mode (Graceful Onboarding)**
     * If a student is awaiting college email credentials, they enter Spectator Mode.
     * **Allowed actions**: Browse college feed, view public profiles, browse CollabHub, view upcoming campus events, register/RSVP for events.
     * **Blocked actions**: Creating posts, writing comments, liking/reacting, sending connection requests, direct messaging, creating projects, selling on EcoCampus, applying for mentorship.
     * **Enforcement**: Database-level Row Level Security (RLS) triggers enforce these rules. Client-side attempts to bypass the UI fail at the PostgreSQL layer.

---

### Feature 1: Scoped Campus Social Feed
* **Objective**: Deliver a high-signal, zero-noise feed containing only updates, queries, and achievements from the student's own verified college.
* **Functional Logic**:
  * Feed queries filter strictly on `profiles.college_domain = auth.jwt() ->> 'college_domain'`.
  * Multi-tab sorting:
    * **Recent**: Chronological timestamp ordering (`created_at DESC`).
    * **Top**: Engagement score based on Wilson score interval of likes, comments, and bookmark velocity.
  * Rich post composer supporting multi-image upload to Supabase Storage, hashtag parsing, and poll creation.
  * Verified club and college administrative announcements receive visual priority and sticky placement at the top of the feed.
  * Absolute college isolation: Users cannot view or cross-post into other colleges' internal feeds, preserving authentic campus privacy.

---

### Feature 2: Gated Direct Messaging
* **Objective**: Prevent unsolicited messaging, spam, and harassment while facilitating high-intent peer communication.
* **Functional Logic**:
  * **Connection-Gated Protocol**: A user cannot initiate a direct message conversation unless both users share an accepted connection (`status = 'accepted'` in `connections` table).
  * **Realtime Delivery**: Backed by Supabase Realtime WebSocket subscriptions on table `messages`.
  * Instant read receipts, typing indicators, and message timestamps.
  * **Floating Chat Bubble**: Global dockable messenger component present across all routes, allowing continuous communication while navigating projects or events.

---

### Feature 3: Campus Network & Connections
* **Objective**: Allow students to discover batchmates, branch peers, seniors, and alumni across their specific college.
* **Functional Logic**:
  * Filterable directory by Graduation Year, Branch/Department (CSE, ECE, Mech, Civil, MBA), and Skill Tags.
  * Connection request pipeline: `Pending` → `Accepted` / `Declined`.
  * Reciprocal graph: Accepting a connection grants bidirectional messaging and full portfolio contact access.

---

### Feature 4: CollabHub (Cross-Campus Team Building)
* **Objective**: Enable students to assemble cross-disciplinary and cross-college teams for hackathons, startup ventures, college fests, and research papers.
* **Functional Logic**:
  * Unlike the social feed, CollabHub is **Cross-Campus by Design**.
  * Project creator specifies project title, description, deadlines, external links (GitHub, Figma), and required role slots (e.g., "Frontend Dev (React)", "UI Designer", "Pitch Deck Specialist").
  * Interested students submit an application with an attached note and their verified Clstr portfolio link.
  * Creator reviews applicants and accepts/rejects. Accepting an applicant automatically initiates a mutual connection and invites the applicant into a shared team workspace.

---

### Feature 5: Verified Clubs & Campus Organizations
* **Objective**: Centralize campus club discoverability, member recruitment, and official notices.
* **Functional Logic**:
  * Role hierarchy: `Club Lead` (Admin), `Core Member`, and `General Member`.
  * Dedicated club showcase pages featuring past achievements, current executive team, upcoming events, and membership applications.
  * Lead verification: Club admin access is governed by verifiable database roles in `club_memberships`, deprecating legacy hardcoded passcodes.

---

### Feature 6: Campus Events & Fest Aggregator
* **Objective**: Unify the scattered campus event landscape across all colleges in the city.
* **Functional Logic**:
  * Discovery filters: "My College Only" vs. "City-Wide / Inter-College".
  * Direct integration with [`Ticket-Platform`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/Ticket-Platform) for paid tickets, RSVP confirmations, and dynamic QR passes.
  * Displays real-time social facepile ("Who's Pulling Up") showing connected peers who have registered.

---

### Feature 7: Interactive Student Portfolio Builder
* **Objective**: Provide an authentic alternative to resume PDFs that dynamically showcases verified skills, projects, and campus achievements.
* **Functional Logic**:
  * Modular sections: Bio, Education, Verified Skills, Featured Projects, GitHub repositories, Club Leadership, Hackathon Wins.
  * Generates clean public vanity URLs (`clstr.in/p/:username`).
  * Instant PDF resume export formatted for campus recruitment drives.

---

### Feature 8: EcoCampus (Student-to-Student Marketplace)
* **Objective**: A hyper-local, high-trust marketplace for textbook exchanges, drafting tools, electronics, lab coats, and hostel essentials.
* **Functional Logic**:
  * Scoped exclusively to the student's campus or physical cluster to ensure safe, on-campus cash/UPI handoffs.
  * Price ceiling policies and anti-scalping protections.
  * 1-click in-app message trigger linking the product card directly to the seller's chat.

---

### Feature 9: Peer & Alumni Mentorship
* **Objective**: Connect juniors with verified placed seniors and working alumni for mock interviews, placement prep, and career guidance.
* **Functional Logic**:
  * Mentors set available weekly time slots, areas of expertise (FAANG prep, Core engineering, CAT/GATE), and meeting links (Google Meet).
  * Juniors book slots with an upfront topic description.
  * Post-session mutual feedback and verified mentorship badge issuance.

---

### Feature 10: Verified Jobs & Internship Board
* **Objective**: Curate early-career opportunities specifically targeting Tier 2 and Tier 3 engineering and arts graduates.
* **Functional Logic**:
  * Direct recruiter listings with clear stipends, eligibility criteria (graduation batch, CGPA requirements, eligible branches).
  * 1-click apply utilizing the candidate's verified Clstr profile and portfolio.

---

### Feature 11: AI Career Assistant (Powered by Qwen 3 235B)
* **Objective**: Provide 24/7 personalized, context-aware placement coaching and technical interview prep.
* **Functional Logic**:
  * Executed through Supabase Deno Edge Function `supabase/functions/ai-chat/` communicating with OpenRouter API.
  * LLM: **Qwen 3 235B**, fine-tuned for Indian academic systems, placement exams (TCS NQT, Infosys, Cognizant, GATE), and resume critiques.
  * Context-aware: Ingests the student's portfolio skills, branch, and target roles to simulate realistic technical and HR interview rounds.

---

### Feature 12: Unified Search & Discovery
* **Objective**: Instant omni-search across students, alumni, clubs, projects, posts, and job listings.
* **Functional Logic**:
  * Backed by PostgreSQL `tsvector` full-text search indexes on indexed columns (`profiles.search_vector`, `posts.search_vector`).
  * Fast autocomplete and fuzzy matching with debounce controls in React.

---

## 3. Technology Stack & Directory Layout

### Frontend Architecture
* **Framework**: React 18.3.1 SPA with TypeScript
* **Build Tool**: Vite 6 with SWC compiler
* **Styling**: Tailwind CSS 3.4 + `tailwindcss-animate`
* **UI Foundation**: Radix UI + shadcn/ui components (`src/components/ui/`)
* **State Management**:
  * Server State: TanStack React Query v5 (query caching, background invalidation)
  * Local/Session State: React Context (`ProfileContext`, `IdentityContext`, `AdminContext`)
* **Routing**: React Router DOM v7 with route code-splitting and animated transitions
* **3D Visuals**: Three.js, React Three Fiber (`@react-three/fiber`), OGL shaders

### Directory Structure of `clstr.network/src`
```
src/
├── api/             # API client functions and Supabase calls
├── components/      # Modular component library
│   ├── auth/        # Verification forms, OTP modals, Tier 2 selector
│   ├── backgrounds/ # 3D Three.js & WebGL animated backgrounds
│   ├── collabhub/   # Project creation, team applicant management
│   ├── feed/        # Feed cards, post composer, poll cards
│   ├── marketplace/ # EcoCampus listings, image gallery
│   ├── messaging/   # Chat bubble, thread list, message bubble
│   ├── portfolio/   # Profile sections, skill tags, project showcase
│   └── ui/          # 69 Radix/shadcn primitive components
├── context/         # Auth, profile, and identity React contexts
├── hooks/           # 39 Custom hooks (useAuth, useFeed, useRealtimeChat)
├── lib/             # 46 utility modules (Supabase client, queries, analytics)
├── pages/           # 45 route page components
└── types/           # TypeScript schema definitions and database types
```

---

## 4. Database Schema & Security Doctrine

### Core Database Entities

```
┌─────────────────────────┐          ┌─────────────────────────┐
│        profiles         │          │       connections       │
├─────────────────────────┤          ├─────────────────────────┤
│ id (UUID, PK)           │◄────┐    │ id (UUID, PK)           │
│ email (text)            │     ├────┤ requester_id (UUID, FK) │
│ full_name (text)        │     └────┤ recipient_id (UUID, FK) │
│ college_id (UUID, FK)   │          │ status (accepted/pend)  │
│ college_domain (text)   │          └─────────────────────────┘
│ is_verified (boolean)   │
│ verification_tier (text)│◄────┐    ┌─────────────────────────┐
│ is_spectator (boolean)  │     │    │          posts          │
└─────────────────────────┘     │    ├─────────────────────────┤
             ▲                  └────┤ author_id (UUID, FK)    │
             │                       │ college_domain (text)   │
             │                       │ content (text)          │
┌─────────────────────────┐          │ media_urls (text[])     │
│   no_edu_colleges       │          └─────────────────────────┘
├─────────────────────────┤                       ▲
│ id (text, PK)           │                       │
│ name (text)             │          ┌────────────┴────────────┐
│ city (text)             │          │        comments         │
│ state (text)            │          ├─────────────────────────┤
│ verification_status     │          │ post_id (UUID, FK)      │
└─────────────────────────┘          │ author_id (UUID, FK)    │
                                     │ content (text)          │
                                     └─────────────────────────┘
```

### Row Level Security (RLS) Invariants
1. **Feed Isolation Invariant**:
   ```sql
   CREATE POLICY "Users can only read posts from their college"
   ON public.posts FOR SELECT
   USING (college_domain = (auth.jwt() ->> 'college_domain'));
   ```
2. **Messaging Privacy Invariant**:
   ```sql
   CREATE POLICY "Users can only access their conversations"
   ON public.messages FOR SELECT
   USING (
     auth.uid() = sender_id OR auth.uid() = receiver_id
   );
   ```
3. **Spectator Mutation Guard**:
   ```sql
   CREATE POLICY "Spectators cannot insert posts"
   ON public.posts FOR INSERT
   WITH CHECK (
     EXISTS (
       SELECT 1 FROM public.profiles
       WHERE id = auth.uid()
       AND is_verified = true
       AND is_spectator = false
     )
   );
   ```

---

## 5. Supabase Edge Functions Inventory

The serverless backend in [`clstr.network/supabase/functions/`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/clstr.network/supabase/functions) runs 12 high-performance Deno functions:

| Function Name | Invocation Trigger | Responsibility |
| :--- | :--- | :--- |
| **`ai-chat`** | HTTP POST from AI Assistant | Streams prompt to OpenRouter (Qwen 3 235B) with student context and returns markdown responses. |
| **`send-email`** | Auth / Notification hooks | Dispatches templated transactional emails via Resend API (OTP, connection alert, fest pass). |
| **`send-push-notification`**| Realtime message / mention | Encrypts and dispatches Web Push payloads via VAPID standard to subscribed browsers. |
| **`verify-domain`** | Onboarding domain input | Validates domain authenticity, checks MX records, and resolves institutional aliases. |
| **`claim-tier2`** | Tier 2 student onboarding | Atomic procedure validating phone OTP, verifying against `no_edu_colleges`, and updating profile role. |
| **`generate-sitemap`** | Cron / Deployment | Builds dynamic XML sitemaps for public SEO profiles, colleges, and event pages. |

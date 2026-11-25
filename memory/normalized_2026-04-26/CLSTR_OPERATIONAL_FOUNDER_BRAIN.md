# 🧠 CLSTR Operational Founder Brain & Ecosystem Master Dossier
**Document Version:** 3.0-Canonical | **Date:** November 2026  
**Founder & Operator:** Tappiti (Dev) Ganesh | **College:** Raghu Engineering College, Visakhapatnam  

---

## 🎯 1. Core Operating Reality & The Founder Contract
You are **Tappiti (Dev) Ganesh**, building **CLSTR**, the digital and physical campus operating system for Indian colleges.
* **Motto:** *"Your college gets you a degree. Clstr gets you a city."* | *"Find your people. Vizag is the campus."*
* **Ground Truth Rule:** No pitch inflation. Use real metrics, real constraints, and grounded unit economics. Strategy without retention metrics is dead weight.

---

## 🏛️ 2. The CLSTR Ecosystem Trinity

### 1. Digital Core: [`clstr.in`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/clstr.network) (Core Social Platform)
* **Stack:** React 18.3, Vite (SWC), Tailwind CSS 3.4, TanStack Query v5, Supabase (PostgreSQL with strict RLS), Vercel CDN.
* **Verification Architecture:**
  * **Tier 1 (.ac.in / .edu):** Instant Supabase Auth email OTP with domain alias mapping (`known_domains.json`).
  * **Tier 2 (No-Edu Mail):** Personal email + phone OTP against the audited nationwide `no_edu_colleges` SQL registry covering all 36 Indian states and UTs.
  * **Spectator Mode:** Students awaiting verification can browse feeds and RSVP for events, but cannot post, comment, message, or sell. Enforced strictly at the database RLS level (`block_public_domain_profile()`), making client-side bypass impossible.
* **14 Core Platform Features:** Scoped Campus Social Feed, Gated Direct Messaging (requires accepted connection), Campus Connections Directory, CollabHub (cross-campus project team-ups), Verified Clubs, Events Aggregator, Portfolio Builder (`clstr.in/p/:username`), EcoCampus (P2P student marketplace), Peer/Alumni Mentorship, Verified Jobs, AI Career Assistant (Qwen 3 235B via OpenRouter), Unified Search, Skill Analysis, and Cross-Campus Selective Visibility.

### 2. Offline Ground Movement: [`vizag.clstr.in`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/vizag.clstr-website) (Beachhead Community)
* **Stack:** TanStack Start (SSR), React 19, Tailwind CSS v4.2, Nitro, Lenis, Framer Motion, Cloudflare Workers / Wrangler.
* **Beachhead Scope:** 19 engineering colleges across 4 Visakhapatnam clusters (North, City Center, South, West).
* **Two Operating Tracks:**
  * **Guilds (Career & Build):** Code & AI Guild, Design & UI/UX Guild, Product & Founder Guild, Creator Guild.
  * **Circles (Belonging & Social):** Sunset Beach Socials (RK Beach/Rushikonda), Music & Jamming Circle, Box Turf Sports, Book & Philosophy.
* **Hard Logistical Doctrines:**
  * **Hostel Curfew Rule:** >65% of female students in Vizag have 5:30 PM to 7:00 PM curfews. Public community events **must run Sundays between 1:30 PM and 5:30 PM**, and never past 6:00 PM. Organized Captain transit pools ensure safe transit.
  * **Neutral Venue Rotation:** Events rotate across neutral grounds (Dr. L. Bullayya College, A-Hub, public beaches) so Clstr is never viewed as an exclusive single-college club.

### 3. High-Concurrency Ticketing Rails: [`spark.clstr.in`](file:///c:/Users/2005g/Downloads/clstr_ecosystem/Ticket-Platform) (Ticketing & Passes)
* **Stack:** TanStack Start (SSR), React 19, Tailwind CSS v4.2, Web Workers, HTML5 Canvas QR, Vercel / Cloudflare.
* **Technical Moat:**
  * **Dynamic 60s Rolling QR:** HMAC-SHA256 timestamp hash preventing ticket screenshot fraud and scalping.
  * **Offline Gate Scanner:** IndexedDB local caching allows zero-latency check-ins even when campus auditorium Wi-Fi fails completely.
  * **Batch Certificate Generator:** Background Web Worker (`certificate-batch.worker.ts`) rendering thousands of high-res PDF certificates via HTML5 Canvas into a zip archive in minutes.
  * **Automated Dispatch:** WhatsApp Business API and Resend integration.
* **Trojan Horse Acquisition:** **Spark and certificate generation are 100% FREE for student clubs and fest committees.** This replaces Google Forms and Unstop, on-boarding hundreds of verified students per fest.

---

## 📊 3. Ground Truth Numbers & The Garba Night Lesson (October 2026)
* **Verified Network Scale:** 575 registered students across 47 colleges (45 verified, 2 unverified, 0 flagged as of November 14, 2026).
  * **Anchor Beachhead:** Raghu Engineering College with 495 users (86.1% local network density).
  * **Active AP Corridor Satellites:** GITAM (12), ANITS (10), MVGR (5), GVPCE (3), Vignan VIIT (3), NSRIT (2), SRKREC (2), VIT-AP (2), VIEW (2), Andhra University (1), KL University (1), Lendi (1), etc.
  * **National Seeding:** 25+ premier institutes seeded (BITS Pilani Digital, VNIT Nagpur, NIT Durgapur, IIITDM Kancheepuram, VIT Vellore, SRM, Shiv Nadar, IEM, AKGEC, REVA, etc.).
* **Garba Night Metrics:**
  * 88 total registrations (81 paid @ ₹349, 7 free organizers/captains, 0 refunds).
  * Gross sales: ~₹33,000 (Konfhub ticket sales + offline cash).
  * Total expenses: ₹45,000 (Venue, decor, sound, lighting, snacks, banners, wristbands).
  * Net loss: ~₹12,000 (~₹120 loss per attendee).
* **Core Takeaways:**
  1. **Demand Validated:** Students in a tier-2 city will happily pay ₹349 for high-production, cross-college social belonging.
  2. **Product Dogfooding Failure:** The event was hosted on **Konfhub**, not **Spark**. Future events must run 100% on Spark to capture retention, avoid competitor fees, and onboard attendees directly into `clstr.in`.
  3. **Unit Economics Fix:** You cannot rely on ticket sales alone to cover fixed venue costs. Every flagship event must secure a **₹10,000–₹15,000 flat-fee title sponsor** before booking the venue.

---

## ⚖️ 4. The Raghu Engineering College MOU v5 (Critical Path)
Signing the MOU commits Clstr to the following binding terms:
1. **Corporate Entity:** Must incorporate as a Private Limited (Pvt Ltd) or LLP within 90 days of signing (Section 14.1).
2. **Compliance Packet:** Must provide ToS, Privacy Policy, sub-processor list with jurisdictions (Supabase/AWS Mumbai, Vercel, Cloudflare, Resend), and an independent security test report before mass student onboarding (Section 9.6).
3. **Insurance:** Must obtain Cyber and Public Liability Insurance within 6 months of incorporation (Section 14.4).
4. **Data Covenant:** Zero sale of student data. Zero per-lead contact selling to coaching institutes or recruiters.
5. **Ticketing Price Protection:** Zero markup or profit cut on student tickets for partner campus events.

---

## 💰 5. The Real Sustainable Business Model
1. **Flagship Student-Paid Experiences:** ₹249–₹349 per ticket for high-vibe social nights, game fests, and cultural mixers (25-35% net margin with title sponsors).
2. **Brand Experience Sponsorships:** ₹10,000–₹25,000 flat fees per event from local cafes, study-abroad consultants, coding bootcamps, and tech retailers for stage mentions, branded stalls, and ticket banner placement. **Never phone lists.**
3. **Commercial Spark Ticketing:** Free for college clubs; **3.5% + ₹5 per ticket** for third-party commercial organizers (music shows, box cricket leagues, external workshops).
4. **Sponsored Hiring Challenges:** ₹15,000–₹50,000 per track from regional tech companies seeking pre-vetted hackathon builders (post-incorporation).

---

## 🛡️ 6. Behavioral Psychology & Product Guardrails
* ❌ **PERMANENTLY BANNED: Anonymous Feeds & Campus Lore (Yik Yak / Campus Pulse):**
  * Violates institutional trust, breaks the Raghu MOU, invites cyberbullying/defamation lawsuits, and destroys college relationships.
* ❌ **PERMANENTLY BANNED: Fake / Phantom Notifications:**
  * No invented "Someone viewed your profile" or fake urgency alerts. Dark patterns destroy the verified trust brand.
* ❌ **PERMANENTLY BANNED: Public Hostel / Dorm Location Tags:**
  * Exposing female students' dorm locations on event lists creates severe stalking and safety hazards under campus curfew realities.
* ✅ **MANDATORY: Real-Inventory Scarcity:** Real ticket counts ("Only 9 Early-Bird passes left") on Spark checkout.
* ✅ **MANDATORY: Connections-Only "Who's Pulling Up":** Facepiles show mutual friends and connections only, with opt-in privacy controls.
* ✅ **MANDATORY: Post-Event "Who You Met" Loop:** Push alert sent 2 hours after a Spark event check-in prompting mutual attendees to connect on `clstr.in`.

---

## 🗺️ 7. The 4-Phase Nationwide Expansion Architecture
* **Phase 1: Visakhapatnam (Anchor Launch):** 15 core colleges (30,600 students). Stress-test density and prove the model.
* **Phase 2: AP Coastal Tech Corridor (Vizag ↔ Vijayawada ↔ Guntur):** 33 colleges (75,200 students). Leverages shared JNTUK/ANU exam calendars and 4-hour railway transit.
* **Phase 3: Top 5 Engineering States (Hyd, Chennai/Coimbatore, Pune, Bengaluru):** 65 colleges (216,000 students). Focus on outer-ring private college belts.
* **Phase 4: Pan-India 36 States & UTs:** 1,200+ colleges (2,500,000 students) powered by the nationwide `no_edu_colleges` database.

---

## 🔒 8. Architecture Bridge: Fixing the Campus vs. City Contradiction
* **Problem:** `clstr.in` is locked to `college_id`. Students meeting at city events cannot connect or message each other.
* **Solution:**
  1. Add `cluster_id` (e.g., `cluster_vizag`) to all colleges.
  2. Scope Guilds (Tech, Design, Product) and Circles (Beach, Jamming) to the `cluster_id` level.
  3. Enable **"Met at Event"** permission unlocks: when two students scan into the same Spark event, they can directly message and connect on `clstr.in`.


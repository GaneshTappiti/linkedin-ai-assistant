# agents/skills

Bundled copies of two upstream skill collections. New skills are added at the top; downstream callers should pick by `name:` from the SKILL frontmatter.

## Sources

- [charlie947/social-media-skills](https://github.com/charlie947/social-media-skills/tree/main/skills) — 17 LinkedIn / content skills
- [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) — 46 marketing / growth skills

## Discovery

opencode auto-loads `agents/skills/*/SKILL.md` (alongside `.claude/skills/`). Reload opencode to pick up new skills.

## Updating

```bash
# from this repo root
git clone --depth=1 https://github.com/charlie947/social-media-skills.git /tmp/sms
git clone --depth=1 https://github.com/coreyhaines31/marketingskills.git /tmp/mkt
cp -r /tmp/sms/skills/*  agents/skills/ 2>/dev/null || true
cp -r /tmp/mkt/skills/*  agents/skills/
rm -rf /tmp/sms /tmp/mkt
git add agents/skills && git commit -m "chore: bump upstream skills"
```

## Inventory

### social-media-skills (charlie947)

| Skill | Purpose |
|---|---|
| analytics-dashboard | LinkedIn / social analytics reporting |
| content-matrix | Content planning matrix |
| gemini-carousel | Carousel generation via Gemini |
| gemini-infographic | Infographic generation via Gemini |
| graphic-designer | Visual / graphic design output |
| hook-generator | Hook line generation |
| newsletter-voice | Newsletter writing in a defined voice |
| niche-research | Niche / audience research |
| pinned-comment | Pinned-comment writing |
| post-formatter | Post formatting (line breaks, emojis) |
| post-scorer | Score a draft post |
| post-writer | Write a LinkedIn post in the user's voice |
| profile-optimizer | Optimize a LinkedIn profile |
| quote-post | Quote-style post generator |
| reels-scripting | Script reels / short-form video |
| voice-builder | Build `about-me.md` + `voice.md` voice system |
| youtube-thumbnail | Thumbnail copy / concepting |

### marketingskills (coreyhaines31)

| Skill | Purpose |
|---|---|
| ab-testing | A/B test design and analysis |
| ad-creative | Ad creative concepts and copy |
| ads | Paid ads strategy and copy |
| ai-seo | SEO for AI search surfaces |
| analytics | Marketing analytics |
| aso | App store optimization |
| attribution | Multi-touch attribution |
| churn-prevention | Reduce customer churn |
| co-marketing | Joint marketing with partners |
| cold-email | Cold outbound email |
| community-marketing | Community-led growth |
| competitor-profiling | Competitor teardowns |
| competitors | Competitive analysis |
| content-strategy | Content strategy and pillars |
| copy-editing | Polish marketing copy |
| copywriting | Long and short form copy |
| cro | Conversion rate optimization |
| customer-research | Voice-of-customer research |
| directory-submissions | Directory listing submissions |
| emails | Lifecycle and broadcast email |
| events | Event marketing |
| free-tools | Free-tool lead generation |
| image | Image / creative direction |
| influencer-marketing | Creator and influencer programs |
| launch | Product launch playbooks |
| lead-magnets | Lead magnet ideas and copy |
| marketing-counsel | Strategic marketing advice |
| marketing-ideas | Marketing idea generation |
| marketing-loops | Viral and growth loops |
| marketing-plan | Marketing plan drafting |
| marketing-psychology | Behavioral science in marketing |
| offers | Offer and pricing framing |
| onboarding | New user onboarding flows |
| paywalls | Paywall design and pricing |
| popups | Onsite popup strategy and copy |
| pricing | Pricing strategy |
| product-marketing | Product marketing |
| programmatic-seo | Programmatic SEO at scale |
| prospecting | Outbound prospecting |
| public-relations | PR strategy and outreach |
| referrals | Referral program design |
| revops | Revenue operations |
| sales-enablement | Sales enablement assets |
| schema | Schema markup and structured data |
| seo-audit | SEO audit and fixes |
| signup | Signup flow optimization |
| site-architecture | Site / IA architecture |
| sms | SMS marketing |
| social | Social media marketing |
| video | Video marketing |

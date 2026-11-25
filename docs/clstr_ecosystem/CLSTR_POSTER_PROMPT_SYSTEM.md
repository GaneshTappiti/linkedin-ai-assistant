# 🎨 CLSTR Visual Standard & ChatGPT Image Prompt System
**Locked Format:** 4:5 Portrait (1080 × 1350 px / 1024 × 1536 px for generation)  
**Applicability:** `vizag.clstr.in` Instagram, event posters, LinkedIn graphics, and community marketing.

---

## 🔒 1. Locked Brand & Design Invariants

* **Aspect Ratio:** Strictly 4:5 portrait (generate at `1024x1536` with 8% top/bottom safe margins, crop to `1024x1280` or `1080x1350`).
* **Brand Logo:** Small "clstr" wordmark in the top-left corner, always lowercase, flat and sharp, no glow, no shadow, no outline, in deep cobalt blue (`#0537B4`) or white (on dark backgrounds).
* **Social Media Rules (Instagram):**
  * **NO QR code on artwork** (friction kills conversion; social has clickable link in bio).
  * **NO clstr.in website URL footer** on image artwork.
  * **NO hard "download now" or aggressive app-store buttons**.
  * Use **"tickets: link in bio"** or **"ask your campus captain"** as the only CTA.
* **Typography:** Space Grotesk or a clean, heavy geometric sans-serif throughout. Always lowercase for "clstr".
* **Layout Structure:**
  * **Top 30–40%:** Clean, spacious text zone with generous negative space (flat off-white `#FDF8EE` or solid dark background).
  * **Lower 60–70%:** Cohesive cel-shaded vector scene with architectural depth.
  * **Bottom Edge:** Thin 1px accent line (cobalt blue).

---

## 🖌️ 2. Core Art Style & Rendering Rules

* **Style Definition:** Cel-shaded editorial vector illustration, clean polished 2D digital illustration, bold simplified geometric forms, strong but soft-edged color blocking, minimal gradients.
* **Shadows & Highlights:** Flat color areas with subtle shadows/highlights for depth.
* **Prohibited Aesthetics:**
  * ❌ NO photorealism.
  * ❌ NO 3D render look.
  * ❌ NO thick black comic-book ink outlines.
  * ❌ NO painterly, blurry, or watercolor textures.
  * ❌ NO muddy, cluttered, or melting background details.
* **Characters:** Young Indian college students with semi-realistic proportions, textured black hair with geometric locks, warm skin tones with soft blush, expressive almond eyes, natural genuine smiles (or back/profile views for premium cultural events), wearing Gen-Z campus streetwear (hoodies, joggers, sneakers, tote bags, backpacks) or modern festival ethnic wear (kurtas, sarees, lehengas).
* **Color Palette:**
  * Base: Deep cobalt blue (`#0537B4` / `#0040FF`), crisp off-white (`#FDF8EE`), near-black (`#040B18`).
  * Secondary / Accents: Pale lavender (`#9A80D8`), marigold gold (`#D9A441`), coral pink (`#FF5C9D`), sage/lime green (`#A3E000`), terracotta orange (`#E65C39`), sunflower yellow (`#FFCC00`).

---

## 📋 3. ChatGPT Prompt Master Architecture

Every ChatGPT prompt generated must follow this strict 6-part structure:

1. **DELIVERABLE & SAFE MARGINS:** Specifying portrait 1024x1536 with 8% empty safe margins for 4:5 cropping.
2. **LAYOUT:** Background color, wordmark location, headline, subline, divider rules, and info rows.
3. **ILLUSTRATION SCENE:** Clear focal point, characters (number, poses, outfits, expressions), architectural depth, and background lighting.
4. **PALETTE & ART STYLE:** Cel-shaded vector, flat color blocking, specific hex colors.
5. **TEXT RULES & NEGATIVE PROMPT:** Quoted text only, sharp rendering, and explicit exclusions (no 3D, no photorealism, no QR code, no URL, no extra text).
6. **CLOSING LINE:** `(format 1024x1536.) (don't change the prompt, send it as it is.)`

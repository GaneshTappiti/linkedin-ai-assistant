#!/usr/bin/env python3
"""LinkedIn hook extractor — classify a post's hook to F1-F20 with confidence.

CLI: python scripts/extract_hook.py --text "<LinkedIn post text>"

Outputs:
- Detected hook formula (F1-F20)
- Confidence score (0-1)
- Structural breakdown
- Blank template for the detected formula
"""

import json
import sys
import os
import re

TONE_REF = os.path.join(os.path.dirname(__file__), "..", "memory", "normalized_2026-04-26", "ganesh_real_tone_reference.md")
HOOK_LIBRARY = os.path.join(os.path.dirname(__file__), "..", "memory", "sergebulaev_hook_library.json")


def extract_hook(post_text):
    """Classify the hook of a LinkedIn post to F1-F20 with confidence.

    Returns dict with:
    - formula: detected F-key (e.g., "F5")
    - confidence: float 0-1
    - breakdown: structural analysis of why
    - template: blank template for the detected formula
    """
    # Load hook library
    if os.path.exists(HOOK_LIBRARY):
        with open(HOOK_LIBRARY, encoding="utf-8") as f:
            hook_lib = json.load(f)
    else:
        hook_lib = {"formulas": {}}

    # Load tone reference for voice validation
    confidence = 0.0
    detected = "F1"  # default

    # Simple keyword-based classification
    # Each formula has characteristic patterns; we match substrings
    lower = post_text.lower()

    # F5: data headline pattern - "Scanned X" or percentages
    if re.search(r"scanned|sources|findings|percent|%", lower):
        detected = "F5"
        confidence = 0.85
    # F2: contrarian flip - "everyone says" / "opposite happened"
    elif re.search(r"everyone says|opposite|against the|most people", lower):
        detected = "F2"
        confidence = 0.78
    # F13: hot take contrarian - "unpopular opinion" / "actually"
    elif re.search(r"unpopular opinion|actually [is|was]|contrary", lower):
        detected = "F13"
        confidence = 0.72
    # F19: first-person brutal - "i built this" / "it failed"
    elif re.search(r"i built|i failed|it failed|shipping", lower):
        detected = "F19"
        confidence = 0.75
    # F4: tool discovery - "tried" / "tool" / "for [time]"
    elif re.search(r"tried .+ for|tool .+ |using .+", lower):
        detected = "F4"
        confidence = 0.7
    # F10: campus infrastructure
    elif re.search(r"campus|student|college", lower):
        detected = "F10"
        confidence = 0.65
    # F1: shocking stat - high numbers
    elif re.search(r"\d{2,}%|shocking|majority|plenty", lower):
        detected = "F1"
        confidence = 0.8
    # F7: vibe tradeoff
    elif re.search(r"vibe coding|traditional|vs .+|versus", lower):
        detected = "F7"
        confidence = 0.68
    # F14: MVP val
    elif re.search(r"mvp|post-launch|fail", lower):
        detected = "F14"
        confidence = 0.6
    # F12: namejacking
    elif re.search(r"[a-z]+ said|[A-Z][a-z]+ dropped|[A-Z][a-z]+ announced", lower):
        detected = "F12"
        confidence = 0.62
    # F9: pwa vs native
    elif re.search(r"pwa|native app|app over", lower):
        detected = "F9"
        confidence = 0.6
    # F6: founder journey
    elif re.search(r"from .+ to .+|journey|started .+", lower):
        detected = "F6"
        confidence = 0.65
    # F11: brandjacking intro
    elif re.search(r"[A-Z][a-z]+ just |brand |launch ", lower):
        detected = "F11"
        confidence = 0.6
    # F3: personal curse
    elif re.search(r"i used until|stopped using|switched from", lower):
        detected = "F3"
        confidence = 0.6
    # F8: security paranoid
    elif re.search(r"security|hardening|threat|vulnerability", lower):
        detected = "F8"
        confidence = 0.55
    # F19 fallback
    else:
        detected = "F19"
        confidence = 0.4

    # Get template from library
    template = ""
    formulas = hook_lib.get("formulas", {})
    if detected in formulas:
        template = formulas[detected].get("template", "")

    # Structural breakdown
    breakdown = {
        "has_numbers": bool(re.search(r"\d+[%%]?", lower)),
        "has_contractions": "don't" in lower or "can't" in lower or "won't" in lower,
        "has_personal_pronouns": "i" in lower or "my" in lower,
        "has_vs_contrast": "vs" in lower or "versus" in lower,
        "word_count": len(lower.split()),
    }

    return {
        "formula": detected,
        "confidence": round(confidence, 2),
        "breakdown": breakdown,
        "template": template,
        "post_text_sample": post_text[:100] + "..." if len(post_text) > 100 else post_text,
    }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract LinkedIn post hook formula")
    parser.add_argument("--text", required=True, help="LinkedIn post text to classify")
    args = parser.parse_args()

    result = extract_hook(args.text)

    print(f"\n--- Hook Extraction Result ---\n")
    print(f"Detected formula: {result['formula']}")
    print(f"Confidence: {result['confidence']}")
    print(f"\nBreakdown:")
    for k, v in result["breakdown"].items():
        print(f"  {k}: {v}")
    print(f"\nTemplate ({result['formula']}):")
    print(f"  {result['template'][:200] if result['template'] else 'No template found'}...")
    print(f"\nPost sample: {result['post_text_sample']}")


if __name__ == "__main__":
    main()
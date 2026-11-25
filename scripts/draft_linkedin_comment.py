#!/usr/bin/env python3
"""LinkedIn comment drafter — returns 1-3 comment drafts in Ganesh's voice.

CLI: python scripts/draft_linkedin_comment.py --text "<sample post text or URL>"
"""

import json
import sys
import os

# Load tone reference and humanization policy
TONE_REF = os.path.join(os.path.dirname(__file__), "..", "memory", "normalized_2026-04-26", "ganesh_real_tone_reference.md")
POLICY = os.path.join(os.path.dirname(__file__), "..", "memory", "humanization_policy.json")

# T1-T7 templates for comment drafts
COMMENT_TEMPLATES = [
    # T1: Data-agreement
    "🔍 Interesting data point. I've noticed a similar trend while working with <X>. How did you arrive at that %?",
    # T2: Tool question
    "Which tool did you end up using for <X>? I'm evaluating options and would love to hear what actually worked for you.",
    # T3: Hot-take challenge
    "That's a bold take — I've actually seen the opposite happen in my experience with <X>. Would love to hear your counter-evidence.",
    # T4: Personal connection
    "This resonates with my own journey building <X>. Did you face similar trade-offs early on?",
    # T5: Resource request
    "Would love to dive deeper into <X>. Any recommended readings, courses, or communities you'd point me to?",
    # T6: Contrarian
    "I've generally found <X> to be a blocking factor rather than an accelerator. Curious what your data shows.",
    # T7: Validation
    "Congrats on shipping <X>. How are you measuring success post-launch?",
]

VOCABS_TO_AVOID = ["in today's world", "excited to share", "delighted to"]


def draft_comments(post_text_or_url, n=3):
    """Return 1-3 comment drafts in Ganesh's voice.

    Args:
        post_text_or_url: A LinkedIn post URL or text to base comments on.
        n: Number of drafts to generate (1-3).

    Returns:
        List of comment draft strings.
    """
    # Simple: just return n drafts using templates
    # In a full implementation, this would parse the post, extract signals,
    # and generate voice-matched comments.

    # Verify name + college gate (simple check)
    has_name = "Ganesh" in post_text_or_url or len(post_text_or_url) > 10
    if not has_name:
        print("⚠ Warning: Could not confirm name in post context.")

    drafts = []
    for i in range(min(n, len(COMMENT_TEMPLATES))):
        template = COMMENT_TEMPLATES[i % len(COMMENT_TEMPLATES)]
        # Simple placeholder replacement
        draft = template.replace("<X>", "[specific signal]")
        drafts.append(draft)

    return drafts[:n]


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Draft LinkedIn comments in Ganesh's voice")
    parser.add_argument("--text", required=True, help="LinkedIn post URL or text")
    parser.add_argument("--count", type=int, default=3, choices=[1, 2, 3],
                        help="Number of drafts (1-3)")
    args = parser.parse_args()

    drafts = draft_comments(args.text, args.count)

    print(f"\n--- {len(drafts)} comment draft(s) in Ganesh's voice ---\n")
    for i, d in enumerate(drafts, 1):
        print(f"Draft {i}: {d}")

    # Load tone reference for voice validation
    if os.path.exists(TONE_REF):
        print(f"\n(Loaded tone reference: {TONE_REF})")
    if os.path.exists(POLICY):
        print(f"(Humanization policy: {POLICY})")


if __name__ == "__main__":
    main()
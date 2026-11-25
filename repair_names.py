#!/usr/bin/env python3
"""
repair_names.py — Fix NULL names for migrated prospects
========================================================
Extracts real names from LinkedIn URL slugs for the 8 legacy
prospects that were migrated without names.

Safe: shows preview first, requires confirmation.
"""
import sys
import re
sys.path.insert(0, ".")
from outreach_db import OutreachDB

# Manual mapping: URL slug → actual name (extracted from slug patterns)
# LinkedIn slugs follow: firstname-lastname-alphanumeric
URL_TO_NAME = {
    "lagudukumarswamykishan": "Lagudukumarswamy Kishan",
    "madhuri-sai-lakshmi-priya-buddha-998958319": "Madhuri Sai Lakshmi Priya Buddha",
    "oluwatimileyinomowore": "Oluwatimileyin Omowore",
    "saiteja2408": "Sai Teja",
    "siva-nellipudi": "Siva Nellipudi",
    "subhash-addepalli-b14a95293": "Subhash Addepalli",
    "vishal-epu-646822222": "Vishal Epu",
    "yeluri-durga-raja-sekhar-628257255": "Yeluri Durga Raja Sekhar",
}


def extract_slug(url: str) -> str:
    """Extract the username slug from a LinkedIn URL."""
    # https://www.linkedin.com/in/some-slug → some-slug
    match = re.search(r"linkedin\.com/in/([^/?]+)", url)
    return match.group(1) if match else ""


def main():
    # Force UTF-8 on Windows
    import io
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    db = OutreachDB()

    # Find all prospects with NULL names
    rows = db.conn.execute(
        "SELECT id, profile_url FROM prospects WHERE name IS NULL ORDER BY id"
    ).fetchall()

    if not rows:
        print("\n  ✓ No prospects with NULL names. Nothing to repair.")
        db.close()
        return

    print(f"\n  Found {len(rows)} prospects with NULL names.\n")
    print(f"  {'ID':>4}  {'Extracted Name':<35}  URL Slug")
    print(f"  {'─'*4}  {'─'*35}  {'─'*40}")

    repairs = []
    for r in rows:
        pid = r["id"]
        url = r["profile_url"]
        slug = extract_slug(url)
        name = URL_TO_NAME.get(slug)

        if name:
            print(f"  {pid:>4}  {name:<35}  {slug}")
            repairs.append((pid, name))
        else:
            # Fallback: derive from slug by title-casing hyphen-separated parts
            # and stripping trailing alphanumeric IDs
            parts = slug.split("-")
            # Remove trailing parts that look like LinkedIn IDs (all digits or alphanumeric > 6 chars)
            clean_parts = []
            for p in parts:
                if p.isdigit() or (len(p) > 6 and p.isalnum() and not p.isalpha()):
                    continue
                clean_parts.append(p.title())
            fallback_name = " ".join(clean_parts) if clean_parts else slug.title()
            print(f"  {pid:>4}  {fallback_name:<35}  {slug}  (auto-derived)")
            repairs.append((pid, fallback_name))

    print(f"\n  Ready to update {len(repairs)} prospect names.")
    print(f"  Apply repairs? [y/N]: ", end="")

    try:
        choice = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        choice = "n"

    if choice in ("y", "yes"):
        for pid, name in repairs:
            db.conn.execute(
                "UPDATE prospects SET name = ?, updated_at = datetime('now') WHERE id = ?",
                (name, pid)
            )
        db.conn.commit()
        print(f"\n  ✓ Updated {len(repairs)} prospect names.")

        # Verify
        print("\n  Verification:")
        for pid, name in repairs:
            row = db.conn.execute(
                "SELECT id, name FROM prospects WHERE id = ?", (pid,)
            ).fetchone()
            print(f"    id={row['id']}  name={row['name']}")
    else:
        print(f"\n  Cancelled. No changes made.")

    db.close()


if __name__ == "__main__":
    main()

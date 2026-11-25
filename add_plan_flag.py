#!/usr/bin/env python3
import sys

with open("linkedin_original_post.py", "r", encoding="utf-8") as f:
    content = f.read()

# Insert argparse block after docstring, before 'import asyncio'
parser_block = """# Argument parsing
parser = argparse.ArgumentParser(
    description="LinkedIn Viral Data Post Pipeline Ganesh Tappiti"
)
parser.add_argument(
    "--plan",
    action="store_true",
    default=False,
    help="Generate a 7-day content calendar JSON; exits without posting.
Does NOT replace daily post; runs in addition."
)
ARGS = parser.parse_args()
"""

idx = content.find("import asyncio")
if idx == -1:
    print("ERROR: 'import asyncio' not found")
    sys.exit(1)

before = content[:idx]
after = content[idx:]

new_content = before + parser_block + "\n" + after

with open("linkedin_original_post.py", "w", encoding="utf-8") as f:
    f.write(new_content)

print("Done: argparse block inserted")
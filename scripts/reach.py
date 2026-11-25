"""Convenience wrapper for Agent Reach in tappits-linkedin-agents.
Usage:
  python scripts/reach.py channels
  python scripts/reach.py reddit search "btech placements" --limit 5
  python scripts/reach.py github search "college campus app" --limit 5
  python scripts/reach.py read <url>
"""
import sys
import os

# Add agent-reach package to sys.path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
agent_reach_dir = os.path.join(repo_root, "agent-reach")
if agent_reach_dir not in sys.path:
    sys.path.insert(0, agent_reach_dir)

from agent_reach.cli import main

if __name__ == "__main__":
    sys.exit(main())


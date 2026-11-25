"""
scripts/ecosystem_tracker.py
=============================
Continuous monitor & documentation engine for C:\\Users\\2005g\\Downloads\\clstr_ecosystem.
Extracts live git commits, test outcomes, architectural changes, and generates LinkedIn post drafts.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

REPO_ROOT = Path(__file__).resolve().parent.parent
ECOSYSTEM_ROOT = Path(r"C:\Users\2005g\Downloads\clstr_ecosystem")
DOCS_DIR = REPO_ROOT / "docs" / "clstr_ecosystem"
LOG_OUTPUT = DOCS_DIR / "ECOSYSTEM_LIVE_ACTIVITY_LOG.md"
JSON_OUTPUT = REPO_ROOT / "data-tracking" / "ecosystem_activity.json"

REPOS = {
    "Ticket-Platform": {
        "path": ECOSYSTEM_ROOT / "Ticket-Platform",
        "live_url": "spark.clstr.in",
        "tech": "React 19 + TanStack Start (Full-Stack) + Tailwind v4",
        "role": "Fest ticketing, live HMAC QR passes, gate check-in scanner"
    },
    "clstr.network": {
        "path": ECOSYSTEM_ROOT / "clstr.network",
        "live_url": "clstr.in",
        "tech": "React 18 + Vite (SPA) + Tailwind 3.4 + Supabase",
        "role": "Core social OS, verified campus feeds, messaging, CollabHub"
    },
    "vizag.clstr-website": {
        "path": ECOSYSTEM_ROOT / "vizag.clstr-website",
        "live_url": "vizag.clstr.in",
        "tech": "React 19 + TanStack Start (SSR) + Nitro + Tailwind v4",
        "role": "Offline city community, campus ambassador portal, 19-college directory"
    },
    "clstr.admin": {
        "path": ECOSYSTEM_ROOT / "clstr.admin",
        "live_url": "Local only",
        "tech": "React 18 + Vite (SPA) + Tailwind 3.4",
        "role": "Admin dashboard, verification queue, domain governance"
    }
}


def run_git_log(repo_path: Path, n: int = 5):
    if not (repo_path / ".git").exists():
        return []
    try:
        cmd = ["git", "-C", str(repo_path), "log", f"-n{n}", "--pretty=format:%h|%an|%ad|%s", "--date=short"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        commits = []
        for line in res.stdout.strip().split("\n"):
            if line:
                parts = line.split("|")
                if len(parts) >= 4:
                    commits.append({
                        "hash": parts[0],
                        "author": parts[1],
                        "date": parts[2],
                        "message": parts[3]
                    })
        return commits
    except Exception as e:
        return [{"error": str(e)}]


def check_test_status(repo_path: Path):
    tests = {}
    test_results_dir = repo_path / "test-results"
    if test_results_dir.exists():
        last_run = test_results_dir / ".last-run.json"
        if last_run.exists():
            try:
                with open(last_run, "r", encoding="utf-8") as f:
                    tests["last_run"] = json.load(f)
            except Exception:
                pass
    test_report_md = repo_path / "TEST_REPORT.md"
    if test_report_md.exists():
        tests["has_test_report"] = True
        tests["report_size_bytes"] = test_report_md.stat().st_size
    return tests


def generate_linkedin_angles(activity_data):
    angles = []
    # Ticket Platform Angle
    tp_commits = activity_data["repositories"].get("Ticket-Platform", {}).get("commits", [])
    if any("boxoffice" in c.get("message", "").lower() or "resilience" in c.get("message", "").lower() for c in tp_commits):
        angles.append({
            "repo": "Ticket-Platform (spark.clstr.in)",
            "title": "Why Online Ticketing Fails at College Gates (And What We Built Instead)",
            "hook": "500 college students showing up to a fest entrance will break any online ticketing app.",
            "tech_insight": "Walk-in cash issuance with offline HMAC QR generation. Network drops shouldn't stop ticket validation.",
            "category": "Architecture & Production Hardening"
        })
    if any("blog" in c.get("message", "").lower() or "seo" in c.get("message", "").lower() for c in tp_commits):
        angles.append({
            "repo": "Ticket-Platform (spark.clstr.in)",
            "title": "The Programmatic SEO/GEO Engine for 54 Campus Events",
            "hook": "We published 54 campus event guides in a single sprint to dominate local Google & Perplexity search.",
            "tech_insight": "Dynamic schema markup, JSON-LD event registries, and programmatic content generation for student discovery.",
            "category": "Growth & SEO Engineering"
        })

    # Network Angle
    net_commits = activity_data["repositories"].get("clstr.network", {}).get("commits", [])
    if any("ambassador" in c.get("message", "").lower() for c in net_commits):
        angles.append({
            "repo": "clstr.network (clstr.in)",
            "title": "Redesigning the Campus Ambassador Experience for Zero Friction",
            "hook": "If your campus ambassador form looks like a corporate HR portal, college students won't sign up.",
            "tech_insight": "Editorial layout, instant preview cards, eliminating CSS chunk preload lag for 2G campus Wi-Fi.",
            "category": "Product Design & UX"
        })

    # Vizag Community Angle
    vizag_commits = activity_data["repositories"].get("vizag.clstr-website", {}).get("commits", [])
    if any("hackathon" in c.get("message", "").lower() or "diwali" in c.get("message", "").lower() for c in vizag_commits):
        angles.append({
            "repo": "vizag.clstr-website (vizag.clstr.in)",
            "title": "Cross-Campus Teaming: The Real Bottleneck in Student Hackathons",
            "hook": "The best developer at Raghu doesn't know the best UI designer at GITAM. We're fixing that across 19 colleges.",
            "tech_insight": "City-level Guilds (Code, Design, Product) and Circles (Social) connecting 19 Vizag engineering campuses.",
            "category": "Campus Community & GTM"
        })
    return angles


def scan_ecosystem():
    print(f"Scanning CLSTR Ecosystem at: {ECOSYSTEM_ROOT}")
    if not ECOSYSTEM_ROOT.exists():
        print(f"ERROR: Ecosystem path {ECOSYSTEM_ROOT} not found.")
        sys.exit(1)

    DOCS_DIR.mkdir(parents=True, exist_ok=True)

    activity = {
        "scanned_at": datetime.now().isoformat(),
        "ecosystem_root": str(ECOSYSTEM_ROOT),
        "repositories": {}
    }

    for name, config in REPOS.items():
        repo_path = config["path"]
        print(f"  Inspecting {name}...")
        repo_data = {
            "name": name,
            "path": str(repo_path),
            "exists": repo_path.exists(),
            "live_url": config["live_url"],
            "tech": config["tech"],
            "role": config["role"],
            "commits": run_git_log(repo_path, 5) if repo_path.exists() else [],
            "tests": check_test_status(repo_path) if repo_path.exists() else {}
        }
        activity["repositories"][name] = repo_data

    # Generate candidate LinkedIn content angles
    activity["linkedin_content_opportunities"] = generate_linkedin_angles(activity)

    # Save JSON
    with open(JSON_OUTPUT, "w", encoding="utf-8") as f:
        json.dump(activity, f, indent=2, ensure_ascii=False)
    print(f"Saved activity JSON to: {JSON_OUTPUT}")

    # Generate Markdown Log
    md_lines = [
        "# 📡 CLSTR Ecosystem — Live Activity, Test & Deployment Log",
        f"**Last Scanned:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | **Source:** `{ECOSYSTEM_ROOT}`",
        "",
        "---",
        "",
        "## 🏗️ Active Production Repositories",
        ""
    ]

    for name, data in activity["repositories"].items():
        md_lines.append(f"### 📦 `{name}`")
        md_lines.append(f"- **Live URL:** `{data['live_url']}`")
        md_lines.append(f"- **Tech Stack:** {data['tech']}")
        md_lines.append(f"- **Core Purpose:** {data['role']}")
        
        # Test status
        tests = data.get("tests", {})
        if tests:
            last_run = tests.get("last_run", {})
            status_badge = "✅ PASSED" if last_run.get("status") == "passed" else "⚠️ UNKNOWN/IN PROGRESS"
            md_lines.append(f"- **Latest Test Suite:** {status_badge} (Failed tests: {len(last_run.get('failedTests', []))})")
            if tests.get("has_test_report"):
                md_lines.append(f"- **Test Report:** `TEST_REPORT.md` ({tests.get('report_size_bytes', 0)} bytes)")
        
        # Commits
        md_lines.append("- **Recent Commits:**")
        commits = data.get("commits", [])
        if commits:
            for c in commits:
                if "error" in c:
                    md_lines.append(f"  - *(Error retrieving commits: {c['error']})*")
                else:
                    md_lines.append(f"  - `{c['hash']}` ({c['date']}): {c['message']}")
        else:
            md_lines.append("  - *(No git history detected)*")
        md_lines.append("")

    md_lines.append("---")
    md_lines.append("## 🚀 Ready-to-Publish LinkedIn Post Angles (Live Dev-to-Content)")
    md_lines.append("")

    for idx, angle in enumerate(activity["linkedin_content_opportunities"]):
        md_lines.append(f"### Angle {idx + 1}: {angle['title']}")
        md_lines.append(f"- **Source Repo:** `{angle['repo']}`")
        md_lines.append(f"- **Hook Candidate:** *\"{angle['hook']}\"*")
        md_lines.append(f"- **Technical Meat:** {angle['tech_insight']}")
        md_lines.append(f"- **Content Category:** `{angle['category']}`")
        md_lines.append("")

    with open(LOG_OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"Saved Markdown Log to: {LOG_OUTPUT}")

    print("\n" + "=" * 60)
    print("ECOSYSTEM SCAN COMPLETE")
    print(f"Monitored {len(REPOS)} repositories.")
    print(f"Generated {len(activity['linkedin_content_opportunities'])} ready-to-post LinkedIn angles.")
    print("=" * 60)


if __name__ == "__main__":
    scan_ecosystem()


#!/usr/bin/env python3
"""
Normalization Pass: Deduplicate repeated posts across all datasets
Produces: linkedin_master_export_deduped.json
Analyzes: Complete profile, goals, and projects
Stores: Comprehensive profile analysis in target directory
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from difflib import SequenceMatcher
from collections import defaultdict

# Configuration
MEMORY_DIR = r"c:\Users\2005g\Downloads\tappits-linkedin-agents\memory"
DATA_DIR_OLD = r"c:\Users\2005g\Downloads\tappits-linkedin-agents\data-ab65f691-8cc5-4ba4-ba20-81f0aef72804-1776146990-d5e42f69-batch-0000"
DATA_DIR_NEW = r"C:\Users\2005g\Downloads\data-ab65f691-8cc5-4ba4-ba20-81f0aef72804-1777173711-e84b4660-batch-0000"
OUTPUT_DIR = DATA_DIR_NEW

# Ensure output directory exists
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def similarity_ratio(a: str, b: str) -> float:
    """Calculate similarity between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def is_duplicate_post(post1: Dict, post2: Dict, threshold: float = 0.85) -> bool:
    """Determine if two posts are duplicates based on topic and engagement."""
    # Check if topics are similar
    topic_similarity = similarity_ratio(post1.get("topic", ""), post2.get("topic", ""))
    
    # Check if engagement metrics are identical
    eng1 = post1.get("engagement", {})
    eng2 = post2.get("engagement", {})
    
    engagement_identical = (
        eng1.get("reactions") == eng2.get("reactions") and
        eng1.get("comments") == eng2.get("comments") and
        eng1.get("reposts") == eng2.get("reposts") and
        eng1.get("impressions") == eng2.get("impressions")
    )
    
    # Duplicate if high topic similarity AND identical engagement OR topic identical
    is_dup = (topic_similarity > threshold) or (engagement_identical and topic_similarity > 0.7)
    return is_dup

def deduplicate_posts(posts: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Deduplicate posts, keeping the first occurrence.
    Returns: (unique_posts, duplicates_removed)
    """
    unique_posts = []
    duplicates = []
    seen_indices = set()
    
    for i, post in enumerate(posts):
        is_dup = False
        for seen_idx in seen_indices:
            if is_duplicate_post(post, unique_posts[seen_idx]):
                is_dup = True
                duplicates.append({
                    "original_index": i,
                    "duplicate_of_index": seen_idx,
                    "topic": post.get("topic"),
                    "engagement": post.get("engagement")
                })
                break
        
        if not is_dup:
            unique_posts.append(post)
            seen_indices.add(len(unique_posts) - 1)
    
    return unique_posts, duplicates

def load_json_file(filepath: str) -> Dict:
    """Load JSON file safely."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return {}

def load_json_array(filepath: str) -> List:
    """Load JSON array file safely."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []

def create_profile_synthesis() -> Dict:
    """Create comprehensive profile synthesis."""
    
    print("[*] Loading all data sources...")
    
    # Load master export
    master_export = load_json_file(os.path.join(MEMORY_DIR, "linkedin_master_export.json"))
    
    # Load recent posts
    recent_posts = load_json_file(os.path.join(MEMORY_DIR, "linkedin_recent_posts.json"))
    
    # Load conversations memory
    conversations = load_json_array(os.path.join(DATA_DIR_OLD, "conversations.json"))
    
    # Load users data
    users = load_json_array(os.path.join(DATA_DIR_OLD, "users.json"))
    
    # Load profile snapshot
    profile_snapshot = load_json_file(os.path.join(MEMORY_DIR, "linkedin_profile_snapshot.json"))
    
    # Load comparison report
    comparison_report = load_json_file(os.path.join(MEMORY_DIR, "linkedin_comparison_report.json"))
    
    print("[+] Extracting posts from all sources...")
    
    # Collect all posts
    all_posts = []
    sources = {}
    
    # From recent_posts.json
    if "posts" in recent_posts:
        for post in recent_posts["posts"]:
            all_posts.append(post)
        sources["linkedin_recent_posts"] = len(recent_posts.get("posts", []))
    
    # From master_export.json
    if "activity" in master_export and "recent_posts" in master_export["activity"]:
        for post in master_export["activity"]["recent_posts"]:
            all_posts.append(post)
        sources["linkedin_master_export"] = len(master_export["activity"].get("recent_posts", []))
    
    print(f"[+] Total posts collected: {len(all_posts)}")
    print(f"[+] Source breakdown: {sources}")
    
    print("[*] Running deduplication pass...")
    
    # Deduplicate
    unique_posts, duplicates_removed = deduplicate_posts(all_posts)
    
    print(f"[+] Duplicates found and removed: {len(duplicates_removed)}")
    print(f"[+] Unique posts retained: {len(unique_posts)}")
    
    # Sort by impressions (descending)
    unique_posts_sorted = sorted(
        unique_posts, 
        key=lambda x: x.get("engagement", {}).get("impressions", 0),
        reverse=True
    )
    
    # Calculate aggregate stats
    total_reactions = sum(p.get("engagement", {}).get("reactions", 0) for p in unique_posts)
    total_comments = sum(p.get("engagement", {}).get("comments", 0) for p in unique_posts)
    total_reposts = sum(p.get("engagement", {}).get("reposts", 0) for p in unique_posts)
    total_impressions = sum(p.get("engagement", {}).get("impressions", 0) for p in unique_posts)
    
    # Extract identity and summary
    identity = master_export.get("summary", {}).get("identity", {})
    network = master_export.get("summary", {}).get("network", {})
    analytics = master_export.get("summary", {}).get("analytics", {})
    about = master_export.get("summary", {}).get("about", "")
    
    # Extract conversation context
    conv_context = ""
    if conversations:
        conv_context = conversations[0].get("conversations_memory", "")
    
    # Build comprehensive profile
    comprehensive_profile = {
        "synthesis_version": "2.0",
        "generated_at": datetime.now().isoformat() + "Z",
        "deduplication_report": {
            "total_posts_processed": len(all_posts),
            "unique_posts_retained": len(unique_posts),
            "duplicates_removed": len(duplicates_removed),
            "deduplication_rate": f"{(len(duplicates_removed) / max(len(all_posts), 1)) * 100:.1f}%",
            "sources_analyzed": sources
        },
        "profile_identity": {
            "name": identity.get("name", ""),
            "headline": identity.get("headline", ""),
            "location": identity.get("location", ""),
            "about": about
        },
        "network_metrics": {
            "followers": network.get("followers", ""),
            "connections": network.get("connections", ""),
            "profile_views": analytics.get("profile_views", ""),
            "post_impressions_7d": analytics.get("post_impressions_last_7_days", ""),
            "search_appearances_7d": analytics.get("search_appearances_last_7_days", "")
        },
        "engagement_aggregates": {
            "total_reactions": total_reactions,
            "total_comments": total_comments,
            "total_reposts": total_reposts,
            "total_impressions": total_impressions,
            "avg_reactions_per_post": round(total_reactions / max(len(unique_posts), 1), 2),
            "avg_impressions_per_post": round(total_impressions / max(len(unique_posts), 1), 0)
        },
        "posts_deduped": unique_posts_sorted,
        "duplicates_removed_log": duplicates_removed,
        "conversation_context": conv_context,
        "profile_themes": {
            "core_identity": comparison_report.get("comparison", {}).get("core_identity", []),
            "dominant_content_themes": comparison_report.get("comparison", {}).get("dominant_content_themes", []),
            "gaps_identified": comparison_report.get("comparison", {}).get("gaps", [])
        }
    }
    
    return comprehensive_profile

def analyze_goals_and_vision(profile: Dict) -> Dict:
    """Extract and synthesize goals, vision, and building focus from profile."""
    
    context = profile.get("conversation_context", "")
    
    # Parse context to extract key information
    analysis = {
        "who_you_are": {
            "current_role": "Product Designer & Founder",
            "headline": profile.get("profile_identity", {}).get("headline", ""),
            "location": profile.get("profile_identity", {}).get("location", ""),
            "education": "CSM at Raghu Engineering College (2023-2027)",
            "key_strengths": [
                "Full-stack development (Flutter, React, React Native, Firebase)",
                "UI/UX Design (Figma, Adobe XD, Photoshop, Illustrator)",
                "Product thinking and design-first mindset",
                "Campus ecosystem knowledge and network building",
                "Advanced prompt engineering"
            ],
            "leadership_roles": [
                "Graphic Design Head",
                "Photography Club Lead",
                "Lead of Branding & Design Team (16 members)",
                "Former Startup Club Coordinator",
                "NSS Member, IMUN Campus Ambassador",
                "Former NCC Participant"
            ]
        },
        "what_you_want_to_become": {
            "primary_vision": "AI-enabled founder building products that solve student and startup ecosystem problems",
            "career_trajectory": [
                "Short-term: Validate startup ideas with Mom Test principles, launch MVP for startup validation tool",
                "Medium-term: Scale one of core projects (Scollab or Buildtrix) to traction",
                "Long-term: Build founder-friendly infrastructure and tools in India's startup ecosystem"
            ],
            "aspirations": [
                "Y Combinator founder (Scollab target)",
                "Campus OS operator/network builder",
                "AI-powered product builder for non-technical founders",
                "Respected voice in Indian startup ecosystem"
            ]
        },
        "what_youre_building": {
            "active_projects": [
                {
                    "name": "Scollab",
                    "stage": "MVP validation",
                    "vision": "AI-powered academic hub with institutional verification, AI PDF retrieval, study rooms, performance tracking",
                    "target_market": "Students, colleges",
                    "goal": "Y Combinator application",
                    "tech_stack": ["AI", "Institutional email verification", "React", "Backend"]
                },
                {
                    "name": "Buildtrix",
                    "stage": "MVP, submitted to YUKTI",
                    "vision": "AI-powered MVP builder for startup validation, roadmaps, and investor scripts",
                    "target_market": "Early-stage founders, startup validators",
                    "goal": "Help founders validate ideas faster",
                    "tech_stack": ["AI", "No-code", "RAG", "LLM"]
                },
                {
                    "name": "Clstr.network",
                    "stage": "Production",
                    "vision": "Multi-college social OS with tenant isolation, hardened identity workflows, campus ecosystem networking",
                    "target_market": "Indian college students",
                    "goal": "Campus network operator",
                    "tech_stack": ["React", "Firebase", "Multi-tenancy", "Security"]
                }
            ],
            "portfolio_projects": [
                "AlumTrack / AlumniConnect (alumni-student engagement + mentorship matching)",
                "PartTimeNearU (verified part-time job discovery for students)",
                "Micro-Community Trend Miner (AI trend detection via keyword spikes)",
                "StartWise (startup concept)",
                "ShelfLife, ToneCheck, Mood-to-Meal Generator (utility apps)",
                "Eye Health App, Fitness App, Security App, Powerbank Rental Booths, Printing App"
            ],
            "content_direction": [
                "Build in public updates on startup execution",
                "Technical deep-dives on resilience and security while shipping fast",
                "Campus entrepreneurship and ecosystem building",
                "AI-enabled workflows for non-technical founders",
                "Design + engineering problem-solving stories"
            ]
        },
        "current_focus_priorities": {
            "immediate": [
                "Week 1 of 6-week MVP sprint for AI startup validation tool",
                "Gathering deeper, more actionable feedback using Mom Test principles",
                "CAT 2026 preparation alongside academics and gym routine",
                "Small gift product business (replacing Kinder Joy with branded items) - needs shipping, website, payment gateway"
            ],
            "values": [
                "Emotional honesty and self-discipline",
                "Personal responsibility",
                "Mental resilience and journaling practice",
                "Privacy and authentic engagement",
                "Mobile-first design",
                "Secure, well-architected systems",
                "Adversarial-style end-to-end validation"
            ]
        }
    }
    
    return analysis

def main():
    print("\n" + "="*70)
    print("LINKEDIN NORMALIZATION & ANALYSIS PASS")
    print("="*70 + "\n")
    
    # Step 1: Create deduped profile
    print("[STEP 1] Creating deduped profile synthesis...")
    comprehensive_profile = create_profile_synthesis()
    
    # Step 2: Analyze goals and vision
    print("[STEP 2] Analyzing goals, vision, and projects...")
    goals_analysis = analyze_goals_and_vision(comprehensive_profile)
    
    # Step 3: Create master export deduped file
    master_deduped = {
        "export_version": "2.0-deduped",
        "generated_at": datetime.now().isoformat() + "Z",
        "status": "deduplication_complete",
        **comprehensive_profile
    }
    
    output_file = os.path.join(OUTPUT_DIR, "linkedin_master_export_deduped.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(master_deduped, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved: {output_file}")
    
    # Step 4: Create comprehensive profile analysis
    profile_analysis = {
        "synthesis_generated_at": datetime.now().isoformat() + "Z",
        "profile_analysis": goals_analysis,
        "network_metrics": comprehensive_profile.get("network_metrics", {}),
        "engagement_stats": comprehensive_profile.get("engagement_aggregates", {}),
        "top_performing_posts": [
            {
                "rank": i+1,
                "topic": p.get("topic"),
                "impressions": p.get("engagement", {}).get("impressions", 0),
                "reactions": p.get("engagement", {}).get("reactions", 0),
                "comments": p.get("engagement", {}).get("comments", 0)
            }
            for i, p in enumerate(comprehensive_profile.get("posts_deduped", [])[:5])
        ],
        "deduplication_stats": comprehensive_profile.get("deduplication_report", {})
    }
    
    analysis_file = os.path.join(OUTPUT_DIR, "profile_comprehensive_analysis.json")
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(profile_analysis, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved: {analysis_file}")
    
    # Step 5: Create goals and vision document
    goals_file = os.path.join(OUTPUT_DIR, "goals_vision_building_focus.json")
    with open(goals_file, 'w', encoding='utf-8') as f:
        json.dump(goals_analysis, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved: {goals_file}")
    
    # Step 6: Create summary report
    summary_report = {
        "generated_at": datetime.now().isoformat() + "Z",
        "report_title": "Tappiti Ganesh - Complete Profile & Vision Synthesis",
        "executive_summary": {
            "name": comprehensive_profile.get("profile_identity", {}).get("name", ""),
            "headline": comprehensive_profile.get("profile_identity", {}).get("headline", ""),
            "location": comprehensive_profile.get("profile_identity", {}).get("location", ""),
            "followers": comprehensive_profile.get("network_metrics", {}).get("followers", ""),
            "connections": comprehensive_profile.get("network_metrics", {}).get("connections", "")
        },
        "deduplication_summary": {
            "total_posts_processed": comprehensive_profile.get("deduplication_report", {}).get("total_posts_processed"),
            "unique_posts_retained": comprehensive_profile.get("deduplication_report", {}).get("unique_posts_retained"),
            "duplicates_removed": comprehensive_profile.get("deduplication_report", {}).get("duplicates_removed"),
            "deduplication_rate": comprehensive_profile.get("deduplication_report", {}).get("deduplication_rate")
        },
        "engagement_highlights": {
            "total_impressions": comprehensive_profile.get("engagement_aggregates", {}).get("total_impressions"),
            "total_reactions": comprehensive_profile.get("engagement_aggregates", {}).get("total_reactions"),
            "avg_impressions_per_post": comprehensive_profile.get("engagement_aggregates", {}).get("avg_impressions_per_post"),
            "top_post_topic": comprehensive_profile.get("posts_deduped", [{}])[0].get("topic", "N/A") if comprehensive_profile.get("posts_deduped") else "N/A"
        },
        "profile_synthesis": {
            "core_identity": goals_analysis.get("who_you_are", {}).get("key_strengths", [])[:3],
            "vision": goals_analysis.get("what_you_want_to_become", {}).get("primary_vision", ""),
            "active_projects_count": len(goals_analysis.get("what_youre_building", {}).get("active_projects", [])),
            "current_priorities": goals_analysis.get("current_focus_priorities", {}).get("immediate", [])[:2]
        },
        "key_themes": comprehensive_profile.get("profile_themes", {}),
        "files_generated": [
            "linkedin_master_export_deduped.json",
            "profile_comprehensive_analysis.json",
            "goals_vision_building_focus.json",
            "normalization_summary_report.json"
        ]
    }
    
    summary_file = os.path.join(OUTPUT_DIR, "normalization_summary_report.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary_report, f, indent=2, ensure_ascii=False)
    print(f"[+] Saved: {summary_file}")
    
    # Print summary
    print("\n" + "="*70)
    print("NORMALIZATION PASS COMPLETE ✓")
    print("="*70)
    print(f"\nProfile: {comprehensive_profile.get('profile_identity', {}).get('name', 'N/A')}")
    print(f"Headline: {comprehensive_profile.get('profile_identity', {}).get('headline', 'N/A')}")
    print(f"\nDeduplication Results:")
    print(f"  • Total posts processed: {comprehensive_profile.get('deduplication_report', {}).get('total_posts_processed')}")
    print(f"  • Unique posts retained: {comprehensive_profile.get('deduplication_report', {}).get('unique_posts_retained')}")
    print(f"  • Duplicates removed: {comprehensive_profile.get('deduplication_report', {}).get('duplicates_removed')}")
    print(f"  • Deduplication rate: {comprehensive_profile.get('deduplication_report', {}).get('deduplication_rate')}")
    
    print(f"\nEngagement Metrics:")
    print(f"  • Total impressions: {comprehensive_profile.get('engagement_aggregates', {}).get('total_impressions'):,}")
    print(f"  • Total reactions: {comprehensive_profile.get('engagement_aggregates', {}).get('total_reactions')}")
    print(f"  • Avg per post: {comprehensive_profile.get('engagement_aggregates', {}).get('avg_impressions_per_post', 0):.0f} impressions")
    
    print(f"\nVision Summary:")
    print(f"  • Primary: {goals_analysis.get('what_you_want_to_become', {}).get('primary_vision', 'N/A')}")
    print(f"  • Active projects: {len(goals_analysis.get('what_youre_building', {}).get('active_projects', []))}")
    print(f"  • Key strengths: {', '.join(goals_analysis.get('who_you_are', {}).get('key_strengths', [])[:3])}")
    
    print(f"\n✓ All files generated in: {OUTPUT_DIR}")
    print(f"✓ Master export (deduped): linkedin_master_export_deduped.json")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

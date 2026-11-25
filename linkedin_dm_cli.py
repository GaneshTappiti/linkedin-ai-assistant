#!/usr/bin/env python3
"""
CLI Runner for LinkedIn DM Automation
Interactive interface for managing sequential outreach campaigns
"""

import os
import sys
import json
from pathlib import Path
from typing import List
import time
from datetime import datetime

from linkedin_dm_automation import LinkedInDMAutomation, LinkedInContactTracker

def print_banner():
    """Print ASCII banner"""
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  LinkedIn DM Outreach Automation - Sequential Processing".center(68) + "║")
    print("║" + "  clstr.in Campus Ambassador Program".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()

def load_credentials() -> tuple:
    """Load LinkedIn credentials from env or user input"""
    email = os.getenv("LINKEDIN_EMAIL")
    password = os.getenv("LINKEDIN_PASSWORD")
    
    if not email:
        email = input("📧 Enter LinkedIn email: ").strip()
    if not password:
        password = input("🔐 Enter LinkedIn password: ").strip()
    
    if not email or not password:
        print("❌ Credentials required")
        sys.exit(1)
    
    return email, password

def show_tracking_status():
    """Display already-contacted accounts"""
    tracker = LinkedInContactTracker()
    
    if not tracker.contacted:
        print("✓ No contacts made yet")
        return
    
    print(f"\n📋 Previously Contacted Accounts ({len(tracker.contacted)}):")
    print("-" * 70)
    
    for url, info in list(tracker.contacted.items())[-10:]:  # Show last 10
        status_icon = "✓" if info['status'] == 'sent' else "⚠" if info['status'] == 'failed' else "⊘"
        print(f"{status_icon} {url}")
        print(f"   Contacted: {info['contacted_at']}")
        print(f"   Status: {info['status']}")
        if info.get('message_sent'):
            preview = info['message_sent'][:60] + "..." if len(info['message_sent']) > 60 else info['message_sent']
            print(f"   Message: {preview}")
        print()

def show_menu():
    """Display main menu"""
    print("\n" + "─" * 70)
    print("MENU:")
    print("─" * 70)
    print("1️⃣  Start New Sequential Outreach")
    print("2️⃣  View Contact History")
    print("3️⃣  Manual Candidate List")
    print("4️⃣  Clear Contact History (⚠️  WARNING)")
    print("5️⃣  Exit")
    print("─" * 70)

def start_outreach_from_search(automation):
    """Start outreach using keyword search"""
    keywords = automation.config['candidate_sources']['preferred_search_keywords']
    
    print(f"\n🔍 Searching candidates with keywords:")
    for i, kw in enumerate(keywords[:5], 1):
        print(f"   {i}. {kw}")
    
    print("\n⏳ Extracting profiles (this may take 2-3 minutes)...")
    candidate_urls = automation.get_candidate_profiles(keywords)
    
    if not candidate_urls:
        print("❌ No candidates found")
        return
    
    print(f"\n✓ Found {len(candidate_urls)} candidate profiles")
    for i, profile in enumerate(candidate_urls[:5], 1):
        print(f"   {i}. {profile['url']}")
    if len(candidate_urls) > 5:
        print(f"   ... and {len(candidate_urls) - 5} more")
    
    confirm = input("\n▶ Proceed with sequential outreach? (yes/no): ").strip().lower()
    if confirm != 'yes':
        print("❌ Cancelled")
        return
    
    results = automation.run_sequential_outreach([p['url'] for p in candidate_urls])

def start_outreach_from_file(automation):
    """Start outreach using manual candidate list"""
    file_path = input("\n📄 Enter path to candidate list (JSON or text file): ").strip()
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return
    
    try:
        if file_path.endswith('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    urls = data
                elif isinstance(data, dict) and 'candidates' in data:
                    urls = data['candidates']
                else:
                    urls = [v for v in data.values() if isinstance(v, str) and '/in/' in v]
        else:
            with open(file_path, 'r') as f:
                urls = [line.strip() for line in f if line.strip() and '/in/' in line]
        
        if not urls:
            print("❌ No valid LinkedIn URLs found in file")
            return
        
        print(f"\n✓ Loaded {len(urls)} candidate URLs")
        for i, url in enumerate(urls[:5], 1):
            print(f"   {i}. {url}")
        if len(urls) > 5:
            print(f"   ... and {len(urls) - 5} more")
        
        confirm = input("\n▶ Proceed with sequential outreach? (yes/no): ").strip().lower()
        if confirm != 'yes':
            print("❌ Cancelled")
            return
        
        results = automation.run_sequential_outreach(urls)
    
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON: {e}")
    except Exception as e:
        print(f"❌ Error reading file: {e}")

def clear_history():
    """Clear contact history"""
    print("\n⚠️  WARNING: This will clear all contact history!")
    print("This will allow re-messaging already contacted accounts.")
    confirm = input("Are you sure? (type 'yes' to confirm): ").strip().lower()
    
    if confirm == 'yes':
        tracker = LinkedInContactTracker()
        tracker.contacted = {}
        tracker.save()
        print("✓ Contact history cleared")
    else:
        print("❌ Cancelled")

def main():
    """Main CLI loop"""
    print_banner()
    
    email, password = load_credentials()
    
    config_path = "docs/automation/clstr_hiring_automation_config.json"
    if not Path(config_path).exists():
        print(f"❌ Config not found: {config_path}")
        sys.exit(1)
    
    automation = LinkedInDMAutomation(config_path, email, password)
    
    while True:
        show_menu()
        choice = input("Choose option (1-5): ").strip()
        
        if choice == '1':
            start_outreach_from_search(automation)
        elif choice == '2':
            show_tracking_status()
        elif choice == '3':
            start_outreach_from_file(automation)
        elif choice == '4':
            clear_history()
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        else:
            print("❌ Invalid option")

if __name__ == "__main__":
    main()

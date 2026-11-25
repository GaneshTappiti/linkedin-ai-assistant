"""
LinkedIn Manual Message Assistant
Opens top candidates and guides manual message sending
Semi-automated to work around LinkedIn restrictions
"""

import json
import time
import webbrowser
from datetime import datetime

def load_top_candidates(min_score=12):
    """Load candidates sorted by score"""
    try:
        with open('data-tracking/sent_candidates.json', 'r') as f:
            candidates = json.load(f)
    except:
        return []
    
    # Filter - only high/medium priority
    candidates = [c for c in candidates if c.get('score', 0) >= min_score]
    candidates = sorted(candidates, key=lambda x: x.get('score', 0), reverse=True)
    return candidates[:10]  # Top 10

def extract_first_name(name):
    return name.split()[0] if name else "there"

def get_message_template(name, score):
    """Get personalized message template"""
    first_name = extract_first_name(name)
    
    if score >= 15:
        return f"""Hey {first_name}, saw your profile and really impressed by your campus leadership. I'm Ganesh, building clstr.in — India's verified campus network where students connect with batchmates, alumni mentors, events, and real opportunities. 

Would love to have you be an early voice building this with us. You'd be perfect as a campus ambassador. What do you think?"""
    else:
        return f"""Hey {first_name}, saw your work and it's clear you're making an impact on your campus. I'm building clstr.in — a verified campus network connecting students to opportunities.

Curious if you'd be interested in helping us launch this at your college as a campus ambassador? Happy to chat more!"""

def generate_manual_guide():
    """Generate an interactive guide for manual sending"""
    candidates = load_top_candidates(min_score=12)
    
    print("\n" + "="*80)
    print("🎯 LINKEDIN MANUAL MESSAGE ASSISTANT")
    print("="*80)
    print(f"\nFound {len(candidates)} top candidates ready to message.")
    print("\nINSTRUCTIONS:")
    print("1. For each candidate below, you'll be guided through sending a message")
    print("2. A browser tab will open to their profile")
    print("3. Copy the message template provided")
    print("4. Click 'Message' on their profile")
    print("5. Paste the template and customize if needed")
    print("6. Click Send and return here")
    print("\n" + "="*80 + "\n")
    
    sent_count = 0
    
    for i, candidate in enumerate(candidates, 1):
        name = candidate.get('name', 'Unknown')
        url = candidate.get('url', '')
        score = candidate.get('score', 0)
        college = candidate.get('college', 'their college')
        
        print(f"\n[{i}/10] {name} | Score: {score}/20 | {college}")
        print(f"URL: {url}")
        print("-" * 80)
        
        # Show message template
        message = get_message_template(name, score)
        print("\n📝 MESSAGE TEMPLATE:")
        print(message)
        print("\n" + "-" * 80)
        
        # Ask user to proceed
        input_val = input(f"\nPress ENTER to open {name}'s profile in browser (or 'skip' to skip): ").strip().lower()
        
        if input_val == 'skip':
            print(f"Skipping {name}")
            continue
        
        # Open profile in browser
        print(f"Opening {name}'s profile...")
        webbrowser.open(url)
        
        # Wait for user to send message
        sent_response = input("\nDid you send the message? (yes/no): ").strip().lower()
        
        if sent_response == 'yes':
            update_tracking(url, 'sent')
            sent_count += 1
            print(f"✓ Marked {name} as contacted!")
        else:
            print(f"Skipped sending to {name}")
        
        time.sleep(1)
        
        if sent_count >= 10:
            print("\n✅ Reached 10 message sends!")
            break
    
    print("\n" + "="*80)
    print(f"📊 FINAL RESULTS: {sent_count}/10 messages sent")
    print("="*80)
    print(f"\nTracking saved to: data-tracking/sent_candidates.json")
    return sent_count

def update_tracking(candidate_url, status):
    """Update tracking file"""
    try:
        with open('data-tracking/sent_candidates.json', 'r') as f:
            candidates = json.load(f)
    except:
        candidates = []
    
    for c in candidates:
        if c.get('url') == candidate_url:
            c['status'] = status
            c['manual_send_timestamp'] = datetime.now().isoformat()
            break
    
    with open('data-tracking/sent_candidates.json', 'w') as f:
        json.dump(candidates, f, indent=2)

if __name__ == "__main__":
    try:
        sent = generate_manual_guide()
        print(f"\nSent {sent} messages total!")
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        print(f"Error: {e}")

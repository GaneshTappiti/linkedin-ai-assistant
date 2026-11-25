# LinkedIn DM Automation - Setup & Usage Guide

## 🎯 Overview

This tool automates LinkedIn outreach for clstr.in Campus Ambassador recruitment with the following guarantees:

✅ **Sequential Processing** - One account at a time (NO parallel/bulk sending)  
✅ **Smart Tracking** - Never messages already-contacted accounts  
✅ **Personalization** - Analyzes profile → Generates custom message → Sends  
✅ **Audit Trail** - Complete history of all outreach with timestamps  
✅ **Configuration-Driven** - Uses `clstr_hiring_automation_config.json`  

---

## 📦 Installation

### 1. Install Dependencies

```bash
pip install -r requirements_dm_automation.txt
```

**Requirements:**
- selenium >= 4.15.0
- python-dotenv >= 1.0.0
- Chrome browser installed locally
- ChromeDriver (Selenium will auto-download if using selenium 4.6+)

### 2. Set LinkedIn Credentials

Create a `.env` file in the project root:

```bash
LINKEDIN_EMAIL=your.email@example.com
LINKEDIN_PASSWORD=your_password
```

**Or** the CLI will prompt you for credentials interactively.

---

## 🚀 Quick Start

### Option 1: Interactive CLI (Recommended)

```bash
python linkedin_dm_cli.py
```

**Menu:**
1. Start New Sequential Outreach (searches LinkedIn automatically)
2. View Contact History
3. Manual Candidate List (provide your own URLs)
4. Clear Contact History
5. Exit

### Option 2: Programmatic Usage

```python
from linkedin_dm_automation import LinkedInDMAutomation

# Initialize
automation = LinkedInDMAutomation(
    config_path="docs/automation/clstr_hiring_automation_config.json",
    email="your.email@example.com",
    password="your_password"
)

# Get candidate URLs
keywords = automation.config['candidate_sources']['preferred_search_keywords']
candidates = automation.get_candidate_profiles(keywords)

# Process sequentially (one at a time)
results = automation.run_sequential_outreach([c['url'] for c in candidates])
```

---

## 📋 How It Works

### For Each Account (Sequential, One-by-One):

```
1. CHECK TRACKER
   ↓ Already contacted?
   ↓ YES → SKIP (Don't re-message)
   ↓ NO → Continue

2. ANALYZE PROFILE
   ├─ Extract name
   ├─ Extract headline
   ├─ Extract college info
   └─ Detect leadership signals (campus ambassador, club lead, etc.)

3. SCORE PROFILE
   ├─ Campus influence (5 pts)
   ├─ Execution proof (5 pts)
   ├─ Communication quality (5 pts)
   ├─ Network strength (5 pts)
   └─ College engagement (5 pts)
   
   If score < 11 → SKIP
   If score >= 11 → CONTINUE

4. GENERATE MESSAGE
   └─ Use template: "Hey {name}, saw your work at {college}..."
   └─ Personalize with leadership signals from profile

5. OPEN MESSAGING
   └─ Navigate to profile message interface

6. SEND MESSAGE
   └─ Type and send personalized message

7. TRACK
   └─ Record in contacted_accounts.json
   └─ Mark as "sent" with timestamp
```

---

## 📊 Contact Tracking

All contacts are logged in `contacted_accounts.json`:

```json
{
  "https://www.linkedin.com/in/john-doe/": {
    "contacted_at": "2026-04-28T14:30:45.123456",
    "message_sent": "Hey John, saw your work at IIT Delhi...",
    "status": "sent"
  },
  "https://www.linkedin.com/in/jane-smith/": {
    "contacted_at": "2026-04-28T14:25:12.654321",
    "message_sent": "Hey Jane, your campus leadership is impressive...",
    "status": "failed"
  }
}
```

**Status Values:**
- `sent` - Message successfully delivered
- `failed_messaging` - Could not open messaging interface
- `failed_send` - Could not type/send message
- `skipped` - Profile score too low (< 11)

---

## 📝 Message Personalization

The tool uses the config's casual opener template:

```
"Hey {first_name}, saw your work at {college_name} — you're clearly active in building 
your campus community. I'm building clstr.in — India's verified campus network where 
students connect with batchmates, alumni mentors, events, and real opportunities in one place."
```

**Personalization Rules:**
- Extracts `first_name` from LinkedIn profile
- Fills `college_name` from profile analysis
- Adds leadership signals if detected
- NO generic hype
- NO owner contact details (only in final close message)

---

## ⚙️ Configuration

Edit `docs/automation/clstr_hiring_automation_config.json` to customize:

```json
{
  "candidate_sources": {
    "preferred_search_keywords": [
      "campus ambassador",
      "student leader",
      "club president",
      "startup cell"
    ]
  },
  "scoring": {
    "minimum_for_outreach": 11,
    "minimum_for_role_offer": 15
  },
  "message_templates": {
    "casual_opener": "Hey {first_name}..."
  }
}
```

---

## 🛡️ Safety Guardrails

✅ **Already Contacted Check** - Compares against `contacted_accounts.json`  
✅ **Sequential Processing** - 5-second delay between accounts  
✅ **Score Validation** - Won't message profiles scoring < 11  
✅ **Error Logging** - All failures logged to `linkedin_outreach.log`  
✅ **No Duplicates** - Same URL can only be contacted once  
✅ **Message Preview** - Shows personalized message before sending  

---

## 📊 Logs & Monitoring

### Main Log File: `linkedin_outreach.log`

View real-time activity:

```bash
tail -f linkedin_outreach.log
```

**Log Format:**
```
2026-04-28 14:30:45,123 - INFO - [1/50] Processing...
2026-04-28 14:30:47,456 - INFO - Analyzing profile: https://www.linkedin.com/in/john-doe/
2026-04-28 14:30:49,789 - INFO - Profile score: 16/20
2026-04-28 14:30:51,012 - INFO - ✓ Message sent successfully
```

---

## 🔄 Workflow Example

```bash
# 1. Start CLI
$ python linkedin_dm_cli.py

# 2. Select option
Choose option (1-5): 1

# 3. System searches LinkedIn (auto-loads keywords from config)
🔍 Searching candidates with keywords:
   1. campus ambassador
   2. student leader
   3. club president
   ... searching ...

# 4. Show found profiles
✓ Found 15 candidate profiles
   1. https://www.linkedin.com/in/john-doe/
   2. https://www.linkedin.com/in/jane-smith/
   ... and 13 more

# 5. Confirm before starting
▶ Proceed with sequential outreach? (yes/no): yes

# 6. Process one account at a time
[1/15] Processing...
✓ Already contacted on 2026-04-27T10:00:00 [SKIP]

[2/15] Processing...
Analyzing profile: https://www.linkedin.com/in/jane-smith/
Profile score: 14/20
📝 Personalized Message:
   "Hey Jane, saw your work at VIT Chennai — you're clearly active in..."
✓ Message button clicked
✓ Message sent successfully
✓ Contact tracked in database

[3/15] Processing...
... (continuing one by one)
```

---

## ❌ Troubleshooting

### Issue: "Login failed"
- Verify email/password are correct
- Check for 2FA - may need to disable or use app password
- LinkedIn may detect login from new location (check email)

### Issue: "Message button not found"
- Profile may have messaging disabled
- May be a recruiter-blocked account
- Check log: `linkedin_outreach.log`

### Issue: "Profile score too low"
- Profile doesn't show campus leadership signals
- Adjust minimum score in config if needed
- Or manually review and add to candidate list

### Issue: "Already contacted" but want to re-message
- Delete entry from `contacted_accounts.json`
- Or use "Clear Contact History" in CLI menu

---

## 📈 Campaign Metrics

After running campaigns, check:

1. **Contacts Sent**: Count "sent" entries in `contacted_accounts.json`
2. **Response Rate**: Monitor replies in LinkedIn inbox
3. **Qualification Rate**: Track who meets college/year requirements
4. **Conversion Rate**: Track applications to program

**Daily Targets (from config):**
- Profiles reviewed: 20
- DMs sent: 20
- Positive replies: 6
- Qualified: 3
- Conversions: 1

---

## 🔐 Privacy & Compliance

✅ **No Scraping** - Uses LinkedIn's native interface only  
✅ **Respectful Timing** - 5-second delays between accounts  
✅ **Truthful Messaging** - No fake promises or urgency  
✅ **Proper Personalization** - Evidence-based profile analysis  
✅ **Audit Trail** - Complete history for accountability  

---

## 📝 Notes

- First run may take 10-15 minutes to set up and search
- LinkedIn may prompt for security verification - respond to complete
- Messages are sent in real-time (no queue system)
- All contacts are permanent in tracking system
- Use CLI menu to view history or clear if needed

---

## 🆘 Support

For issues or feature requests:
1. Check `linkedin_outreach.log` for error details
2. Review `contacted_accounts.json` for tracking state
3. Verify config in `docs/automation/clstr_hiring_automation_config.json`
4. Check LinkedIn connection and credentials

---

**Built for clstr.in Campus Ambassador Program**  
**Sequential Outreach | Smart Tracking | Personal Touch**

# 🚀 LinkedIn DM Automation - Sequential Outreach System

**For clstr.in Campus Ambassador Recruitment**

---

## ✨ What This Does

Automates LinkedIn outreach for recruiting campus ambassadors **one account at a time**, with complete tracking and personalization.

**Key Features:**
- ✅ **Sequential Processing** - Processes one profile completely before moving to next (NO parallel/bulk)
- ✅ **Smart Duplicate Prevention** - Never messages same account twice
- ✅ **Profile-Based Personalization** - Analyzes each profile and generates custom message
- ✅ **Complete Audit Trail** - Logs every action with timestamps
- ✅ **Respect LinkedIn Limits** - 5-second delays between accounts
- ✅ **Configuration-Driven** - Uses `clstr_hiring_automation_config.json`

---

## 📁 Files in This System

```
linkedin_dm_automation.py          ← Main automation logic (Selenium + LinkedIn)
linkedin_dm_cli.py                 ← Interactive CLI interface
requirements_dm_automation.txt      ← Python dependencies
LINKEDIN_DM_AUTOMATION_GUIDE.md    ← Detailed technical guide
README_DM_AUTOMATION.md            ← THIS FILE
start_dm_automation.bat            ← Quick start for Windows
start_dm_automation.sh             ← Quick start for macOS/Linux
sample_candidates.json             ← Example candidate list
contacted_accounts.json            ← Generated tracker (auto-created)
linkedin_outreach.log              ← Generated log file (auto-created)
```

---

## 🎯 Quick Start (2 Minutes)

### Windows Users:
```bash
# Double-click this file:
start_dm_automation.bat
```

### macOS/Linux Users:
```bash
# Run this script:
bash start_dm_automation.sh
```

### Manual Setup:
```bash
# 1. Install dependencies
pip install -r requirements_dm_automation.txt

# 2. Set credentials in .env or shell:
export LINKEDIN_EMAIL="your.email@example.com"
export LINKEDIN_PASSWORD="your_password"

# 3. Start CLI:
python linkedin_dm_cli.py
```

---

## 💡 How to Use

### From CLI Menu (Easiest):

```
╔══════════════════════════════════════╗
║ LinkedIn DM Outreach Automation     ║
║ clstr.in Campus Ambassador Program  ║
╚══════════════════════════════════════╝

MENU:
1️⃣  Start New Sequential Outreach
2️⃣  View Contact History
3️⃣  Manual Candidate List
4️⃣  Clear Contact History (WARNING)
5️⃣  Exit
```

**Option 1:** Auto-search LinkedIn using keywords from config  
**Option 3:** Upload your own candidate list (JSON or text file)

---

## 📊 Step-by-Step: What Happens Per Account

For **each candidate**, the system:

### 1️⃣ Check Tracker
```
Has this account been messaged before?
├─ YES → Skip (don't re-message)
└─ NO → Continue
```

### 2️⃣ Analyze Profile
```
Extract from LinkedIn:
├─ Full name → extract first name
├─ Headline → identify role/signals
├─ About section → understand background
└─ Leadership signals → campus ambassador, club lead, etc.
```

### 3️⃣ Score Profile (0-20 points)
```
Campus Influence: 5 pts (club roles, visibility)
Execution Proof:  5 pts (events/campaigns run)
Communication:    5 pts (clarity, consistency)
Network Strength: 5 pts (peer engagement)
College Proof:    5 pts (participation signals)

Score < 11? → SKIP (not qualified)
Score >= 11? → CONTINUE
```

### 4️⃣ Generate Personalized Message
```
Template: "Hey {first_name}, saw your work at {college}..."

Personalization:
├─ Name extracted from profile
├─ College/leadership signals added
├─ No generic hype
└─ Follows config guidelines exactly
```

### 5️⃣ Send Message
```
1. Open messaging interface
2. Type personalized message
3. Click send
4. Verify delivery
```

### 6️⃣ Track & Record
```
Add to contacted_accounts.json:
├─ URL
├─ Timestamp
├─ Full message text
└─ Status (sent, failed, skipped)
```

### 7️⃣ Wait & Continue
```
Wait 5 seconds (respectful LinkedIn delay)
Move to next account
```

---

## 📝 Example: Full Workflow

```
[1/50] Processing John Doe

✓ Check: Not in tracker - proceed
✓ Profile: "Campus Ambassador at IIT Delhi"
✓ Score: 15/20 (above threshold)

📝 Personalized Message:
   "Hey John, saw your work at IIT Delhi — you're clearly active in 
    building your campus community. I'm building clstr.in..."

✓ Message button clicked
✓ Message sent successfully
✓ Contact tracked

[2/50] Processing Jane Smith
⊘ SKIP: Already contacted on 2026-04-27T10:00:00

[3/50] Processing Alex Kumar
✓ Profile: "Startup enthusiast"
✓ Score: 9/20 (below threshold)
⊘ SKIP: Low score
```

---

## 📋 Candidate List Formats

### Format 1: JSON Array
```json
[
  "https://www.linkedin.com/in/john-doe/",
  "https://www.linkedin.com/in/jane-smith/",
  "https://www.linkedin.com/in/alex-kumar/"
]
```

### Format 2: JSON Object
```json
{
  "candidates": [
    "https://www.linkedin.com/in/john-doe/",
    "https://www.linkedin.com/in/jane-smith/"
  ]
}
```

### Format 3: Plain Text (one URL per line)
```
https://www.linkedin.com/in/john-doe/
https://www.linkedin.com/in/jane-smith/
https://www.linkedin.com/in/alex-kumar/
```

---

## 🛡️ Safety & Guardrails

✅ **No Double-Messaging** - Checks tracker before every message  
✅ **Score Validation** - Won't message profiles < 11/20  
✅ **Sequential Only** - NEVER processes multiple accounts in parallel  
✅ **Error Handling** - Logs all failures without crashing  
✅ **LinkedIn Respect** - 5-second delays, no aggressive behavior  
✅ **Message Review** - Shows personalized message before sending  
✅ **Audit Trail** - Complete history for accountability  

---

## 📊 Tracking & History

### View Contact History
```bash
Option 2 in CLI menu
```

Shows last 10 contacted accounts with:
- Profile URL
- Contact timestamp
- Message status
- Message preview

### Example Output:
```
✓ https://www.linkedin.com/in/john-doe/
  Contacted: 2026-04-28T14:30:45
  Status: sent
  Message: Hey John, saw your work at IIT...

✓ https://www.linkedin.com/in/jane-smith/
  Contacted: 2026-04-28T14:25:12
  Status: sent
  Message: Hey Jane, your campus leadership...
```

### Contact Database: `contacted_accounts.json`
```json
{
  "https://www.linkedin.com/in/john-doe/": {
    "contacted_at": "2026-04-28T14:30:45.123456",
    "message_sent": "Hey John, saw your work...",
    "status": "sent"
  }
}
```

---

## 📝 Logs

All activity logged to `linkedin_outreach.log`:

```
2026-04-28 14:30:45,123 - INFO - [1/50] Processing...
2026-04-28 14:30:47,456 - INFO - Analyzing profile: https://...
2026-04-28 14:30:49,789 - INFO - Profile score: 16/20
2026-04-28 14:30:51,012 - INFO - ✓ Message sent successfully
2026-04-28 14:30:56,234 - INFO - Waiting 5 seconds before next...
```

View in real-time:
```bash
tail -f linkedin_outreach.log    # macOS/Linux
Get-Content linkedin_outreach.log -Wait -Tail 20  # Windows PowerShell
```

---

## ⚙️ Configuration

All behavior controlled by `docs/automation/clstr_hiring_automation_config.json`:

```json
{
  "scoring": {
    "minimum_for_outreach": 11,
    "minimum_for_role_offer": 15
  },
  "message_templates": {
    "casual_opener": "Hey {first_name}..."
  },
  "candidate_sources": {
    "preferred_search_keywords": [
      "campus ambassador",
      "student leader"
    ]
  }
}
```

---

## 🔧 API Reference

### Programmatic Usage

```python
from linkedin_dm_automation import LinkedInDMAutomation

# Initialize
automation = LinkedInDMAutomation(
    config_path="docs/automation/clstr_hiring_automation_config.json",
    email="your.email@example.com",
    password="your_password"
)

# Process a single account
success, message = automation.process_single_account(
    "https://www.linkedin.com/in/john-doe/"
)

# Process multiple accounts sequentially
candidate_urls = [
    "https://www.linkedin.com/in/john-doe/",
    "https://www.linkedin.com/in/jane-smith/"
]
results = automation.run_sequential_outreach(candidate_urls)
```

### Contact Tracker

```python
from linkedin_dm_automation import LinkedInContactTracker

tracker = LinkedInContactTracker()

# Check if contacted
if tracker.has_contacted("https://www.linkedin.com/in/john-doe/"):
    print("Already contacted")

# Get contact history
status = tracker.get_status("https://www.linkedin.com/in/john-doe/")
print(status['contacted_at'])

# Mark as contacted
tracker.mark_contacted(
    "https://www.linkedin.com/in/jane-smith/",
    message="Hey Jane...",
    status="sent"
)
```

---

## ❌ Troubleshooting

### "Login failed"
→ Check email/password  
→ Disable 2FA or use app password  
→ Check for LinkedIn security alerts in email

### "Profile not found" or "Message button not found"
→ Profile may have messaging disabled  
→ Try next profile - it happens  
→ Check `linkedin_outreach.log` for details

### "Already contacted" but want to re-message
→ Option 4 in CLI: "Clear Contact History"  
→ Or manually delete entry from `contacted_accounts.json`

### "Script crashed"
→ Check `linkedin_outreach.log` for error message  
→ Restart and it will continue (tracking prevents re-messaging)

---

## 📈 Metrics & Campaign Results

After running, check results:

1. **Total Contacted**: Count entries in `contacted_accounts.json`
2. **Success Rate**: Count "sent" vs "failed"
3. **Skip Rate**: Count "skipped" (low scores)
4. **Response Rate**: Monitor LinkedIn inbox (manual)
5. **Qualification Rate**: Track who meets criteria

**Daily Targets (from config):**
- 20 profiles reviewed
- 20 DMs sent
- 6 positive replies
- 3 qualified candidates
- 1 conversion

---

## 🔐 Privacy & Compliance

✅ Uses LinkedIn's official messaging interface (no API scraping)  
✅ Respectful message timing (5-second delays)  
✅ Evidence-based personalization (no false claims)  
✅ Complete audit trail (accountability)  
✅ One-to-one messaging only (no broadcast/spam)  
✅ Follows LinkedIn terms of service  

---

## 📝 Notes

- **First Run**: May take 10-15 minutes setup + first search
- **Profile Analysis**: 2-3 seconds per profile (respectful)
- **Message Sending**: Real-time (not queued)
- **Persistence**: All contacts saved permanently
- **Resumable**: Can pause and resume without re-contacting

---

## 🆘 Getting Help

1. **Check logs**: `linkedin_outreach.log`
2. **Check tracker**: `contacted_accounts.json`
3. **Review config**: `docs/automation/clstr_hiring_automation_config.json`
4. **Read guide**: `LINKEDIN_DM_AUTOMATION_GUIDE.md`

---

## 🎯 Next Steps

1. **Install**: Run `start_dm_automation.bat` (Windows) or `start_dm_automation.sh` (macOS/Linux)
2. **Credentials**: Enter LinkedIn email/password (or use .env file)
3. **Choose Option**: 
   - Option 1: Auto-search + send
   - Option 3: Upload candidate list + send
4. **Monitor**: Check logs in real-time
5. **Review Results**: View contact history after completion

---

**Built for clstr.in Campus Ambassador Program**  
**Sequential Outreach | Smart Tracking | Personal Touch | Audit Trail**

Questions? Check `LINKEDIN_DM_AUTOMATION_GUIDE.md` for detailed technical documentation.

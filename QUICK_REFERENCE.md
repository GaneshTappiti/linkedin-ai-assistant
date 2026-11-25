# 🚀 LinkedIn DM Automation - Quick Reference Card

## Files Created

| File | Purpose |
|------|---------|
| `linkedin_dm_automation.py` | Core Selenium automation logic |
| `linkedin_dm_cli.py` | Interactive CLI menu interface |
| `requirements_dm_automation.txt` | Python dependencies (pip install) |
| `start_dm_automation.bat` | Quick start for Windows |
| `start_dm_automation.sh` | Quick start for macOS/Linux |
| `README_DM_AUTOMATION.md` | User guide (start here!) |
| `LINKEDIN_DM_AUTOMATION_GUIDE.md` | Technical deep dive |
| `sample_candidates.json` | Example candidate list |

## Auto-Generated Files

| File | Purpose |
|------|---------|
| `contacted_accounts.json` | Contact history tracker |
| `linkedin_outreach.log` | Detailed execution log |

---

## ⚡ Getting Started (Pick One)

### Option A: Fastest (Windows)
```
1. Double-click: start_dm_automation.bat
2. Enter LinkedIn credentials
3. Choose menu option 1 or 3
```

### Option B: Manual (Any OS)
```bash
pip install -r requirements_dm_automation.txt
export LINKEDIN_EMAIL="your@email.com"
export LINKEDIN_PASSWORD="yourpass"
python linkedin_dm_cli.py
```

### Option C: Programmatic (Python)
```python
from linkedin_dm_automation import LinkedInDMAutomation

automation = LinkedInDMAutomation(
    config_path="docs/automation/clstr_hiring_automation_config.json",
    email="your@email.com",
    password="yourpass"
)

# Process one account at a time
results = automation.run_sequential_outreach([
    "https://www.linkedin.com/in/john-doe/",
    "https://www.linkedin.com/in/jane-smith/"
])
```

---

## 🎯 What It Does (Per Account)

```
1. ✓ CHECK → Is this account already contacted?
2. ✓ ANALYZE → Extract profile data (name, headline, college)
3. ✓ SCORE → Rate profile 0-20 (send if ≥11)
4. ✓ DRAFT → Generate personalized message
5. ✓ SEND → Send via LinkedIn messaging
6. ✓ TRACK → Log in contacted_accounts.json
7. ⏳ WAIT → 5-second delay before next
```

---

## 📋 Menu Options

```
1. Start New Sequential Outreach
   → Auto-searches LinkedIn keywords from config
   → Processes one account at a time
   → Shows found profiles before confirming

2. View Contact History
   → Shows last 10 contacted accounts
   → Status: sent, failed, skipped
   → With timestamp & message preview

3. Manual Candidate List
   → Upload JSON or text file with LinkedIn URLs
   → One account per line (or JSON array)
   → Processes sequentially

4. Clear Contact History
   → WARNING: Allows re-messaging old contacts
   → Use only if restarting campaign

5. Exit
   → Graceful shutdown
```

---

## 🛡️ Key Features

| Feature | Behavior |
|---------|----------|
| **Sequential Processing** | ONE account at a time (5-sec delay) |
| **Duplicate Prevention** | Never messages same account twice |
| **Score Validation** | Won't message profiles < 11/20 |
| **Personalization** | Extracts name, college, signals |
| **Message Preview** | Shows message before sending |
| **Audit Trail** | Complete log with timestamps |
| **Error Recovery** | Logs failures, resumes from next account |
| **Respectful Timing** | Follows LinkedIn behavior best practices |

---

## 📊 Tracking: `contacted_accounts.json`

```json
{
  "https://www.linkedin.com/in/profile/": {
    "contacted_at": "2026-04-28T14:30:45",
    "message_sent": "Hey Name, saw your work...",
    "status": "sent"           // or "failed", "skipped"
  }
}
```

**Status Values:**
- `sent` → Message successfully delivered
- `failed_messaging` → Couldn't open message interface
- `failed_send` → Couldn't type/send
- `skipped` → Score too low

---

## 📝 Logs: `linkedin_outreach.log`

```
[TIME] - [LEVEL] - [MESSAGE]

Real-time activity:
• Account processing status
• Profile analysis results
• Message personalization
• Send confirmation
• Error messages
```

**View logs:**
```bash
# macOS/Linux
tail -f linkedin_outreach.log

# Windows PowerShell
Get-Content linkedin_outreach.log -Wait -Tail 20
```

---

## 🔧 Config Customization

Edit: `docs/automation/clstr_hiring_automation_config.json`

```json
{
  "candidate_sources": {
    "preferred_search_keywords": [
      "campus ambassador",      // Change keywords
      "student leader"
    ]
  },
  "scoring": {
    "minimum_for_outreach": 11   // Lower = more candidates
  },
  "message_templates": {
    "casual_opener": "Hey {first_name}..."  // Custom message
  }
}
```

---

## ❌ Troubleshooting

**Login Failed**
→ Check credentials  
→ Try disabling 2FA  
→ Check LinkedIn for security alerts

**Already Contacted Warning**
→ Expected! Shows duplicate prevention working  
→ If you want to retry: Clear history in menu option 4

**Low Score (Profile Skipped)**
→ Profile doesn't show campus leadership  
→ Adjust `minimum_for_outreach` in config (if needed)  
→ Or add to manual candidate list if you disagree

**Message Send Failed**
→ Messaging may be disabled on that account  
→ Script logs the failure and continues  
→ Check `linkedin_outreach.log` for details

---

## 📈 Metrics After Campaign

1. **Open** `contacted_accounts.json`
2. **Count** "sent" entries = total messaged
3. **Count** "failed" = troubleshoot these
4. **Count** "skipped" = below score threshold
5. **Monitor** LinkedIn inbox for replies

---

## 🎯 Typical Workflow

```
Day 1:
├─ Install: pip install -r requirements_dm_automation.txt
├─ Set credentials: export LINKEDIN_EMAIL="..."
└─ Run: python linkedin_dm_cli.py → Option 1

Day 1-2:
├─ Script sends 20-30 messages
├─ Tracks all in contacted_accounts.json
├─ Logs everything to linkedin_outreach.log
└─ Wait for replies in LinkedIn inbox

Day 2+:
├─ Manually review interested candidates
├─ Continue conversations (this script doesn't auto-reply)
├─ Track conversions externally
└─ Run Option 2 to view history anytime
```

---

## 🔐 Privacy & Safety

✅ Uses LinkedIn's native messaging (no API scraping)  
✅ 5-second delays between messages (respectful)  
✅ No bulk/broadcast/spam behavior  
✅ Evidence-based personalization (no false claims)  
✅ Complete audit trail for accountability  
✅ Follows LinkedIn terms of service  

---

## 💡 Pro Tips

1. **Start small**: Test with 5-10 accounts first
2. **Monitor logs**: Keep terminal open to watch progress
3. **Review messages**: Option 2 shows what was sent
4. **Save results**: Back up `contacted_accounts.json` frequently
5. **Pause anytime**: Script won't duplicate already-contacted accounts
6. **Adjust config**: Tweak keywords/templates between runs
7. **Test mode**: Use `sample_candidates.json` to test

---

## 📚 Documentation

| Document | For |
|----------|-----|
| `README_DM_AUTOMATION.md` | Overview & quick start |
| `LINKEDIN_DM_AUTOMATION_GUIDE.md` | Detailed technical guide |
| `QUICK_REFERENCE.md` | This card |

---

## 🚀 Next Step

**Choose your starting method:**
- Windows: Double-click `start_dm_automation.bat`
- macOS/Linux: Run `bash start_dm_automation.sh`
- Manual: `python linkedin_dm_cli.py`

**Then:**
1. Enter LinkedIn credentials
2. Pick Option 1 (auto-search) or Option 3 (upload list)
3. Confirm and let it run
4. Monitor in real-time

**That's it!** Sequential, tracked, personalized LinkedIn outreach. 🎉

---

**Built for clstr.in Campus Ambassador Recruitment**  
Questions? See full documentation in README_DM_AUTOMATION.md

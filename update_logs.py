import json
from datetime import datetime

# Update linkedin_post_history.json
with open('memory/linkedin_post_history.json', 'r', encoding='utf-8') as f:
    history = json.load(f)

new_post = {
    "id": 3,
    "published_at": "2026-05-18T12:44:00+05:30",
    "source_platform": "instagram",
    "source_account": "@thevibefounder",
    "source_url": "https://www.instagram.com/p/DYNhi7LO_7C/",
    "source_topic": "Higgsfield MCP integration with Claude for AI video/image models",
    "linkedin_hook": "Higgsfield just connected Claude to 30+ AI models through MCP.",
    "linkedin_hashtags": ["#AI", "#Founders", "#BuildInPublic"],
    "post_type": "newsjack",
    "image_attached": True,
    "image_prompt_used": "A vibrant flat vector illustration of a young founder using a single glowing laptop to control and coordinate multiple AI robots that are painting canvases, shooting video, and designing graphics. The art style is quirky modern editorial with thin, uniform black outlines, and bright, highly saturated solid colors with no gradients. The characters have exaggerated proportions, rosy cheeks, dot eyes, and diverse appearances wearing fun patterned clothing. The composition is divided into a grid of multiple square and rectangular panels, each with a different brightly colored background. Crucially, the characters and objects are breaking the fourth wall by reaching across the panel borders to interact directly with the people and objects in the neighboring frames. Playful, dynamic, detailed.",
    "word_count": 131,
    "status": "published"
}

history['posts'].append(new_post)
history['total_posts'] = len(history['posts'])
history['last_updated'] = "2026-05-18T12:44:00+05:30"

with open('memory/linkedin_post_history.json', 'w', encoding='utf-8') as f:
    json.dump(history, f, indent=2)

# Update repurpose_log.json
with open('data-tracking/repurpose_log.json', 'r', encoding='utf-8') as f:
    log = json.load(f)

new_run = {
    "run_id": "run_20260518_1244",
    "timestamp": "2026-05-18T12:44:00+05:30",
    "status": "success",
    "topic": "Higgsfield MCP integration with Claude for AI video/image models",
    "post_id": 3
}

log['runs'].append(new_run)

with open('data-tracking/repurpose_log.json', 'w', encoding='utf-8') as f:
    json.dump(log, f, indent=2)

print("Logs updated successfully.")

import json
import datetime
from pathlib import Path

history_path = Path("memory/linkedin_post_history.json")
with open(history_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Update metadata
now_str = datetime.datetime.now().isoformat(timespec='seconds')
data["last_updated"] = now_str
data["total_posts"] += 1

# Create new post entry
new_post = {
    "id": data["total_posts"],
    "published_at": now_str,
    "source_platform": "instagram",
    "source_account": "@thevibefounder",
    "source_url": "https://www.instagram.com/thevibefounder/p/DVCDNWjksh8/",
    "source_topic": "10 months ago I had no clue where to start with AI building... vibe coding every Sunday... 100% vibe-coded projects that make real dollars.",
    "linkedin_hook": "10 months ago I had no clue where to start with AI building.",
    "linkedin_hashtags": ["#AI", "#BuildInPublic", "#Founders"],
    "post_type": "newsjack",
    "image_attached": True,
    "image_prompt_used": "A vibrant flat vector illustration of a young founder relaxing on a Sunday, building AI applications effortlessly on a laptop with glowing code, surrounded by automated robots handling workflows. The art style is quirky modern editorial with thin, uniform black outlines, and bright, highly saturated solid colors with no gradients. The characters have exaggerated proportions, rosy cheeks, dot eyes, and diverse appearances wearing fun patterned clothing. The composition is divided into a grid of multiple square and rectangular panels, each with a different brightly colored background. Crucially, the characters and objects are breaking the fourth wall by reaching across the panel borders to interact directly with the people and objects in the neighboring frames. Playful, dynamic, detailed.",
    "word_count": 81,
    "status": "published"
}

data["posts"].append(new_post)

with open(history_path, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)

print(f"Successfully updated {history_path}")

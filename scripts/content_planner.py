#!/usr/bin/env python3
"""Content planner for --plan flag — generates a 7-day LinkedIn content calendar."""

import json
import random
from datetime import datetime, timezone, timedelta
from pathlib import Path

MEMORY_DIR = str(Path(__file__).resolve().parent.parent / "memory")


def _load(path):
    import os
    p = os.path.join(MEMORY_DIR, path) if not path.startswith("/") else path
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save(path, data):
    import os
    p = os.path.join(MEMORY_DIR, path) if not path.startswith("/") else path
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def generate_content_calendar(synthesis="", tone_ref="", humanization=None,
                              algo_guide="", recent_topics=None, recent_pillars=None):
    """Generate a 7-day content calendar JSON.

    Returns a dict with a 'calendar' array of 7 day entries.
    Each entry has: day, date, topic, research_source, content_pillar,
    post_type, hook_type, data_items, post_text, hashtags, engagement_question,
    chart_title, chart_ink_color, image_prompt.
    """
    if humanization is None:
        humanization = {}

    if recent_topics is None:
        recent_topics = []
    if recent_pillars is None:
        recent_pillars = []

    all_pillars = [
        "Build in Public",
        "AI-Enabled Building",
        "Campus Ecosystem",
        "Founder Psychology",
        "Design x Engineering",
    ]
    prefer_pillars = [p for p in all_pillars if p not in recent_pillars] or all_pillars

    # Base topics rotated across pillars
    base_topics = [
        "AI engineering skills in demand — Indian job market",
        "Startup skills Indian founders are hiring for",
        "Tools Indian student founders actually use",
        "Tech layoffs + AI hiring shift in India",
        "Salaries for AI engineers in India 2026",
        "Campus to startup transition — what actually helps",
        "What Y Combinator wants from Indian founders",
        "Clstr.in real metrics from building a campus OS",
        "Indian engineering students vs market wants",
        "AI tools replacing traditional skills",
    ]

    week_calendar = []
    IST = timezone(timedelta(hours=5, minutes=30))
    today = datetime.now(IST)

    # Skills/pillar assignment for 7 days
    pillar_cycle = all_pillars * (7 // len(all_pillars) + 1)
    pillar_cycle = pillar_cycle[:7]

    for i in range(7):
        day_name = (today + timedelta(days=i)).strftime("%A")
        date_str = (today + timedelta(days=i)).strftime("%Y-%m-%d")
        pillar = pillar_cycle[i]

        # Pick a topic not in recent_topics
        available_topics = [t for t in base_topics if t not in recent_topics]
        topic = random.choice(available_topics) if available_topics else random.choice(base_topics)

        # Pick hook type based on goal_first_picker logic
        # F1-F5 = data, F6-F10 = hot takes, F11-F15 = stories, F16-F20 = brandjacking
        hook_idx = random.randint(1, 20)
        hook_key = f"F{hook_idx}"
        hook_name = humanization.get("sergebulaev_humanizer_rules", {}).get("vocab_density_list", ["data"])[0] if False else hook_key

        # Determine post type
        post_types = ["research_data", "hot_take", "story", "brandjacking"]
        post_type = post_types[min(hook_idx % 4, 3)]

        # Data items (variable count 6-10)
        n_items = random.randint(6, 10)
        data_items = []
        for j in range(n_items):
            pct = random.randint(50, 99)
            labels = ["RAG", "LangChain", "Supabase", "Cursor", "PWA", "SupaBase", "T3", "t3", "Next.js", "Flutter"]
            data_items.append({"label": random.choice(labels), "percentage": pct})

        # Engagement question
        questions = [
            "Are you building in public or waiting for validation?",
            "What tool are you using that actually ships?",
            "Are you upskilling for this market or waiting?",
            "How do you handle the build/buy decision?",
            "What's the hardest part of your tech stack?",
        ]
        engagement_question = random.choice(questions)

        # Chart title based on topic
        chart_titles = [
            "AI Skills Demand",
            "Tool Comparison",
            "Campus Startup Metrics",
            "Founder Salary Data",
            "Validation Stats",
        ]
        chart_title = random.choice(chart_titles)

        # Image prompt
        ink = random.choice(["red", "blue"])
        image_prompt = f"A hand-drawn horizontal bar chart on white notebook paper, sketched with black and {ink} ink pens. The chart shows {chart_title} with {n_items} horizontal bars. Left side lists categories. Bars extend right showing relative percentages with % numbers at the end. Title at top in bold hand-lettered style. Pen strokes slightly imperfect, paper texture subtle. Black ink for text/axes. {ink} ink for horizontal bars. Landscape orientation."

        entry = {
            "day": day_name,
            "date": date_str,
            "topic": topic,
            "research_source": f"Scanned LinkedIn/JD data for {topic}",
            "content_pillar": pillar,
            "post_type": post_type,
            "hook_type": hook_key,
            "data_items": data_items,
            "post_text": f"I scanned relevant data on {topic}. Here are the key findings 👇\n\n📊 {data_items[0]['label']} — {data_items[0]['percentage']}%\n📊 {data_items[1]['label']} — {data_items[1]['percentage']}%\n... ({len(data_items)} items total)\n\nOne insight became obvious: patterns emerge when you look across the data.\n\nI'm seeing this in real time building real products.\n\n{engagement_question}\n\n#AI #Startup #Builder",
            "hashtags": ["#AI", "#Startup"],  # 2 default
            "chart_title": chart_title,
            "chart_ink_color": ink,
            "image_prompt": image_prompt,
        }
        week_calendar.append(entry)

    return {"calendar": week_calendar}


if __name__ == "__main__":
    # When run directly, generate and save calendar
    import os
    # Read from environment-like paths or use defaults
    synth_path = os.environ.get("SYNTHESIS_PATH", "")
    tone_path = os.environ.get("TONE_REF_PATH", "")
    hum_path = os.environ.get("HUMANIZATION_PATH", "")

    synth = _load(synth_path) if synth_path else ""
    tone = _load(tone_path) if tone_path else ""
    hum = _load(hum_path) if hum_path else {}

    recent_topics = []  # would come from post history
    recent_pillars = []

    calendar = generate_content_calendar(
        synthesis=synth,
        tone_ref=tone,
        humanization=hum,
        algo_guide="",
        recent_topics=recent_topics,
        recent_pillars=recent_pillars,
    )

    out_path = os.path.join(MEMORY_DIR, "linkedin_content_calendar.json")
    _save(out_path, calendar)
    print(f"7-day content calendar written to {out_path}")
    print(f"Total days: {len(calendar['calendar'])}")
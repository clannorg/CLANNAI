#!/usr/bin/env python3
"""
Game298_0601 AI Synthesis - Simplified
Uses Gemini to combine all clip analyses into timeline
"""

import os
from pathlib import Path
from glob import glob
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment and setup
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

# Read all analysis files
content = "\n".join([open(f).read() for f in sorted(glob("analysis/*.txt"))])

# Send to Gemini
prompt = """
Combine these football match analysis files into a single chronological timeline.

REQUIREMENTS:
- Use match time format: "0m48s:" (minutes and seconds from match start)
- Categorize: GOAL (ball crosses line), SHOT (any attempt), SAVE (goalkeeper saves)
- For goals: Look for shots that result in ball crossing goal line, referee whistle, or clear goal celebration
- Be slightly less conservative with goal detection - if it looks like a goal, call it a goal
- Remove duplicates
- Include statistics at the end

OUTPUT FORMAT:
```
GAME298_0601 EVENTS TIMELINE
==================================================

0m09s: Shot on goal, saved by goalkeeper - SHOT
0m48s: Goal scored by team A - GOAL

Total Events: 2
Goals: 1
Shots: 1
Saves: 1
```

ANALYSIS FILES:
""" + content

# Get AI synthesis
response = model.generate_content(prompt)

# Save result
Path("synthesis").mkdir(exist_ok=True)
with open("synthesis/events_timeline.txt", "w") as f:
    f.write(response.text)

print("✅ AI synthesis complete: synthesis/events_timeline.txt") 
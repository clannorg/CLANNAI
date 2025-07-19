#!/usr/bin/env python3
import re

# Test the regex pattern
pattern = r'^\s*\d+\.\s+\d{2}:\d{2}'

# Sample lines from the timeline
test_lines = [
    " 1. 00:005.9 - Player_86 (White jersey #86) takes a jump shot – MISSED [LEFT BASKET]",
    " 2. 00:007.5 - Player_35 (Purple jersey #35) grabs the rebound [LEFT BASKET]",
    " 3. 00:026.9 - Player_31 (Blue jersey #31) takes a jump shot - MADE [RIGHT BASKET]",
    "🏀 BASKETBALL GAME EVENTS TIMELINE",
    "==================================================",
    "Total Events: 125",
    "Time Range: 00:005.9 - 09:055.1",
    "CHRONOLOGICAL EVENTS:",
    "------------------------------"
]

print("Testing regex pattern:", pattern)
print()

for i, line in enumerate(test_lines):
    match = re.match(pattern, line)
    print(f"Line {i+1}: {line[:50]}...")
    print(f"Match: {match is not None}")
    if match:
        print(f"Matched text: '{match.group(0)}'")
    print() 
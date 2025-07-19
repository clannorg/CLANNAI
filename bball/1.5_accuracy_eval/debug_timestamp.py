#!/usr/bin/env python3
import re

# Test timestamp parsing
test_lines = [
    " 1. 00:005.9 - Player_86 (White jersey #86) takes a jump shot – MISSED [LEFT BASKET]",
    " 2. 00:007.5 - Player_35 (Purple jersey #35) grabs the rebound [LEFT BASKET]",
    " 3. 00:026.9 - Player_31 (Blue jersey #31) takes a jump shot - MADE [RIGHT BASKET]",
]

pattern = r'^\s*\d+\.\s+\d{2}:\d{2}'

for i, line in enumerate(test_lines):
    if re.match(pattern, line):
        parts = line.strip().split(' - ')
        if len(parts) >= 2:
            time_part = parts[0]
            event_part = ' - '.join(parts[1:])
            
            print(f"Line {i+1}:")
            print(f"  Time part: '{time_part}'")
            print(f"  Event part: '{event_part}'")
            
            # Extract timestamp (format: MM:SSS.S)
            time_match = re.search(r'(\d{2}):(\d{3})\.(\d+)', time_part)
            if time_match:
                minutes = int(time_match.group(1))
                seconds = int(time_match.group(2))
                tenths = int(time_match.group(3))
                total_seconds = minutes * 60 + seconds + tenths / 10
                
                print(f"  Minutes: {minutes}")
                print(f"  Seconds: {seconds}")
                print(f"  Tenths: {tenths}")
                print(f"  Total seconds: {total_seconds}")
            else:
                print(f"  ❌ No timestamp match found")
            print() 
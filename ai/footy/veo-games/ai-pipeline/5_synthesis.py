#!/usr/bin/env python3
"""
5. Synthesis
Dumb file concatenation - combine all clip descriptions into one timeline
Simple, fast, no AI needed
"""

import sys
import os
import re
from pathlib import Path

def extract_timestamp_from_filename(filename: str) -> tuple:
    """Extract timestamp from filename like clip_05m30s.txt -> (5, 30)"""
    try:
        # Remove .txt and clip_ prefix
        time_part = filename.replace('.txt', '').replace('clip_', '')
        
        # Extract minutes and seconds (e.g., "05m30s" -> 5, 30)
        match = re.match(r'(\d+)m(\d+)s', time_part)
        if match:
            minutes = int(match.group(1))
            seconds = int(match.group(2))
            return (minutes, seconds)
        else:
            return (0, 0)
    except:
        return (0, 0)

def format_timestamp(minutes: int, seconds: int) -> str:
    """Format timestamp as MM:SS"""
    return f"{minutes:02d}:{seconds:02d}"

def synthesize_timeline(match_id: str) -> bool:
    """Combine all clip descriptions into one timeline file"""
    print(f"📝 Synthesizing timeline for {match_id}")
    
    data_dir = Path("../data") / match_id
    descriptions_dir = data_dir / "clip_descriptions"
    output_path = data_dir / "complete_timeline.txt"
    
    if not descriptions_dir.exists():
        print(f"❌ Clip descriptions directory not found: {descriptions_dir}")
        return False
    
    # Get all description files
    description_files = list(descriptions_dir.glob("clip_*.txt"))
    
    if not description_files:
        print(f"❌ No clip description files found in {descriptions_dir}")
        return False
    
    print(f"📊 Found {len(description_files)} description files")
    
    # Read and sort by timestamp
    timeline_entries = []
    
    for file_path in description_files:
        try:
            # Extract timestamp from filename
            minutes, seconds = extract_timestamp_from_filename(file_path.name)
            timestamp = format_timestamp(minutes, seconds)
            
            # Read description
            with open(file_path, 'r') as f:
                description = f.read().strip()
            
            # Add to timeline
            timeline_entries.append((minutes * 60 + seconds, timestamp, description))
            
        except Exception as e:
            print(f"⚠️ Warning: Could not process {file_path.name}: {str(e)}")
    
    # Sort by total seconds
    timeline_entries.sort(key=lambda x: x[0])
    
    # Write combined timeline
    with open(output_path, 'w') as f:
        f.write(f"# Complete Match Timeline - {match_id}\n")
        f.write(f"# Generated from {len(timeline_entries)} clip descriptions\n\n")
        
        for _, timestamp, description in timeline_entries:
            f.write(f"{timestamp} - {description}\n")
    
    print(f"✅ Timeline synthesis complete!")
    print(f"📊 Combined {len(timeline_entries)} descriptions")
    print(f"📁 Output saved to: {output_path}")
    
    # Show sample of timeline
    print("\n🎯 Timeline Sample:")
    for i, (_, timestamp, description) in enumerate(timeline_entries[:5]):
        print(f"  {timestamp} - {description}")
    if len(timeline_entries) > 5:
        print("  ...")
        for _, timestamp, description in timeline_entries[-2:]:
            print(f"  {timestamp} - {description}")
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python 5_synthesis.py <match-id>")
        print("Example: python 5_synthesis.py ballyclare-20250111")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    try:
        success = synthesize_timeline(match_id)
        
        if success:
            print("🎉 Timeline synthesis completed successfully!")
        else:
            print("❌ Timeline synthesis failed!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
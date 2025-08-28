#!/usr/bin/env python3
"""
1.6 Synthesis
Combine all clip descriptions into one chronological timeline
Simple, fast, no AI needed - just file concatenation and sorting
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

def parse_and_adjust_timings(description: str, clip_start_minutes: int, clip_start_seconds: int) -> str:
    """Parse internal clip timings and adjust them to match timestamps"""
    import re
    
    # Find all timestamps in format 00:XX within the description
    timestamp_pattern = r'00:(\d{2})'
    
    def replace_timestamp(match):
        clip_seconds = int(match.group(1))
        
        # Calculate total seconds from start of match
        total_seconds = (clip_start_minutes * 60) + clip_start_seconds + clip_seconds
        
        # Convert back to MM:SS format
        final_minutes = total_seconds // 60
        final_seconds = total_seconds % 60
        
        return f"{final_minutes:02d}:{final_seconds:02d}"
    
    # Replace all 00:XX timestamps with match timestamps
    adjusted_description = re.sub(timestamp_pattern, replace_timestamp, description)
    
    return adjusted_description

def synthesize_timeline(match_id: str) -> bool:
    """Combine all clip descriptions into one timeline file"""
    print(f"📝 Synthesizing timeline for {match_id}")
    
    # Use V5 directory structure
    data_dir = Path(__file__).parent.parent / "outputs" / match_id
    descriptions_dir = data_dir / "1.5_clip_descriptions"
    output_path = data_dir / "1.6_complete_timeline.txt"
    
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
            
            # Read the simple description (no timestamp prefix expected)
            with open(file_path, 'r') as f:
                description = f.read().strip()
            
            # Adjust any internal clip timings (00:XX) to match timestamps
            adjusted_description = parse_and_adjust_timings(description, minutes, seconds)
            
            # Add to timeline with filename timestamp + adjusted events
            timeline_entries.append((minutes * 60 + seconds, timestamp, adjusted_description))
            
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
        print("Usage: python 1.6_synthesis.py <match-id>")
        print("Example: python 1.6_synthesis.py 20250427-match-apr-27-2025-9bd1cf29")
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
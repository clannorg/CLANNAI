#!/usr/bin/env python3
"""
2. Make Clips
Split video into 15-second clips for analysis
Adapted from veo-games-v4 but simplified for 5-a-side
"""

import sys
import os
import json
import subprocess
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_clip_fast(video_path, start_time, duration, output_path):
    """Extract a single clip using GPU-accelerated processing"""
    cmd = [
        'ffmpeg',
        '-hwaccel', 'cuda',  # Use GPU acceleration if available
        '-i', str(video_path),
        '-ss', str(start_time),
        '-t', str(duration),
        '-c', 'copy',  # Copy streams without re-encoding - FAST!
        '-avoid_negative_ts', 'make_zero',
        '-y',  # Overwrite
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError:
        # Fallback to CPU if GPU fails
        cmd_fallback = [
            'ffmpeg',
            '-i', str(video_path),
            '-ss', str(start_time),
            '-t', str(duration),
            '-c', 'copy',
            '-avoid_negative_ts', 'make_zero',
            '-y',
            str(output_path)
        ]
        try:
            subprocess.run(cmd_fallback, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

def get_video_duration(video_path):
    """Get video duration in seconds"""
    cmd = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_format',
        str(video_path)
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        return float(data['format']['duration'])
    except:
        return None

def main():
    if len(sys.argv) != 3:
        print("Usage: python 2_make_clips.py <video-path> <match-id>")
        print("Example: python 2_make_clips.py /path/to/game.mp4 sunday-league-game-1")
        sys.exit(1)
    
    video_path = Path(sys.argv[1])
    match_id = sys.argv[2]
    
    if not video_path.exists():
        print(f"❌ Error: Video file not found: {video_path}")
        sys.exit(1)
    
    # Create outputs directory
    outputs_dir = Path(__file__).parent.parent / 'outputs' / match_id
    clips_dir = outputs_dir / 'clips'
    clips_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"🎬 Making clips for: {video_path}")
    print(f"📁 Match ID: {match_id}")
    print("=" * 50)
    
    # Get video duration
    duration = get_video_duration(video_path)
    if not duration:
        print("❌ Error: Could not determine video duration")
        sys.exit(1)
    
    print(f"⏱️  Video duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
    
    # Generate clips every 15 seconds
    clip_duration = 15
    clips_to_make = []
    
    current_time = 0
    clip_number = 0
    
    while current_time < duration:
        # Don't make clips that would extend past the video
        actual_duration = min(clip_duration, duration - current_time)
        if actual_duration < 5:  # Skip very short clips at the end
            break
            
        minutes = int(current_time // 60)
        seconds = int(current_time % 60)
        clip_filename = f"clip_{minutes:02d}m{seconds:02d}s.mp4"
        clip_path = clips_dir / clip_filename
        
        clips_to_make.append({
            'start_time': current_time,
            'duration': actual_duration,
            'output_path': clip_path,
            'filename': clip_filename
        })
        
        current_time += clip_duration
        clip_number += 1
    
    print(f"📊 Will create {len(clips_to_make)} clips")
    
    # Extract clips in parallel
    successful_clips = []
    failed_clips = []
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all clip extraction jobs
        future_to_clip = {
            executor.submit(
                extract_clip_fast, 
                video_path, 
                clip['start_time'], 
                clip['duration'], 
                clip['output_path']
            ): clip for clip in clips_to_make
        }
        
        # Process completed clips
        for i, future in enumerate(as_completed(future_to_clip)):
            clip = future_to_clip[future]
            try:
                success = future.result()
                if success:
                    successful_clips.append(clip['filename'])
                    print(f"✅ [{i+1}/{len(clips_to_make)}] {clip['filename']}")
                else:
                    failed_clips.append(clip['filename'])
                    print(f"❌ [{i+1}/{len(clips_to_make)}] Failed: {clip['filename']}")
            except Exception as e:
                failed_clips.append(clip['filename'])
                print(f"❌ [{i+1}/{len(clips_to_make)}] Error: {clip['filename']} - {e}")
    
    # Save clip manifest
    manifest = {
        'match_id': match_id,
        'video_path': str(video_path),
        'video_duration': duration,
        'clip_duration': clip_duration,
        'total_clips': len(clips_to_make),
        'successful_clips': len(successful_clips),
        'failed_clips': len(failed_clips),
        'clips': successful_clips
    }
    
    manifest_file = outputs_dir / 'clips_manifest.json'
    with open(manifest_file, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n✅ Clip creation complete!")
    print(f"📊 Success: {len(successful_clips)}/{len(clips_to_make)} clips")
    if failed_clips:
        print(f"❌ Failed: {len(failed_clips)} clips")
    print(f"📄 Manifest saved to: {manifest_file}")
    print(f"\n🎯 Ready for step 3: python 3_analyze_clips.py {match_id}")

if __name__ == "__main__":
    main()
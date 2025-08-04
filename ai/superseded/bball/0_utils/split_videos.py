#!/usr/bin/env python3
"""
Split Basketball Videos into 15-second clips
Split both left and right camera videos into synchronized clips for analysis
"""

import os
import subprocess
import time
from pathlib import Path

def extract_clip_fast(video_path, start_time, duration, output_path):
    """Extract a single clip using stream copying (NO re-encoding) - MUCH faster"""
    cmd = [
        'ffmpeg',
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
        return False

def split_basketball_videos():
    """Split both basketball videos into 15-second clips"""
    print("🏀 BASKETBALL VIDEO SPLITTER")
    print("=" * 50)
    
    # Get script directory and set up paths
    script_dir = Path(__file__).parent
    output_dir = script_dir / "output"
    
    # Video paths (from download_videos.py output)
    left_video = output_dir / "left_camera.mp4"
    right_video = output_dir / "right_camera.mp4"
    
    # Clips output directory
    clips_dir = output_dir / "clips"
    clips_dir.mkdir(exist_ok=True)
    
    # Check if videos exist
    if not left_video.exists():
        print(f"❌ Left video not found: {left_video}")
        print("   Run download_videos.py first!")
        return
    if not right_video.exists():
        print(f"❌ Right video not found: {right_video}")
        print("   Run download_videos.py first!")
        return
    
    print(f"📹 Processing videos:")
    print(f"   Left camera: {left_video}")
    print(f"   Right camera: {right_video}")
    print("⚡ Using stream copying (no re-encoding) for maximum speed!")
    print()
    
    # Create clips for first 10 minutes (40 clips of 15 seconds each)
    clip_duration = 15
    max_clips = 40  # 10 minutes worth
    
    successful_clips = 0
    processing_start_time = time.time()
    
    for i in range(max_clips):
        clip_start_time = i * clip_duration
        minutes = clip_start_time // 60
        seconds = clip_start_time % 60
        timestamp = f"{minutes}_{seconds:02d}"
        
        print(f"🎬 Creating clip {i+1}/{max_clips}: {minutes}:{seconds:02d}")
        
        # Left side clip
        left_clip = clips_dir / f"left_{timestamp}.mp4"
        if not left_clip.exists():
            if extract_clip_fast(left_video, clip_start_time, clip_duration, left_clip):
                size_mb = left_clip.stat().st_size / (1024*1024)
                print(f"  ✅ Left: {left_clip.name} ({size_mb:.1f}MB)")
            else:
                print(f"  ❌ Failed: Left side")
                continue
        else:
            size_mb = left_clip.stat().st_size / (1024*1024)
            print(f"  ♻️  Left: {left_clip.name} ({size_mb:.1f}MB)")
        
        # Right side clip
        right_clip = clips_dir / f"right_{timestamp}.mp4"
        if not right_clip.exists():
            if extract_clip_fast(right_video, clip_start_time, clip_duration, right_clip):
                size_mb = right_clip.stat().st_size / (1024*1024)
                print(f"  ✅ Right: {right_clip.name} ({size_mb:.1f}MB)")
                successful_clips += 1
            else:
                print(f"  ❌ Failed: Right side")
                continue
        else:
            size_mb = right_clip.stat().st_size / (1024*1024)
            print(f"  ♻️  Right: {right_clip.name} ({size_mb:.1f}MB)")
            successful_clips += 1
    
        # Show speed metrics every 10 clips
        if (i + 1) % 10 == 0:
            elapsed = time.time() - processing_start_time
            rate = (i + 1) / elapsed
            print(f"  📊 Speed: {rate:.1f} clips/sec | Elapsed: {elapsed:.1f}s")
    
    total_time = time.time() - processing_start_time
    
    print("\n⚡ FAST SPLITTING COMPLETE!")
    print("=" * 50)
    print(f"✅ Created {successful_clips} synchronized clip pairs")
    print(f"⏱️  Total time: {total_time:.1f} seconds")
    print(f"🚀 Speed: {successful_clips/total_time:.1f} clips/second")
    print(f"📁 Clips saved to: {clips_dir}")
    
    return successful_clips

if __name__ == "__main__":
    split_basketball_videos() 
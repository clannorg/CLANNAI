#!/usr/bin/env python3
"""
3. Generate Clips
Segments video into 15-second clips using ultra-fast stream copying
"""

import sys
import os
import json
import subprocess
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

def extract_clip_fast(video_path, start_time, duration, output_path):
    """Extract a single clip using GPU-accelerated processing - ULTRA FAST!"""
    cmd = [
        'ffmpeg',
        '-hwaccel', 'cuda',  # Use Tesla T4 GPU acceleration!
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
    """Get video duration in seconds using ffprobe"""
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
        duration = float(data['format']['duration'])
        return duration
    except (subprocess.CalledProcessError, KeyError, ValueError):
        print("⚠️  Could not determine video duration, using 90 minutes default")
        return 5400  # 90 minutes default

def generate_clips_ultra_fast(video_path, clips_dir, video_duration):
    """ULTRA FAST: Single ffmpeg command to generate all clips at once"""
    print("🚀 ULTRA FAST MODE: Using ffmpeg segment (10-50x faster!)")
    
    try:
        # Single GPU-accelerated command to create ALL clips
        cmd = [
            'ffmpeg',
            '-hwaccel', 'cuda',  # GPU acceleration
            '-i', str(video_path),
            '-f', 'segment',  # Segment mode - creates all clips in one pass!
            '-segment_time', '15',  # 15-second segments
            '-segment_format', 'mp4',
            '-c', 'copy',  # Stream copy - no re-encoding
            '-reset_timestamps', '1',  # Reset timestamps for each clip
            '-segment_start_number', '0',
            '-y',  # Overwrite
            str(clips_dir / 'temp_clip_%04d.mp4')  # Temporary naming
        ]
        
        print("⚡ Running single ffmpeg command for all clips...")
        start_time = time.time()
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        segment_time = time.time() - start_time
        print(f"✅ Segmentation complete in {segment_time:.1f} seconds!")
        
        # Rename clips to our time-based format
        print("🔄 Renaming clips to time-based format...")
        rename_start = time.time()
        
        temp_clips = sorted(clips_dir.glob('temp_clip_*.mp4'))
        renamed_count = 0
        
        for i, temp_clip in enumerate(temp_clips):
            start_seconds = i * 15
            minutes = int(start_seconds // 60)
            seconds = int(start_seconds % 60)
            
            new_name = f"clip_{minutes:02d}m{seconds:02d}s.mp4"
            new_path = clips_dir / new_name
            
            temp_clip.rename(new_path)
            renamed_count += 1
        
        rename_time = time.time() - rename_start
        total_time = time.time() - start_time
        
        print(f"✅ Renamed {renamed_count} clips in {rename_time:.1f} seconds")
        print(f"🚀 TOTAL TIME: {total_time:.1f} seconds ({renamed_count/total_time:.1f} clips/sec)")
        
        return renamed_count
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ultra-fast mode failed: {e}")
        print("🔄 Falling back to parallel processing...")
        return None

def generate_clips(match_id):
    """Generate 15-second clips from FULL GAME using time-based naming"""
    print(f"✂️ Step 3: Generating clips for {match_id} (FULL GAME)")
    
    data_dir = Path("../outputs") / match_id
    video_path = data_dir / "video.mp4"
    clips_dir = data_dir / "1.4_clips"
    
    if not video_path.exists():
        print(f"❌ Video not found: {video_path}")
        print("Run Step 2 first: python 2_download_video.py")
        return False
    
    # Create clips directory
    clips_dir.mkdir(exist_ok=True)
    
    print(f"📹 Processing video: {video_path}")
    print("⚡ Attempting ULTRA FAST mode with GPU acceleration...")
    
    # Get actual video duration
    video_duration = get_video_duration(video_path)
    print(f"📊 Full video duration: {video_duration/60:.1f} minutes")
    
    # Try ultra-fast mode first
    ultra_fast_result = generate_clips_ultra_fast(video_path, clips_dir, video_duration)
    if ultra_fast_result:
        print(f"🎯 ULTRA FAST SUCCESS! Created {ultra_fast_result} clips")
        return True
    
    # Fallback to parallel processing if ultra-fast fails
    print("🔄 Using parallel processing fallback...")
    print("⚡ Using GPU-accelerated parallel processing for maximum speed!")
    
    # PROCESS FULL GAME (no time limit)
    processing_duration = video_duration
    
    # Calculate number of clips for full game
    clip_duration = 15
    num_clips = int(processing_duration // clip_duration)
    
    print(f"🎯 Processing FULL GAME: {processing_duration/60:.1f} minutes")
    print(f"📊 Will create {num_clips} clips of {clip_duration} seconds each")
    print()
    
    clips_info = {
        "total_clips": num_clips,
        "clip_duration_seconds": clip_duration,
        "processing_duration_seconds": processing_duration,
        "video_duration_seconds": video_duration,
        "clips": []
    }
    
    successful_clips = 0
    processing_start_time = time.time()
    
    def process_single_clip(i):
        """Process a single clip with time-based naming"""
        start_time = i * clip_duration
        minutes = int(start_time // 60)
        seconds = int(start_time % 60)
        
        # TIME-BASED NAMING: clip_00m00s.mp4, clip_00m15s.mp4, etc.
        clip_filename = f"clip_{minutes:02d}m{seconds:02d}s.mp4"
        
        end_time = min(start_time + clip_duration, processing_duration)
        actual_duration = end_time - start_time
        
        clip_path = clips_dir / clip_filename
        
        # Skip if clip already exists
        if clip_path.exists():
            size_mb = clip_path.stat().st_size / (1024*1024)
            return f"♻️  Already exists: {clip_filename} ({size_mb:.1f}MB)", True
        
        # Extract the clip
        if extract_clip_fast(video_path, start_time, actual_duration, clip_path):
            size_mb = clip_path.stat().st_size / (1024*1024)
            return f"✅ Created: {clip_filename} ({size_mb:.1f}MB)", True
        else:
            return f"❌ Failed: {clip_filename}", False
    
    # Process clips in parallel (8 workers + GPU acceleration for maximum performance)
    print("🚀 Using GPU acceleration + parallel processing (8 threads)")
    print("⚡ Tesla T4 GPU + 4-core Xeon optimization enabled!")
    
    with ThreadPoolExecutor(max_workers=8) as executor:
        # Submit all clip creation tasks
        future_to_clip = {executor.submit(process_single_clip, i): i for i in range(num_clips)}
        
        # Process results as they complete
        for i, future in enumerate(as_completed(future_to_clip), 1):
            clip_index = future_to_clip[future]
            try:
                result_message, success = future.result()
                print(f"🔄 {i}/{num_clips}: {result_message}")
                
                if success:
                    successful_clips += 1
                    
                    # Add to clips info with time-based naming
                    start_seconds = clip_index * clip_duration
                    end_seconds = min(start_seconds + clip_duration, processing_duration)
                    minutes = int(start_seconds // 60)
                    seconds = int(start_seconds % 60)
                    
                    clips_info["clips"].append({
                        "filename": f"clip_{minutes:02d}m{seconds:02d}s.mp4",
                        "start_seconds": start_seconds,
                        "end_seconds": end_seconds,
                        "duration": end_seconds - start_seconds,
                        "timestamp": f"{minutes:02d}:{seconds:02d}"
                    })
                
                # Show speed metrics every 20 clips
                if i % 20 == 0:
                    elapsed = time.time() - processing_start_time
                    rate = i / elapsed
                    print(f"  📊 Speed: {rate:.1f} clips/sec | Elapsed: {elapsed:.1f}s")
                    
            except Exception as e:
                print(f"❌ Error processing clip {clip_index}: {e}")
    
    total_time = time.time() - processing_start_time
    
    # Sort clips info by start time
    clips_info["clips"].sort(key=lambda x: x["start_seconds"])
    
    # Save clips metadata
    with open(clips_dir / "segments.json", 'w') as f:
        json.dump(clips_info, f, indent=2)
    
    print("\n⚡ FULL GAME CLIPPING COMPLETE!")
    print("=" * 50)
    print(f"✅ Created {successful_clips}/{num_clips} clips")
    print(f"🎯 Coverage: 0:00 to {processing_duration//60:02.0f}:{processing_duration%60:02.0f}")
    print(f"⏱️  Total time: {total_time:.1f} seconds")
    print(f"🚀 Speed: {successful_clips/total_time:.1f} clips/second")
    print(f"📁 Clips saved to: {clips_dir}")
    print(f"📊 Metadata saved: {clips_dir}/segments.json")
    
    return successful_clips > 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 3_generate_clips.py <match-id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    success = generate_clips(match_id)
    
    if success:
        print(f"🎯 Ready for Step 3.5: Video compression")
    else:
        sys.exit(1) 
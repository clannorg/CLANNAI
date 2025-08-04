#!/usr/bin/env python3
"""
Compress Basketball Video Clips
Compresses 15-second clips for efficient API processing
"""

import subprocess
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def compress_clip(input_path, output_path):
    """Compress a single video clip for API processing"""
    cmd = [
        'ffmpeg',
        '-i', str(input_path),
        '-c:v', 'libx264',
        '-crf', '23',  # Good quality for API (18-28 range)
        '-preset', 'fast',  # Faster encoding for many clips
        '-c:a', 'aac',
        '-b:a', '96k',  # Compress audio
        '-vf', 'scale=640:480',  # Resize for API efficiency
        '-y',  # Overwrite output
        str(output_path)
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def compress_videos():
    """Compress all 15-second clips for API processing using parallel processing"""
    print("🗜️  COMPRESSING VIDEO CLIPS (PARALLEL)")
    print("=" * 50)
    
    # Get script directory and set up paths
    script_dir = Path(__file__).parent
    output_dir = script_dir / "output"
    clips_dir = output_dir / "clips"
    compressed_dir = output_dir / "compressed_clips"
    
    # Create compressed clips directory
    compressed_dir.mkdir(exist_ok=True)
    
    # Check if clips exist
    if not clips_dir.exists():
        print(f"❌ Clips directory not found: {clips_dir}")
        print("   Run split_videos.py first!")
        return
    
    # Get all clip files
    clip_files = list(clips_dir.glob("*.mp4"))
    if not clip_files:
        print(f"❌ No clip files found in {clips_dir}")
        print("   Run split_videos.py first!")
        return
    
    print(f"📹 Found {len(clip_files)} clips to compress")
    print(f"📁 Output: {compressed_dir}")
    print("🚀 Using parallel processing (4 threads)")
    print()
    
    # Thread-safe counters
    successful_compressions = 0
    total_original_size = 0
    total_compressed_size = 0
    lock = threading.Lock()
    
    def compress_single_clip(clip_file):
        """Compress a single clip with progress tracking"""
        nonlocal successful_compressions, total_original_size, total_compressed_size
        
        # Create compressed filename
        compressed_file = compressed_dir / f"compressed_{clip_file.name}"
        
        # Skip if already compressed
        if compressed_file.exists():
            size_mb = compressed_file.stat().st_size / (1024*1024)
            with lock:
                successful_compressions += 1
            return f"♻️  Already compressed: {clip_file.name} ({size_mb:.1f}MB)"
        
        # Get original size
        original_size = clip_file.stat().st_size / (1024*1024)  # MB
        
        with lock:
            total_original_size += original_size
        
        # Compress the clip
        if compress_clip(clip_file, compressed_file):
            compressed_size = compressed_file.stat().st_size / (1024*1024)  # MB
            compression_ratio = (1 - compressed_size/original_size) * 100
            
            with lock:
                total_compressed_size += compressed_size
                successful_compressions += 1
            
            return f"✅ Compressed: {compressed_file.name} ({compressed_size:.1f}MB, {compression_ratio:.1f}% smaller)"
        else:
            return f"❌ Failed to compress: {clip_file.name}"
    
    # Process clips in parallel
    processing_start_time = time.time()
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all compression tasks
        future_to_clip = {executor.submit(compress_single_clip, clip_file): clip_file for clip_file in clip_files}
        
        # Process results as they complete
        for i, future in enumerate(as_completed(future_to_clip), 1):
            clip_file = future_to_clip[future]
            try:
                result = future.result()
                print(f"🔄 {i}/{len(clip_files)}: {result}")
            except Exception as e:
                print(f"❌ Error compressing {clip_file.name}: {e}")
    
    total_time = time.time() - processing_start_time
    
    print("\n✅ PARALLEL COMPRESSION COMPLETE!")
    print("=" * 50)
    print(f"✅ Compressed {successful_compressions}/{len(clip_files)} clips")
    print(f"📊 Total original size: {total_original_size:.1f}MB")
    print(f"📊 Total compressed size: {total_compressed_size:.1f}MB")
    if total_original_size > 0:
        overall_compression = (1 - total_compressed_size/total_original_size) * 100
        print(f"📊 Overall compression: {overall_compression:.1f}% smaller")
    print(f"⏱️  Processing time: {total_time:.1f} seconds")
    print(f"🚀 Speed: {len(clip_files)/total_time:.1f} clips/second")
    print(f"📁 Compressed clips saved to: {compressed_dir}")
    
    return successful_compressions

if __name__ == "__main__":
    compress_videos() 
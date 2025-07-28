#!/usr/bin/env python3
"""
3.5. Compress Clips
Compresses 15-second clips for efficient Gemini API processing
"""

import sys
import os
import json
import subprocess
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

def compress_clip_for_api(input_path, output_path):
    """Compress a single video clip for Gemini API processing"""
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

def compress_clips(match_id):
    """Compress all 15-second clips for Gemini API processing using parallel processing"""
    print(f"🗜️ Step 3.5: Compressing clips for {match_id}")
    
    data_dir = Path("../data") / match_id
    clips_dir = data_dir / "clips"
    compressed_dir = data_dir / "compressed_clips"
    
    # Check if clips exist
    if not clips_dir.exists():
        print(f"❌ Clips directory not found: {clips_dir}")
        print("Run Step 3 first: python 3_generate_clips.py")
        return False
    
    # Load clips metadata
    segments_file = clips_dir / "segments.json"
    if not segments_file.exists():
        print(f"❌ Segments metadata not found: {segments_file}")
        return False
    
    with open(segments_file, 'r') as f:
        segments_data = json.load(f)
    
    # Create compressed clips directory
    compressed_dir.mkdir(exist_ok=True)
    
    # Get all clip files
    clip_files = [clips_dir / clip_info['filename'] for clip_info in segments_data['clips']]
    clip_files = [f for f in clip_files if f.exists()]
    
    if not clip_files:
        print(f"❌ No clip files found in {clips_dir}")
        return False
    
    print(f"📹 Found {len(clip_files)} clips to compress")
    print(f"📁 Output: {compressed_dir}")
    print("🚀 Using parallel processing (4 threads)")
    print("🎯 Optimizing for Gemini API: 640x480, CRF 23")
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
        if compress_clip_for_api(clip_file, compressed_file):
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
                
                # Show speed metrics every 50 clips
                if i % 50 == 0:
                    elapsed = time.time() - processing_start_time
                    rate = i / elapsed
                    print(f"  📊 Speed: {rate:.1f} clips/sec | Elapsed: {elapsed:.1f}s")
                    
            except Exception as e:
                print(f"❌ Error compressing {clip_file.name}: {e}")
    
    total_time = time.time() - processing_start_time
    
    # Create compressed clips metadata
    compressed_info = {
        "total_compressed_clips": successful_compressions,
        "original_clips_processed": len(clip_files),
        "compression_stats": {
            "total_original_size_mb": total_original_size,
            "total_compressed_size_mb": total_compressed_size,
            "overall_compression_ratio": (1 - total_compressed_size/total_original_size) * 100 if total_original_size > 0 else 0,
            "processing_time_seconds": total_time,
            "compression_speed_clips_per_second": len(clip_files)/total_time
        },
        "settings": {
            "resolution": "640x480",
            "video_codec": "libx264",
            "crf": 23,
            "audio_codec": "aac",
            "audio_bitrate": "96k"
        }
    }
    
    # Save compression metadata
    with open(compressed_dir / "compression_info.json", 'w') as f:
        json.dump(compressed_info, f, indent=2)
    
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
    print(f"📊 Metadata saved: {compressed_dir}/compression_info.json")
    
    return successful_compressions > 0

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 3.5_compress_clips.py <match-id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    success = compress_clips(match_id)
    
    if success:
        print(f"🎯 Ready for Step 4: Gemini clip analysis")
    else:
        sys.exit(1) 
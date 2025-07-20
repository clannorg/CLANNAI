#!/usr/bin/env python3
"""
Video Segmentation for Game298_0601
Splits the 15-minute game into 30-second clips for AI analysis
"""

import subprocess
import logging
from pathlib import Path
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoSegmentation:
    """Segments video into clips for AI analysis"""
    
    def __init__(self):
        """Initialize segmentation system"""
        self.input_video = Path("Game298_0601_p1.mp4")
        self.clips_dir = Path("clips")
        self.clip_duration = 15  # 15 seconds per clip for better precision
        self.overlap = 5  # 5 second overlap
        self.total_duration = 917.6  # Total video duration in seconds
        
        # Create clips directory
        self.clips_dir.mkdir(exist_ok=True)
        
    def get_video_duration(self) -> float:
        """Get actual video duration using ffprobe"""
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', 
                '-show_entries', 'format=duration', 
                '-of', 'csv=p=0', 
                str(self.input_video)
            ], capture_output=True, text=True, check=True)
            
            duration = float(result.stdout.strip())
            logger.info(f"Video duration: {duration:.2f} seconds")
            return duration
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting video duration: {e}")
            return self.total_duration
    
    def create_clip(self, start_time: float, end_time: float, clip_number: int) -> bool:
        """Create a single clip using ffmpeg"""
        # Name clip based on start time in minutes and seconds (e.g., clip_0m00s.mp4, clip_0m30s.mp4)
        minutes = int(start_time // 60)
        seconds = int(start_time % 60)
        start_time_str = f"{minutes}m{seconds:02d}s"
        output_filename = f"clip_{start_time_str}.mp4"
        output_path = self.clips_dir / output_filename
        
        try:
            # Use ffmpeg to extract clip
            cmd = [
                'ffmpeg', '-i', str(self.input_video),
                '-ss', str(start_time),
                '-t', str(end_time - start_time),
                '-c', 'copy',  # Copy without re-encoding for speed
                '-avoid_negative_ts', 'make_zero',
                '-y',  # Overwrite output file
                str(output_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            # Verify clip was created and has content
            if output_path.exists() and output_path.stat().st_size > 0:
                logger.info(f"✅ Created clip {clip_number:03d}: {start_time:.1f}s - {end_time:.1f}s ({output_filename})")
                return True
            else:
                logger.error(f"❌ Clip {clip_number:03d} was not created properly")
                return False
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Error creating clip {clip_number:03d}: {e}")
            return False
    
    def segment_video(self) -> bool:
        """Segment the entire video into 15-second overlapping clips"""
        duration = self.get_video_duration()
        
        # Calculate number of clips with overlap
        effective_duration = self.clip_duration - self.overlap  # 10 seconds of new content per clip
        num_clips = int(duration // effective_duration) + 1
        logger.info(f"Creating {num_clips} clips of {self.clip_duration}s each with {self.overlap}s overlap")
        
        success_count = 0
        
        for i in range(num_clips):
            start_time = i * effective_duration
            end_time = min(start_time + self.clip_duration, duration)
            
            # Skip if start time is beyond video duration
            if start_time >= duration:
                break
                
            clip_number = i + 1
            
            if self.create_clip(start_time, end_time, clip_number):
                success_count += 1
        
        logger.info(f"✅ Successfully created {success_count}/{num_clips} clips")
        return success_count == num_clips
    
    def verify_clips(self) -> dict:
        """Verify all clips were created and get their info"""
        clips_info = {}
        
        for clip_file in sorted(self.clips_dir.glob("Game298_0601_clip_*.mp4")):
            try:
                # Get clip duration
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet',
                    '-show_entries', 'format=duration',
                    '-of', 'csv=p=0',
                    str(clip_file)
                ], capture_output=True, text=True, check=True)
                
                duration = float(result.stdout.strip())
                clips_info[clip_file.name] = {
                    'duration': duration,
                    'size_mb': clip_file.stat().st_size / (1024 * 1024)
                }
                
            except Exception as e:
                logger.error(f"Error verifying {clip_file.name}: {e}")
        
        return clips_info
    
    def print_summary(self, clips_info: dict):
        """Print summary of created clips"""
        print("\n" + "=" * 60)
        print("VIDEO SEGMENTATION SUMMARY")
        print("=" * 60)
        
        total_duration = sum(info['duration'] for info in clips_info.values())
        total_size = sum(info['size_mb'] for info in clips_info.values())
        
        print(f"Total clips created: {len(clips_info)}")
        print(f"Total duration: {total_duration:.1f} seconds")
        print(f"Total size: {total_size:.1f} MB")
        print(f"Average clip size: {total_size/len(clips_info):.1f} MB")
        
        print("\nClip Details:")
        for clip_name, info in clips_info.items():
            print(f"  {clip_name}: {info['duration']:.1f}s ({info['size_mb']:.1f} MB)")
        
        print("=" * 60)

def main():
    """Main segmentation process"""
    logger.info("🎬 Starting video segmentation for Game298_0601")
    
    # Check if input video exists
    input_video = Path("Game298_0601_p1.mp4")
    if not input_video.exists():
        logger.error(f"❌ Input video not found: {input_video}")
        return False
    
    # Initialize segmentation
    segmenter = VideoSegmentation()
    
    # Create clips
    success = segmenter.segment_video()
    
    if success:
        # Verify clips
        clips_info = segmenter.verify_clips()
        segmenter.print_summary(clips_info)
        
        logger.info("✅ Video segmentation completed successfully!")
        return True
    else:
        logger.error("❌ Video segmentation failed!")
        return False

if __name__ == "__main__":
    main() 
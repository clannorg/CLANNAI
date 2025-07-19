#!/usr/bin/env python3
"""
Create Action Period Clips
Segments the 18-22 minute action period into 30-second clips
named by their start timestamp
"""

import os
import subprocess
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ActionPeriodProcessor:
    """
    Processes the 18-22 minute action period into timestamped clips
    """
    
    def __init__(self, input_dir: str = "input", output_dir: str = "0_utils/output"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Action period settings
        self.clip_duration = 30  # 30 seconds
        self.target_fps = 15  # 15 FPS for better analysis
        self.target_resolution = (1280, 720)  # 720p
        self.codec = "libx264"
        self.preset = "ultrafast"
        self.crf = 25  # Good quality for analysis
        
    def get_video_info(self, video_path: str) -> dict:
        """
        Get video information using ffprobe
        """
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", video_path
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                logger.error(f"ffprobe failed: {result.stderr}")
                return {}
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {}
    
    def format_timestamp(self, seconds: int) -> str:
        """
        Convert seconds to MM:SS format for clip naming
        """
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes:02d}:{remaining_seconds:02d}"
    
    def format_match_time(self, seconds: int) -> str:
        """
        Convert seconds to match time format (18:00, 18:30, etc.)
        Action period starts at 18:00 (1080 seconds into match)
        """
        # Add 18 minutes (1080 seconds) to get actual match time
        match_seconds = seconds + 1080
        minutes = match_seconds // 60
        remaining_seconds = match_seconds % 60
        return f"{minutes:02d}:{remaining_seconds:02d}"
    
    def create_action_clips(self, video_path: str) -> list:
        """
        Create 30-second clips from action period with timestamp naming
        """
        video_info = self.get_video_info(video_path)
        if not video_info:
            return []
        
        # Get video duration
        duration = float(video_info.get("format", {}).get("duration", 0))
        total_clips = int(duration // self.clip_duration)
        
        logger.info(f"Action period duration: {duration:.1f} seconds")
        logger.info(f"Creating {total_clips} clips of {self.clip_duration} seconds each")
        
        clip_paths = []
        
        for i in range(total_clips):
            start_time = i * self.clip_duration
            match_time = self.format_match_time(start_time)
            
            # Name clips by their actual match time (18:00, 18:30, 19:00, etc.)
            output_filename = f"match_{match_time.replace(':', 'm')}s.mp4"
            output_path = self.output_dir / output_filename
            
            # FFmpeg command for action period clips
            cmd = [
                "ffmpeg", "-y",  # Overwrite output
                "-i", video_path,
                "-ss", str(start_time),
                "-t", str(self.clip_duration),
                "-vf", f"scale={self.target_resolution[0]}:{self.target_resolution[1]},fps={self.target_fps}",
                "-c:v", self.codec,
                "-preset", self.preset,
                "-crf", str(self.crf),
                "-c:a", "aac",
                "-b:a", "128k",
                str(output_path)
            ]
            
            try:
                logger.info(f"Processing clip {i+1}/{total_clips} (match time: {match_time})")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    clip_paths.append(str(output_path))
                    logger.info(f"Created clip: {output_filename}")
                else:
                    logger.error(f"Failed to create clip {i}: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"Error processing clip {i}: {e}")
        
        return clip_paths
    
    def create_clip_info(self, clip_paths: list) -> dict:
        """
        Create information about the clips created
        """
        clip_info = {
            "total_clips": len(clip_paths),
            "clip_duration": self.target_fps,
            "resolution": self.target_resolution,
            "clips": []
        }
        
        for i, clip_path in enumerate(clip_paths):
            start_time = i * self.clip_duration
            match_time = self.format_match_time(start_time)
            
            clip_info["clips"].append({
                "filename": Path(clip_path).name,
                "start_time": start_time,
                "match_time": match_time,
                "path": clip_path
            })
        
        return clip_info

def main():
    """
    Main function to create action period clips
    """
    processor = ActionPeriodProcessor()
    
    # Process the action period video
    action_video = processor.input_dir / "action_period.mp4"
    
    if not action_video.exists():
        logger.error(f"Action period video not found: {action_video}")
        return
    
    logger.info("Starting action period clip creation...")
    
    # Create clips
    clip_paths = processor.create_action_clips(str(action_video))
    
    if clip_paths:
        # Create clip information
        clip_info = processor.create_clip_info(clip_paths)
        
        logger.info("=== ACTION PERIOD CLIPS CREATED ===")
        logger.info(f"Total clips: {clip_info['total_clips']}")
        logger.info(f"Clip duration: {clip_info['clip_duration']} seconds")
        logger.info(f"Resolution: {clip_info['resolution']}")
        
        logger.info("\nClip details:")
        for clip in clip_info["clips"]:
            logger.info(f"  {clip['filename']} - starts at {clip['match_time']}")
        
        # Save clip information
        info_path = processor.output_dir / "action_clips_info.json"
        with open(info_path, 'w') as f:
            json.dump(clip_info, f, indent=2)
        
        logger.info(f"\nClip information saved to: {info_path}")
        logger.info("✅ Action period clips created successfully!")
    else:
        logger.error("❌ Failed to create action period clips")

if __name__ == "__main__":
    main() 
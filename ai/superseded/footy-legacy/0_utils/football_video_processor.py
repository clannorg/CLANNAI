#!/usr/bin/env python3
"""
Football Video Processor
Adapts basketball video processing for football/soccer analysis
"""

import os
import cv2
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FootballVideoProcessor:
    """
    Processes football videos for Gemini AI analysis
    Optimized for 90-minute matches with 30-second clips
    """
    
    def __init__(self, input_dir: str = "input", output_dir: str = "0_utils/output"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Football-specific settings
        self.clip_duration = 30  # 30 seconds (vs 15 for basketball)
        self.target_fps = 2  # 2 FPS for API optimization
        self.target_resolution = (1280, 720)  # 720p for better field visibility
        self.codec = "libx264"
        self.preset = "ultrafast"
        self.crf = 28  # Slightly higher compression for longer clips
        
    def download_video(self, url: str, filename: str = "football_match.mp4") -> str | None:
        """
        Download football video from URL
        """
        output_path = self.input_dir / filename
        
        try:
            # Use curl to download video
            cmd = [
                "curl", "-L", "-o", str(output_path), url
            ]
            
            logger.info(f"Downloading football video from {url}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully downloaded: {output_path}")
                return str(output_path)
            else:
                logger.error(f"Download failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None
    
    def get_video_info(self, video_path: str) -> Dict:
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
    
    def segment_video(self, video_path: str) -> List[str]:
        """
        Segment football video into 30-second clips
        """
        video_info = self.get_video_info(video_path)
        if not video_info:
            return []
        
        # Get video duration
        duration = float(video_info.get("format", {}).get("duration", 0))
        total_clips = int(duration // self.clip_duration)
        
        clip_paths = []
        
        for i in range(total_clips):
            start_time = i * self.clip_duration
            output_filename = f"football_clip_{i:03d}.mp4"
            output_path = self.output_dir / output_filename
            
            # FFmpeg command for football video processing
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
                logger.info(f"Processing clip {i+1}/{total_clips} (time: {start_time}s)")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    clip_paths.append(str(output_path))
                    logger.info(f"Created clip: {output_filename}")
                else:
                    logger.error(f"Failed to create clip {i}: {result.stderr}")
                    
            except Exception as e:
                logger.error(f"Error processing clip {i}: {e}")
        
        return clip_paths
    
    def optimize_for_api(self, clip_path: str) -> str:
        """
        Further optimize clip for Gemini API
        """
        input_path = Path(clip_path)
        output_filename = f"api_optimized_{input_path.name}"
        output_path = self.output_dir / output_filename
        
        # Additional optimization for API
        cmd = [
            "ffmpeg", "-y",
            "-i", clip_path,
            "-vf", "scale=640:480,fps=2",  # API-optimized size
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-crf", "30",  # Higher compression for API
            "-c:a", "aac",
            "-b:a", "64k",  # Lower audio bitrate
            str(output_path)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"API optimization complete: {output_filename}")
                return str(output_path)
            else:
                logger.error(f"API optimization failed: {result.stderr}")
                return clip_path
        except Exception as e:
            logger.error(f"Error optimizing for API: {e}")
            return clip_path
    
    def process_football_video(self, video_path: str | None = None, url: str | None = None) -> List[str]:
        """
        Complete football video processing pipeline
        """
        if url:
            video_path = self.download_video(url)
            if not video_path:
                logger.error("Failed to download video")
                return []
        
        if not video_path or not os.path.exists(video_path):
            logger.error(f"Video file not found: {video_path}")
            return []
        
        # Get video info
        video_info = self.get_video_info(video_path)
        duration = float(video_info.get("format", {}).get("duration", 0))
        
        logger.info(f"Processing football video: {duration:.1f} seconds")
        logger.info(f"Expected clips: {int(duration // self.clip_duration)}")
        
        # Segment video
        clip_paths = self.segment_video(video_path)
        
        # Optimize clips for API
        optimized_clips = []
        for clip_path in clip_paths:
            optimized_path = self.optimize_for_api(clip_path)
            optimized_clips.append(optimized_path)
        
        logger.info(f"Processing complete: {len(optimized_clips)} clips created")
        return optimized_clips
    
    def create_processing_report(self, clip_paths: List[str]) -> Dict:
        """
        Create processing report for football video
        """
        total_size = sum(os.path.getsize(path) for path in clip_paths)
        total_duration = len(clip_paths) * self.clip_duration
        
        report = {
            "total_clips": len(clip_paths),
            "clip_duration": self.clip_duration,
            "total_duration": total_duration,
            "total_size_mb": total_size / (1024 * 1024),
            "avg_clip_size_mb": (total_size / len(clip_paths)) / (1024 * 1024) if clip_paths else 0,
            "target_fps": self.target_fps,
            "target_resolution": self.target_resolution,
            "estimated_api_calls": len(clip_paths) * 2,  # Events + insights
            "estimated_cost": len(clip_paths) * 2 * 0.000210  # Based on basketball costs
        }
        
        return report

def main():
    """
    Main function for football video processing
    """
    processor = FootballVideoProcessor()
    
    # Example usage with provided URL
    url = "https://c.veocdn.com/c9543847-6cfa-45ad-bc85-60a6cafb7a5d/standard/machine/7775a871/video.mp4"
    
    logger.info("Starting football video processing...")
    
    # Process video
    clip_paths = processor.process_football_video(url=url)
    
    if clip_paths:
        # Generate report
        report = processor.create_processing_report(clip_paths)
        
        logger.info("=== FOOTBALL VIDEO PROCESSING REPORT ===")
        logger.info(f"Total clips: {report['total_clips']}")
        logger.info(f"Total duration: {report['total_duration']} seconds")
        logger.info(f"Total size: {report['total_size_mb']:.2f} MB")
        logger.info(f"Avg clip size: {report['avg_clip_size_mb']:.2f} MB")
        logger.info(f"Estimated API calls: {report['estimated_api_calls']}")
        logger.info(f"Estimated cost: ${report['estimated_cost']:.4f}")
        
        # Save report
        report_path = processor.output_dir / "processing_report.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Report saved: {report_path}")
    else:
        logger.error("No clips were processed successfully")

if __name__ == "__main__":
    main() 
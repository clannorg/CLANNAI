#!/usr/bin/env python3
"""
Video Segmentation for Match Videos
Splits the 15-minute game into 15-second clips for AI analysis
"""

import subprocess
import logging
from pathlib import Path
import sys
import argparse
import asyncio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoSegmentation:
    """Segments video into clips for AI analysis"""
    
    def __init__(self, game_name: str):
        """Initialize segmentation system"""
        self.game_name = game_name
        self.base_data_dir = Path.cwd() / "data"
        self.game_dir = self.base_data_dir / self.game_name
        self.input_video = self.game_dir / f"{self.game_name}_p1.mp4"
        self.clips_dir = self.game_dir / "clips"
        self.clip_duration = 15  # 15 seconds per clip for better precision
        self.overlap = 5  # 5 second overlap
        
        # Create clips directory
        self.clips_dir.mkdir(parents=True, exist_ok=True)
        
    async def get_video_duration(self) -> float:
        """Get actual video duration using ffprobe"""
        try:
            process = await asyncio.create_subprocess_exec(
                'ffprobe', '-v', 'quiet', 
                '-show_entries', 'format=duration', 
                '-of', 'csv=p=0', 
                str(self.input_video),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, "ffprobe", stderr=stderr)
            
            duration = float(stdout.decode().strip())
            logger.info(f"Video duration: {duration:.2f} seconds")
            return duration
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error getting video duration: {e.stderr.decode()}")
            raise
    
    async def create_clip(self, start_time: float, end_time: float, clip_number: int, semaphore: asyncio.Semaphore) -> bool:
        """Create a single clip using ffmpeg, managed by a semaphore."""
        async with semaphore:
            # Name clip to reflect the full time range
            start_min, start_sec = int(start_time // 60), int(start_time % 60)
            end_min, end_sec = int(end_time // 60), int(end_time % 60)
            
            output_filename = f"clip_{start_min}m{start_sec:02d}s_to_{end_min}m{end_sec:02d}s.mp4"
            output_path = self.clips_dir / output_filename
            
            # Skip if the clip already exists
            if output_path.exists():
                logger.info(f"⏭️  Skipping existing clip {clip_number:03d}: {output_filename}")
                return True
                
            try:
                logger.info(f"🚀 Creating clip {clip_number:03d}: {output_filename}")
                cmd = [
                    'ffmpeg', '-i', str(self.input_video),
                    '-ss', str(start_time),
                    '-t', str(end_time - start_time),
                    '-c', 'copy',
                    '-avoid_negative_ts', 'make_zero',
                    '-y',
                    str(output_path)
                ]
                
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = await process.communicate()

                if process.returncode != 0:
                    raise subprocess.CalledProcessError(process.returncode, "ffmpeg", stderr=stderr)
                
                if output_path.exists() and output_path.stat().st_size > 0:
                    logger.info(f"✅ Created clip {clip_number:03d}: {start_time:.1f}s - {end_time:.1f}s")
                    return True
                else:
                    logger.error(f"❌ Clip {clip_number:03d} was not created properly")
                    return False
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Error creating clip {clip_number:03d}: {e.stderr.decode()}")
                return False
    
    async def segment_video(self) -> bool:
        """Segment the entire video into 15-second overlapping clips"""
        try:
            duration = await self.get_video_duration()
        except subprocess.CalledProcessError:
            logger.error("Failed to get video duration. Aborting segmentation.")
            return False
        
        effective_duration = self.clip_duration - self.overlap
        num_clips = int(duration // effective_duration) + 1
        logger.info(f"Creating {num_clips} clips of {self.clip_duration}s each with {self.overlap}s overlap, using up to 4 parallel processes...")
        
        semaphore = asyncio.Semaphore(4)
        tasks = []
        
        for i in range(num_clips):
            start_time = i * effective_duration
            end_time = min(start_time + self.clip_duration, duration)
            
            if start_time >= duration:
                break
                
            clip_number = i + 1
            tasks.append(self.create_clip(start_time, end_time, clip_number, semaphore))

        results = await asyncio.gather(*tasks)
        success_count = sum(results)
        
        logger.info(f"✅ Successfully created {success_count}/{len(tasks)} clips")
        return success_count == len(tasks)
    
    async def _verify_single_clip(self, clip_file: Path, semaphore: asyncio.Semaphore) -> tuple[str, dict]:
        """Verify a single clip using ffprobe."""
        async with semaphore:
            try:
                process = await asyncio.create_subprocess_exec(
                    'ffprobe', '-v', 'quiet',
                    '-show_entries', 'format=duration',
                    '-of', 'csv=p=0',
                    str(clip_file),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout, stderr = await process.communicate()
                if process.returncode != 0:
                    raise subprocess.CalledProcessError(process.returncode, "ffprobe", stderr=stderr)

                duration = float(stdout.decode().strip())
                return clip_file.name, {
                    'duration': duration,
                    'size_mb': clip_file.stat().st_size / (1024 * 1024)
                }
            except Exception as e:
                logger.error(f"Error verifying {clip_file.name}: {e}")
                return clip_file.name, None

    async def verify_clips(self) -> dict:
        """Verify all clips were created and get their info"""
        logger.info("Verifying clips...")
        
        semaphore = asyncio.Semaphore(8)
        tasks = []
        
        for clip_file in sorted(self.clips_dir.glob("clip_*.mp4")):
            tasks.append(self._verify_single_clip(clip_file, semaphore))

        results = await asyncio.gather(*tasks)
        clips_info = {name: info for name, info in results if info is not None}
        
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

async def main():
    """Main segmentation process"""
    parser = argparse.ArgumentParser(description="Segment a match video into clips.")
    parser.add_argument("--game_name", required=True, help="The name of the game to segment (e.g., Game298_0601).")
    args = parser.parse_args()

    logger.info(f"🎬 Starting video segmentation for {args.game_name}")
    
    segmenter = VideoSegmentation(args.game_name)

    if not segmenter.input_video.exists():
        logger.error(f"❌ Input video not found: {segmenter.input_video}")
        return False
    
    success = await segmenter.segment_video()
    
    if success:
        clips_info = await segmenter.verify_clips()
        segmenter.print_summary(clips_info)
        
        logger.info("✅ Video segmentation completed successfully!")
        return True
    else:
        logger.error("❌ Video segmentation failed!")
        return False

if __name__ == "__main__":
    if not asyncio.run(main()):
        sys.exit(1) 
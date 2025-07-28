#!/usr/bin/env python3
"""
Veo Match Analyzer
Analyzes football matches downloaded from Veo platform
Integrates with existing CLANNAI football analysis pipeline
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add the parent directories to the path to import existing modules
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / '0_utils'))
sys.path.append(str(Path(__file__).parent.parent / '1_game_events'))

from veo_downloader import VeoDownloader
from video_segmentation import VideoSegmentation
from football_events_analyzer import FootballEventsAnalyzer
from football_events_synthesis import FootballEventsSynthesis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VeoMatchAnalyzer:
    """
    Complete analysis pipeline for Veo matches
    """
    
    def __init__(self, match_folder: str):
        self.match_folder = Path(match_folder)
        self.match_info_path = self.match_folder / "match_info.json"
        
        # Load match info
        with open(self.match_info_path, 'r') as f:
            self.match_info = json.load(f)
        
        # Initialize components
        self.downloader = VeoDownloader(str(self.match_folder / "raw_video"))
        self.segmenter = VideoSegmentation()
        self.events_analyzer = FootballEventsAnalyzer()
        self.synthesizer = FootballEventsSynthesis()
        
        logger.info(f"Initialized VeoMatchAnalyzer for {self.match_info['match_name']}")
    
    def download_match(self) -> bool:
        """
        Download the match video from Veo
        """
        try:
            logger.info(f"Downloading match from {self.match_info['veo_url']}")
            
            video_path = self.downloader.download_match(
                self.match_info['veo_url'],
                f"{self.match_info['match_id']}.mp4"
            )
            
            if video_path:
                self.match_info['files']['raw_video'] = str(video_path)
                self.match_info['analysis_pipeline']['download_completed'] = True
                self._save_match_info()
                logger.info(f"Successfully downloaded to {video_path}")
                return True
            else:
                logger.error("Failed to download video")
                return False
                
        except Exception as e:
            logger.error(f"Error downloading match: {e}")
            return False
    
    def process_clips(self) -> bool:
        """
        Split the downloaded video into 30-second clips
        """
        try:
            if not self.match_info['analysis_pipeline']['download_completed']:
                logger.error("Cannot process clips - video not downloaded")
                return False
            
            video_path = self.match_info['files']['raw_video']
            clips_dir = self.match_folder / "clips"
            
            logger.info(f"Processing video into clips: {video_path}")
            
            clips = self.segmenter.segment_video(
                video_path,
                str(clips_dir),
                segment_duration=30
            )
            
            self.match_info['files']['clips_count'] = len(clips)
            self.match_info['analysis_pipeline']['clips_processed'] = True
            self._save_match_info()
            
            logger.info(f"Created {len(clips)} clips")
            return True
            
        except Exception as e:
            logger.error(f"Error processing clips: {e}")
            return False
    
    def analyze_events(self) -> bool:
        """
        Analyze all clips for football events
        """
        try:
            if not self.match_info['analysis_pipeline']['clips_processed']:
                logger.error("Cannot analyze events - clips not processed")
                return False
            
            clips_dir = self.match_folder / "clips"
            analysis_dir = self.match_folder / "analysis"
            
            logger.info("Analyzing clips for football events")
            
            # Analyze each clip
            analysis_files = []
            for clip_file in clips_dir.glob("*.mp4"):
                output_file = analysis_dir / f"{clip_file.stem}_analysis.json"
                
                events = self.events_analyzer.analyze_clip(str(clip_file))
                
                with open(output_file, 'w') as f:
                    json.dump(events, f, indent=2)
                
                analysis_files.append(str(output_file))
            
            self.match_info['files']['analysis_files'] = analysis_files
            self.match_info['analysis_pipeline']['events_analyzed'] = True
            self._save_match_info()
            
            logger.info(f"Analyzed {len(analysis_files)} clips")
            return True
            
        except Exception as e:
            logger.error(f"Error analyzing events: {e}")
            return False
    
    def synthesize_match(self) -> bool:
        """
        Synthesize all analysis into match timeline and statistics
        """
        try:
            if not self.match_info['analysis_pipeline']['events_analyzed']:
                logger.error("Cannot synthesize - events not analyzed")
                return False
            
            analysis_dir = self.match_folder / "analysis"
            synthesis_dir = self.match_folder / "synthesis"
            
            logger.info("Synthesizing match timeline and statistics")
            
            # Collect all analysis files
            analysis_files = [str(f) for f in analysis_dir.glob("*_analysis.json")]
            
            # Generate synthesis
            timeline, stats = self.synthesizer.synthesize_match(analysis_files)
            
            # Save synthesis files
            timeline_file = synthesis_dir / "events_timeline.json"
            stats_file = synthesis_dir / "event_statistics.json"
            
            with open(timeline_file, 'w') as f:
                json.dump(timeline, f, indent=2)
            
            with open(stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
            
            self.match_info['files']['synthesis_files'] = [str(timeline_file), str(stats_file)]
            self.match_info['analysis_pipeline']['synthesis_completed'] = True
            self.match_info['status'] = "completed"
            self._save_match_info()
            
            logger.info("Match synthesis completed")
            return True
            
        except Exception as e:
            logger.error(f"Error synthesizing match: {e}")
            return False
    
    def run_full_pipeline(self) -> bool:
        """
        Run the complete analysis pipeline
        """
        logger.info(f"Starting full pipeline for {self.match_info['match_name']}")
        
        steps = [
            ("Download", self.download_match),
            ("Process Clips", self.process_clips),
            ("Analyze Events", self.analyze_events),
            ("Synthesize Match", self.synthesize_match)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"Running step: {step_name}")
            if not step_func():
                logger.error(f"Failed at step: {step_name}")
                return False
        
        logger.info("Full pipeline completed successfully!")
        return True
    
    def _save_match_info(self):
        """Save updated match info to file"""
        with open(self.match_info_path, 'w') as f:
            json.dump(self.match_info, f, indent=2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python veo_match_analyzer.py <match_folder>")
        sys.exit(1)
    
    match_folder = sys.argv[1]
    analyzer = VeoMatchAnalyzer(match_folder)
    
    if analyzer.run_full_pipeline():
        print("✅ Match analysis completed successfully!")
    else:
        print("❌ Match analysis failed!")
        sys.exit(1) 
#!/usr/bin/env python3
"""
Veo Pipeline Manager
Manages multiple Veo match analyses and batch operations
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

from veo_match_analyzer import VeoMatchAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VeoPipeline:
    """
    Manages the analysis pipeline for multiple Veo matches
    """
    
    def __init__(self, veo_games_dir: str = None):
        if veo_games_dir is None:
            veo_games_dir = Path(__file__).parent
        
        self.veo_games_dir = Path(veo_games_dir)
        self.matches = self._discover_matches()
        
        logger.info(f"Initialized VeoPipeline with {len(self.matches)} matches")
    
    def _discover_matches(self) -> List[Path]:
        """
        Discover all match folders in the veo-games directory
        """
        matches = []
        for item in self.veo_games_dir.iterdir():
            if item.is_dir() and (item / "match_info.json").exists():
                matches.append(item)
        
        return sorted(matches)
    
    def list_matches(self) -> List[Dict]:
        """
        List all discovered matches with their status
        """
        match_list = []
        
        for match_dir in self.matches:
            try:
                with open(match_dir / "match_info.json", 'r') as f:
                    match_info = json.load(f)
                
                match_list.append({
                    "folder": match_dir.name,
                    "match_name": match_info.get("match_name", "Unknown"),
                    "date": match_info.get("date", "Unknown"),
                    "status": match_info.get("status", "Unknown"),
                    "veo_url": match_info.get("veo_url", "Unknown"),
                    "pipeline_status": match_info.get("analysis_pipeline", {})
                })
                
            except Exception as e:
                logger.error(f"Error reading match info for {match_dir}: {e}")
                continue
        
        return match_list
    
    def analyze_match(self, match_folder: str) -> bool:
        """
        Analyze a specific match
        """
        match_path = self.veo_games_dir / match_folder
        
        if not match_path.exists():
            logger.error(f"Match folder not found: {match_folder}")
            return False
        
        if not (match_path / "match_info.json").exists():
            logger.error(f"match_info.json not found in {match_folder}")
            return False
        
        try:
            analyzer = VeoMatchAnalyzer(str(match_path))
            return analyzer.run_full_pipeline()
        except Exception as e:
            logger.error(f"Error analyzing match {match_folder}: {e}")
            return False
    
    def analyze_all_matches(self) -> Dict[str, bool]:
        """
        Analyze all discovered matches
        """
        results = {}
        
        for match_dir in self.matches:
            match_name = match_dir.name
            logger.info(f"Starting analysis for {match_name}")
            
            results[match_name] = self.analyze_match(match_name)
            
            if results[match_name]:
                logger.info(f"✅ Completed: {match_name}")
            else:
                logger.error(f"❌ Failed: {match_name}")
        
        return results
    
    def create_new_match(self, veo_url: str, match_name: str = None) -> str:
        """
        Create a new match folder structure from a Veo URL
        """
        # Extract match ID from URL
        url_parts = veo_url.split('/')
        match_id = None
        
        for part in url_parts:
            if '-' in part and len(part) > 10:  # Basic heuristic for match ID
                match_id = part
                break
        
        if not match_id:
            logger.error(f"Could not extract match ID from URL: {veo_url}")
            return None
        
        # Create folder name
        folder_name = match_id.replace('/', '-')
        match_folder = self.veo_games_dir / folder_name
        
        # Create directory structure
        try:
            match_folder.mkdir(exist_ok=True)
            (match_folder / "raw_video").mkdir(exist_ok=True)
            (match_folder / "clips").mkdir(exist_ok=True)
            (match_folder / "analysis").mkdir(exist_ok=True)
            (match_folder / "synthesis").mkdir(exist_ok=True)
            
            # Create match_info.json
            if not match_name:
                match_name = f"Match {match_id}"
            
            match_info = {
                "match_id": match_id,
                "match_name": match_name,
                "date": datetime.now().strftime("%Y-%m-%d"),
                "veo_url": veo_url,
                "teams": {
                    "home": "TBD",
                    "away": "TBD"
                },
                "status": "pending_download",
                "created_at": datetime.now().isoformat(),
                "analysis_pipeline": {
                    "download_completed": False,
                    "clips_processed": False,
                    "events_analyzed": False,
                    "synthesis_completed": False
                },
                "files": {
                    "raw_video": None,
                    "clips_count": 0,
                    "analysis_files": [],
                    "synthesis_files": []
                }
            }
            
            with open(match_folder / "match_info.json", 'w') as f:
                json.dump(match_info, f, indent=2)
            
            logger.info(f"Created new match folder: {folder_name}")
            return folder_name
            
        except Exception as e:
            logger.error(f"Error creating match folder: {e}")
            return None
    
    def print_status_report(self):
        """
        Print a comprehensive status report of all matches
        """
        matches = self.list_matches()
        
        print("\n" + "="*80)
        print("🎯 VEO MATCHES STATUS REPORT")
        print("="*80)
        
        if not matches:
            print("No matches found.")
            return
        
        for match in matches:
            print(f"\n📁 {match['folder']}")
            print(f"   Name: {match['match_name']}")
            print(f"   Date: {match['date']}")
            print(f"   Status: {match['status']}")
            
            pipeline = match['pipeline_status']
            steps = [
                ("Download", pipeline.get('download_completed', False)),
                ("Clips", pipeline.get('clips_processed', False)),
                ("Events", pipeline.get('events_analyzed', False)),
                ("Synthesis", pipeline.get('synthesis_completed', False))
            ]
            
            status_line = "   Pipeline: "
            for step_name, completed in steps:
                status_line += f"{step_name}:{'✅' if completed else '❌'} "
            
            print(status_line)
        
        print("\n" + "="*80)


def main():
    parser = argparse.ArgumentParser(description="Veo Pipeline Manager")
    parser.add_argument("command", choices=["list", "analyze", "analyze-all", "create", "status"],
                       help="Command to execute")
    parser.add_argument("--match", help="Match folder name (for analyze command)")
    parser.add_argument("--url", help="Veo URL (for create command)")
    parser.add_argument("--name", help="Match name (for create command)")
    
    args = parser.parse_args()
    
    pipeline = VeoPipeline()
    
    if args.command == "list":
        matches = pipeline.list_matches()
        print(json.dumps(matches, indent=2))
    
    elif args.command == "analyze":
        if not args.match:
            print("Error: --match required for analyze command")
            sys.exit(1)
        
        success = pipeline.analyze_match(args.match)
        sys.exit(0 if success else 1)
    
    elif args.command == "analyze-all":
        results = pipeline.analyze_all_matches()
        failed = [name for name, success in results.items() if not success]
        
        if failed:
            print(f"Failed matches: {failed}")
            sys.exit(1)
        else:
            print("All matches analyzed successfully!")
    
    elif args.command == "create":
        if not args.url:
            print("Error: --url required for create command")
            sys.exit(1)
        
        folder_name = pipeline.create_new_match(args.url, args.name)
        if folder_name:
            print(f"Created match folder: {folder_name}")
        else:
            sys.exit(1)
    
    elif args.command == "status":
        pipeline.print_status_report()


if __name__ == "__main__":
    main() 
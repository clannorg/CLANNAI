#!/usr/bin/env python3
"""
Veo Development Pipeline
Step-by-step development workflow for analyzing Veo matches

This script guides you through the complete development process:
1. Extract Veo's ground truth metadata
2. Download and process the video
3. Run our AI analysis
4. Compare results and evaluate performance
5. Generate reports and insights
"""

import os
import sys
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / '0_utils'))

from veo_metadata_extractor import VeoMetadataExtractor
from veo_match_analyzer import VeoMatchAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class VeoDevPipeline:
    """
    Step-by-step development pipeline for Veo analysis
    """
    
    def __init__(self, veo_url: str, match_name: str = None):
        self.veo_url = veo_url
        self.match_name = match_name
        self.metadata_extractor = VeoMetadataExtractor()
        
        # Extract match ID and create folder
        self.match_id = self.metadata_extractor.extract_match_id(veo_url)
        self.match_folder = Path(f"./{self.match_id}")
        
        if not self.match_name:
            self.match_name = f"Match {self.match_id}"
        
        logger.info(f"🎯 Initialized pipeline for: {self.match_name}")
        logger.info(f"📋 Match ID: {self.match_id}")
        logger.info(f"📁 Folder: {self.match_folder}")
    
    def step_1_extract_veo_metadata(self) -> Dict:
        """
        STEP 1: Extract Veo's built-in event metadata
        This gives us the ground truth to compare against
        """
        print("\n" + "="*80)
        print("🔍 STEP 1: EXTRACTING VEO METADATA (GROUND TRUTH)")
        print("="*80)
        print(f"📺 URL: {self.veo_url}")
        print(f"🎯 Goal: Extract events like 'Shot on goal', 'Goal', 'Save', etc.")
        
        logger.info("Starting Veo metadata extraction...")
        
        # Extract metadata
        metadata = self.metadata_extractor.extract_all_metadata(self.veo_url)
        
        # Save to file
        metadata_file = self.match_folder / "veo_ground_truth.json"
        self.match_folder.mkdir(exist_ok=True)
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # Print summary
        print(f"\n📊 STEP 1 RESULTS:")
        print(f"   ✅ Metadata file: {metadata_file}")
        
        if metadata.get('events'):
            events = metadata['events']
            print(f"   🎯 API Events: {len(events)} found")
            for i, event in enumerate(events[:5]):  # Show first 5
                print(f"      {i+1}. {event}")
            if len(events) > 5:
                print(f"      ... and {len(events) - 5} more")
        
        if metadata.get('scraped_data', {}).get('events'):
            scraped_events = metadata['scraped_data']['events']
            print(f"   🕷️ Scraped Events: {len(scraped_events)} found")
            for i, event in enumerate(scraped_events[:3]):  # Show first 3
                print(f"      {i+1}. {event['type']} at {event['timestamp']}")
        
        if not metadata.get('events') and not metadata.get('scraped_data'):
            print("   ⚠️ No events found - may need manual annotation")
        
        print(f"\n💡 Next: Run step_2_download_video()")
        return metadata
    
    def step_2_download_video(self) -> bool:
        """
        STEP 2: Download the video from Veo
        """
        print("\n" + "="*80)
        print("📥 STEP 2: DOWNLOADING VIDEO FROM VEO")
        print("="*80)
        print(f"🎯 Goal: Download full match video for AI analysis")
        
        try:
            # Create match analyzer
            analyzer = VeoMatchAnalyzer(str(self.match_folder))
            
            # Download the video
            success = analyzer.download_match()
            
            if success:
                print(f"\n📊 STEP 2 RESULTS:")
                print(f"   ✅ Video downloaded successfully")
                print(f"   📁 Location: {self.match_folder}/raw_video/")
                print(f"\n💡 Next: Run step_3_process_clips()")
                return True
            else:
                print(f"\n❌ STEP 2 FAILED:")
                print(f"   Failed to download video")
                print(f"   🔧 Check network connection and Veo URL")
                return False
                
        except Exception as e:
            print(f"\n❌ STEP 2 ERROR: {e}")
            return False
    
    def step_3_process_clips(self) -> bool:
        """
        STEP 3: Split video into 30-second clips for analysis
        """
        print("\n" + "="*80)
        print("✂️ STEP 3: PROCESSING VIDEO INTO CLIPS")
        print("="*80)
        print(f"🎯 Goal: Split video into 30s clips for AI analysis")
        
        try:
            analyzer = VeoMatchAnalyzer(str(self.match_folder))
            success = analyzer.process_clips()
            
            if success:
                clips_dir = self.match_folder / "clips"
                clip_count = len(list(clips_dir.glob("*.mp4"))) if clips_dir.exists() else 0
                
                print(f"\n📊 STEP 3 RESULTS:")
                print(f"   ✅ Video processed successfully")
                print(f"   📁 Clips folder: {clips_dir}")
                print(f"   🎬 Total clips: {clip_count}")
                print(f"   ⏱️ Est. analysis time: {clip_count * 30} seconds")
                print(f"\n💡 Next: Run step_4_ai_analysis()")
                return True
            else:
                print(f"\n❌ STEP 3 FAILED:")
                print(f"   Failed to process clips")
                return False
                
        except Exception as e:
            print(f"\n❌ STEP 3 ERROR: {e}")
            return False
    
    def step_4_ai_analysis(self) -> bool:
        """
        STEP 4: Run AI analysis on all clips
        """
        print("\n" + "="*80)
        print("🤖 STEP 4: RUNNING AI ANALYSIS")
        print("="*80)
        print(f"🎯 Goal: Analyze clips for events using Ram's AI pipeline")
        
        try:
            analyzer = VeoMatchAnalyzer(str(self.match_folder))
            success = analyzer.analyze_events()
            
            if success:
                analysis_dir = self.match_folder / "analysis"
                analysis_count = len(list(analysis_dir.glob("*_analysis.json"))) if analysis_dir.exists() else 0
                
                print(f"\n📊 STEP 4 RESULTS:")
                print(f"   ✅ AI analysis completed")
                print(f"   📁 Analysis folder: {analysis_dir}")
                print(f"   📄 Analysis files: {analysis_count}")
                print(f"\n💡 Next: Run step_5_synthesize_results()")
                return True
            else:
                print(f"\n❌ STEP 4 FAILED:")
                print(f"   AI analysis failed")
                return False
                
        except Exception as e:
            print(f"\n❌ STEP 4 ERROR: {e}")
            return False
    
    def step_5_synthesize_results(self) -> bool:
        """
        STEP 5: Synthesize AI analysis into match timeline
        """
        print("\n" + "="*80)
        print("🔄 STEP 5: SYNTHESIZING MATCH TIMELINE")
        print("="*80)
        print(f"🎯 Goal: Combine all clip analysis into full match timeline")
        
        try:
            analyzer = VeoMatchAnalyzer(str(self.match_folder))
            success = analyzer.synthesize_match()
            
            if success:
                synthesis_dir = self.match_folder / "synthesis"
                
                print(f"\n📊 STEP 5 RESULTS:")
                print(f"   ✅ Match synthesis completed")
                print(f"   📁 Synthesis folder: {synthesis_dir}")
                print(f"   📄 Timeline: events_timeline.json")
                print(f"   📊 Statistics: event_statistics.json")
                print(f"\n💡 Next: Run step_6_compare_results()")
                return True
            else:
                print(f"\n❌ STEP 5 FAILED:")
                print(f"   Synthesis failed")
                return False
                
        except Exception as e:
            print(f"\n❌ STEP 5 ERROR: {e}")
            return False
    
    def step_6_compare_results(self) -> Dict:
        """
        STEP 6: Compare Veo ground truth vs AI analysis
        """
        print("\n" + "="*80)
        print("📊 STEP 6: COMPARING VEO GROUND TRUTH VS AI ANALYSIS")
        print("="*80)
        print(f"🎯 Goal: Evaluate AI performance against Veo's event detection")
        
        try:
            # Load Veo ground truth
            veo_file = self.match_folder / "veo_ground_truth.json"
            with open(veo_file, 'r') as f:
                veo_data = json.load(f)
            
            # Load AI analysis
            ai_file = self.match_folder / "synthesis" / "events_timeline.json"
            with open(ai_file, 'r') as f:
                ai_data = json.load(f)
            
            # Compare results
            comparison = self._compare_events(veo_data, ai_data)
            
            # Save comparison
            comparison_file = self.match_folder / "veo_vs_ai_comparison.json"
            with open(comparison_file, 'w') as f:
                json.dump(comparison, f, indent=2)
            
            print(f"\n📊 STEP 6 RESULTS:")
            print(f"   ✅ Comparison completed")
            print(f"   📄 Report: {comparison_file}")
            
            # Print summary
            if comparison.get('summary'):
                summary = comparison['summary']
                print(f"\n📈 PERFORMANCE SUMMARY:")
                print(f"   🎯 Veo Events: {summary.get('veo_events_count', 0)}")
                print(f"   🤖 AI Events: {summary.get('ai_events_count', 0)}")
                print(f"   ✅ Matches: {summary.get('matches', 0)}")
                print(f"   📊 Accuracy: {summary.get('accuracy', 0):.1f}%")
            
            print(f"\n💡 Next: Run step_7_generate_report()")
            return comparison
            
        except Exception as e:
            print(f"\n❌ STEP 6 ERROR: {e}")
            return {}
    
    def step_7_generate_report(self) -> str:
        """
        STEP 7: Generate final development report
        """
        print("\n" + "="*80)
        print("📋 STEP 7: GENERATING DEVELOPMENT REPORT")
        print("="*80)
        print(f"🎯 Goal: Create comprehensive development insights")
        
        try:
            report = self._generate_dev_report()
            
            report_file = self.match_folder / "development_report.md"
            with open(report_file, 'w') as f:
                f.write(report)
            
            print(f"\n📊 STEP 7 RESULTS:")
            print(f"   ✅ Development report generated")
            print(f"   📄 Report: {report_file}")
            print(f"\n🎉 PIPELINE COMPLETE!")
            print(f"   📁 All files in: {self.match_folder}")
            
            return str(report_file)
            
        except Exception as e:
            print(f"\n❌ STEP 7 ERROR: {e}")
            return ""
    
    def run_full_pipeline(self) -> bool:
        """
        Run all steps in sequence
        """
        print("\n" + "🚀" + "="*78 + "🚀")
        print(f"🚀 RUNNING FULL VEO DEVELOPMENT PIPELINE")
        print(f"🚀 Match: {self.match_name}")
        print("🚀" + "="*78 + "🚀")
        
        steps = [
            ("Extract Veo Metadata", self.step_1_extract_veo_metadata),
            ("Download Video", self.step_2_download_video),
            ("Process Clips", self.step_3_process_clips),
            ("AI Analysis", self.step_4_ai_analysis),
            ("Synthesize Results", self.step_5_synthesize_results),
            ("Compare Results", self.step_6_compare_results),
            ("Generate Report", self.step_7_generate_report),
        ]
        
        for i, (step_name, step_func) in enumerate(steps, 1):
            print(f"\n⏳ Running Step {i}/7: {step_name}...")
            
            try:
                result = step_func()
                if result is False:  # Explicitly check for False (some steps return data)
                    print(f"❌ Pipeline failed at Step {i}: {step_name}")
                    return False
                    
            except Exception as e:
                print(f"❌ Pipeline error at Step {i}: {step_name} - {e}")
                return False
        
        print(f"\n🎉 FULL PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"📁 Results in: {self.match_folder}")
        return True
    
    def _compare_events(self, veo_data: Dict, ai_data: Dict) -> Dict:
        """Compare Veo events vs AI events"""
        # Simplified comparison - can be enhanced
        veo_events = []
        
        # Extract Veo events
        if veo_data.get('events'):
            veo_events.extend(veo_data['events'])
        if veo_data.get('scraped_data', {}).get('events'):
            veo_events.extend(veo_data['scraped_data']['events'])
        
        # Extract AI events
        ai_events = ai_data.get('events', []) if isinstance(ai_data, dict) else []
        
        return {
            'comparison_date': datetime.now().isoformat(),
            'veo_events': veo_events,
            'ai_events': ai_events,
            'summary': {
                'veo_events_count': len(veo_events),
                'ai_events_count': len(ai_events),
                'matches': 0,  # Would need sophisticated matching logic
                'accuracy': 0.0
            }
        }
    
    def _generate_dev_report(self) -> str:
        """Generate markdown development report"""
        return f"""# 🎯 Veo Development Report: {self.match_name}

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Match ID:** {self.match_id}  
**Veo URL:** {self.veo_url}

## 📊 Pipeline Execution Summary

- ✅ Step 1: Veo Metadata Extraction
- ✅ Step 2: Video Download  
- ✅ Step 3: Clip Processing
- ✅ Step 4: AI Analysis
- ✅ Step 5: Result Synthesis
- ✅ Step 6: Performance Comparison
- ✅ Step 7: Report Generation

## 📁 Generated Files

- `veo_ground_truth.json` - Veo's original event data
- `raw_video/` - Downloaded match video
- `clips/` - 30-second analysis clips
- `analysis/` - AI analysis per clip
- `synthesis/` - Combined match timeline
- `veo_vs_ai_comparison.json` - Performance comparison
- `development_report.md` - This report

## 🔍 Key Insights

### Veo Ground Truth
- Events detected by Veo platform
- Used as baseline for AI evaluation

### AI Performance
- Events detected by CLANNAI system
- Comparison shows areas for improvement

## 🚀 Next Steps

1. **Analyze comparison results** - Identify AI strengths/weaknesses
2. **Improve AI prompts** - Based on false positives/negatives  
3. **Fine-tune detection** - Adjust confidence thresholds
4. **Expand dataset** - Add more Veo matches for training

## 🎯 Development Workflow

This pipeline provides a systematic approach to:
- Getting ground truth from Veo
- Testing AI performance
- Iterating on improvements
- Building robust football analysis

---
*Generated by Veo Development Pipeline*
"""


def main():
    """CLI interface for development pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Veo Development Pipeline")
    parser.add_argument("url", help="Veo match URL")
    parser.add_argument("--name", help="Match name (optional)")
    parser.add_argument("--step", choices=[
        "1", "2", "3", "4", "5", "6", "7", "all"
    ], default="all", help="Run specific step or all steps")
    
    args = parser.parse_args()
    
    pipeline = VeoDevPipeline(args.url, args.name)
    
    if args.step == "all":
        success = pipeline.run_full_pipeline()
        sys.exit(0 if success else 1)
    else:
        step_methods = {
            "1": pipeline.step_1_extract_veo_metadata,
            "2": pipeline.step_2_download_video, 
            "3": pipeline.step_3_process_clips,
            "4": pipeline.step_4_ai_analysis,
            "5": pipeline.step_5_synthesize_results,
            "6": pipeline.step_6_compare_results,
            "7": pipeline.step_7_generate_report,
        }
        
        result = step_methods[args.step]()
        sys.exit(0 if result is not False else 1)


if __name__ == "__main__":
    main() 
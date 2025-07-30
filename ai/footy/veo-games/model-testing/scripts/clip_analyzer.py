#!/usr/bin/env python3
"""
Model Clip Analyzer
Analyzes 80 clips in parallel using specified Gemini model
Based on 3_generate_clips.py structure
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ModelClipAnalyzer:
    def __init__(self, model_name):
        """Initialize with specified Gemini model"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self.model = genai.GenerativeModel(model_name)
        
    def get_football_analysis_prompt(self):
        """Get simplified prompt for concise match description"""
        return """🏟️ FOOTBALL MATCH CLIP ANALYSIS

Describe what happens in this 15-second football clip in 1-2 short sentences.

🎯 FOCUS ON:
- What are both teams doing?
- Ball possession and movement
- Key actions (passes, tackles, shots, saves)
- Player positions (attacking, defending, midfield)

⚡ BE CONCISE:
Just describe the main action happening.

Examples:
"Red team attacks down the left wing, cross is headed away by blue defender"
"Blue goalkeeper kicks ball long to midfield, players compete for possession"
"Red player shoots from outside penalty area, ball goes wide of goal"
"Corner kick taken by blue team, ball cleared by red team defense"
"Both teams battle for possession in midfield, play moves left to right"

Focus on the most significant action in the 15 seconds."""

    def analyze_single_clip(self, clip_path, clip_info):
        """Analyze a single clip with the model"""
        try:
            start_time = time.time()
            
            # Upload video file
            video_file = genai.upload_file(path=str(clip_path))
            
            # Wait for processing
            while video_file.state.name == "PROCESSING":
                time.sleep(0.5)
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                raise Exception(f"Video processing failed for {clip_path.name}")
            
            # Generate analysis
            prompt = self.get_football_analysis_prompt()
            response = self.model.generate_content([video_file, prompt])
            
            # Clean up
            genai.delete_file(video_file.name)
            
            processing_time = time.time() - start_time
            
            return {
                "clip_filename": clip_info['filename'],
                "start_seconds": clip_info['start_seconds'],
                "timestamp": clip_info['timestamp'],
                "model": self.model_name,
                "analysis_timestamp": datetime.now().isoformat(),
                "events_analysis": response.text.strip(),
                "processing_time_seconds": processing_time,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "clip_filename": clip_info['filename'],
                "start_seconds": clip_info['start_seconds'],
                "timestamp": clip_info['timestamp'],
                "model": self.model_name,
                "analysis_timestamp": datetime.now().isoformat(),
                "events_analysis": f"Error: {str(e)}",
                "processing_time_seconds": 0,
                "status": "error"
            }

def load_target_clips(match_id):
    """Load the 80 target clips from configs"""
    config_dir = Path("../configs")
    clip_list_path = config_dir / "clip_list.txt"
    
    if not clip_list_path.exists():
        raise FileNotFoundError(f"Clip list not found: {clip_list_path}")
    
    # Load clip filenames
    with open(clip_list_path, 'r') as f:
        clip_filenames = [line.strip() for line in f if line.strip()]
    
    # Load segments metadata to get timing info
    data_dir = Path("../../data") / match_id
    segments_path = data_dir / "clips" / "segments.json"
    
    if not segments_path.exists():
        raise FileNotFoundError(f"Segments metadata not found: {segments_path}")
    
    with open(segments_path, 'r') as f:
        segments_data = json.load(f)
    
    # Match clip filenames with metadata
    target_clips = []
    for clip_filename in clip_filenames:
        # Find matching metadata
        for clip_info in segments_data['clips']:
            if clip_info['filename'] == clip_filename:
                target_clips.append(clip_info)
                break
    
    return target_clips

def analyze_clips_parallel(model_name, match_id):
    """Analyze clips in parallel using specified model"""
    print(f"🤖 Model Clip Analysis: {model_name}")
    print(f"📊 Match: {match_id}")
    print("=" * 60)
    
    # Load target clips
    try:
        target_clips = load_target_clips(match_id)
        print(f"📋 Loaded {len(target_clips)} target clips for analysis")
    except Exception as e:
        print(f"❌ Error loading clips: {e}")
        return False
    
    # Setup directories
    results_dir = Path("../results") / match_id / model_name
    analyses_dir = results_dir / "clip_analyses"
    analyses_dir.mkdir(parents=True, exist_ok=True)
    
    clips_dir = Path("../../data") / match_id / "clips"
    
    # Initialize analyzer
    try:
        analyzer = ModelClipAnalyzer(model_name)
        print(f"✅ Initialized {model_name} analyzer")
    except Exception as e:
        print(f"❌ Failed to initialize analyzer: {e}")
        return False
    
    successful_analyses = 0
    failed_analyses = 0
    total_processing_time = 0
    analysis_start_time = time.time()
    
    def process_single_clip(clip_info):
        """Process a single clip analysis"""
        clip_filename = clip_info['filename']
        clip_path = clips_dir / clip_filename
        
        # Check if analysis already exists
        analysis_filename = clip_filename.replace('.mp4', '_analysis.json')
        analysis_path = analyses_dir / analysis_filename
        
        if analysis_path.exists():
            return f"♻️  Already analyzed: {clip_filename}", True, 0
        
        # Check if clip exists
        if not clip_path.exists():
            return f"❌ Clip not found: {clip_filename}", False, 0
        
        # Analyze the clip
        result = analyzer.analyze_single_clip(clip_path, clip_info)
        
        # Save analysis
        with open(analysis_path, 'w') as f:
            json.dump(result, f, indent=2)
        
        if result['status'] == 'success':
            return f"✅ Analyzed: {clip_filename} ({result['processing_time_seconds']:.1f}s)", True, result['processing_time_seconds']
        else:
            return f"❌ Failed: {clip_filename} - {result['events_analysis'][:50]}...", False, 0
    
    print("🚀 Starting MASSIVE parallel analysis (60 threads)")
    print("⚠️  Rate limiting: No delays - full API concurrency")
    
    # Process ALL clips simultaneously with massive parallelization
    batch_size = len(target_clips)  # All clips in one batch
    num_batches = 1
    
    print(f"\n🔄 MASSIVE Batch 1/1 - All {len(target_clips)} clips simultaneously")
    
    with ThreadPoolExecutor(max_workers=60) as executor:
        # Submit ALL clips simultaneously 
        future_to_clip = {executor.submit(process_single_clip, clip_info): clip_info for clip_info in target_clips}
        
        # Process results as they complete
        for future in as_completed(future_to_clip):
            clip_info = future_to_clip[future]
            try:
                result_message, success, processing_time = future.result()
                print(f"  {result_message}")
                
                if success:
                    successful_analyses += 1
                    total_processing_time += processing_time
                else:
                    failed_analyses += 1
                    
            except Exception as e:
                print(f"  ❌ Error analyzing {clip_info['filename']}: {e}")
                failed_analyses += 1
        
        # No rate limiting needed - single massive batch!
    
    total_time = time.time() - analysis_start_time
    
    # Generate metadata
    metadata = {
        "model_name": model_name,
        "match_id": match_id,
        "analysis_timestamp": datetime.now().isoformat(),
        "clips_analyzed": len(target_clips),
        "successful_analyses": successful_analyses,
        "failed_analyses": failed_analyses,
        "success_rate_percent": (successful_analyses / len(target_clips)) * 100,
        "total_analysis_time_seconds": total_time,
        "total_processing_time_seconds": total_processing_time,
        "avg_processing_time_seconds": total_processing_time / successful_analyses if successful_analyses > 0 else 0,
        "analysis_rate_clips_per_second": len(target_clips) / total_time
    }
    
    # Save metadata
    with open(results_dir / "batch_metadata.json", 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print("\n🏁 CLIP ANALYSIS COMPLETE!")
    print("=" * 50)
    print(f"🤖 Model: {model_name}")
    print(f"✅ Successful: {successful_analyses}/{len(target_clips)} clips")
    print(f"❌ Failed: {failed_analyses} clips")
    print(f"📊 Success rate: {metadata['success_rate_percent']:.1f}%")
    print(f"⏱️  Total time: {total_time:.1f} seconds")
    print(f"🚀 Average speed: {metadata['analysis_rate_clips_per_second']:.2f} clips/second")
    print(f"📁 Results saved to: {results_dir}")
    
    return successful_analyses > 0

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clip_analyzer.py <model-name> <match-id>")
        print("Example: python clip_analyzer.py gemini-2.5-flash ballyclare-20250111")
        print("\nAvailable models:")
        print("  - gemini-2.5-flash")
        print("  - gemini-2.5-pro") 
        print("  - gemini-2.0-flash")
        print("  - gemini-1.5-pro")
        print("  - gemini-1.5-flash")
        sys.exit(1)
    
    model_name = sys.argv[1]
    match_id = sys.argv[2]
    
    success = analyze_clips_parallel(model_name, match_id)
    
    if success:
        print(f"\n🎯 Ready for synthesis: python synthesis.py {model_name} {match_id}")
    else:
        sys.exit(1) 
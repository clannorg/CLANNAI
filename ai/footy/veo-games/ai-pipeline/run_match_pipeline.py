#!/usr/bin/env python3
"""
Run Match Pipeline
Orchestrates all 8 steps for complete match analysis with optimized processing
"""

import sys
import subprocess
import json
import re
from pathlib import Path

def run_pipeline(veo_url):
    """Run complete pipeline for a Veo match URL"""
    print(f"🚀 Starting Complete Veo Analysis Pipeline")
    print(f"📋 URL: {veo_url}")
    print("=" * 60)
    
    steps = [
        ("1_extract_veo_data.py", f"Extract Veo ground truth", [veo_url]),
        ("2_download_video.py", f"Download match video", [veo_url]),
        ("3_generate_clips.py", f"Generate 15-second clips", ["MATCH_ID"]),
        ("3.5_compress_clips.py", f"Compress clips for API", ["MATCH_ID"]),
        ("4_gemini_clip_analyzer.py", f"Gemini clip analysis", ["MATCH_ID"]),
        ("5_gemini_synthesis.py", f"Synthesize match timeline", ["MATCH_ID"]),
        ("6_web_formatter.py", f"Format for website", ["MATCH_ID"]),
        ("7_accuracy_evaluator.py", f"AI vs Veo evaluation", ["MATCH_ID"])
    ]
    
    match_id = None
    successful_steps = 0
    
    for step_num, (step_file, step_name, args) in enumerate(steps, 1):
        print(f"\n📍 Step {step_num}/{len(steps)}: {step_name}...")
        
        # Replace MATCH_ID placeholder with actual match_id
        if "MATCH_ID" in args:
            if not match_id:
                print("❌ Match ID not available from previous steps")
                return False, successful_steps
            args = [match_id if arg == "MATCH_ID" else arg for arg in args]
        
        try:
            # Run the step
            result = subprocess.run([
                "python", step_file
            ] + args, check=True, capture_output=True, text=True, cwd=Path(__file__).parent)
            
            # Print step output
            if result.stdout:
                print(result.stdout)
            
            # Extract match_id from step 1 output (improved extraction)
            if step_file == "1_extract_veo_data.py" and not match_id:
                # Try multiple patterns to extract match_id
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    # Look for various match ID patterns
                    match_patterns = [
                        r"Match ID:\s*([^\s]+)",
                        r"match[_-]?id[:\s=]+([^\s]+)",
                        r"Saved to.*?([a-zA-Z0-9\-_]+)/?$"
                    ]
                    for pattern in match_patterns:
                        match = re.search(pattern, line, re.IGNORECASE)
                        if match:
                            match_id = match.group(1).strip('/')
                            print(f"📝 Extracted Match ID: {match_id}")
                            break
                    if match_id:
                        break
                
                # Fallback: try to extract from data directory
                if not match_id:
                    data_dir = Path("../data")
                    if data_dir.exists():
                        dirs = [d for d in data_dir.iterdir() if d.is_dir()]
                        if dirs:
                            # Get the most recently created directory
                            match_id = max(dirs, key=lambda d: d.stat().st_mtime).name
                            print(f"📝 Fallback Match ID from data dir: {match_id}")
            
            # Show warnings if any
            if result.stderr:
                print(f"⚠️  Warnings: {result.stderr}")
            
            successful_steps += 1
            print(f"✅ Step {step_num} complete: {step_name}")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Step {step_num} failed: {step_name}")
            if e.stdout:
                print(f"Output: {e.stdout}")
            if e.stderr:
                print(f"Error: {e.stderr}")
            return False, successful_steps
        except FileNotFoundError:
            print(f"❌ Script not found: {step_file}")
            print(f"   Make sure the script exists in the ai-pipeline directory")
            return False, successful_steps
        except Exception as e:
            print(f"❌ Unexpected error in step {step_num}: {e}")
            return False, successful_steps
    
    print("\n" + "=" * 60)
    print(f"🎉 Complete Pipeline Success!")
    print(f"✅ All {len(steps)} steps completed successfully")
    
    if match_id:
        data_dir = Path("../data") / match_id
        print(f"📁 All results saved to: {data_dir}")
        
        # Show output files
        output_files = {
            "veo_ground_truth.json": "Veo events (ground truth)",
            "video.mp4": "Full match video",
            "clips/segments.json": "Video clips metadata",
            "compressed_clips/compression_info.json": "Compression statistics",
            "clip_analyses/": "Individual clip analyses",
            "match_timeline.json": "Synthesized match timeline",
            "web_format.json": "Website JSON",
            "accuracy_evaluation.json": "AI vs Veo accuracy report"
        }
        
        print(f"\n📊 Output Files:")
        for filename, description in output_files.items():
            file_path = data_dir / filename
            if file_path.exists():
                if file_path.is_file():
                    size_kb = file_path.stat().st_size / 1024
                    print(f"   ✅ {filename} ({size_kb:.1f}KB) - {description}")
                else:
                    # Directory
                    num_files = len(list(file_path.glob('*'))) if file_path.is_dir() else 0
                    print(f"   ✅ {filename} ({num_files} files) - {description}")
            else:
                print(f"   ❌ {filename} - {description} (missing)")
        
        print(f"\n🌐 Key outputs:")
        print(f"   📈 Website JSON: {data_dir}/web_format.json")
        print(f"   ⚖️  Accuracy report: {data_dir}/accuracy_evaluation.json")
        
        # Show processing statistics if available
        compression_file = data_dir / "compressed_clips" / "compression_info.json"
        if compression_file.exists():
            try:
                with open(compression_file, 'r') as f:
                    compression_stats = json.load(f)
                print(f"\n📊 Processing Statistics:")
                stats = compression_stats.get('compression_stats', {})
                print(f"   🗜️  Compression: {stats.get('overall_compression_ratio', 0):.1f}% size reduction")
                print(f"   ⚡ Speed: {stats.get('compression_speed_clips_per_second', 0):.1f} clips/second")
            except:
                pass
    
    return True, successful_steps

def validate_veo_url(url):
    """Validate Veo URL format"""
    if not url or not isinstance(url, str):
        return False, "URL must be a string"
    
    if "veo.co/matches/" not in url:
        return False, "Invalid Veo URL format. Expected: https://app.veo.co/matches/match-id/"
    
    # Extract match ID for basic validation
    try:
        match_id_part = url.split("veo.co/matches/")[1].rstrip('/')
        if not match_id_part or len(match_id_part) < 5:
            return False, "Match ID appears to be too short or invalid"
    except IndexError:
        return False, "Could not extract match ID from URL"
    
    return True, "Valid Veo URL"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("🏈 Veo Games - AI Football Analysis Pipeline")
        print("=" * 50)
        print("Usage: python run_match_pipeline.py <veo-url>")
        print()
        print("Example:")
        print("  python run_match_pipeline.py 'https://app.veo.co/matches/20250111-ballyclare-425e4c3f/'")
        print()
        print("Pipeline Steps:")
        print("  1. Extract Veo ground truth")
        print("  2. Download match video")
        print("  3. Generate 15-second clips")
        print("  3.5. Compress clips for API")
        print("  4. Gemini clip analysis")
        print("  5. Synthesize match timeline")
        print("  6. Format for website")
        print("  7. AI vs Veo evaluation")
        sys.exit(1)
    
    veo_url = sys.argv[1]
    
    # Validate URL
    is_valid, message = validate_veo_url(veo_url)
    if not is_valid:
        print(f"❌ {message}")
        print("Expected format: https://app.veo.co/matches/match-id/")
        sys.exit(1)
    
    print(f"✅ Valid Veo URL: {message}")
    
    # Run pipeline
    success, completed_steps = run_pipeline(veo_url)
    
    if success:
        print(f"\n🎯 Pipeline completed successfully!")
        print(f"   All {completed_steps} steps executed")
        print(f"   Ready for website integration")
    else:
        print(f"\n❌ Pipeline failed after {completed_steps} steps")
        print(f"   Check logs above for error details")
        print(f"   You can resume from the failed step if needed")
        sys.exit(1) 
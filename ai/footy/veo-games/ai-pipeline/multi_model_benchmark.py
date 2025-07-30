#!/usr/bin/env python3
"""
Multi-Model Benchmark for Football Analysis
Test multiple Gemini models against Veo ground truth to find the best performer
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics

# Load environment variables
load_dotenv()

class FootballModelBenchmark:
    def __init__(self):
        """Initialize with multiple Gemini models for benchmarking"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        
        # Models to benchmark
        self.models_to_test = {
            'gemini-2.5-flash': 'Latest stable model',
            'gemini-2.5-pro': 'Most powerful model', 
            'gemini-2.0-flash': 'Current stable 2.0',
            'gemini-1.5-pro': 'Proven reliable',
            'gemini-1.5-flash': 'Fast and efficient'
        }
        
        self.results = {}
        
    def get_football_analysis_prompt(self, compressed_clip_path: str) -> str:
        """Get standardized prompt for football analysis"""
        return f"""
🏟️ FOOTBALL MATCH ANALYSIS

Analyze this 15-second football clip and identify key events.

🎯 WHAT TO DETECT:
- GOALS: Any ball crossing the goal line
- SHOTS: Any attempt at goal (on target, off target, blocked)
- SAVES: Goalkeeper stopping shots
- FOULS: Rule violations, yellow/red cards
- SET PIECES: Free kicks, corners, throw-ins
- KICKOFFS: Center circle restarts

⚡ RESPONSE FORMAT (be concise):
Just describe what you see happening in 1-2 sentences.

Examples:
"Shot by red team from penalty area - saved by goalkeeper"
"Goal scored by blue team - ball crosses line after header"
"Free kick taken by red team - ball goes wide"
"Goalkeeper kicks ball from penalty area"

Focus on the most significant event in the clip.
"""

    def analyze_clip_with_model(self, model_name: str, compressed_clip_path: str, clip_info: dict) -> dict:
        """Analyze a single clip with specified model"""
        try:
            model = genai.GenerativeModel(model_name)
            prompt = self.get_football_analysis_prompt(compressed_clip_path)
            
            # Upload video file
            start_time = time.time()
            video_file = genai.upload_file(path=compressed_clip_path)
            
            # Wait for processing
            while video_file.state.name == "PROCESSING":
                time.sleep(0.5)
                video_file = genai.get_file(video_file.name)
            
            if video_file.state.name == "FAILED":
                raise Exception(f"Video processing failed for {compressed_clip_path}")
            
            # Generate analysis
            response = model.generate_content([video_file, prompt])
            api_time = time.time() - start_time
            
            # Clean up
            genai.delete_file(video_file.name)
            
            return {
                "clip_filename": clip_info['clip_filename'],
                "start_seconds": clip_info['start_seconds'],
                "timestamp": clip_info['timestamp'],
                "model": model_name,
                "analysis_timestamp": datetime.now().isoformat(),
                "events_analysis": response.text.strip(),
                "processing_time": api_time,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "clip_filename": clip_info['clip_filename'],
                "start_seconds": clip_info['start_seconds'],
                "timestamp": clip_info['timestamp'],
                "model": model_name,
                "analysis_timestamp": datetime.now().isoformat(),
                "events_analysis": f"Error: {str(e)}",
                "processing_time": 0,
                "status": "error"
            }

    def select_strategic_clips(self, match_id: str, max_clips: int = 60) -> list:
        """Select strategic subset of clips for testing"""
        data_dir = Path("../data") / match_id
        clips_dir = data_dir / "compressed_clips"
        
        if not clips_dir.exists():
            raise FileNotFoundError(f"Compressed clips directory not found: {clips_dir}")
        
        # Load clip metadata
        segments_file = data_dir / "clips" / "segments.json"
        if not segments_file.exists():
            raise FileNotFoundError(f"Segments file not found: {segments_file}")
        
        with open(segments_file, 'r') as f:
            segments_data = json.load(f)
        
        clips = segments_data['clips']
        
        # Strategic selection: 
        # 1. Early game (0-15 min) - 15 clips
        # 2. Mid game (30-45 min) - 15 clips  
        # 3. Late game (75-90 min) - 15 clips
        # 4. Random sampling - 15 clips
        
        selected_clips = []
        
        # Early game clips (0-15 minutes)
        early_clips = [c for c in clips if c['start_seconds'] <= 900]
        selected_clips.extend(early_clips[:15])
        
        # Mid game clips (30-45 minutes)
        mid_clips = [c for c in clips if 1800 <= c['start_seconds'] <= 2700]
        selected_clips.extend(mid_clips[:15])
        
        # Late game clips (75-90 minutes)
        late_clips = [c for c in clips if 4500 <= c['start_seconds'] <= 5400]
        selected_clips.extend(late_clips[:15])
        
        # Random sampling from remaining
        remaining_clips = [c for c in clips if c not in selected_clips]
        import random
        random.shuffle(remaining_clips)
        selected_clips.extend(remaining_clips[:15])
        
        # Limit to max_clips
        return selected_clips[:max_clips]

    def benchmark_models(self, match_id: str, max_clips: int = 60):
        """Run benchmark across all models"""
        print(f"🏆 Starting Multi-Model Benchmark for {match_id}")
        print(f"📊 Testing {len(self.models_to_test)} models on {max_clips} clips")
        print("=" * 60)
        
        # Select strategic clips
        selected_clips = self.select_strategic_clips(match_id, max_clips)
        print(f"✅ Selected {len(selected_clips)} strategic clips")
        
        data_dir = Path("../data") / match_id
        clips_dir = data_dir / "compressed_clips"
        
        # Run each model
        for model_name, description in self.models_to_test.items():
            print(f"\n🤖 Testing {model_name} ({description})")
            
            model_results = []
            successful_analyses = 0
            total_time = 0
            
            for i, clip_info in enumerate(selected_clips):
                clip_filename = f"compressed_{clip_info['clip_filename']}"
                clip_path = clips_dir / clip_filename
                
                if not clip_path.exists():
                    print(f"⚠️  Clip not found: {clip_path}")
                    continue
                
                print(f"  📹 {i+1}/{len(selected_clips)}: {clip_info['timestamp']}", end=" ")
                
                result = self.analyze_clip_with_model(model_name, str(clip_path), clip_info)
                model_results.append(result)
                
                if result['status'] == 'success':
                    successful_analyses += 1
                    total_time += result['processing_time']
                    print("✅")
                else:
                    print("❌")
                
                # Rate limiting
                time.sleep(1)
            
            # Store results
            self.results[model_name] = {
                'clips_analyzed': len(selected_clips),
                'successful_analyses': successful_analyses,
                'success_rate': successful_analyses / len(selected_clips) * 100,
                'total_processing_time': total_time,
                'avg_processing_time': total_time / successful_analyses if successful_analyses > 0 else 0,
                'analyses': model_results
            }
            
            print(f"  📊 Success rate: {self.results[model_name]['success_rate']:.1f}%")
            print(f"  ⏱️  Avg time: {self.results[model_name]['avg_processing_time']:.1f}s")

    def compare_with_veo_ground_truth(self, match_id: str):
        """Compare model results with Veo ground truth"""
        print(f"\n🎯 Comparing with Veo Ground Truth")
        
        data_dir = Path("../data") / match_id
        veo_truth_path = data_dir / "veo_ground_truth.json"
        
        if not veo_truth_path.exists():
            print(f"❌ Veo ground truth not found: {veo_truth_path}")
            return
        
        # Load Veo ground truth
        with open(veo_truth_path, 'r') as f:
            veo_data = json.load(f)
        
        print(f"📊 Veo detected {veo_data['total_events']} total events")
        
        # Extract Veo goals
        veo_goals = [e for e in veo_data['events'] if e['event_type'] == 'Goal']
        veo_shots = [e for e in veo_data['events'] if e['event_type'] == 'Shot on goal']
        
        print(f"⚽ Veo Goals: {len(veo_goals)}")
        print(f"🎯 Veo Shots: {len(veo_shots)}")
        
        # Analyze each model's performance
        for model_name, model_data in self.results.items():
            print(f"\n🤖 {model_name} Performance:")
            
            # Count detected events
            goals_detected = 0
            shots_detected = 0
            
            for analysis in model_data['analyses']:
                if analysis['status'] == 'success':
                    text = analysis['events_analysis'].lower()
                    if 'goal' in text and ('scored' in text or 'crosses' in text):
                        goals_detected += 1
                    elif 'shot' in text or 'save' in text:
                        shots_detected += 1
            
            model_data['goals_detected'] = goals_detected
            model_data['shots_detected'] = shots_detected
            model_data['goal_precision'] = goals_detected / len(veo_goals) * 100 if veo_goals else 0
            model_data['shot_precision'] = shots_detected / len(veo_shots) * 100 if veo_shots else 0
            
            print(f"  ⚽ Goals detected: {goals_detected}")
            print(f"  🎯 Shots detected: {shots_detected}")
            print(f"  📊 Goal precision: {model_data['goal_precision']:.1f}%")
            print(f"  📊 Shot precision: {model_data['shot_precision']:.1f}%")

    def generate_benchmark_report(self, match_id: str):
        """Generate comprehensive benchmark report"""
        data_dir = Path("../data") / match_id
        report_path = data_dir / "model_benchmark_report.json"
        
        benchmark_report = {
            "match_id": match_id,
            "benchmark_timestamp": datetime.now().isoformat(),
            "models_tested": len(self.models_to_test),
            "clips_per_model": len(next(iter(self.results.values()))['analyses']) if self.results else 0,
            "results": self.results,
            "summary": {
                "best_accuracy": None,
                "fastest_model": None,
                "most_reliable": None,
                "recommendations": []
            }
        }
        
        if self.results:
            # Find best performing models
            best_goal_precision = max(self.results.items(), key=lambda x: x[1].get('goal_precision', 0))
            fastest_model = min(self.results.items(), key=lambda x: x[1].get('avg_processing_time', float('inf')))
            most_reliable = max(self.results.items(), key=lambda x: x[1].get('success_rate', 0))
            
            benchmark_report["summary"]["best_accuracy"] = {
                "model": best_goal_precision[0],
                "goal_precision": best_goal_precision[1].get('goal_precision', 0)
            }
            
            benchmark_report["summary"]["fastest_model"] = {
                "model": fastest_model[0],
                "avg_time": fastest_model[1].get('avg_processing_time', 0)
            }
            
            benchmark_report["summary"]["most_reliable"] = {
                "model": most_reliable[0],
                "success_rate": most_reliable[1].get('success_rate', 0)
            }
        
        # Save report
        with open(report_path, 'w') as f:
            json.dump(benchmark_report, f, indent=2)
        
        print(f"\n📋 Benchmark report saved: {report_path}")
        
        # Print summary
        print(f"\n🏆 BENCHMARK SUMMARY")
        print("=" * 40)
        if benchmark_report["summary"]["best_accuracy"]:
            print(f"🎯 Best Accuracy: {benchmark_report['summary']['best_accuracy']['model']}")
            print(f"⚡ Fastest Model: {benchmark_report['summary']['fastest_model']['model']}")
            print(f"🛡️  Most Reliable: {benchmark_report['summary']['most_reliable']['model']}")

def run_benchmark(match_id: str, max_clips: int = 60):
    """Run complete model benchmark"""
    benchmark = FootballModelBenchmark()
    
    try:
        # Run benchmark across all models
        benchmark.benchmark_models(match_id, max_clips)
        
        # Compare with Veo ground truth
        benchmark.compare_with_veo_ground_truth(match_id)
        
        # Generate report
        benchmark.generate_benchmark_report(match_id)
        
        print(f"\n✅ Multi-model benchmark complete!")
        
    except Exception as e:
        print(f"❌ Benchmark failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python multi_model_benchmark.py <match-id> [max_clips]")
        print("Example: python multi_model_benchmark.py ballyclare-20250111 60")
        sys.exit(1)
    
    match_id = sys.argv[1]
    max_clips = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    
    success = run_benchmark(match_id, max_clips)
    sys.exit(0 if success else 1) 
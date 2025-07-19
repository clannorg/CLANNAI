#!/usr/bin/env python3
"""
Player Clip Analyzer - Dual-View Basketball Player Identification
Analyzes synchronized left/right camera clips to identify all players
"""

import os
import json
import base64
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")
genai.configure(api_key=GEMINI_API_KEY)

class PlayerClipAnalyzer:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.analysis_results = []
        
    def encode_video_base64(self, video_path: str) -> str:
        """Encode video file to base64 for API submission"""
        try:
            with open(video_path, 'rb') as video_file:
                return base64.b64encode(video_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding video {video_path}: {e}")
            return None

    def get_dual_view_analysis_prompt(self, timestamp: str) -> str:
        """Generate prompt for dual-view player analysis"""
        return f"""
🏀 BASKETBALL PLAYER IDENTIFICATION
===================================
Timestamp: {timestamp}

MISSION: Analyze the ENTIRE 15-second dual-camera video and identify ALL people visible throughout the clip. Classify them as ACTIVE PLAYERS or BYSTANDERS.

CONTEXT: You have synchronized left and right camera views of the same 15-second basketball session. Use BOTH camera angles to get a complete picture of everyone present.

STRICT CLASSIFICATION RULES:

🏀 ACTIVE PLAYERS = Only people who are:
- Taking shots WITH defenders present
- Passing the ball to teammates
- Switching possession after scoring (other team takes the ball)
- Participating in organized game flow (offense/defense)

👥 BYSTANDERS = Everyone else:
- Taking shots alone (no defenders)
- Collecting their own ball after shooting
- Walking around while others play
- Standing/sitting on sidelines
- Shooting around separately from main game
- Just hanging out, not in organized play

FOR EACH PERSON VISIBLE THROUGHOUT THE 15-SECOND CLIP, PROVIDE:
1. Name/ID (jersey number if visible, or distinctive feature)
2. Brief physical description (jersey color, build, distinctive features)
3. What they're doing during the clip (specific activity)
4. Ball possession behavior (who gets the ball after shots)
5. Classification: ACTIVE or BYSTANDER

IMPORTANT: 
- If you can see a jersey number, clearly state it (e.g., "Blue jersey #31")
- Give ONE summary per person for the entire 15-second clip
- Use both camera angles to identify everyone present

RESPONSE FORMAT (SIMPLE TEXT):
```
ESTIMATED TOTALS:
- Active Players: ~X people
- Bystanders: ~Y people  
- Total Individuals: ~Z people

DETAILED ANALYSIS:
Player_23: Red jersey #23, athletic build, dribbling with defenders, other team gets ball, ACTIVE
Player_45: Green jersey #45, slim build, playing defense near key, other team gets ball, ACTIVE
BlueJersey_TallPlayer: Blue jersey, tall build, running court and setting plays, other team gets ball, ACTIVE
GrayShirt_Player: Gray shirt, stocky build, taking shots alone, collects own ball, BYSTANDER
Bystander_BlackShirt: Black T-shirt, standing on sideline observing, no ball involvement, BYSTANDER
```

FIRST GIVE YOUR ESTIMATE OF TOTAL COUNTS, THEN LIST EACH PERSON.
GIVE ONE SUMMARY PER PERSON FOR THE ENTIRE 15-SECOND CLIP. NO TIMESTAMPS.

NAMING:
- If jersey number visible: "Player_[NUMBER]" (e.g., "Player_31", "Player_86")
- If no number: "ColorJersey_Feature" (e.g., "BlueJersey_TallPlayer")
- Bystanders: "Bystander_Description" (e.g., "Bystander_BlackShirt")

IMPORTANT:
- ALWAYS use jersey numbers when visible (Player_31, Player_86, etc.)
- Be consistent with jersey number identification
- If same jersey number appears multiple times, it's the same player
- Be conservative with bystander classification - only people clearly not playing

KEEP DESCRIPTIONS CONCISE AND FOCUS ON THE STRICT ACTIVE/BYSTANDER CLASSIFICATION.
"""

    def analyze_dual_view_clip(self, left_clip_path: str, right_clip_path: str, timestamp: str) -> dict:
        """Analyze a synchronized dual-view clip for player identification"""
        print(f"🎨 Analyzing dual-view clip: {timestamp}")
        
        start_time = time.time()
        
        # Encode both videos
        encode_start = time.time()
        left_video_base64 = self.encode_video_base64(left_clip_path)
        right_video_base64 = self.encode_video_base64(right_clip_path)
        
        if not left_video_base64 or not right_video_base64:
            print(f"❌ Failed to encode videos for {timestamp}")
            return None
            
        encode_time = time.time() - encode_start
        
        # Generate prompt
        prompt = self.get_dual_view_analysis_prompt(timestamp)
        
        try:
            # API call with both videos
            api_start = time.time()
            response = self.model.generate_content([
                prompt,
                {
                    "mime_type": "video/mp4",
                    "data": left_video_base64
                },
                {
                    "mime_type": "video/mp4", 
                    "data": right_video_base64
                }
            ])
            api_time = time.time() - api_start
            
            # Get the full conversational response
            response_text = response.text.strip()
            
            # Handle empty responses
            if not response_text or response_text.strip() == '':
                print(f"⚠️  Empty response from Gemini for {timestamp}")
                return {
                    "timestamp": timestamp,
                    "error": "Empty response from API",
                    "analysis": "",
                    "total_players_visible": 0
                }
            
            # Save the conversational analysis
            result = {
                "timestamp": timestamp,
                "analysis": response_text,
                "total_players_visible": 0,  # We'll extract this if needed
                "processing_info": {
                    'encode_time': encode_time,
                    'api_time': api_time,
                    'total_time': time.time() - start_time,
                    'left_clip_path': str(left_clip_path),
                    'right_clip_path': str(right_clip_path)
                }
            }
            
            # Add processing metadata
            result['processing_info'] = {
                'encode_time': encode_time,
                'api_time': api_time,
                'total_time': time.time() - start_time,
                'left_clip_path': str(left_clip_path),
                'right_clip_path': str(right_clip_path)
            }
            
            print(f"✅ Completed analysis for {timestamp} ({result.get('total_players_visible', 0)} players)")
            return result
            
        except Exception as e:
            print(f"❌ Error analyzing clip {timestamp}: {e}")
            return {
                "timestamp": timestamp,
                "error": str(e),
                "processing_info": {
                    'encode_time': encode_time,
                    'total_time': time.time() - start_time,
                    'left_clip_path': left_clip_path,
                    'right_clip_path': right_clip_path
                }
            }

    def get_clip_pairs(self, clips_dir: Path, sample_size: int = 4) -> list:
        """Get synchronized left/right clip pairs for analysis"""
        clip_pairs = []
        
        # Get first N clips (default: first minute = 4 clips)
        for i in range(sample_size):
            minutes = i // 4
            seconds = (i % 4) * 15
            timestamp = f"{minutes}_{seconds:02d}"
            
            # Use compressed clips for API processing
            left_clip = clips_dir / f"compressed_left_{timestamp}.mp4"
            right_clip = clips_dir / f"compressed_right_{timestamp}.mp4"
            
            if left_clip.exists() and right_clip.exists():
                clip_pairs.append((left_clip, right_clip, timestamp))
            else:
                print(f"⚠️  Missing compressed clip pair for {timestamp}")
        
        return clip_pairs

    def analyze_clips_parallel(self, max_workers: int = 2) -> list:
        """Analyze clips in parallel"""
        # Get script directory and set up paths
        script_dir = Path(__file__).parent
        utils_output_dir = script_dir.parent / "0_utils" / "output"
        clips_dir = utils_output_dir / "compressed_clips"
        
        # Check if clips exist
        if not clips_dir.exists():
            print(f"❌ Clips directory not found: {clips_dir}")
            print("   Run split_videos.py first!")
            return []
        
        # Get clip pairs for analysis
        clip_pairs = self.get_clip_pairs(clips_dir, sample_size=8)  # First 2 minutes (8 clips)
        
        if not clip_pairs:
            print("❌ No clip pairs found for analysis")
            return []
        
        print(f"🎬 Found {len(clip_pairs)} clip pairs for analysis")
        print("🚀 Using parallel processing for player identification")
        print()
        
        results = []
        
        # Process clips in parallel - API calls are I/O bound, so we can use more threads
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Submit all analysis tasks
            future_to_clip = {
                executor.submit(self.analyze_dual_view_clip, left_clip, right_clip, timestamp): (left_clip, right_clip, timestamp)
                for left_clip, right_clip, timestamp in clip_pairs
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_clip):
                left_clip, right_clip, timestamp = future_to_clip[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        print(f"✅ Completed analysis for {timestamp}")
                    else:
                        print(f"❌ Failed to analyze {timestamp}")
                except Exception as e:
                    print(f"❌ Exception for {timestamp}: {e}")
        
        return results

    def save_results(self, results: list):
        """Save analysis results to output directory"""
        output_dir = Path(__file__).parent / "output"
        output_dir.mkdir(exist_ok=True)
        
        # Save individual clip analyses
        for result in results:
            timestamp = result.get('timestamp', 'unknown')
            safe_timestamp = timestamp.replace(':', '_')
            
            # Save JSON version
            json_filename = f"player_analysis_{safe_timestamp}.json"
            json_file = output_dir / json_filename
            with open(json_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            # Save text version (just the analysis)
            if 'analysis' in result and result['analysis']:
                text_filename = f"player_analysis_{safe_timestamp}.txt"
                text_file = output_dir / text_filename
                with open(text_file, 'w') as f:
                    f.write(f"BASKETBALL PLAYER ANALYSIS - {timestamp}\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(result['analysis'])
        
        # Save combined results
        combined_file = output_dir / "player_analysis_combined.json"
        with open(combined_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"📁 Results saved to: {output_dir}")
        print("   📄 JSON files: player_analysis_*.json")
        print("   📝 Text files: player_analysis_*.txt")

def main():
    """Run player clip analysis"""
    print("🎨 BASKETBALL PLAYER CLIP ANALYZER")
    print("=" * 50)
    
    analyzer = PlayerClipAnalyzer()
    results = analyzer.analyze_clips_parallel()
    
    if results:
        analyzer.save_results(results)
        print(f"\n✅ Analysis complete! Processed {len(results)} clips")
    else:
        print("\n❌ No results generated")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
5. Gemini Goals & Shots Error-Correcting Detection
Uses Gemini 2.5 Pro to detect goals and shots with strict validation logic
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class IntelligentMatchSynthesizer:
    def __init__(self):
        """Initialize with Gemini 2.5 Pro for intelligent synthesis"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        # Use 2.5 Pro for intelligent synthesis
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
    def get_intelligent_synthesis_prompt(self, clip_analyses: list, batch_num: int, total_batches: int) -> str:
        """Generate prompt for intelligent match synthesis with batch info"""
        
        # Combine all clip analyses into one context
        all_clips_text = ""
        for i, analysis in enumerate(clip_analyses):
            clip_time = analysis['start_seconds']
            minutes = clip_time // 60
            seconds = clip_time % 60
            timestamp = f"{minutes:02.0f}:{seconds:02.0f}"
            
            all_clips_text += f"\n--- CLIP {i+1} ({timestamp}) ---\n"
            all_clips_text += analysis['events_analysis']
            all_clips_text += "\n"
        
        return f"""
🧠 GOALS & SHOTS DETECTION WITH ERROR CORRECTION
==============================================
📦 BATCH {batch_num}/{total_batches} - SEQUENTIAL PROCESSING

You are an expert football analyst reviewing clips from a match.
Focus ONLY on detecting GOALS and SHOTS with strict validation.
This is batch {batch_num} of {total_batches} - extract ALL events from these clips.

🚨 ULTRA-STRICT GOAL DETECTION (NO FALSE POSITIVES):

RULE 1: ONLY count as goal if clip explicitly says "GOAL", "SCORES", "BALL CROSSES LINE"
- NOT: "shot", "save", "celebration", "close attempt"
- Must be CLEAR goal statement

RULE 2: KICKOFF VALIDATION REQUIRED
- Real goal MUST be followed by kickoff at CENTER CIRCLE
- Opposing team takes kickoff (NOT the scoring team)
- No kickoff = NO GOAL (was probably saved/missed)

RULE 3: LOGICAL VALIDATION
- If RED scores → BLACK takes kickoff
- If BLACK scores → RED takes kickoff  
- Same team kickoff = CONTRADICTION = NOT A GOAL

RULE 4: TEMPORAL VALIDATION
- Cannot have 2 kickoffs within 60 seconds by same team
- Cannot have 2 goals within 30 seconds (extremely rare)

📊 YOUR TASKS:

1. **CONSERVATIVE GOAL DETECTION**:
   - Find clips that explicitly state "GOAL" 
   - Check next clip for CENTER CIRCLE kickoff by OPPOSING team
   - REJECT if scoring team takes kickoff (breaks football rules)

2. **SHOT DETECTION**:
   - Find all attempts at goal: "shot", "strike", "effort"
   - Classify outcome: "goal", "saved", "off_target", "blocked"
   - Include team and approximate timing

3. **CONFIDENCE ASSESSMENT**:
   - HIGH: Explicit statement + clear evidence
   - MEDIUM: Clear action but some uncertainty
   - LOW: Possible but unclear

🔍 CLIP ANALYSES TO SYNTHESIZE:
{all_clips_text}

📤 OUTPUT FORMAT (JSON):
{{
  "goals_detected": [
    {{
      "timestamp": "2:45",
      "scoring_team": "team in blue jerseys", 
      "description": "Shot from penalty area crosses goal line",
      "confidence": "HIGH",
      "evidence": "Explicit GOAL statement + opposing team kickoff at 2:50",
      "source_clips": ["clip_0011", "clip_0012"]
    }}
  ],
  "shots_detected": [
    {{
      "timestamp": "1:23",
      "team": "team in red jerseys",
      "outcome": "saved",
      "description": "Long range shot saved by goalkeeper",
      "confidence": "HIGH",
      "source_clips": ["clip_0005"]
    }},
    {{
      "timestamp": "8:12",
      "team": "team in blue jerseys", 
      "outcome": "off_target",
      "description": "Shot from edge of box goes wide",
      "confidence": "MEDIUM",
      "source_clips": ["clip_0032"]
    }}
  ],
  "rejected_false_positives": [
    {{
      "timestamp": "4:45",
      "type": "goal",
      "reason": "Scoring team took kickoff - violates football rules",
      "original_description": "Shot from free kick"
    }}
  ],
  "kickoff_analysis": [
    {{
      "kickoff_time": "2:50",
      "inferred_goal_time": "2:45", 
      "evidence": "Teams lined up after celebration"
    }}
  ],
  "summary": {{
    "total_goals": 1,
    "total_shots": 7,
    "total_false_positives_rejected": 2,
    "validation_method": "Ultra-strict detection with kickoff validation"
  }}
}}

🚨 CRITICAL REMINDER: 
- GOALS: REJECT if no explicit "GOAL" statement  
- GOALS: REJECT if same team takes kickoff (rule violation)
- GOALS: REJECT if kickoffs too close together (impossible timing)
- SHOTS: Include all clear attempts at goal, classify outcome accurately
- BETTER TO MISS than create FALSE POSITIVES
- Conservative detection = accurate results!
"""

    def process_batch_and_append(self, clip_batch: list, match_id: str, batch_num: int, total_batches: int) -> bool:
        """Process a batch of clips and append events to output file"""
        data_dir = Path("../data") / match_id
        output_file = data_dir / "all_match_events.json"
        
        print(f"📦 Processing batch {batch_num}/{total_batches} ({len(clip_batch)} clips)...")
        
        # Generate prompt for this batch
        prompt = self.get_intelligent_synthesis_prompt(clip_batch, batch_num, total_batches)
        
        try:
            start_time = time.time()
            
            # Call Gemini 2.5 Pro for this batch
            response = self.model.generate_content(prompt)
            processing_time = time.time() - start_time
            
            # Parse response
            response_text = response.text.strip()
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            try:
                batch_analysis = json.loads(json_text)
            except json.JSONDecodeError:
                print(f"⚠️  Batch {batch_num} response wasn't valid JSON")
                return False
            
            # Load existing events or create new file
            if output_file.exists():
                with open(output_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {
                    "match_id": match_id,
                    "processing_method": "sequential_batch_processing",
                    "events": []
                }
            
            # Extract events from this batch and append
            new_events = []
            
            # Add goals as events
            for goal in batch_analysis.get("goals_detected", []):
                new_events.append({
                    "timestamp": goal.get("timestamp"),
                    "type": "goal",
                    "team": goal.get("scoring_team"),
                    "description": goal.get("description"),
                    "confidence": goal.get("confidence"),
                    "source_batch": batch_num
                })
            
            # Add shots as events  
            for shot in batch_analysis.get("shots_detected", []):
                new_events.append({
                    "timestamp": shot.get("timestamp"),
                    "type": "shot",
                    "team": shot.get("team"),
                    "outcome": shot.get("outcome"),
                    "description": shot.get("description"),
                    "confidence": shot.get("confidence"),
                    "source_batch": batch_num
                })
            
            # Append new events
            data["events"].extend(new_events)
            data[f"batch_{batch_num}_processing_time"] = processing_time
            
            # Save back to file
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Batch {batch_num} complete - {len(new_events)} events added ({processing_time:.1f}s)")
            return True
            
        except Exception as e:
            print(f"❌ Error processing batch {batch_num}: {e}")
            return False

    def synthesize_intelligently(self, match_id: str) -> dict:
        """Use Gemini 2.5 Pro to process all clips in sequential batches"""
        print(f"🧠 Step 5: Sequential Goals & Shots detection using Gemini 2.5 Pro for {match_id}")
        
        data_dir = Path("../data") / match_id
        analyses_dir = data_dir / "clip_analyses"
        
        if not analyses_dir.exists():
            print(f"❌ Clip analyses not found: {analyses_dir}")
            return None
        
        # Load all clip analyses
        analysis_files = sorted(list(analyses_dir.glob("*_analysis.json")))
        if not analysis_files:
            print(f"❌ No analysis files found in {analyses_dir}")
            return None
            
        print(f"📊 Loading {len(analysis_files)} clip analyses...")
        
        clip_analyses = []
        for analysis_file in analysis_files:
            with open(analysis_file, 'r') as f:
                analysis = json.load(f)
                clip_analyses.append(analysis)
        
        # Split into batches of 60 clips max
        BATCH_SIZE = 60
        batches = [clip_analyses[i:i + BATCH_SIZE] for i in range(0, len(clip_analyses), BATCH_SIZE)]
        total_batches = len(batches)
        
        print(f"🚀 Processing {len(clip_analyses)} clips in {total_batches} batches (max {BATCH_SIZE} clips per batch)")
        
        # Process each batch sequentially
        success_count = 0
        for i, batch in enumerate(batches, 1):
            success = self.process_batch_and_append(batch, match_id, i, total_batches)
            if success:
                success_count += 1
            
            # Add delay between batches to respect rate limits
            if i < total_batches:
                print(f"⏳ Waiting 10 seconds before next batch...")
                time.sleep(10)
        
        print(f"✅ Sequential processing complete!")
        print(f"📊 Processed {success_count}/{total_batches} batches successfully")
        
        # Load final results
        output_file = data_dir / "all_match_events.json"
        if output_file.exists():
            with open(output_file, 'r') as f:
                final_data = json.load(f)
            
            total_events = len(final_data.get("events", []))
            goals = [e for e in final_data["events"] if e.get("type") == "goal"]
            shots = [e for e in final_data["events"] if e.get("type") == "shot"]
            
            print(f"🎯 Final Results:")
            print(f"   📊 Total events: {total_events}")
            print(f"   ⚽ Goals: {len(goals)}")
            print(f"   🏹 Shots: {len(shots)}")
            print(f"💾 Saved to: {output_file}")
            
            return final_data
        
        return None

def synthesize_match(match_id):
    """Main synthesis function using intelligent analysis"""
    try:
        synthesizer = IntelligentMatchSynthesizer()
        result = synthesizer.synthesize_intelligently(match_id)
        return result is not None
    except ValueError as e:
        print(f"❌ Failed to initialize synthesizer: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python 5_gemini_goals_error_correcting.py <match-id>")
        sys.exit(1)
    
    match_id = sys.argv[1]
    success = synthesize_match(match_id)
    
    if success:
        print(f"🎯 Ready for Step 6: Web formatting")
    else:
        sys.exit(1) 
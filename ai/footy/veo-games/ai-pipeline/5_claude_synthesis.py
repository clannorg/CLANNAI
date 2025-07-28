#!/usr/bin/env python3
"""
5. Claude Synthesis (Alternative to Gemini)
Uses Anthropic Claude API for more accurate match synthesis
"""

import sys
import os
import json
import time
from pathlib import Path
from datetime import datetime
import anthropic
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class ClaudeMatchSynthesizer:
    def __init__(self):
        """Initialize with Anthropic Claude"""
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        
    def get_claude_synthesis_prompt(self, clip_analyses: list) -> str:
        """Generate prompt for Claude match synthesis"""
        
        # Combine all clip analyses
        all_clips_text = ""
        for i, analysis in enumerate(clip_analyses):
            clip_time = analysis['start_seconds']
            minutes = clip_time // 60
            seconds = clip_time % 60
            timestamp = f"{minutes:02.0f}:{seconds:02.0f}"
            
            all_clips_text += f"\n--- CLIP {i+1} ({timestamp}) ---\n"
            all_clips_text += analysis['events_analysis']
            all_clips_text += "\n"
        
        return f"""You are an expert football analyst reviewing 15-minute match clips. Your task is to identify REAL GOALS (not celebrations, saves, or near misses) using logical reasoning.

🚨 STRICT GOAL DETECTION RULES:

1. **KICKOFF VALIDATION (CRITICAL):**
   - Real goals MUST be followed by kickoff from CENTER CIRCLE
   - After goal: opposing team takes kickoff (not the scoring team)
   - If goal at 5:30 → look for kickoff at 5:35-5:45
   - NO KICKOFF = NO GOAL (probably save/miss)

2. **GOAL EVIDENCE REQUIRED:**
   - Clear statement: "goal", "ball crosses line", "scores"
   - NOT just: "shot", "save", "celebration", "close"
   - Ball must actually go IN the goal

3. **KICKOFF vs GOAL KICK DISTINCTION:**
   - KICKOFF: Both teams at center circle, after goals
   - GOAL KICK: Goalkeeper kicks from penalty area
   - Only KICKOFFS validate goals!

CLIP ANALYSES:
{all_clips_text}

Analyze these clips and return ONLY goals that meet ALL criteria:
1. Clear goal statement in clip
2. Followed by center circle kickoff
3. Opposing team takes the kickoff

Return JSON format:
{{
  "real_goals": [
    {{
      "timestamp": "06:09",
      "team": "BLACK",
      "evidence": "Clip says 'Goal! Ball goes into lower left corner'",
      "kickoff_validation": "RED team kickoff at center circle in next clip",
      "confidence": "HIGH"
    }}
  ],
  "false_positives": [
    {{
      "timestamp": "04:45", 
      "reason": "Scoring team took kickoff - violates football rules"
    }}
  ],
  "summary": "Found X real goals with kickoff validation"
}}"""

    def synthesize_match(self, match_id: str) -> bool:
        """Synthesize match using Claude"""
        print(f"🧠 Step 5: Claude synthesis for {match_id}")
        
        data_dir = Path("../data") / match_id
        
        # Load all clip analyses
        analyses_dir = data_dir / "clip_analyses"
        if not analyses_dir.exists():
            print(f"❌ No analyses found in {analyses_dir}")
            return False
        
        clip_analyses = []
        analysis_files = sorted(analyses_dir.glob("*.json"))
        
        for file_path in analysis_files:
            with open(file_path, 'r') as f:
                analysis = json.load(f)
                clip_analyses.append(analysis)
        
        print(f"📊 Loading {len(clip_analyses)} clip analyses...")
        
        # Generate synthesis prompt
        prompt = self.get_claude_synthesis_prompt(clip_analyses)
        
        try:
            start_time = time.time()
            
            # Call Claude
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.1,  # Low temperature for accuracy
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            processing_time = time.time() - start_time
            
            # Parse Claude's response
            response_text = response.content[0].text.strip()
            
            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text
            
            try:
                claude_analysis = json.loads(json_text)
            except json.JSONDecodeError:
                print("⚠️  Claude response wasn't valid JSON")
                claude_analysis = {
                    "raw_analysis": response_text,
                    "processing_note": "Response was text, not JSON"
                }
            
            # Create timeline
            match_timeline = {
                "match_id": match_id,
                "synthesis_timestamp": datetime.now().isoformat(),
                "synthesis_method": "claude_4_sonnet",
                "clips_analyzed": len(clip_analyses),
                "processing_time_seconds": processing_time,
                "claude_analysis": claude_analysis,
                "source_clips": [f"clip_{analysis['timestamp']}" for analysis in clip_analyses]
            }
            
            # Save timeline
            timeline_path = data_dir / "claude_match_timeline.json"
            with open(timeline_path, 'w') as f:
                json.dump(match_timeline, f, indent=2)
            
            print(f"✅ Claude synthesis complete!")
            print(f"⏱️  Processing time: {processing_time:.1f}s")
            
            # Print summary
            if "real_goals" in claude_analysis:
                goals = claude_analysis["real_goals"]
                print(f"⚽ Real goals detected: {len(goals)}")
                for goal in goals:
                    print(f"   🥅 {goal['timestamp']} - {goal['team']} team")
            
            if "false_positives" in claude_analysis:
                fps = claude_analysis["false_positives"] 
                print(f"❌ False positives filtered: {len(fps)}")
                
            return True
            
        except Exception as e:
            print(f"❌ Claude synthesis failed: {e}")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python 5_claude_synthesis.py <match-id>")
        return
    
    match_id = sys.argv[1]
    
    synthesizer = ClaudeMatchSynthesizer()
    success = synthesizer.synthesize_match(match_id)
    
    if success:
        print("🎯 Ready for Step 6: Web formatting")
    else:
        print("❌ Synthesis failed")

if __name__ == "__main__":
    main() 
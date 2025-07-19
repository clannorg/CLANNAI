#!/usr/bin/env python3
"""
Player Synthesis - Team Organization and Description
Analyzes raw player analysis to create organized team breakdowns
"""

import os
import json
import time
from pathlib import Path
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable not set")
genai.configure(api_key=GEMINI_API_KEY)

class PlayerSynthesis:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    def load_raw_analysis(self) -> dict:
        """Load all text analysis files and extract unique players"""
        output_dir = Path(__file__).parent / "output"
        
        all_players = []
        all_bystanders = []
        estimated_active_list = []
        estimated_bystanders_list = []
        
        # Find all text analysis files
        text_files = list(output_dir.glob("player_analysis_*.txt"))
        
        if not text_files:
            raise FileNotFoundError("No player analysis text files found in output directory")
        
        print(f"📂 Loading {len(text_files)} analysis files...")
        
        for text_file in text_files:
            with open(text_file, 'r') as f:
                content = f.read()
                
            # Extract estimated totals and player lines from the analysis
            lines = content.split('\n')
            estimated_active = 0
            estimated_bystanders = 0
            
            for line in lines:
                line = line.strip()
                
                # Parse estimated totals
                if 'Active Players:' in line:
                    try:
                        estimated_active = int(line.split('~')[1].split()[0])
                        estimated_active_list.append(estimated_active)
                    except:
                        pass
                elif 'Bystanders:' in line:
                    try:
                        estimated_bystanders = int(line.split('~')[1].split()[0])
                        estimated_bystanders_list.append(estimated_bystanders)
                    except:
                        pass
                
                # Parse player information
                if ':' in line and ('ACTIVE' in line or 'BYSTANDER' in line):
                    if 'ACTIVE' in line:
                        all_players.append(line)
                    elif 'BYSTANDER' in line:
                        all_bystanders.append(line)
        
        # Calculate dynamic caps based on analyzer estimates
        if estimated_active_list:
            max_active = max(estimated_active_list)
            avg_active = sum(estimated_active_list) // len(estimated_active_list)
            active_cap = max_active + 1  # Allow 1 more than max estimate
        else:
            active_cap = 12  # Fallback
            
        if estimated_bystanders_list:
            max_bystanders = max(estimated_bystanders_list)
            avg_bystanders = sum(estimated_bystanders_list) // len(estimated_bystanders_list)
            bystander_cap = max_bystanders + 1  # Allow 1 more than max estimate
        else:
            bystander_cap = 5  # Fallback
        
        # Create structured data for synthesis
        analysis_data = {
            "total_clips_analyzed": len(text_files),
            "active_players": all_players,
            "bystanders": all_bystanders,
            "total_active_players": len(set(all_players)),
            "total_bystanders": len(set(all_bystanders)),
            "estimated_active": estimated_active_list[-1] if estimated_active_list else 0,
            "estimated_bystanders": estimated_bystanders_list[-1] if estimated_bystanders_list else 0,
            "active_cap": active_cap,
            "bystander_cap": bystander_cap,
            "all_estimates": {
                "active": estimated_active_list,
                "bystanders": estimated_bystanders_list
            }
        }
        
        print(f"✅ Found {len(set(all_players))} unique active players")
        print(f"✅ Found {len(set(all_bystanders))} unique bystanders")
        print(f"📊 Analyzer estimates: ~{estimated_active_list[-1] if estimated_active_list else 0} active, ~{estimated_bystanders_list[-1] if estimated_bystanders_list else 0} bystanders")
        print(f"🎯 Dynamic caps: {active_cap} active, {bystander_cap} bystanders")
        
        return analysis_data
    
    def get_team_synthesis_prompt(self, raw_analysis: dict) -> str:
        """Generate prompt for player synthesis analysis"""
        active_cap = raw_analysis.get('active_cap', 12)
        bystander_cap = raw_analysis.get('bystander_cap', 5)
        
        return f"""
🏀 BASKETBALL PLAYER SYNTHESIS
==============================

You have {raw_analysis['total_clips_analyzed']} text files, each containing 15 seconds of basketball player analysis. Each file shows who was visible during that 15-second interval.

PLAYER DATA FROM {raw_analysis['total_clips_analyzed']} CLIPS:
{json.dumps(raw_analysis, indent=2)}

TASK: Create a complete description of all the players in the game.

Using all clips, identify:
1. All the ACTIVE PLAYERS (people actually playing basketball)
2. All the BYSTANDERS (people watching, not playing)

For each person, provide:
- Jersey number and color (if visible)
- Physical description
- What they were doing
- How many clips they appeared in

RESPONSE FORMAT (SIMPLE TEXT):
```
🏀 ACTIVE PLAYERS
=================
Player_31: Blue jersey #31, athletic build, dribbling and passing, appears in 3 clips
Player_86: White jersey #86, slim build, running court and shooting, appears in 5 clips
BlueJersey_TallPlayer: Blue jersey, tall build, setting plays, appears in 2 clips

👥 BYSTANDERS
==============
Bystander_BlackShirt: Black T-shirt, standing on sideline, appears in 2 clips
GrayShirt_Player: Gray shirt, taking shots alone, appears in 1 clip
```

CRITICAL CONSTRAINTS:
- The analyzer estimates there are about {active_cap} active players and {bystander_cap} bystanders in total.
- You MUST NOT output more than {active_cap} active players and {bystander_cap} bystanders.
- If you see more, merge similar descriptions until you reach these totals.
- Use all the descriptions from all clips to make each player's profile as complete as possible.

DEDUPLICATION RULES:
- Same jersey number = SAME PLAYER (Player_31 and White jersey #31 are the same person)
- Same jersey color + similar description = SAME PLAYER
- Same clothing description = SAME BYSTANDER
- Be VERY conservative - if descriptions are similar, assume same person

CRITICAL: You MUST deduplicate aggressively:
- If you see "Player_31" and "Blue jersey #31" - they are the SAME person
- If you see "WhiteJersey_Player" and "White jersey" - they are the SAME person
- If you see "BlueJersey_TallPlayer" and "Blue jersey" - they are the SAME person
- Combine all mentions of the same person into ONE entry
- Count total appearances across all clips for each unique person

IMPORTANT: 
- Count how many clips each person appears in
- Be conservative - if unsure, assume same person
- Focus on jersey numbers for player identification
- You MUST merge similar players until you reach the cap of {active_cap} active and {bystander_cap} bystanders
"""

    def synthesize_teams(self, raw_analysis: dict) -> dict:
        """Use Gemini to synthesize raw analysis into organized teams"""
        print("🎨 SYNTHESIZING TEAM ANALYSIS")
        print("=" * 40)
        
        start_time = time.time()
        
        # Generate prompt
        prompt = self.get_team_synthesis_prompt(raw_analysis)
        
        try:
            # API call
            print("🤖 Sending to Gemini 2.5 Pro for team synthesis...")
            api_start = time.time()
            response = self.model.generate_content(prompt)
            api_time = time.time() - api_start
            
            # Get response
            response_text = response.text.strip()
            
            # Handle empty responses
            if not response_text or response_text.strip() == '':
                print("⚠️  Empty response from Gemini")
                return {
                    "error": "Empty response from API",
                    "processing_time": time.time() - start_time
                }
            
            # Handle text response
            try:
                # Clean up response if it has markdown formatting
                if response_text.startswith('```'):
                    response_text = response_text[3:-3]
                
                result = {
                    "analysis": response_text,
                    "processing_info": {
                        'api_time': api_time,
                        'total_time': time.time() - start_time,
                        'raw_analysis_source': 'player_analysis_combined.json'
                    }
                }
                
                print(f"✅ Team synthesis completed in {api_time:.2f}s")
                return result
                
            except Exception as e:
                print(f"⚠️  Error processing response: {e}")
                return {
                    "error": f"Processing error: {str(e)}",
                    "raw_response": response_text[:500],
                    "processing_time": time.time() - start_time
                }
                
        except Exception as e:
            print(f"❌ Error in team synthesis: {e}")
            return {
                "error": str(e),
                "processing_time": time.time() - start_time
            }
    
    def save_synthesis_results(self, synthesis_result: dict):
        """Save synthesis results to synthesis_output directory"""
        synthesis_dir = Path(__file__).parent / "synthesis_output"
        synthesis_dir.mkdir(exist_ok=True)
        
        # Save text version
        text_file = synthesis_dir / "player_synthesis.txt"
        with open(text_file, 'w') as f:
            f.write("🏀 BASKETBALL PLAYER SYNTHESIS REPORT\n")
            f.write("=" * 50 + "\n\n")
            
            if 'error' in synthesis_result:
                f.write(f"❌ ERROR: {synthesis_result['error']}\n")
                if 'raw_response' in synthesis_result:
                    f.write(f"\nRaw Response:\n{synthesis_result['raw_response']}\n")
            else:
                # Just write the text response directly
                f.write(synthesis_result.get('analysis', 'No analysis available'))
        
        print(f"📁 Synthesis results saved to: {synthesis_dir}")
        print("   📝 Text: player_synthesis.txt")

def main():
    """Run team synthesis analysis"""
    print("🎨 BASKETBALL TEAM SYNTHESIS")
    print("=" * 40)
    
    synthesizer = PlayerSynthesis()
    
    try:
        # Load raw analysis
        print("📂 Loading raw player analysis...")
        raw_analysis = synthesizer.load_raw_analysis()
        print(f"✅ Loaded analysis with {len(raw_analysis)} clips")
        
        # Synthesize teams
        synthesis_result = synthesizer.synthesize_teams(raw_analysis)
        
        # Save results
        synthesizer.save_synthesis_results(synthesis_result)
        
        if 'error' not in synthesis_result:
            print(f"\n✅ Player synthesis complete!")
            
            # Parse the text response to count players
            analysis_text = synthesis_result.get('analysis', '')
            active_count = 0
            bystander_count = 0
            
            if analysis_text:
                lines = analysis_text.split('\n')
                in_active_section = False
                in_bystander_section = False
                
                for line in lines:
                    line = line.strip()
                    if 'ACTIVE PLAYERS' in line or '🏀 ACTIVE PLAYERS' in line:
                        in_active_section = True
                        in_bystander_section = False
                    elif 'BYSTANDERS' in line or '👥 BYSTANDERS' in line:
                        in_active_section = False
                        in_bystander_section = True
                    elif line and ':' in line and in_active_section:
                        active_count += 1
                    elif line and ':' in line and in_bystander_section:
                        bystander_count += 1
            
            print(f"   🏀 In Game Players: {active_count} players")
            print(f"   👥 Bystanders: {bystander_count} individuals")
        else:
            print(f"\n❌ Synthesis failed: {synthesis_result['error']}")
            
    except Exception as e:
        print(f"❌ Error in synthesis: {e}")

if __name__ == "__main__":
    main() 
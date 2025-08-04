#!/usr/bin/env python3
"""
7.5 Definite Events Builder
Cross-references VEO ground truth with AI descriptions to create validated events
Only includes events that match VEO timestamps ±30 seconds with rich AI descriptions
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
load_dotenv(Path(__file__).parent.parent / '.env')

class DefiniteEventsBuilder:
    def __init__(self):
        """Initialize with Gemini for intelligent cross-referencing"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        print("🎯 Definite Events Builder initialized with Gemini AI")

    def get_cross_reference_prompt(self, veo_comparison: str, ai_timeline: str) -> str:
        """Create prompt for intelligent cross-referencing"""
        return f"""You are an expert football analyst tasked with creating a definitive events list by cross-referencing VEO ground truth with AI descriptions.

TASK: Create a clean list of events that are confirmed by VEO ground truth AND have rich AI descriptions.

VEO ACCURACY COMPARISON (Shows which AI events match VEO):
{veo_comparison}

AI VALIDATED TIMELINE (Contains rich descriptions):
{ai_timeline}

INSTRUCTIONS:
1. Only include events that are marked as "MATCH" or "validated" in the VEO comparison
2. For each validated event, find the corresponding AI description from the timeline
3. Extract goals, shots, and any other significant events that VEO confirmed
4. Keep the rich AI descriptions for context and engagement
5. Maintain exact timestamps from the AI timeline (not VEO, as AI has more context)

OUTPUT FORMAT:
=== DEFINITE GOALS ===
Timestamp: XX:XX (XXXX seconds)
Team: [red/yellow/black/etc]
Description: [Rich AI description from timeline]
VEO Validation: [Confirmation details]

=== DEFINITE SHOTS ===
Timestamp: XX:XX (XXXX seconds)  
Team: [red/yellow/black/etc]
Description: [Rich AI description from timeline]
Outcome: [saved/missed/blocked/etc]
VEO Validation: [Confirmation details]

=== OTHER VALIDATED EVENTS ===
[Any other events VEO confirmed - corners, fouls, etc.]

QUALITY CONTROL:
- Only include events with VEO confirmation
- Use AI timestamps (more contextual than VEO)
- Keep detailed descriptions for user engagement
- Mark confidence level for each event

Be thorough but strict - quality over quantity. Rich descriptions make the difference."""

    def build_definite_events(self, match_id: str) -> bool:
        """Create definitive events list using Gemini cross-referencing"""
        print(f"🎯 Building definite events for {match_id}")
        
        data_dir = Path("../data") / match_id
        veo_comparison_path = data_dir / "7_accuracy_comparison.txt"
        ai_timeline_path = data_dir / "6_validated_timeline.txt"
        output_path = data_dir / "7.5_definite_events.txt"
        
        # Check input files exist
        if not veo_comparison_path.exists():
            print(f"❌ VEO comparison file not found: {veo_comparison_path}")
            return False
            
        if not ai_timeline_path.exists():
            print(f"❌ AI timeline file not found: {ai_timeline_path}")
            return False
        
        # Read input files
        print("📥 Reading VEO comparison and AI timeline...")
        with open(veo_comparison_path, 'r') as f:
            veo_comparison = f.read()
            
        with open(ai_timeline_path, 'r') as f:
            ai_timeline = f.read()
        
        # Generate cross-reference analysis
        print("🧠 Cross-referencing VEO truth with AI descriptions...")
        cross_reference_prompt = self.get_cross_reference_prompt(veo_comparison, ai_timeline)
        
        try:
            response = self.model.generate_content(cross_reference_prompt)
            definite_events_content = response.text
            
            # Save definite events
            print(f"💾 Saving definite events to: {output_path}")
            with open(output_path, 'w') as f:
                f.write(f"# Definite Events - {match_id}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Method: VEO truth + AI descriptions cross-reference\n")
                f.write(f"# Quality: Only VEO-confirmed events with rich context\n\n")
                f.write(definite_events_content)
            
            print("✅ Definite events created successfully!")
            print(f"📊 Output: {output_path}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error during cross-referencing: {e}")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python 7.5_definite_events_builder.py <match_id>")
        print("Example: python 7.5_definite_events_builder.py newmills-20250222")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    builder = DefiniteEventsBuilder()
    success = builder.build_definite_events(match_id)
    
    if success:
        print(f"\n🎯 Definite events ready for {match_id}!")
        print("📝 Contains only VEO-validated events with rich AI descriptions")
        print("🔄 Next: Run 8.5_other_events_extractor.py for additional events")
    else:
        print(f"\n❌ Failed to build definite events for {match_id}")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
CLANNAI Match Commentary Generator (Step 5.2)
============================================

Creates a complete, second-by-second match narrative from individual clip analyses.
This bridges the gap between granular clip data and high-level tactical insights.

Input: Individual clip analyses from Step 4
Output: match_commentary.md - Professional live commentary style narrative

Part of the CLANNAI AI Pipeline v3.0
"""

import json
import os
import sys
from pathlib import Path
import google.generativeai as genai
from datetime import datetime
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MatchCommentaryGenerator:
    def __init__(self):
        # Configure Gemini API
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
    def load_clip_analyses(self, data_dir):
        """Load all clip analyses and sort by timestamp"""
        analyses_dir = data_dir / "clip_analyses"
        if not analyses_dir.exists():
            raise FileNotFoundError(f"Clip analyses directory not found: {analyses_dir}")
        
        analyses = []
        for analysis_file in analyses_dir.glob("*_analysis.json"):
            try:
                with open(analysis_file, 'r') as f:
                    analysis = json.load(f)
                    if analysis.get("status") == "success":
                        analyses.append(analysis)
            except Exception as e:
                print(f"⚠️  Failed to load {analysis_file}: {e}")
        
        # Sort by timestamp to ensure chronological order
        analyses.sort(key=lambda x: x.get("timestamp", 0))
        print(f"📊 Loaded {len(analyses)} clip analyses for commentary generation")
        return analyses
    
    def create_match_commentary_prompt(self, analyses):
        """Create the prompt for generating match commentary"""
        
        # Prepare the clip summaries for the prompt
        clip_summaries = []
        for i, analysis in enumerate(analyses):
            start_seconds = analysis.get("start_seconds", i * 15)
            events = analysis.get("events_analysis", "No events detected")
            
            # Convert timestamp to MM:SS format
            minutes = start_seconds // 60
            seconds = start_seconds % 60
            time_str = f"{minutes}:{seconds:02d}"
            
            clip_summaries.append(f"{time_str} - {events}")
        
        prompt = f"""You are creating a factual match event timeline from football clip analyses.

Transform these clip analyses into a clean, chronological event log. Focus on FACTS ONLY - what actually happened in each clip.

CLIP ANALYSES (chronological order):
{chr(10).join(clip_summaries)}

REQUIREMENTS:
1. **Factual Only**: Report exactly what's described in each clip analysis
2. **No Drama**: Avoid commentary language like "OH MY WORD!" or "UNBELIEVABLE!"
3. **No Invention**: Don't add events not mentioned in the source clips
4. **Team Colors**: Use "Red team" and "Black team" consistently
5. **Key Events**: Focus on goals, shots, passes, tackles, fouls, saves
6. **Concise**: Brief, clear descriptions suitable for data analysis

OUTPUT FORMAT:
# MATCH EVENT TIMELINE

**Time** - Brief factual description

EXAMPLE STYLE:
**0:15** - Black team plays long ball up right flank
**0:23** - Cross delivered into penalty area
**0:31** - Red goalkeeper punches ball clear
**0:37** - Black team scores from loose ball in penalty area
**0:45** - Red team attacks, shot saved by goalkeeper

Generate the factual event timeline now:"""

        return prompt
    
    def create_sequential_commentary_prompt(self, analyses, batch_num, total_batches, last_timestamp):
        """Create prompt for sequential batch processing"""
        
        # Prepare the clip summaries for the prompt
        clip_summaries = []
        for i, analysis in enumerate(analyses):
            start_seconds = analysis.get("start_seconds", i * 15)
            events = analysis.get("events_analysis", "No events detected")
            
            # Convert timestamp to MM:SS format
            minutes = start_seconds // 60
            seconds = start_seconds % 60
            time_str = f"{minutes}:{seconds:02d}"
            
            clip_summaries.append(f"{time_str} - {events}")
        
        context_info = ""
        if batch_num > 1:
            context_info = f"""
CONTEXT: This is batch {batch_num} of {total_batches}. Continue the timeline seamlessly from the previous batch.
Previous batch ended around {last_timestamp}. Maintain consistent team naming (Red team/Black team).
"""
        
        prompt = f"""You are creating a factual match event timeline from football clip analyses.
{context_info}
Transform these clip analyses into a clean, chronological event log. Focus on FACTS ONLY - what actually happened in each clip.

CLIP ANALYSES (chronological order):
{chr(10).join(clip_summaries)}

REQUIREMENTS:
1. **Factual Only**: Report exactly what's described in each clip analysis
2. **No Drama**: Avoid commentary language like "OH MY WORD!" or "UNBELIEVABLE!"
3. **No Invention**: Don't add events not mentioned in the source clips
4. **Team Colors**: Use "Red team" and "Black team" consistently
5. **Key Events**: Focus on goals, shots, passes, tackles, fouls, saves
6. **Concise**: Brief, clear descriptions suitable for data analysis
7. **Sequential**: {'Continue timeline from previous batch' if batch_num > 1 else 'Start the timeline'}

OUTPUT FORMAT (events only, no headers):
**Time** - Brief factual description

EXAMPLE STYLE:
**0:15** - Black team plays long ball up right flank
**0:23** - Cross delivered into penalty area
**0:31** - Red goalkeeper punches ball clear

Generate the factual event timeline now:"""

        return prompt
    
    def process_batch_and_append(self, batch, batch_num, total_batches, output_path, match_id):
        """Process a batch and append commentary to file"""
        print(f"📦 Processing batch {batch_num}/{total_batches} ({len(batch)} clips)...")
        
        # Generate context-aware prompt for this batch
        last_timestamp = ""
        if batch_num > 1:
            # Get last timestamp from previous batch
            if batch:
                prev_seconds = batch[0].get("start_seconds", 0) - 15
                prev_minutes = prev_seconds // 60
                prev_secs = prev_seconds % 60
                last_timestamp = f"{prev_minutes}:{prev_secs:02d}"
        
        prompt = self.create_sequential_commentary_prompt(batch, batch_num, total_batches, last_timestamp)
        
        try:
            print("⏳ Sending request to Gemini API...")
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=8192,
                )
            )
            
            if response.text:
                # Extract just the event lines (skip headers if present)
                commentary_text = response.text.strip()
                if "# MATCH EVENT TIMELINE" in commentary_text:
                    lines = commentary_text.split('\n')
                    # Find first event line (starts with **)
                    event_lines = []
                    for line in lines:
                        if line.strip().startswith('**') and '**' in line[2:]:
                            event_lines.append(line)
                    commentary_text = '\n'.join(event_lines)
                
                # Append to file
                with open(output_path, 'a', encoding='utf-8') as f:
                    if batch_num == 1:
                        # First batch - add header
                        f.write(f"# MATCH EVENT TIMELINE - {match_id.upper()}\n\n")
                        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write(f"**AI Model:** Gemini 2.5 Pro (Sequential Processing)\n\n")
                        f.write("---\n\n")
                    
                    f.write(commentary_text + '\n\n')
                
                event_count = len([line for line in commentary_text.split('\n') if line.strip().startswith('**')])
                print(f"✅ Batch {batch_num} complete - {event_count} events added")
                return True
        else:
                print(f"❌ No commentary generated for batch {batch_num}")
                return False
                
        except Exception as e:
            print(f"❌ Error processing batch {batch_num}: {e}")
            return False

    def generate_commentary(self, analyses, output_path, match_id):
        """Generate match commentary using sequential batch processing"""
        print("📊 Generating factual event timeline with Gemini 2.5 Pro...")
        
        # Use 60-clip batches (same as error-correcting script)
        batch_size = 60
        batches = [analyses[i:i + batch_size] for i in range(0, len(analyses), batch_size)]
        total_batches = len(batches)
        
        print(f"🚀 Processing {len(analyses)} clips in {total_batches} batches (max {batch_size} clips per batch)")
        
        # Remove existing file if it exists
        if output_path.exists():
            output_path.unlink()
        
        # Process each batch sequentially
        success_count = 0
        for i, batch in enumerate(batches, 1):
            success = self.process_batch_and_append(batch, i, total_batches, output_path, match_id)
            if success:
                success_count += 1
            
            # Add delay between batches
            if i < total_batches:
                print(f"⏳ Waiting 5 seconds before next batch...")
                time.sleep(5)
        
        print(f"✅ Sequential commentary generation complete!")
        print(f"📊 Processed {success_count}/{total_batches} batches successfully")
        
        return success_count == total_batches
    
    def generate_batch_commentary(self, analyses):
        """Generate commentary for a batch of analyses"""
        prompt = self.create_match_commentary_prompt(analyses)
        
        # Debug: Check input size
        prompt_length = len(prompt)
        prompt_words = len(prompt.split())
        estimated_tokens = prompt_words * 1.3  # Rough estimate: 1.3 tokens per word
        print(f"🔍 Input size: {prompt_length:,} chars, ~{estimated_tokens:,.0f} tokens")
        print(f"📊 Processing {len(analyses)} clips")
        
        try:
            print("⏳ Sending request to Gemini API...")
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Low temperature for factual reporting
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=32768,  # Increase to 32K (avoid the 35K soft limit)
                )
            )
            print("✅ API response received")
            
            if response.text:
                response_length = len(response.text)
                response_lines = len(response.text.split('\n'))
                print(f"✅ Commentary generated: {response_length} chars, {response_lines} lines")
                
                # Debug: show first and last few lines
                lines = response.text.split('\n')
                print(f"🔍 First line: {lines[0][:100] if lines else 'None'}")
                print(f"🔍 Last line: {lines[-1][:100] if len(lines) > 0 else 'None'}")
                
                return response.text
            else:
                print("❌ No commentary generated")
                return None
                
        except Exception as e:
            print(f"❌ Error generating commentary: {e}")
            return None
    
    def save_commentary(self, commentary, output_path):
        """Save the commentary to a markdown file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                # Add header with metadata
                f.write(f"# MATCH EVENT TIMELINE\n\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**AI Model:** Gemini 2.5 Pro\n")
                f.write(f"**Pipeline:** CLANNAI v3.0 Step 5.2\n\n")
                f.write("---\n\n")
                f.write(commentary)
            
            print(f"💾 Commentary saved to: {output_path}")
            return True
            
        except Exception as e:
            print(f"❌ Error saving commentary: {e}")
            return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python 5.2-match-commentary.py <match_id>")
        print("Example: python 5.2-match-commentary.py ballyclare-20250111")
        sys.exit(1)
    
    match_id = sys.argv[1]
    
    # Set up paths
    script_dir = Path(__file__).parent
    data_dir = script_dir.parent / "data" / match_id
    output_path = data_dir / "match_commentary.md"
    
    if not data_dir.exists():
        print(f"❌ Match data directory not found: {data_dir}")
        sys.exit(1)
    
    print(f"🎬 CLANNAI Match Commentary Generator (Step 5.2)")
    print(f"📁 Match: {match_id}")
    print(f"📊 Data: {data_dir}")
    print(f"💾 Output: {output_path}")
    print()
    
    try:
        # Initialize generator
        generator = MatchCommentaryGenerator()
        
        # Load clip analyses
        print("📖 Loading clip analyses...")
        analyses = generator.load_clip_analyses(data_dir)
        
        if not analyses:
            print("❌ No valid clip analyses found!")
            sys.exit(1)
        
        # Generate commentary
        print("🎤 Generating live match commentary...")
        success = generator.generate_commentary(analyses, output_path, match_id)
        
        if not success:
            print("❌ Failed to generate commentary!")
            sys.exit(1)
        
        # Commentary already saved during processing
        if output_path.exists():
            print()
            print("🎉 SUCCESS! Match commentary generated!")
            print(f"📄 Output: {output_path}")
            print()
            print("🔥 This completes CLANNAI v3.0 Step 5.2")
            print("📚 Your match now has a complete narrative story!")
            print("💬 Perfect context for enhanced coaching insights and chatbot!")
        else:
            print("❌ Failed to save commentary!")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
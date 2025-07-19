#!/usr/bin/env python3
"""
Convert Events Timeline to JSON Format
=====================================

Uses Gemini 2.5 to convert the basketball events timeline from text format
to structured JSON format for easier analysis and processing.
"""

import os
import json
import google.generativeai as genai
from pathlib import Path
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TimelineConverter:
    def __init__(self, api_key: str):
        """Initialize the converter with Gemini API key"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    def read_timeline_file(self, file_path: str) -> str:
        """Read the events timeline file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.info(f"Successfully read timeline file: {file_path}")
            return content
        except Exception as e:
            logger.error(f"Error reading timeline file: {e}")
            raise
    
    def convert_to_json(self, timeline_text: str) -> dict:
        """Convert timeline text to JSON using Gemini 2.5"""
        
        prompt = f"""
Convert this basketball events timeline to simple JSON format.

Output format:
{{
  "events": [
    {{
      "team": "red/blue/white/purple",
      "action": "Shot/Rebound/Pass/Dribble",
      "outcome": "Miss/2Point/3Point/Offensive/Defensive/Success",
      "time": <seconds>,
      "description": "Brief description of the action"
    }}
  ]
}}

Rules:
- Convert timestamps like "00:005.9" to seconds (5.9)
- Determine team from jersey color: White/Blue = blue team, Purple/Red = red team
- For shots: outcome is "Miss", "2Point", or "3Point" 
- For rebounds: outcome is "Offensive" or "Defensive"
- For other actions: outcome is "Success"
- Keep descriptions brief but clear

Here's the timeline:

{timeline_text}

Return only valid JSON, no additional text.
"""
        
        try:
            response = self.model.generate_content(prompt)
            json_str = response.text.strip()
            # Remove code block markers if present
            if json_str.startswith('```json'):
                json_str = json_str[7:]
            if json_str.startswith('```'):
                json_str = json_str[3:]
            if json_str.endswith('```'):
                json_str = json_str[:-3]
            json_str = json_str.strip()
            # Try to parse the JSON to validate it
            result = json.loads(json_str)
            logger.info("Successfully converted timeline to JSON")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Gemini: {e}")
            logger.error(f"Response: {response.text}")
            raise
        except Exception as e:
            logger.error(f"Error converting timeline: {e}")
            raise
    
    def save_json(self, data: dict, output_path: str):
        """Save the JSON data to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved JSON to: {output_path}")
        except Exception as e:
            logger.error(f"Error saving JSON: {e}")
            raise

def main():
    """Main function to convert timeline to JSON"""
    
    # Load environment variables from .env file
    load_dotenv('scripts/project_gemini/.env')
    
    # Get API key from environment
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable not set")
        return
    
    # File paths
    timeline_file = "scripts/project_gemini/A2/1_game_events/synthesis_output/events_timeline.txt"
    output_file = "scripts/project_gemini/A2/1_game_events/synthesis_output/events_timeline.json"
    
    # Check if input file exists
    if not os.path.exists(timeline_file):
        logger.error(f"Timeline file not found: {timeline_file}")
        return
    
    try:
        # Initialize converter
        converter = TimelineConverter(api_key)
        
        # Read timeline
        timeline_text = converter.read_timeline_file(timeline_file)
        
        # Convert to JSON
        json_data = converter.convert_to_json(timeline_text)
        
        # Save JSON
        converter.save_json(json_data, output_file)
        
        # Print summary
        print(f"\n✅ Conversion complete!")
        print(f"📊 Total events: {len(json_data['events'])}")
        print(f"💾 Saved to: {output_file}")
        
        # Show first few events as preview
        print(f"\n📋 Preview of first 3 events:")
        for event in json_data['events'][:3]:
            print(f"  {event['time']}s - {event['team']} team {event['action']} ({event['outcome']})")
        
    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        return

if __name__ == "__main__":
    main() 
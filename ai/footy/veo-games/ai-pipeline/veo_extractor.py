#!/usr/bin/env python3
"""
Veo Final Event Extractor - WORKING VERSION
Uses the discovered highlights endpoint with AI events
"""

import requests
import json
import re
from datetime import datetime
from urllib.parse import urlparse

class VeoEventExtractor:
    def __init__(self):
        self.session = requests.Session()
        
        # Set browser-like headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': '',  # Will be set dynamically
        })
    
    def extract_match_id_from_url(self, veo_url):
        """Extract match ID from Veo URL"""
        # Pattern: https://app.veo.co/matches/20250111-ballyclare-425e4c3f/
        pattern = r'/matches/([^/]+)/?'
        match = re.search(pattern, veo_url)
        if match:
            return match.group(1)
        return None
    
    def get_events(self, veo_url):
        """Extract all events from a Veo match URL"""
        print(f"🎯 Extracting events from: {veo_url}")
        
        # Extract match ID
        match_id = self.extract_match_id_from_url(veo_url)
        if not match_id:
            print("❌ Could not extract match ID from URL")
            return None
            
        print(f"📋 Match ID: {match_id}")
        
        # Set referer
        self.session.headers['Referer'] = veo_url
        
        # Build the highlights API URL with exact parameters
        api_url = f"https://app.veo.co/api/app/matches/{match_id}/highlights/"
        params = {
            'include_ai': 'true',
            'fields': [
                'id', 'ai_resolution', 'created', 'comment', 'duration',
                'has_camera_directions', 'involved_players', 'is_ai_generated',
                'start', 'tags', 'modified', 'should_render'
            ]
        }
        
        print(f"🌐 API URL: {api_url}")
        print(f"📊 Parameters: {params}")
        
        try:
            # Make the request
            response = self.session.get(api_url, params=params, timeout=15)
            print(f"📨 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                events = response.json()
                print(f"✅ Successfully extracted {len(events)} events!")
                return events
            else:
                print(f"❌ Failed: {response.status_code}")
                print(f"📄 Response: {response.text[:200]}...")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return None
    
    def format_events_for_ai(self, events):
        """Format events for AI evaluation pipeline"""
        if not events:
            return None
            
        formatted_events = []
        
        for event in events:
            # Convert start time to minutes:seconds
            start_seconds = event.get('start', 0)
            minutes = start_seconds // 60
            seconds = start_seconds % 60
            timestamp = f"{minutes}:{seconds:02d}"
            
            # Extract event type
            event_type = "Unknown"
            if event.get('tags'):
                event_type = event['tags'][0].get('name', 'Unknown')
            
            formatted_event = {
                'timestamp': timestamp,
                'timestamp_seconds': start_seconds,
                'event_type': event_type,
                'event_id': event.get('id'),
                'duration': event.get('duration', 0),
                'is_ai_generated': event.get('is_ai_generated', False),
                'created': event.get('created'),
                'tags': event.get('tags', [])
            }
            
            formatted_events.append(formatted_event)
        
        # Sort by timestamp
        formatted_events.sort(key=lambda x: x['timestamp_seconds'])
        
        return {
            'match_url': getattr(self, 'current_url', ''),
            'extraction_time': datetime.now().isoformat(),
            'total_events': len(formatted_events),
            'events': formatted_events,
            'summary': self._generate_summary(formatted_events)
        }
    
    def _generate_summary(self, events):
        """Generate event summary for AI evaluation"""
        summary = {
            'total_events': len(events),
            'goals': len([e for e in events if e['event_type'] == 'Goal']),
            'shots_on_goal': len([e for e in events if e['event_type'] == 'Shot on goal']),
            'ai_generated_events': len([e for e in events if e['is_ai_generated']]),
            'event_types': {}
        }
        
        # Count event types
        for event in events:
            event_type = event['event_type']
            summary['event_types'][event_type] = summary['event_types'].get(event_type, 0) + 1
        
        return summary
    
    def extract_and_save(self, veo_url, output_file=None):
        """Extract events and save to file"""
        self.current_url = veo_url
        
        # Extract events
        raw_events = self.get_events(veo_url)
        if not raw_events:
            return None
        
        # Format for AI pipeline
        formatted_data = self.format_events_for_ai(raw_events)
        
        # Save to file
        if not output_file:
            match_id = self.extract_match_id_from_url(veo_url)
            output_file = f"veo_events_{match_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w') as f:
            json.dump(formatted_data, f, indent=2)
        
        print(f"💾 Saved to: {output_file}")
        
        # Print summary
        summary = formatted_data['summary']
        print(f"\n📊 EXTRACTION SUMMARY:")
        print(f"Total Events: {summary['total_events']}")
        print(f"Goals: {summary['goals']}")
        print(f"Shots on Goal: {summary['shots_on_goal']}")
        print(f"AI Generated: {summary['ai_generated_events']}")
        
        print(f"\n⚽ EVENT TIMELINE:")
        for event in formatted_data['events'][:10]:  # Show first 10
            icon = "🥅" if event['event_type'] == 'Goal' else "🎯"
            print(f"{icon} {event['timestamp']} - {event['event_type']}")
        
        if len(formatted_data['events']) > 10:
            print(f"... and {len(formatted_data['events']) - 10} more events")
        
        return formatted_data

if __name__ == "__main__":
    # Test with the Ballyclare match
    extractor = VeoEventExtractor()
    veo_url = "https://app.veo.co/matches/20250111-ballyclare-425e4c3f/"
    
    print("🚀 Testing Veo Event Extraction...")
    result = extractor.extract_and_save(veo_url)
    
    if result:
        print("\n🎉 SUCCESS! Event extraction working perfectly!")
        print(f"Ready for Ram's AI evaluation pipeline! 🎯")
    else:
        print("\n❌ Extraction failed") 
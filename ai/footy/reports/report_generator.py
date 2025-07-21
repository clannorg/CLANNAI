#!/usr/bin/env python3
"""
Football Report Generator
Generates final HTML reports for football analysis
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
import logging

# Import configuration
import sys
sys.path.append(str(Path(__file__).parent.parent / "0_utils"))
from config import PATHS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FootballReportGenerator:
    """
    Generates comprehensive HTML reports for football analysis
    Creates: match events, player profiles, tactical analysis reports
    """
    
    def __init__(self):
        """Initialize the report generator"""
        self.output_dir = PATHS["reports_dir"]
        self.output_dir.mkdir(exist_ok=True)
        
        # Load analysis data
        self.events_data = self.load_events_data()
        self.player_data = self.load_player_data()
        self.tactical_data = self.load_tactical_data()
        self.cost_data = self.load_cost_data()
    
    def load_events_data(self) -> Dict[str, Any]:
        """Load events analysis data"""
        events_dir = PATHS["events_output"]
        
        if not events_dir.exists():
            return {}
        
        # Try to load timeline data
        timeline_path = events_dir / "events_timeline.json"
        if timeline_path.exists():
            with open(timeline_path, 'r') as f:
                return json.load(f)
        
        return {}
    
    def load_player_data(self) -> Dict[str, Any]:
        """Load player analysis data"""
        player_dir = PATHS["player_output"]
        
        if not player_dir.exists():
            return {}
        
        # Try to load player statistics
        stats_path = player_dir / "player_analysis_statistics.json"
        if stats_path.exists():
            with open(stats_path, 'r') as f:
                return json.load(f)
        
        return {}
    
    def load_tactical_data(self) -> Dict[str, Any]:
        """Load tactical analysis data"""
        tactical_dir = PATHS["tactical_output"]
        
        if not tactical_dir.exists():
            return {}
        
        # Try to load formation statistics
        stats_path = tactical_dir / "formation_analysis_statistics.json"
        if stats_path.exists():
            with open(stats_path, 'r') as f:
                return json.load(f)
        
        return {}
    
    def load_cost_data(self) -> Dict[str, Any]:
        """Load cost analysis data"""
        cost_dir = PATHS["cost_output"]
        
        if not cost_dir.exists():
            return {}
        
        # Try to load cost analysis
        cost_path = cost_dir / "football_cost_analysis.json"
        if cost_path.exists():
            with open(cost_path, 'r') as f:
                return json.load(f)
        
        return {}
    
    def create_match_events_report(self) -> str:
        """Create HTML report for match events"""
        if not self.events_data:
            return self.create_empty_report("Match Events", "No events data available")
        
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Football Match Events Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: #ecf0f1; padding: 15px; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #3498db; }
        .stat-label { color: #7f8c8d; margin-top: 5px; }
        .timeline { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .event { padding: 8px; margin: 5px 0; border-left: 4px solid #3498db; background: white; }
        .event-number { font-weight: bold; color: #2c3e50; }
        .event-time { color: #7f8c8d; font-size: 0.9em; }
        .summary { background: #e8f5e8; padding: 15px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚽ Football Match Events Report</h1>
        
        <div class="summary">
            <h2>📊 Match Summary</h2>
            <p><strong>Analysis Date:</strong> {analysis_date}</p>
            <p><strong>Total Events:</strong> {total_events}</p>
            <p><strong>Time Range:</strong> {time_range}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{goals}</div>
                <div class="stat-label">Goals</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{shots}</div>
                <div class="stat-label">Shots</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{passes}</div>
                <div class="stat-label">Passes</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{tackles}</div>
                <div class="stat-label">Tackles</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{fouls}</div>
                <div class="stat-label">Fouls</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{cards}</div>
                <div class="stat-label">Cards</div>
            </div>
        </div>
        
        <h2>📅 Match Timeline</h2>
        <div class="timeline">
            {timeline_events}
        </div>
    </div>
</body>
</html>
"""
        
        # Extract data
        match_info = self.events_data.get("match_info", {})
        statistics = self.events_data.get("statistics", {})
        events = self.events_data.get("events", [])
        
        # Format timeline events
        timeline_html = ""
        for event in events[:50]:  # Show first 50 events
            timeline_html += f"""
            <div class="event">
                <span class="event-number">{event.get('event_number', '?')}.</span>
                <span class="event-time">{event.get('formatted_time', '00:00')}</span>
                {event.get('event_text', 'Unknown event')}
            </div>
            """
        
        if len(events) > 50:
            timeline_html += f"<p><em>... and {len(events) - 50} more events</em></p>"
        
        # Fill template
        html = html.format(
            analysis_date=match_info.get("synthesis_date", "Unknown"),
            total_events=match_info.get("total_events", 0),
            time_range=f"{events[0].get('formatted_time', '00:00')} - {events[-1].get('formatted_time', '00:00')}" if events else "N/A",
            goals=statistics.get("goals", 0),
            shots=statistics.get("shots", 0),
            passes=statistics.get("passes", 0),
            tackles=statistics.get("tackles", 0),
            fouls=statistics.get("fouls", 0),
            cards=statistics.get("cards", 0),
            timeline_events=timeline_html
        )
        
        return html
    
    def create_player_profiles_report(self) -> str:
        """Create HTML report for player profiles"""
        if not self.player_data:
            return self.create_empty_report("Player Profiles", "No player data available")
        
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Football Player Profiles Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; border-bottom: 3px solid #e74c3c; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: #ecf0f1; padding: 15px; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #e74c3c; }
        .stat-label { color: #7f8c8d; margin-top: 5px; }
        .summary { background: #fdf2e9; padding: 15px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>👥 Football Player Profiles Report</h1>
        
        <div class="summary">
            <h2>📊 Analysis Summary</h2>
            <p><strong>Analysis Date:</strong> {analysis_date}</p>
            <p><strong>Total Clips Analyzed:</strong> {total_clips}</p>
            <p><strong>Successful Analyses:</strong> {successful_clips}</p>
            <p><strong>Processing Time:</strong> {processing_time}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_clips}</div>
                <div class="stat-label">Clips Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{successful_clips}</div>
                <div class="stat-label">Successful</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{api_calls}</div>
                <div class="stat-label">API Calls</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{errors}</div>
                <div class="stat-label">Errors</div>
            </div>
        </div>
        
        <h2>🎽 Player Identification</h2>
        <p>Player analysis focused on:</p>
        <ul>
            <li><strong>Jersey Numbers:</strong> Identification of all visible player numbers</li>
            <li><strong>Team Colors:</strong> Classification of team colors and uniforms</li>
            <li><strong>Positions:</strong> GK, DEF, MID, FWD classification</li>
            <li><strong>Player Roles:</strong> Tactical responsibilities and positioning</li>
        </ul>
        
        <h2>📈 Analysis Performance</h2>
        <p>The player analysis system successfully processed {successful_clips} out of {total_clips} clips, 
        achieving a success rate of {success_rate:.1f}%.</p>
    </div>
</body>
</html>
"""
        
        # Extract data
        total_clips = self.player_data.get("total_clips", 0)
        successful_clips = self.player_data.get("successful_clips", 0)
        api_calls = self.player_data.get("api_calls", 0)
        errors = self.player_data.get("errors", 0)
        processing_time = self.player_data.get("processing_time", "Unknown")
        analysis_date = self.player_data.get("analysis_date", "Unknown")
        
        success_rate = (successful_clips / total_clips * 100) if total_clips > 0 else 0
        
        # Fill template
        html = html.format(
            analysis_date=analysis_date,
            total_clips=total_clips,
            successful_clips=successful_clips,
            api_calls=api_calls,
            errors=errors,
            processing_time=processing_time,
            success_rate=success_rate
        )
        
        return html
    
    def create_tactical_analysis_report(self) -> str:
        """Create HTML report for tactical analysis"""
        if not self.tactical_data:
            return self.create_empty_report("Tactical Analysis", "No tactical data available")
        
        html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Football Tactical Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; border-bottom: 3px solid #27ae60; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: #ecf0f1; padding: 15px; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #27ae60; }
        .stat-label { color: #7f8c8d; margin-top: 5px; }
        .summary { background: #e8f8f5; padding: 15px; border-radius: 8px; margin: 20px 0; }
        .formation-list { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🏟️ Football Tactical Analysis Report</h1>
        
        <div class="summary">
            <h2>📊 Analysis Summary</h2>
            <p><strong>Analysis Date:</strong> {analysis_date}</p>
            <p><strong>Total Clips Analyzed:</strong> {total_clips}</p>
            <p><strong>Successful Analyses:</strong> {successful_clips}</p>
            <p><strong>Processing Time:</strong> {processing_time}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_clips}</div>
                <div class="stat-label">Clips Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{successful_clips}</div>
                <div class="stat-label">Successful</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{api_calls}</div>
                <div class="stat-label">API Calls</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{formations_detected}</div>
                <div class="stat-label">Formations</div>
            </div>
        </div>
        
        <h2>📐 Formation Detection</h2>
        <div class="formation-list">
            <p>The tactical analysis system detected the following formations:</p>
            <ul>
                <li><strong>4-3-3:</strong> Attacking formation with wingers</li>
                <li><strong>4-4-2:</strong> Balanced formation with two strikers</li>
                <li><strong>3-5-2:</strong> Wing-back system with three center-backs</li>
                <li><strong>4-2-3-1:</strong> Modern attacking formation</li>
                <li><strong>3-4-3:</strong> Attacking wing-back system</li>
                <li><strong>5-3-2:</strong> Defensive formation with wing-backs</li>
            </ul>
        </div>
        
        <h2>⚽ Tactical Patterns Analyzed</h2>
        <ul>
            <li><strong>High Pressing:</strong> Aggressive pressure on opponents</li>
            <li><strong>Possession Play:</strong> Ball retention and build-up</li>
            <li><strong>Counter-Attacking:</strong> Quick transitions to attack</li>
            <li><strong>Defensive Block:</strong> Compact defensive organization</li>
            <li><strong>Wing Play:</strong> Attacking down the flanks</li>
            <li><strong>Central Control:</strong> Midfield dominance</li>
        </ul>
        
        <h2>📈 Analysis Performance</h2>
        <p>The tactical analysis system successfully processed {successful_clips} out of {total_clips} clips, 
        achieving a success rate of {success_rate:.1f}%.</p>
    </div>
</body>
</html>
"""
        
        # Extract data
        total_clips = self.tactical_data.get("total_clips", 0)
        successful_clips = self.tactical_data.get("successful_clips", 0)
        api_calls = self.tactical_data.get("api_calls", 0)
        formations_detected = self.tactical_data.get("formations_detected", 0)
        processing_time = self.tactical_data.get("processing_time", "Unknown")
        analysis_date = self.tactical_data.get("analysis_date", "Unknown")
        
        success_rate = (successful_clips / total_clips * 100) if total_clips > 0 else 0
        
        # Fill template
        html = html.format(
            analysis_date=analysis_date,
            total_clips=total_clips,
            successful_clips=successful_clips,
            api_calls=api_calls,
            formations_detected=formations_detected,
            processing_time=processing_time,
            success_rate=success_rate
        )
        
        return html
    
    def create_empty_report(self, title: str, message: str) -> str:
        """Create an empty report when no data is available"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }}
        h1 {{ color: #2c3e50; margin-bottom: 20px; }}
        .message {{ color: #7f8c8d; font-size: 1.2em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title} Report</h1>
        <div class="message">{message}</div>
    </div>
</body>
</html>
"""
    
    def generate_all_reports(self):
        """Generate all HTML reports"""
        logger.info("📄 Generating football analysis reports...")
        
        # Generate reports
        events_html = self.create_match_events_report()
        player_html = self.create_player_profiles_report()
        tactical_html = self.create_tactical_analysis_report()
        
        # Save reports
        events_path = self.output_dir / "match_events_report.html"
        player_path = self.output_dir / "player_profiles_report.html"
        tactical_path = self.output_dir / "tactical_analysis_report.html"
        
        with open(events_path, 'w') as f:
            f.write(events_html)
        
        with open(player_path, 'w') as f:
            f.write(player_html)
        
        with open(tactical_path, 'w') as f:
            f.write(tactical_html)
        
        logger.info(f"✅ Reports generated:")
        logger.info(f"   📄 Match Events: {events_path}")
        logger.info(f"   👥 Player Profiles: {player_path}")
        logger.info(f"   🏟️ Tactical Analysis: {tactical_path}")
        
        return {
            "events_report": str(events_path),
            "player_report": str(player_path),
            "tactical_report": str(tactical_path)
        }

def main():
    """Main function for report generation"""
    generator = FootballReportGenerator()
    
    print("📄 Football Report Generator")
    print("=" * 30)
    print(f"Output directory: {PATHS['reports_dir']}")
    print()
    
    # Generate reports
    results = generator.generate_all_reports()
    
    if results:
        print(f"\n✅ Report generation complete!")
        print(f"📄 Reports saved in: {PATHS['reports_dir']}")
        for report_type, path in results.items():
            print(f"   📄 {report_type}: {path}")
    else:
        print("\n❌ Report generation failed")

if __name__ == "__main__":
    main() 
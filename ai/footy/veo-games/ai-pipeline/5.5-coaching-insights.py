#!/usr/bin/env python3
"""
5.5 AI Coach Content Generator - Web App Integration
Reads match commentary and generates tactical analysis for web app left panel
Outputs coaching insights in format ready for AI coach interface
"""

import json
import re
import os
from pathlib import Path
from collections import defaultdict, Counter
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

class TacticalAnalyzer:
    def __init__(self):
        """Initialize Gemini AI and load environment"""
        # Load environment and configure Gemini
        load_dotenv()
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.5-pro')
        
        # What's WORKING patterns
        self.effective_patterns = {
            'successful_attacks': [
                r'creates? (a )?chance', r'dangerous.*attack', r'good.*movement',
                r'breaks? through', r'finds? space', r'excellent.*pass',
                r'scores?', r'goal', r'beats.*defender', r'clever.*play'
            ],
            'solid_defending': [
                r'good.*tackle', r'excellent.*save', r'solid.*defense',
                r'intercepts?.*well', r'clears?.*danger', r'blocks?.*shot',
                r'keeper.*stops', r'defensive.*wall'
            ],
            'good_passing': [
                r'accurate.*pass', r'finds.*teammate', r'good.*delivery',
                r'precise.*cross', r'thread.*pass', r'splits.*defense'
            ]
        }
        
        # What's NOT WORKING patterns
        self.ineffective_patterns = {
            'poor_attacks': [
                r'attack.*breaks.*down', r'loses.*possession', r'misplaced.*pass',
                r'shot.*wide', r'shot.*over', r'poor.*touch', r'heavy.*touch',
                r'offside', r'final.*pass.*fails'
            ],
            'defensive_errors': [
                r'poor.*clearance', r'defensive.*mistake', r'loses.*ball',
                r'caught.*out', r'wrong.*footed', r'mis.*hit'
            ],
            'turnover_patterns': [
                r'loses.*ball', r'possession.*lost', r'intercepted',
                r'tackles.*away', r'dispossessed', r'gives.*ball.*away'
            ]
        }
        
        # Play style patterns
        self.play_style_patterns = {
            'direct_play': [
                r'long.*ball', r'direct.*pass', r'over.*the.*top',
                r'clearance.*forward', r'punt.*forward'
            ],
            'possession_play': [
                r'short.*pass', r'builds?.*from.*back', r'patient.*buildup',
                r'keeps?.*possession', r'circulates?.*ball'
            ],
            'wing_play': [
                r'down.*the.*wing', r'crosses?.*from.*wide', r'wide.*play',
                r'overlapping.*run', r'gets.*to.*byline'
            ],
            'central_play': [
                r'through.*the.*middle', r'central.*area', r'midfield.*battle'
            ]
        }
        
    def extract_timing_events(self, analysis_text: str) -> list:
        """Extract timed events from analysis text"""
        # Look for patterns like "2s: event", "7s: another event"
        timing_pattern = r'(\d+)s:\s*([^0-9\n]+?)(?=\d+s:|$)'
        matches = re.findall(timing_pattern, analysis_text, re.IGNORECASE | re.DOTALL)
        
        events = []
        for time_str, event_desc in matches:
            events.append({
                'time_in_clip': int(time_str),
                'description': event_desc.strip()
            })
        
        return events
    
    def analyze_with_gemini(self, commentary_text: str) -> dict:
        """Use Gemini to intelligently analyze match commentary for professional insights"""
        
        # Split commentary if too long (keep under 100k chars)
        max_chars = 100000
        if len(commentary_text) > max_chars:
            commentary_text = commentary_text[:max_chars] + "\n[Commentary truncated for analysis...]"
        
        prompt = f"""
You are a professional football analyst. Analyze this match commentary and provide detailed tactical insights.

MATCH COMMENTARY:
{commentary_text}

Provide analysis in the following JSON format:

{{
    "set_pieces": {{
        "corner_kicks": {{
            "total_attempts": 0,
            "on_target": 0,
            "goals": 0,
            "analysis": "Assessment of corner kick effectiveness"
        }},
        "free_kicks": {{
            "close_range_attempts": 0,
            "long_range_attempts": 0,
            "goals": 0,
            "analysis": "Free kick effectiveness breakdown"
        }},
        "penalties": {{
            "awarded": 0,
            "scored": 0,
            "missed": 0,
            "analysis": "Penalty situation analysis"
        }},
        "throw_ins": {{
            "attacking_third": 0,
            "possession_retained": 0,
            "analysis": "Throw-in effectiveness"
        }}
    }},
    "tactical_patterns": {{
        "red_team": {{
            "dominant_formation": "Formation observed",
            "attacking_style": "Direct/Possession/Counter/Mixed",
            "defensive_style": "High press/Mid block/Deep/Mixed",
            "strengths": ["List key strengths with evidence"],
            "weaknesses": ["List key weaknesses with evidence"],
            "key_players": ["Notable performances without names"]
        }},
        "black_team": {{
            "dominant_formation": "Formation observed", 
            "attacking_style": "Direct/Possession/Counter/Mixed",
            "defensive_style": "High press/Mid block/Deep/Mixed",
            "strengths": ["List key strengths with evidence"],
            "weaknesses": ["List key weaknesses with evidence"],
            "key_players": ["Notable performances without names"]
        }}
    }},
    "match_flow": {{
        "periods_of_dominance": ["Which team dominated when"],
        "momentum_shifts": ["Key moments that changed the game"],
        "intensity_levels": ["High/medium/low intensity periods"]
    }},
    "spatial_analysis": {{
        "most_active_areas": ["Which areas of pitch saw most action"],
        "attacking_patterns": ["Common attack routes"],
        "defensive_vulnerabilities": ["Areas where teams were exposed"]
    }},
    "coaching_recommendations": {{
        "red_team": ["Specific actionable advice"],
        "black_team": ["Specific actionable advice"],
        "general": ["Overall match insights"]
    }}
}}

IMPORTANT: Provide specific evidence from the commentary for all insights. Be detailed and professional.
"""
        
        try:
            response = self.model.generate_content(prompt)
            # Parse JSON response
            analysis_text = response.text.strip()
            
            # Clean up the response if it has markdown formatting
            if '```json' in analysis_text:
                # Extract JSON from markdown code block
                start = analysis_text.find('```json') + 7
                end = analysis_text.rfind('```')
                if end > start:
                    analysis_text = analysis_text[start:end].strip()
            
            analysis = json.loads(analysis_text)
            return analysis
            
        except Exception as e:
            print(f"⚠️ Gemini analysis failed: {e}")
            # Fallback to basic analysis
            return self.fallback_analysis()
    
    def fallback_analysis(self) -> dict:
        """Fallback analysis if Gemini fails"""
        return {
            "set_pieces": {
                "corner_kicks": {"total_attempts": 0, "analysis": "Analysis unavailable"},
                "free_kicks": {"close_range_attempts": 0, "analysis": "Analysis unavailable"},
                "penalties": {"awarded": 0, "analysis": "Analysis unavailable"},
                "throw_ins": {"attacking_third": 0, "analysis": "Analysis unavailable"}
            },
            "tactical_patterns": {
                "red_team": {"strengths": ["Analysis unavailable"], "weaknesses": ["Analysis unavailable"]},
                "black_team": {"strengths": ["Analysis unavailable"], "weaknesses": ["Analysis unavailable"]}
            },
            "coaching_recommendations": {
                "red_team": ["Detailed analysis unavailable - using fallback"],
                "black_team": ["Detailed analysis unavailable - using fallback"],
                "general": ["Professional analysis requires Gemini API"]
            }
        }
    
    def count_pattern_matches(self, text: str, patterns: list) -> int:
        """Count how many times any pattern matches in text"""
        count = 0
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            count += len(matches)
        return count
    

    
    def analyze_tactical_effectiveness_from_commentary(self, commentary_text: str) -> dict:
        """Analyze tactical effectiveness from match commentary"""
        
        effectiveness = {
            'red_team': {
                'what_works': defaultdict(int),
                'what_doesnt_work': defaultdict(int),
                'play_styles': defaultdict(int),
                'turnovers_caused': 0,
                'turnovers_conceded': 0
            },
            'black_team': {
                'what_works': defaultdict(int),
                'what_doesnt_work': defaultdict(int), 
                'play_styles': defaultdict(int),
                'turnovers_caused': 0,
                'turnovers_conceded': 0
            }
        }
        
        # Analyze the commentary text for tactical patterns
        text = commentary_text.lower()
        
        for team in ['red', 'black']:
            team_key = f'{team}_team'
            
            # What's working well
            for category, patterns in self.effective_patterns.items():
                for pattern in patterns:
                    matches = re.findall(f'{team}.*{pattern}|{pattern}.*{team}', text, re.IGNORECASE)
                    effectiveness[team_key]['what_works'][category] += len(matches)
            
            # What's not working
            for category, patterns in self.ineffective_patterns.items():
                for pattern in patterns:
                    matches = re.findall(f'{team}.*{pattern}|{pattern}.*{team}', text, re.IGNORECASE)
                    effectiveness[team_key]['what_doesnt_work'][category] += len(matches)
            
            # Play styles being used
            for style, patterns in self.play_style_patterns.items():
                for pattern in patterns:
                    matches = re.findall(f'{team}.*{pattern}|{pattern}.*{team}', text, re.IGNORECASE)
                    effectiveness[team_key]['play_styles'][style] += len(matches)
            
            # Turnovers
            opponent = 'black' if team == 'red' else 'red'
            for pattern in self.ineffective_patterns['turnover_patterns']:
                # Team loses ball (turnover conceded)
                loses_ball = re.findall(f'{team}.*{pattern}', text, re.IGNORECASE)
                effectiveness[team_key]['turnovers_conceded'] += len(loses_ball)
                
                # Opponent loses ball (turnover caused)
                opponent_loses = re.findall(f'{opponent}.*{pattern}', text, re.IGNORECASE)
                effectiveness[team_key]['turnovers_caused'] += len(opponent_loses)
        
        return effectiveness

    def analyze_tactical_effectiveness(self, clip_analyses: list) -> dict:
        """Analyze what's working vs what's not working for each team"""
        
        effectiveness = {
            'red_team': {
                'what_works': defaultdict(int),
                'what_doesnt_work': defaultdict(int),
                'play_styles': defaultdict(int),
                'turnovers_caused': 0,
                'turnovers_conceded': 0
            },
            'black_team': {
                'what_works': defaultdict(int),
                'what_doesnt_work': defaultdict(int), 
                'play_styles': defaultdict(int),
                'turnovers_caused': 0,
                'turnovers_conceded': 0
            }
        }
        
        for clip in clip_analyses:
            text = clip.get('events_analysis', '').lower()
            
            # Analyze what's working for each team
            for team in ['red', 'black']:
                team_key = f'{team}_team'
                
                # What's working well
                for category, patterns in self.effective_patterns.items():
                    for pattern in patterns:
                        matches = re.findall(f'{team}.*{pattern}|{pattern}.*{team}', text, re.IGNORECASE)
                        effectiveness[team_key]['what_works'][category] += len(matches)
                
                # What's not working
                for category, patterns in self.ineffective_patterns.items():
                    for pattern in patterns:
                        matches = re.findall(f'{team}.*{pattern}|{pattern}.*{team}', text, re.IGNORECASE)
                        effectiveness[team_key]['what_doesnt_work'][category] += len(matches)
                
                # Play styles being used
                for style, patterns in self.play_style_patterns.items():
                    for pattern in patterns:
                        matches = re.findall(f'{team}.*{pattern}|{pattern}.*{team}', text, re.IGNORECASE)
                        effectiveness[team_key]['play_styles'][style] += len(matches)
                
                # Turnovers
                opponent = 'black' if team == 'red' else 'red'
                for pattern in self.ineffective_patterns['turnover_patterns']:
                    # Team loses ball (turnover conceded)
                    loses_ball = re.findall(f'{team}.*{pattern}', text, re.IGNORECASE)
                    effectiveness[team_key]['turnovers_conceded'] += len(loses_ball)
                    
                    # Opponent loses ball (turnover caused)
                    opponent_loses = re.findall(f'{opponent}.*{pattern}', text, re.IGNORECASE)
                    effectiveness[team_key]['turnovers_caused'] += len(opponent_loses)
        
        return effectiveness
    

    
    def generate_coaching_insights(self, match_id: str) -> dict:
        """Generate professional tactical insights using Gemini AI analysis"""
        print(f"🏆 AI-Powered Tactical Analysis for {match_id}")
        
        # Load match commentary
        data_dir = Path("../data") / match_id
        commentary_file = data_dir / "match_commentary.md"
        
        if not commentary_file.exists():
            print(f"❌ No match commentary found: {commentary_file}")
            return None
        
        # Read the commentary content
        with open(commentary_file, 'r', encoding='utf-8') as f:
            commentary_text = f.read()
        
        print(f"🤖 Analyzing with Gemini 2.5 Pro for professional insights...")
        
        # Use Gemini for intelligent analysis
        gemini_analysis = self.analyze_with_gemini(commentary_text)
        
        # Calculate key metrics from commentary
        event_lines = [line for line in commentary_text.split('\n') if line.startswith('**') and '**' in line[2:]]
        total_events = len(event_lines)
        
        # Format professional analysis content
        current_analysis_content = self.format_professional_analysis(gemini_analysis)
        
        # Extract coaching recommendations
        coaching_points = []
        if 'coaching_recommendations' in gemini_analysis:
            coaching_points.extend(gemini_analysis['coaching_recommendations'].get('red_team', []))
            coaching_points.extend(gemini_analysis['coaching_recommendations'].get('black_team', []))
            coaching_points.extend(gemini_analysis['coaching_recommendations'].get('general', []))
        
        # Professional web app format
        ai_coach_content = {
            'current_analysis': {
                'title': 'Professional Tactical Analysis',
                'content': current_analysis_content
            },
            'coaching_points': coaching_points[:8],  # More detailed recommendations
            'detailed_analysis': gemini_analysis,  # Full Gemini analysis
            'chat_context': f'Professional AI analysis of {total_events} match events with tactical insights, set piece analysis, and coaching recommendations',
            'metadata': {
                'match_id': match_id,
                'analysis_timestamp': datetime.now().isoformat(),
                'total_events_analyzed': total_events,
                'analysis_engine': 'Gemini 2.5 Pro'
            }
        }
        
        # Save enhanced coaching content
        output_path = data_dir / "ai_coach_content.json"
        with open(output_path, 'w') as f:
            json.dump(ai_coach_content, f, indent=2)
        
        print(f"✅ Professional AI coach content saved to: {output_path}")
        return ai_coach_content
    
    def format_professional_analysis(self, gemini_analysis: dict) -> str:
        """Format Gemini analysis into professional coaching content"""
        content_parts = []
        
        # Set Pieces Analysis
        if 'set_pieces' in gemini_analysis:
            set_pieces = gemini_analysis['set_pieces']
            content_parts.append("## 🎯 Set Piece Analysis")
            
            if 'corner_kicks' in set_pieces:
                ck = set_pieces['corner_kicks']
                content_parts.append(f"**Corner Kicks:** {ck.get('total_attempts', 0)} attempts, {ck.get('on_target', 0)} on target, {ck.get('goals', 0)} goals")
                content_parts.append(f"- {ck.get('analysis', 'No analysis available')}")
            
            if 'free_kicks' in set_pieces:
                fk = set_pieces['free_kicks']
                content_parts.append(f"**Free Kicks:** {fk.get('close_range_attempts', 0)} close-range, {fk.get('long_range_attempts', 0)} long-range, {fk.get('goals', 0)} goals")
                content_parts.append(f"- {fk.get('analysis', 'No analysis available')}")
            
            if 'penalties' in set_pieces:
                pen = set_pieces['penalties']
                content_parts.append(f"**Penalties:** {pen.get('awarded', 0)} awarded, {pen.get('scored', 0)} scored, {pen.get('missed', 0)} missed")
                content_parts.append(f"- {pen.get('analysis', 'No analysis available')}")
        
        # Team Tactical Analysis
        if 'tactical_patterns' in gemini_analysis:
            content_parts.append("\n## ⚔️ Tactical Analysis")
            
            for team_color in ['red_team', 'black_team']:
                if team_color in gemini_analysis['tactical_patterns']:
                    team_data = gemini_analysis['tactical_patterns'][team_color]
                    team_name = team_color.replace('_', ' ').title()
                    
                    content_parts.append(f"\n**{team_name}:**")
                    content_parts.append(f"- Formation: {team_data.get('dominant_formation', 'Unknown')}")
                    content_parts.append(f"- Attack Style: {team_data.get('attacking_style', 'Unknown')}")
                    content_parts.append(f"- Defense Style: {team_data.get('defensive_style', 'Unknown')}")
                    
                    strengths = team_data.get('strengths', [])
                    if strengths:
                        content_parts.append("- **Strengths:**")
                        for strength in strengths[:3]:  # Top 3
                            content_parts.append(f"  • {strength}")
                    
                    weaknesses = team_data.get('weaknesses', [])
                    if weaknesses:
                        content_parts.append("- **Areas for Improvement:**")
                        for weakness in weaknesses[:3]:  # Top 3
                            content_parts.append(f"  • {weakness}")
        
        # Spatial Analysis
        if 'spatial_analysis' in gemini_analysis:
            spatial = gemini_analysis['spatial_analysis']
            content_parts.append("\n## 🗺️ Spatial Analysis")
            
            active_areas = spatial.get('most_active_areas', [])
            if active_areas:
                content_parts.append(f"**Most Active Areas:** {', '.join(active_areas[:3])}")
            
            attack_patterns = spatial.get('attacking_patterns', [])
            if attack_patterns:
                content_parts.append("**Attack Patterns:**")
                for pattern in attack_patterns[:2]:
                    content_parts.append(f"- {pattern}")
        
        return "\n".join(content_parts)
    
    def format_analysis_content(self, red_strengths, black_strengths, red_weaknesses, black_weaknesses, key_insights):
        """Format analysis for web app display"""
        content_parts = []
        
        # Key strengths section
        if red_strengths or black_strengths:
            content_parts.append("### Key Strengths to Reinforce:")
            
            if red_strengths:
                top_red = red_strengths[0]
                content_parts.append(f"**Red Team {top_red['category'].replace('_', ' ').title()}:** Strong performance in this area with {top_red['frequency']} effective instances. This is working well and should be maintained.")
            
            if black_strengths:
                top_black = black_strengths[0]
                content_parts.append(f"**Black Team {top_black['category'].replace('_', ' ').title()}:** Effective execution with {top_black['frequency']} successful instances. Continue building on this strength.")
        
        # Areas for improvement
        if red_weaknesses or black_weaknesses:
            content_parts.append("\n### Areas for Improvement:")
            
            if red_weaknesses:
                top_red_weak = red_weaknesses[0]
                content_parts.append(f"**Red Team:** Work on {top_red_weak['category'].replace('_', ' ')} - showing {top_red_weak['frequency']} instances of difficulty in this area.")
            
            if black_weaknesses:
                top_black_weak = black_weaknesses[0]
                content_parts.append(f"**Black Team:** Focus on improving {top_black_weak['category'].replace('_', ' ')} - identified {top_black_weak['frequency']} problematic instances.")
        
        # Key insights
        if key_insights:
            content_parts.append("\n### Match Insights:")
            for insight in key_insights[:3]:  # Top 3 insights
                content_parts.append(f"• {insight}")
        
        return "\n".join(content_parts)

    def get_top_strengths(self, what_works: dict) -> list:
        """Get top 3 things that are working well"""
        sorted_strengths = sorted(what_works.items(), key=lambda x: x[1], reverse=True)
        return [{'category': cat, 'frequency': freq} for cat, freq in sorted_strengths[:3] if freq > 0]
    
    def get_top_weaknesses(self, what_doesnt_work: dict) -> list:
        """Get top 3 things that aren't working"""
        sorted_weaknesses = sorted(what_doesnt_work.items(), key=lambda x: x[1], reverse=True)
        return [{'category': cat, 'frequency': freq} for cat, freq in sorted_weaknesses[:3] if freq > 0]
    
    def get_dominant_play_style(self, play_styles: dict) -> dict:
        """Get the most frequently used play style"""
        if not play_styles:
            return {'style': 'unknown', 'frequency': 0}
        
        dominant_style = max(play_styles.items(), key=lambda x: x[1])
        return {'style': dominant_style[0], 'frequency': dominant_style[1]}
    
    def calculate_turnover_ratio(self, team_data: dict) -> dict:
        """Calculate turnover ratio (caused vs conceded)"""
        caused = team_data['turnovers_caused']
        conceded = team_data['turnovers_conceded']
        
        if conceded == 0:
            ratio = float('inf') if caused > 0 else 0
        else:
            ratio = round(caused / conceded, 2)
        
        return {
            'turnovers_caused': caused,
            'turnovers_conceded': conceded,
            'ratio': ratio,
            'assessment': 'positive' if ratio > 1 else 'negative' if ratio < 1 else 'neutral'
        }
    
    def generate_tactical_recommendations(self, effectiveness: dict) -> dict:
        """Generate specific tactical recommendations for each team"""
        recommendations = {
            'red_team': [],
            'black_team': []
        }
        
        for team in ['red_team', 'black_team']:
            team_data = effectiveness[team]
            team_name = team.replace('_', ' ').title()
            
            # Analyze strengths and build on them
            top_strengths = self.get_top_strengths(team_data['what_works'])
            if top_strengths:
                top_strength = top_strengths[0]['category'].replace('_', ' ')
                recommendations[team].append(f"Continue {top_strength} - this is working well")
            
            # Address weaknesses
            top_weaknesses = self.get_top_weaknesses(team_data['what_doesnt_work'])
            if top_weaknesses:
                top_weakness = top_weaknesses[0]['category'].replace('_', ' ')
                recommendations[team].append(f"Work on {top_weakness} - major area for improvement")
            
            # Turnover advice
            turnover_data = self.calculate_turnover_ratio(team_data)
            if turnover_data['assessment'] == 'negative':
                recommendations[team].append("Focus on ball retention - giving away possession too often")
            elif turnover_data['assessment'] == 'positive':
                recommendations[team].append("Excellent at winning ball back - keep up the pressing")
            
            # Play style advice
            play_style = self.get_dominant_play_style(team_data['play_styles'])
            if play_style['style'] != 'unknown':
                style_name = play_style['style'].replace('_', ' ')
                recommendations[team].append(f"Effective use of {style_name} - consider expanding this approach")
        
        return recommendations
    
    def generate_key_insights(self, effectiveness: dict) -> list:
        """Generate high-level insights about the match"""
        insights = []
        
        # Compare teams
        red_attacking = sum(effectiveness['red_team']['what_works'].values())
        black_attacking = sum(effectiveness['black_team']['what_works'].values())
        
        if red_attacking > black_attacking:
            insights.append("Red team more effective in attack - creating better chances")
        elif black_attacking > red_attacking:
            insights.append("Black team more effective in attack - creating better chances")
        else:
            insights.append("Both teams equally effective in attack - tight contest")
        
        # Turnover battle
        red_turnovers = effectiveness['red_team']['turnovers_caused']
        black_turnovers = effectiveness['black_team']['turnovers_caused'] 
        
        if red_turnovers > black_turnovers:
            insights.append("Red team winning the pressing battle - forcing more turnovers")
        elif black_turnovers > red_turnovers:
            insights.append("Black team winning the pressing battle - forcing more turnovers")
        
        # Play style contrast
        red_style = self.get_dominant_play_style(effectiveness['red_team']['play_styles'])
        black_style = self.get_dominant_play_style(effectiveness['black_team']['play_styles'])
        
        if (red_style['style'] != black_style['style'] and 
            red_style['style'] != 'unknown' and black_style['style'] != 'unknown'):
            red_name = red_style['style'].replace('_', ' ')
            black_name = black_style['style'].replace('_', ' ')
            insights.append(f"Tactical contrast: Red team using {red_name} vs Black team using {black_name}")
        
        return insights

def main():
    """Generate AI coach content for web app from match commentary"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python 5.5-coaching-insights.py <match-id>")
        print("Example: python 5.5-coaching-insights.py ballyclare-20250111")
        return
    
    match_id = sys.argv[1]
    analyzer = TacticalAnalyzer()
    ai_coach_content = analyzer.generate_coaching_insights(match_id)
    
    if ai_coach_content:
        print("\n🤖 AI COACH CONTENT GENERATED:")
        print(f"📝 Title: {ai_coach_content['current_analysis']['title']}")
        print(f"📊 Events analyzed: {ai_coach_content['metadata']['total_events_analyzed']}")
        print(f"💡 Coaching points: {len(ai_coach_content['coaching_points'])}")
        
        print("\n📋 TOP COACHING RECOMMENDATIONS:")
        for i, point in enumerate(ai_coach_content['coaching_points'][:3], 1):
            print(f"   {i}. {point}")
        
        print(f"\n✅ Ready for web app integration!")
        print(f"📄 Output: ai_coach_content.json")

if __name__ == "__main__":
    main()
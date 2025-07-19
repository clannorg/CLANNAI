#!/usr/bin/env python3
"""
Football Cost Tracker
Monitors API usage and costs for football analysis
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
from config import COST_SETTINGS, PATHS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FootballCostTracker:
    """
    Tracks costs and API usage for football analysis
    Compares with basketball costs and provides optimization insights
    """
    
    def __init__(self):
        """Initialize the cost tracker"""
        self.output_dir = PATHS["cost_output"]
        self.output_dir.mkdir(exist_ok=True)
        
        # Cost tracking data
        self.cost_data = {
            "analysis_date": datetime.now().isoformat(),
            "football_costs": {},
            "basketball_comparison": {},
            "optimization_suggestions": []
        }
    
    def analyze_events_costs(self) -> Dict[str, Any]:
        """Analyze costs from events analysis"""
        events_dir = PATHS["events_output"]
        
        if not events_dir.exists():
            logger.warning("Events output directory not found")
            return {}
        
        # Count analysis files
        analysis_files = list(events_dir.glob("events_analysis_*.json"))
        
        if not analysis_files:
            logger.warning("No events analysis files found")
            return {}
        
        # Calculate costs
        total_clips = len(analysis_files)
        total_api_calls = total_clips
        total_cost = total_clips * COST_SETTINGS["cost_per_clip"]
        
        return {
            "module": "events_analysis",
            "total_clips": total_clips,
            "api_calls": total_api_calls,
            "cost_per_clip": COST_SETTINGS["cost_per_clip"],
            "total_cost": total_cost,
            "processing_efficiency": "high"
        }
    
    def analyze_player_costs(self) -> Dict[str, Any]:
        """Analyze costs from player analysis"""
        player_dir = PATHS["player_output"]
        
        if not player_dir.exists():
            logger.warning("Player output directory not found")
            return {}
        
        # Count analysis files
        analysis_files = list(player_dir.glob("player_analysis_*.json"))
        
        if not analysis_files:
            logger.warning("No player analysis files found")
            return {}
        
        # Calculate costs
        total_clips = len(analysis_files)
        total_api_calls = total_clips
        total_cost = total_clips * COST_SETTINGS["cost_per_clip"]
        
        return {
            "module": "player_analysis",
            "total_clips": total_clips,
            "api_calls": total_api_calls,
            "cost_per_clip": COST_SETTINGS["cost_per_clip"],
            "total_cost": total_cost,
            "processing_efficiency": "high"
        }
    
    def analyze_tactical_costs(self) -> Dict[str, Any]:
        """Analyze costs from tactical analysis"""
        tactical_dir = PATHS["tactical_output"]
        
        if not tactical_dir.exists():
            logger.warning("Tactical output directory not found")
            return {}
        
        # Count analysis files
        analysis_files = list(tactical_dir.glob("formation_analysis_*.json"))
        
        if not analysis_files:
            logger.warning("No tactical analysis files found")
            return {}
        
        # Calculate costs (tactical uses more expensive model)
        total_clips = len(analysis_files)
        total_api_calls = total_clips
        # Tactical analysis uses 2.5 Flash model (more expensive)
        tactical_cost_per_clip = COST_SETTINGS["cost_per_clip"] * 1.5  # Estimate
        total_cost = total_clips * tactical_cost_per_clip
        
        return {
            "module": "tactical_analysis",
            "total_clips": total_clips,
            "api_calls": total_api_calls,
            "cost_per_clip": tactical_cost_per_clip,
            "total_cost": total_cost,
            "processing_efficiency": "medium"
        }
    
    def calculate_total_costs(self) -> Dict[str, Any]:
        """Calculate total costs across all modules"""
        events_costs = self.analyze_events_costs()
        player_costs = self.analyze_player_costs()
        tactical_costs = self.analyze_tactical_costs()
        
        total_cost = 0
        total_clips = 0
        total_api_calls = 0
        
        for costs in [events_costs, player_costs, tactical_costs]:
            if costs:
                total_cost += costs.get("total_cost", 0)
                total_clips += costs.get("total_clips", 0)
                total_api_calls += costs.get("api_calls", 0)
        
        return {
            "total_cost": total_cost,
            "total_clips": total_clips,
            "total_api_calls": total_api_calls,
            "modules": {
                "events": events_costs,
                "player": player_costs,
                "tactical": tactical_costs
            }
        }
    
    def compare_with_basketball(self) -> Dict[str, Any]:
        """Compare football costs with basketball costs"""
        football_costs = self.calculate_total_costs()
        
        # Basketball comparison (based on A2 results)
        basketball_data = {
            "total_cost": 0.0208,  # From A2 analysis
            "total_clips": 99,  # From A2 analysis
            "duration_minutes": 10,  # Basketball game duration
            "cost_per_minute": 0.00168
        }
        
        # Football data
        football_data = {
            "total_cost": football_costs["total_cost"],
            "total_clips": football_costs["total_clips"],
            "duration_minutes": 90,  # Football game duration
            "cost_per_minute": football_costs["total_cost"] / 90 if football_costs["total_cost"] > 0 else 0
        }
        
        # Calculate efficiency
        cost_efficiency = football_data["cost_per_minute"] / basketball_data["cost_per_minute"] if basketball_data["cost_per_minute"] > 0 else 0
        
        return {
            "basketball": basketball_data,
            "football": football_data,
            "comparison": {
                "cost_efficiency_ratio": cost_efficiency,
                "football_more_efficient": cost_efficiency < 1,
                "cost_difference_per_minute": football_data["cost_per_minute"] - basketball_data["cost_per_minute"]
            }
        }
    
    def generate_optimization_suggestions(self) -> List[str]:
        """Generate cost optimization suggestions"""
        suggestions = []
        
        # Check for processing efficiency
        total_costs = self.calculate_total_costs()
        
        if total_costs["total_clips"] > 0:
            cost_per_clip = total_costs["total_cost"] / total_costs["total_clips"]
            
            if cost_per_clip > COST_SETTINGS["cost_per_clip"] * 1.5:
                suggestions.append("Consider using more efficient API models for routine analysis")
            
            if total_costs["total_clips"] < COST_SETTINGS["estimated_clips_per_match"] * 0.5:
                suggestions.append("Increase clip sampling for better coverage")
            
            if total_costs["total_api_calls"] > total_costs["total_clips"] * 1.5:
                suggestions.append("Optimize API calls to reduce redundant requests")
        
        # Football-specific suggestions
        suggestions.append("Use tactical analysis selectively (most expensive module)")
        suggestions.append("Consider batch processing for large datasets")
        suggestions.append("Monitor rate limits to avoid API errors")
        
        return suggestions
    
    def generate_cost_report(self) -> Dict[str, Any]:
        """Generate comprehensive cost report"""
        logger.info("📊 Generating football cost analysis...")
        
        # Calculate all costs
        total_costs = self.calculate_total_costs()
        comparison = self.compare_with_basketball()
        suggestions = self.generate_optimization_suggestions()
        
        # Create comprehensive report
        report = {
            "analysis_date": datetime.now().isoformat(),
            "football_costs": total_costs,
            "basketball_comparison": comparison,
            "optimization_suggestions": suggestions,
            "cost_efficiency": {
                "football_cost_per_minute": comparison["football"]["cost_per_minute"],
                "basketball_cost_per_minute": comparison["basketball"]["cost_per_minute"],
                "efficiency_ratio": comparison["comparison"]["cost_efficiency_ratio"]
            }
        }
        
        # Save detailed report
        report_path = self.output_dir / "football_cost_analysis.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save comparison report
        comparison_path = self.output_dir / "cost_comparison.txt"
        with open(comparison_path, 'w') as f:
            f.write(self.create_comparison_text(comparison, suggestions))
        
        logger.info(f"✅ Cost analysis complete: {report_path}")
        return report
    
    def create_comparison_text(self, comparison: Dict[str, Any], suggestions: List[str]) -> str:
        """Create human-readable cost comparison"""
        text = "💰 FOOTBALL vs BASKETBALL COST COMPARISON\n"
        text += "=" * 50 + "\n\n"
        
        # Football costs
        football = comparison["football"]
        text += f"⚽ FOOTBALL ANALYSIS:\n"
        text += f"   Total Cost: ${football['total_cost']:.4f}\n"
        text += f"   Total Clips: {football['total_clips']}\n"
        text += f"   Duration: {football['duration_minutes']} minutes\n"
        text += f"   Cost per Minute: ${football['cost_per_minute']:.4f}\n\n"
        
        # Basketball costs
        basketball = comparison["basketball"]
        text += f"🏀 BASKETBALL ANALYSIS:\n"
        text += f"   Total Cost: ${basketball['total_cost']:.4f}\n"
        text += f"   Total Clips: {basketball['total_clips']}\n"
        text += f"   Duration: {basketball['duration_minutes']} minutes\n"
        text += f"   Cost per Minute: ${basketball['cost_per_minute']:.4f}\n\n"
        
        # Comparison
        comp = comparison["comparison"]
        text += f"📊 COMPARISON:\n"
        text += f"   Efficiency Ratio: {comp['cost_efficiency_ratio']:.2f}x\n"
        text += f"   Football More Efficient: {comp['football_more_efficient']}\n"
        text += f"   Cost Difference per Minute: ${comp['cost_difference_per_minute']:.4f}\n\n"
        
        # Suggestions
        text += f"💡 OPTIMIZATION SUGGESTIONS:\n"
        for i, suggestion in enumerate(suggestions, 1):
            text += f"   {i}. {suggestion}\n"
        
        return text

def main():
    """Main function for football cost tracking"""
    tracker = FootballCostTracker()
    
    print("💰 Football Cost Analysis")
    print("=" * 30)
    print(f"Output directory: {PATHS['cost_output']}")
    print()
    
    # Generate cost report
    report = tracker.generate_cost_report()
    
    if report:
        print(f"\n✅ Cost analysis complete!")
        print(f"📊 Total cost: ${report['football_costs']['total_cost']:.4f}")
        print(f"📈 Total clips: {report['football_costs']['total_clips']}")
        print(f"💰 Cost per minute: ${report['cost_efficiency']['football_cost_per_minute']:.4f}")
        
        # Print efficiency comparison
        efficiency = report['cost_efficiency']['efficiency_ratio']
        print(f"⚡ Efficiency vs Basketball: {efficiency:.2f}x")
        
        if efficiency < 1:
            print("✅ Football is more cost-efficient than basketball!")
        else:
            print("⚠️ Football is less cost-efficient than basketball")
    else:
        print("\n❌ Cost analysis failed")

if __name__ == "__main__":
    main() 
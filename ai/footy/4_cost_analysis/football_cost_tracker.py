#!/usr/bin/env python3
"""
Football Cost Tracker
Monitors API usage and costs for football analysis based on token consumption.
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
    Tracks costs and API usage for football analysis by reading detailed
    run logs from the gemini_runs directory.
    """
    
    def __init__(self):
        """Initialize the cost tracker"""
        self.output_dir = PATHS["cost_output"]
        self.output_dir.mkdir(exist_ok=True)
        self.gemini_runs_dir = Path.cwd() / "gemini_runs"

    def find_latest_run_file(self) -> Path:
        """Finds the most recent run file in the gemini_runs directory."""
        if not self.gemini_runs_dir.exists():
            logger.error(f"Gemini runs directory not found at: {self.gemini_runs_dir}")
            return None

        run_files = list(self.gemini_runs_dir.glob("*.json"))
        if not run_files:
            logger.error(f"No run files found in {self.gemini_runs_dir}")
            return None
            
        latest_file = max(run_files, key=lambda f: f.stat().st_mtime)
        logger.info(f"Found latest run file: {latest_file.name}")
        return latest_file

    def calculate_run_costs(self, run_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates total cost and other metrics from a run's metadata."""
        total_cost = 0
        total_input_tokens = 0
        total_output_tokens = 0
        total_tokens = 0
        model_usage = {}

        for call in run_data:
            model_name = call.get("model_name")
            if not model_name or model_name not in COST_SETTINGS["models"]:
                logger.warning(f"Cost settings for model '{model_name}' not found. Skipping call.")
                continue

            model_costs = COST_SETTINGS["models"][model_name]
            input_tokens = call.get("prompt_token_count", 0)
            output_tokens = call.get("candidates_token_count", 0)

            # Calculate cost for this specific call
            input_cost = (input_tokens / 1000) * model_costs["input_cost_per_1k_tokens"]
            output_cost = (output_tokens / 1000) * model_costs["output_cost_per_1k_tokens"]
            call_cost = input_cost + output_cost
            
            total_cost += call_cost
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            total_tokens += call.get("total_token_count", 0)

            # Track usage per model
            if model_name not in model_usage:
                model_usage[model_name] = {"api_calls": 0, "total_tokens": 0, "cost": 0}
            model_usage[model_name]["api_calls"] += 1
            model_usage[model_name]["total_tokens"] += call.get("total_token_count", 0)
            model_usage[model_name]["cost"] += call_cost

        return {
            "total_cost": total_cost,
            "total_clips_analyzed": len(run_data),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens_processed": total_tokens,
            "model_usage_summary": model_usage
        }

    def generate_cost_report(self) -> Dict[str, Any]:
        """Generate comprehensive cost report from the latest run file."""
        logger.info("📊 Generating football cost analysis from run log...")
        
        latest_run_file = self.find_latest_run_file()
        if not latest_run_file:
            return None

        try:
            with open(latest_run_file, 'r') as f:
                run_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error reading or parsing run file {latest_run_file}: {e}")
            return None

        if not run_data:
            logger.warning("Run file is empty. No costs to analyze.")
            return None

        cost_analysis = self.calculate_run_costs(run_data)
        
        # Add footage metrics (assuming 10s clips from analyzer)
        clip_duration_seconds = 10
        total_footage_seconds = cost_analysis["total_clips_analyzed"] * clip_duration_seconds
        total_footage_minutes = total_footage_seconds / 60
        cost_per_minute_footage = cost_analysis["total_cost"] / total_footage_minutes if total_footage_minutes > 0 else 0

        # Create comprehensive report
        report = {
            "analysis_date": datetime.now().isoformat(),
            "source_file": latest_run_file.name,
            "cost_analysis": cost_analysis,
            "footage_metrics": {
                "total_clips_analyzed": cost_analysis["total_clips_analyzed"],
                "clip_duration_seconds": clip_duration_seconds,
                "total_footage_seconds": total_footage_seconds,
                "total_footage_minutes": total_footage_minutes,
                "cost_per_minute_of_footage": cost_per_minute_footage
            }
        }
        
        # Create timestamped filenames for the output reports
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        json_report_filename = f"football_cost_analysis_{timestamp}.json"
        txt_summary_filename = f"cost_summary_{timestamp}.txt"

        # Save detailed report
        report_path = self.output_dir / json_report_filename
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Save summary report
        summary_path = self.output_dir / txt_summary_filename
        with open(summary_path, 'w') as f:
            f.write(self.create_summary_text(report))
        
        logger.info(f"✅ Cost analysis complete. Reports saved in {self.output_dir}")
        return report
    
    def create_summary_text(self, report: Dict[str, Any]) -> str:
        """Create human-readable cost summary."""
        cost_analysis = report["cost_analysis"]
        footage_metrics = report["footage_metrics"]
        
        text = "💰 FOOTBALL ANALYSIS COST & USAGE REPORT\n"
        text += "=" * 50 + "\n"
        text += f"Source File: {report['source_file']}\n"
        text += f"Analysis Date: {datetime.fromisoformat(report['analysis_date']).strftime('%Y-%m-%d %H:%M:%S')}\n"
        text += "-" * 50 + "\n\n"

        text += "📊 COST SUMMARY\n"
        text += f"   Total Cost: ${cost_analysis['total_cost']:.6f}\n"
        text += f"   Cost per Minute of Footage: ${footage_metrics['cost_per_minute_of_footage']:.6f}\n\n"
        
        text += "📹 FOOTAGE & CLIP METRICS\n"
        text += f"   Total Clips Analyzed: {footage_metrics['total_clips_analyzed']}\n"
        text += f"   Total Footage Duration: {footage_metrics['total_footage_minutes']:.2f} minutes\n\n"

        text += "🤖 API & TOKEN USAGE\n"
        for model, usage in cost_analysis["model_usage_summary"].items():
            text += f"   Model: {model}\n"
            text += f"     - API Calls: {usage['api_calls']}\n"
            text += f"     - Total Tokens: {usage['total_tokens']}\n"
            text += f"     - Calculated Cost: ${usage['cost']:.6f}\n"
        
        text += f"\n   Overall Input Tokens: {cost_analysis['total_input_tokens']}\n"
        text += f"   Overall Output Tokens: {cost_analysis['total_output_tokens']}\n"
        text += f"   Overall Total Tokens: {cost_analysis['total_tokens_processed']}\n"

        return text

def main():
    """Main function for football cost tracking"""
    tracker = FootballCostTracker()
    
    print("💰 Football Cost Analysis")
    print("=" * 30)
    print(f"Output directory: {PATHS['cost_output']}")
    print(f"Reading from: {tracker.gemini_runs_dir}")
    print()
    
    # Generate cost report
    report = tracker.generate_cost_report()
    
    if report:
        cost_analysis = report['cost_analysis']
        footage_metrics = report['footage_metrics']
        print(f"\n✅ Cost analysis complete!")
        print(f"Source File: {report['source_file']}")
        print(f"📊 Total cost: ${cost_analysis['total_cost']:.6f}")
        print(f"📈 Total clips analyzed: {footage_metrics['total_clips_analyzed']}")
        print(f"⏱️ Total footage analyzed: {footage_metrics['total_footage_minutes']:.2f} minutes")
        print(f"💰 Cost per minute of footage: ${footage_metrics['cost_per_minute_of_footage']:.6f}")
    else:
        print("\n❌ Cost analysis failed. Check logs for details.")

if __name__ == "__main__":
    main() 
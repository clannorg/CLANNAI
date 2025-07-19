#!/usr/bin/env python3
"""
Basketball Game Analysis Cost Calculator
Based on actual token usage data and current Google Gemini pricing
"""

import os
import json
import glob
from datetime import datetime
from typing import Dict, List, Tuple

# Current Google Gemini Pricing (as of July 2024)
GEMINI_PRICING = {
    "2.0_flash": {
        "input_cost_per_1m": 0.10,      # $0.10 per 1M input tokens
        "output_cost_per_1m": 0.40,     # $0.40 per 1M output tokens
        "rpm": 15,                      # Requests per minute
        "rpd": 200,                     # Requests per day
        "free_tier": {
            "input_cost_per_1m": 0.0005, # $0.0005 per 1M input tokens
            "output_cost_per_1m": 0.015, # $0.015 per 1M output tokens
        }
    },
    "2.5_flash": {
        "input_cost_per_1m": 0.30,
        "output_cost_per_1m": 2.50,
        "rpm": 10,
        "rpd": 250,
        "free_tier": {
            "input_cost_per_1m": 0.0005,
            "output_cost_per_1m": 0.015,
        }
    },
    "1.5_pro": {
        "input_cost_per_1m": 1.25,
        "output_cost_per_1m": 5.00,
        "rpm": 5,
        "rpd": 100,
        "free_tier": {
            "input_cost_per_1m": 0.0025,
            "output_cost_per_1m": 0.075,
        }
    }
}

# Actual token usage from your real testing data
ACTUAL_TOKEN_USAGE = {
    "input_tokens_per_clip": 2615,      # From your actual testing
    "output_tokens_per_clip": 45,       # From your actual testing
    "total_tokens_per_clip": 2660,      # From your actual testing
    "processing_time_per_clip": 6.3,    # Seconds from your actual testing
    "video_size_mb": 2.8,               # MB from your actual testing
}

class BasketballGameCostCalculator:
    def __init__(self, project_dir: str = "."):
        self.project_dir = project_dir
        self.output_dir = os.path.join(project_dir, "1_game_events", "output")
        
    def count_processed_clips(self) -> Dict[str, int]:
        """Count the number of processed clips from output directory"""
        json_files = glob.glob(os.path.join(self.output_dir, "events_analysis_*.json"))
        txt_files = glob.glob(os.path.join(self.output_dir, "events_analysis_*.txt"))
        
        # Exclude the combined file
        json_files = [f for f in json_files if "combined" not in f]
        
        return {
            "total_clips": len(json_files),
            "json_files": len(json_files),
            "txt_files": len(txt_files),
            "combined_files": len([f for f in json_files if "combined" in f])
        }
    
    def calculate_token_costs(self, model: str = "2.0_flash", use_free_tier: bool = True) -> Dict[str, float]:
        """Calculate costs based on actual token usage"""
        pricing = GEMINI_PRICING[model]
        
        if use_free_tier:
            input_cost_per_token = pricing["free_tier"]["input_cost_per_1m"] / 1_000_000
            output_cost_per_token = pricing["free_tier"]["output_cost_per_1m"] / 1_000_000
        else:
            input_cost_per_token = pricing["input_cost_per_1m"] / 1_000_000
            output_cost_per_token = pricing["output_cost_per_1m"] / 1_000_000
        
        input_cost = ACTUAL_TOKEN_USAGE["input_tokens_per_clip"] * input_cost_per_token
        output_cost = ACTUAL_TOKEN_USAGE["output_tokens_per_clip"] * output_cost_per_token
        total_cost_per_clip = input_cost + output_cost
        
        return {
            "input_cost_per_clip": input_cost,
            "output_cost_per_clip": output_cost,
            "total_cost_per_clip": total_cost_per_clip,
            "input_tokens": ACTUAL_TOKEN_USAGE["input_tokens_per_clip"],
            "output_tokens": ACTUAL_TOKEN_USAGE["output_tokens_per_clip"],
            "total_tokens": ACTUAL_TOKEN_USAGE["total_tokens_per_clip"]
        }
    
    def calculate_rate_limits(self, model: str = "2.0_flash") -> Dict[str, int]:
        """Get rate limits for the specified model"""
        pricing = GEMINI_PRICING[model]
        return {
            "requests_per_minute": pricing["rpm"],
            "requests_per_day": pricing["rpd"],
            "max_concurrent_requests": pricing["rpm"]
        }
    
    def calculate_processing_time(self, total_clips: int, model: str = "2.0_flash") -> Dict[str, float]:
        """Calculate total processing time considering rate limits"""
        rate_limits = self.calculate_rate_limits(model)
        time_per_clip = ACTUAL_TOKEN_USAGE["processing_time_per_clip"]
        
        # Sequential processing (respecting rate limits)
        total_time_sequential = total_clips * time_per_clip
        
        # Parallel processing (limited by rate limits)
        max_parallel = rate_limits["requests_per_minute"]
        batches = (total_clips + max_parallel - 1) // max_parallel  # Ceiling division
        total_time_parallel = batches * 60  # 60 seconds per batch
        
        return {
            "time_per_clip_seconds": time_per_clip,
            "total_time_sequential_minutes": total_time_sequential / 60,
            "total_time_parallel_minutes": total_time_parallel / 60,
            "max_parallel_requests": max_parallel,
            "total_batches": batches
        }
    
    def generate_cost_report(self, model: str = "2.0_flash", use_free_tier: bool = True) -> Dict:
        """Generate comprehensive cost report"""
        clip_counts = self.count_processed_clips()
        token_costs = self.calculate_token_costs(model, use_free_tier)
        rate_limits = self.calculate_rate_limits(model)
        processing_times = self.calculate_processing_time(clip_counts["total_clips"], model)
        
        # Calculate total costs
        total_cost = token_costs["total_cost_per_clip"] * clip_counts["total_clips"]
        
        # Calculate for different scenarios
        scenarios = {
            "current_game": {
                "clips": clip_counts["total_clips"],
                "cost": total_cost,
                "time_minutes": processing_times["total_time_parallel_minutes"]
            },
            "10_games": {
                "clips": clip_counts["total_clips"] * 10,
                "cost": total_cost * 10,
                "time_minutes": processing_times["total_time_parallel_minutes"] * 10
            },
            "100_games": {
                "clips": clip_counts["total_clips"] * 100,
                "cost": total_cost * 100,
                "time_minutes": processing_times["total_time_parallel_minutes"] * 100
            }
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "model": model,
            "tier": "free" if use_free_tier else "paid",
            "clip_analysis": clip_counts,
            "token_analysis": token_costs,
            "rate_limits": rate_limits,
            "processing_times": processing_times,
            "cost_scenarios": scenarios,
            "pricing_reference": {
                "input_cost_per_1m_tokens": GEMINI_PRICING[model]["input_cost_per_1m"],
                "output_cost_per_1m_tokens": GEMINI_PRICING[model]["output_cost_per_1m"],
                "free_tier_available": True
            }
        }
    
    def print_cost_report(self, model: str = "2.0_flash", use_free_tier: bool = True):
        """Print a formatted cost report"""
        report = self.generate_cost_report(model, use_free_tier)
        
        print("🏀 BASKETBALL GAME ANALYSIS COST REPORT")
        print("=" * 50)
        print(f"📅 Generated: {report['timestamp']}")
        print(f"🤖 Model: Gemini {model.replace('_', ' ').upper()}")
        print(f"💰 Tier: {report['tier'].upper()}")
        print()
        
        print("📊 GAME ANALYSIS SUMMARY")
        print("-" * 30)
        print(f"🎬 Total clips processed: {report['clip_analysis']['total_clips']}")
        print(f"📁 JSON analysis files: {report['clip_analysis']['json_files']}")
        print(f"📄 Text report files: {report['clip_analysis']['txt_files']}")
        print()
        
        print("💵 COST BREAKDOWN")
        print("-" * 30)
        print(f"📥 Input tokens per clip: {report['token_analysis']['input_tokens']:,}")
        print(f"📤 Output tokens per clip: {report['token_analysis']['output_tokens']:,}")
        print(f"📊 Total tokens per clip: {report['token_analysis']['total_tokens']:,}")
        print(f"💰 Cost per clip: ${report['token_analysis']['total_cost_per_clip']:.6f}")
        print()
        
        print("⏱️ PROCESSING TIMES")
        print("-" * 30)
        print(f"⏱️ Time per clip: {report['processing_times']['time_per_clip_seconds']:.1f} seconds")
        print(f"🔄 Max parallel requests: {report['processing_times']['max_parallel_requests']}")
        print(f"📦 Total batches needed: {report['processing_times']['total_batches']}")
        print(f"⏰ Total processing time: {report['processing_times']['total_time_parallel_minutes']:.1f} minutes")
        print()
        
        print("💰 COST SCENARIOS")
        print("-" * 30)
        for scenario, data in report['cost_scenarios'].items():
            scenario_name = scenario.replace('_', ' ').title()
            print(f"🎯 {scenario_name}:")
            print(f"   📊 Clips: {data['clips']:,}")
            print(f"   💵 Cost: ${data['cost']:.4f}")
            print(f"   ⏰ Time: {data['time_minutes']:.1f} minutes")
            print()
        
        print("🚦 RATE LIMITS")
        print("-" * 30)
        print(f"⚡ Requests per minute: {report['rate_limits']['requests_per_minute']}")
        print(f"📅 Requests per day: {report['rate_limits']['requests_per_day']}")
        print()
        
        print("💡 RECOMMENDATIONS")
        print("-" * 30)
        if report['tier'] == 'free':
            print("✅ Use free tier - incredibly cost-effective!")
        else:
            print("💳 Consider free tier for massive cost savings")
        
        if report['cost_scenarios']['current_game']['cost'] < 0.01:
            print("🎉 Current game analysis costs less than 1 cent!")
        elif report['cost_scenarios']['current_game']['cost'] < 0.10:
            print("🎯 Current game analysis costs less than 10 cents!")
        
        print("📈 Scale to 100+ games for comprehensive analysis")
        print("🔄 Use parallel processing to minimize total time")

def main():
    """Main function to run the cost calculator"""
    calculator = BasketballGameCostCalculator()
    
    print("🏀 Basketball Game Analysis Cost Calculator")
    print("=" * 50)
    print()
    
    # Generate reports for different models
    models = ["2.0_flash", "2.5_flash", "1.5_pro"]
    
    for model in models:
        print(f"\n{'='*20} {model.upper()} {'='*20}")
        calculator.print_cost_report(model, use_free_tier=True)
        
        # Also show paid tier for comparison
        if model == "2.0_flash":  # Only show paid for the recommended model
            print(f"\n{'='*20} {model.upper()} (PAID TIER) {'='*20}")
            calculator.print_cost_report(model, use_free_tier=False)
    
    # Save detailed report to JSON
    detailed_report = calculator.generate_cost_report("2.0_flash", use_free_tier=True)
    report_file = os.path.join(calculator.project_dir, "4_gemini_info", "cost_analysis_report.json")
    
    with open(report_file, 'w') as f:
        json.dump(detailed_report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")

if __name__ == "__main__":
    main() 
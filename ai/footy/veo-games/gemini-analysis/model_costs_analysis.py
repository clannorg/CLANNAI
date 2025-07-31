#!/usr/bin/env python3
"""
Veo Games - Gemini Model Cost Analysis
Analyzes costs and rates for different Gemini models to optimize video analysis pipeline
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

class VeoGeminiCostAnalyzer:
    """Analyzes costs and optimization for Gemini models in video analysis"""
    
    def __init__(self):
        """Initialize with current Gemini pricing (as of July 2024)"""
        
        # Current Gemini API Pricing (per 1M tokens)
        self.pricing = {
            # Gemini 2.0 Flash - FASTEST, CHEAPEST
            "gemini-2.0-flash": {
                "input_cost_per_1m": 0.10,    # $0.10 per 1M input tokens
                "output_cost_per_1m": 0.40,   # $0.40 per 1M output tokens
                "speed": "Fast",
                "video_support": True,
                "free_tier": "50 requests/day",
                "description": "Fastest, cheapest for video analysis"
            },
            "gemini-2.0-flash-exp": {
                "input_cost_per_1m": 0.10,    # Same as flash
                "output_cost_per_1m": 0.40,
                "speed": "Fast", 
                "video_support": True,
                "free_tier": "50 requests/day",
                "description": "Experimental version, potentially better video understanding"
            },
            
            # Gemini 2.5 Flash - MORE EXPENSIVE BUT BETTER
            "gemini-2.5-flash": {
                "input_cost_per_1m": 0.30,    # $0.30 per 1M input tokens
                "output_cost_per_1m": 2.50,   # $2.50 per 1M output tokens
                "speed": "Fast",
                "video_support": True,
                "free_tier": "50 requests/day",
                "description": "Better accuracy, 2.5x more expensive input, 6x output"
            },
            "gemini-2.5-flash-exp": {
                "input_cost_per_1m": 0.30,
                "output_cost_per_1m": 2.50,
                "speed": "Fast",
                "video_support": True, 
                "free_tier": "50 requests/day",
                "description": "Experimental 2.5, potentially best video understanding"
            },
            
            # Gemini 2.5 Pro - HIGHEST QUALITY, MOST EXPENSIVE
            "gemini-2.5-pro": {
                "input_cost_per_1m": 1.50,    # $1.50 per 1M input tokens
                "output_cost_per_1m": 7.50,   # $7.50 per 1M output tokens
                "speed": "Slow",
                "video_support": True,
                "free_tier": "50 requests/day",
                "description": "Highest quality, best for synthesis/insights"
            }
        }
        
        # Estimated token usage based on our pipeline
        self.token_estimates = {
            "video_analysis_prompt": 1000,    # Our football prompt
            "video_tokens_per_clip": 2000,    # 15s compressed video
            "typical_response": 150,          # Average response length
            "detailed_response": 300          # Longer event descriptions
        }
    
    def calculate_clip_cost(self, model: str, response_type: str = "typical") -> Dict[str, float]:
        """Calculate cost per clip for different models"""
        if model not in self.pricing:
            raise ValueError(f"Unknown model: {model}")
        
        pricing = self.pricing[model]
        
        # Input tokens: prompt + video
        input_tokens = self.token_estimates["video_analysis_prompt"] + self.token_estimates["video_tokens_per_clip"]
        
        # Output tokens based on response type
        output_tokens = self.token_estimates[f"{response_type}_response"]
        
        # Calculate costs
        input_cost = (input_tokens / 1_000_000) * pricing["input_cost_per_1m"]
        output_cost = (output_tokens / 1_000_000) * pricing["output_cost_per_1m"]
        total_cost = input_cost + output_cost
        
        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "input_cost": input_cost,
            "output_cost": output_cost,
            "total_cost_per_clip": total_cost,
            "model": model
        }
    
    def analyze_match_costs(self, num_clips: int = 360) -> Dict[str, Any]:
        """Analyze costs for full match analysis (360 clips = 90 minutes)"""
        
        results = {
            "match_duration_minutes": num_clips * 15 / 60,
            "total_clips": num_clips,
            "model_comparison": {}
        }
        
        print(f"💰 COST ANALYSIS FOR {num_clips} CLIPS ({results['match_duration_minutes']} minutes)")
        print("=" * 70)
        
        for model, pricing in self.pricing.items():
            clip_cost = self.calculate_clip_cost(model)
            total_cost = clip_cost["total_cost_per_clip"] * num_clips
            
            # Time estimates (assuming 8 clips per batch, 60s delay)
            if "flash" in model:
                processing_time_hours = (num_clips / 8) * (60 + 30) / 3600  # Batch time + processing
            else:
                processing_time_hours = (num_clips / 8) * (60 + 60) / 3600  # Slower processing
            
            model_analysis = {
                "cost_per_clip": clip_cost["total_cost_per_clip"],
                "total_match_cost": total_cost,
                "processing_time_hours": processing_time_hours,
                "cost_per_hour": total_cost / processing_time_hours if processing_time_hours > 0 else 0,
                "free_tier_clips": 50,  # All models have same free tier
                "paid_cost_after_free": max(0, total_cost - (50 * clip_cost["total_cost_per_clip"])),
                "description": pricing["description"]
            }
            
            results["model_comparison"][model] = model_analysis
            
            print(f"\n🤖 {model}")
            print(f"   Cost per clip: ${clip_cost['total_cost_per_clip']:.6f}")
            print(f"   Full match cost: ${total_cost:.2f}")
            print(f"   Free tier covers: {50} clips ({50*15/60:.1f} minutes)")
            print(f"   Cost after free: ${model_analysis['paid_cost_after_free']:.2f}")
            print(f"   Processing time: {processing_time_hours:.1f} hours")
            print(f"   {pricing['description']}")
        
        return results
    
    def recommend_model_strategy(self, budget: float = None, priority: str = "cost") -> Dict[str, Any]:
        """Recommend optimal model strategy based on budget and priorities"""
        
        print(f"\n🎯 MODEL RECOMMENDATIONS")
        print("=" * 50)
        
        recommendations = {
            "priority": priority,
            "budget": budget
        }
        
        if priority == "cost":
            print("💰 COST-OPTIMIZED STRATEGY:")
            print("   Primary: gemini-2.0-flash-exp")
            print("   - Cheapest option with experimental improvements")
            print("   - Free tier: 50 clips = 12.5 minutes")
            print("   - Best for: Initial testing, large-scale analysis")
            print("   ")
            print("   Synthesis: gemini-2.5-flash")
            print("   - Better for combining results into insights")
            print("   - Use only for final synthesis step")
            
            recommendations["primary_model"] = "gemini-2.0-flash-exp"
            recommendations["synthesis_model"] = "gemini-2.5-flash"
            
        elif priority == "accuracy":
            print("🎯 ACCURACY-OPTIMIZED STRATEGY:")
            print("   Primary: gemini-2.5-flash-exp")
            print("   - Better video understanding")
            print("   - 3x more expensive but higher quality")
            print("   ")
            print("   Synthesis: gemini-2.5-pro")
            print("   - Highest quality insights")
            print("   - Use for final analysis and reporting")
            
            recommendations["primary_model"] = "gemini-2.5-flash-exp" 
            recommendations["synthesis_model"] = "gemini-2.5-pro"
            
        elif priority == "hybrid":
            print("⚖️  HYBRID STRATEGY:")
            print("   Screening: gemini-2.0-flash-exp")
            print("   - Fast, cheap initial analysis")
            print("   - Filter for clips with potential events")
            print("   ")
            print("   Deep analysis: gemini-2.5-flash-exp")
            print("   - Only on flagged clips (20-30% of total)")
            print("   - Best accuracy where it matters")
            print("   ")
            print("   Synthesis: gemini-2.5-pro")
            print("   - Premium insights generation")
            
            recommendations["screening_model"] = "gemini-2.0-flash-exp"
            recommendations["analysis_model"] = "gemini-2.5-flash-exp"
            recommendations["synthesis_model"] = "gemini-2.5-pro"
        
        return recommendations
    
    def estimate_test_costs(self):
        """Estimate costs for our current 15-minute test"""
        print(f"\n🧪 CURRENT TEST ANALYSIS (60 clips, 15 minutes)")
        print("=" * 50)
        
        for model in ["gemini-2.0-flash-exp", "gemini-2.5-flash-exp"]:
            clip_cost = self.calculate_clip_cost(model)
            total_test_cost = clip_cost["total_cost_per_clip"] * 60
            
            print(f"\n{model}:")
            print(f"   60 clips cost: ${total_test_cost:.3f}")
            print(f"   Within free tier: {'✅ Yes' if 60 <= 50 else '❌ No, need paid API'}")
            if 60 > 50:
                paid_cost = clip_cost["total_cost_per_clip"] * (60 - 50)
                print(f"   Paid portion: ${paid_cost:.3f}")

def main():
    """Run comprehensive cost analysis for veo-games pipeline"""
    
    analyzer = VeoGeminiCostAnalyzer()
    
    print("🏈 VEO GAMES - GEMINI MODEL COST ANALYSIS")
    print("=" * 70)
    
    # Analyze different match lengths
    analyzer.analyze_match_costs(num_clips=60)    # 15 minutes test
    analyzer.analyze_match_costs(num_clips=240)   # 60 minutes 
    analyzer.analyze_match_costs(num_clips=360)   # 90 minutes full match
    
    # Test cost analysis
    analyzer.estimate_test_costs()
    
    # Strategy recommendations
    analyzer.recommend_model_strategy(priority="cost")
    analyzer.recommend_model_strategy(priority="accuracy")
    analyzer.recommend_model_strategy(priority="hybrid")
    
    # Save analysis
    output_dir = Path(__file__).parent
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    with open(output_dir / f"cost_analysis_{timestamp}.json", 'w') as f:
        analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "pricing": analyzer.pricing,
            "token_estimates": analyzer.token_estimates,
            "match_analysis": analyzer.analyze_match_costs(360),
            "recommendations": {
                "cost_optimized": analyzer.recommend_model_strategy(priority="cost"),
                "accuracy_optimized": analyzer.recommend_model_strategy(priority="accuracy"),
                "hybrid": analyzer.recommend_model_strategy(priority="hybrid")
            }
        }
        json.dump(analysis_data, f, indent=2)
    
    print(f"\n📊 Analysis saved to: cost_analysis_{timestamp}.json")

if __name__ == "__main__":
    main() 
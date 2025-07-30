# Veo Games - AI Football Analysis Pipeline

**Simple AI analysis pipeline: Veo URL → Complete match analysis**

## 🏗️ Project Structure

```
veo-games/
├── ai-pipeline/                # All processing scripts
│   ├── 1_extract_veo_data.py   # URL → veo_ground_truth.json
│   ├── 2_download_video.py     # URL → video.mp4  
│   ├── 3_generate_clips.py     # video → 15-second clips (FAST!)
│   ├── 3.5_compress_clips.py   # clips → API-optimized clips
│   ├── 4_gemini_clip_analyzer.py # analyze clips with batching
│   ├── 5_gemini_synthesis.py   # combine clips → match timeline
│   ├── 6_web_formatter.py      # timeline → web JSON
│   ├── 7_accuracy_evaluator.py # AI vs Veo comparison
│   └── run_match_pipeline.py   # Orchestrate everything
│
└── data/                       # Self-contained match folders
    ├── ballyclare-20250111/
    │   ├── source.json          # URL, metadata, teams
    │   ├── video.mp4            # Raw match video
    │   ├── veo_ground_truth.json # Veo events (truth)
    │   ├── clips/               # Video segments (stream copy)
    │   ├── compressed_clips/    # API-optimized clips
    │   ├── clip_analyses/       # AI analysis results
    │   ├── match_timeline.json  # Synthesized timeline
    │   ├── web_format.json      # Website-ready JSON
    │   └── accuracy_evaluation.json # AI vs Veo metrics
    │
    └── [other-matches]/
```

## 🔄 Pipeline Workflow

### Simple Flow
**Input**: Veo URL  
**Command**: `python ai-pipeline/run_match_pipeline.py <veo-url>`  
**Output**: Complete self-contained match folder in ~50 minutes

### What Happens (Optimized)
1. **Extract Veo Data**: Gets ground truth events from Veo API
2. **Download Video**: Downloads match video from Veo
3. **Generate Clips**: Ultra-fast stream copying (no re-encoding) - ~2 minutes
4. **Compress Clips**: Parallel compression for API efficiency - ~5 minutes
5. **Gemini Analysis**: Batch processing with gemini-2.5-pro for 100% accuracy - ~40 minutes
6. **Synthesis**: Combines all clip analyses into match timeline
7. **Web Formatter**: Converts timeline to website JSON
8. **Accuracy Evaluation**: Compares AI vs Veo results

## 🚀 Usage

### Setup
```bash
# Install dependencies
pip install google-generativeai python-dotenv opencv-python

# Set up environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Analyze Single Match
```bash
# One command does everything (now ~50 minutes instead of hours!)
python ai-pipeline/run_match_pipeline.py "https://app.veo.co/matches/20250111-ballyclare-425e4c3f/"

# Result: Complete analysis in data/ballyclare-20250111/
```

### Individual Steps (Optional)
```bash
# If you want to run steps manually
python ai-pipeline/1_extract_veo_data.py <veo-url>
python ai-pipeline/2_download_video.py <veo-url>
python ai-pipeline/3_generate_clips.py <match-id>
python ai-pipeline/3.5_compress_clips.py <match-id>
python ai-pipeline/4_gemini_clip_analyzer.py <match-id>
python ai-pipeline/5_gemini_synthesis.py <match-id>
python ai-pipeline/6_web_formatter.py <match-id>
python ai-pipeline/7_accuracy_evaluator.py <match-id>
```

## 📊 Output Structure

Each match gets a complete folder with everything:

```
data/match-id/
├── source.json              # Match metadata
├── video.mp4               # Full match video
├── veo_ground_truth.json   # Veo's event data (truth)
├── clips/                  # 15-second video segments
│   ├── clip_0001.mp4       # Raw clips (stream copy)
│   ├── clip_0002.mp4
│   └── segments.json       # Clips metadata
├── compressed_clips/       # API-optimized clips
│   ├── compressed_clip_0001.mp4  # 640x480, optimized
│   ├── compressed_clip_0002.mp4
│   └── compression_info.json     # Compression stats
├── clip_analyses/          # Individual clip analysis
│   ├── clip_0001_analysis.json
│   ├── clip_0002_analysis.json
│   └── ...
├── match_timeline.json     # Synthesized match events
├── web_format.json         # Website-ready data
└── accuracy_evaluation.json # AI vs Veo comparison
```

## ⚡ Performance Optimizations

### Ultra-Fast Video Processing
- **Stream Copying**: No re-encoding for clip generation (10x faster)
- **Parallel Compression**: 4 threads for API optimization
- **Smart Batching**: Processes clips in groups to avoid rate limits

### Gemini API Optimization
- **Batch Processing**: 8 clips per batch with 60s delays
- **Parallel Workers**: 4 concurrent analyses per batch
- **Video Compression**: 640x480 resolution for faster uploads
- **Football-Specific Prompts**: Optimized for football event detection

### Processing Speed
- **Full Pipeline**: ~50 minutes (vs hours previously)
- **Video Clipping**: ~2 minutes for 90-minute match
- **Compression**: ~5 minutes parallel processing
- **AI Analysis**: ~40 minutes with rate limiting

## 📋 Example Output

### Web Format JSON
```json
{
  "match_id": "ballyclare-20250111",
  "teams": ["Ballyclare", "Opponent"],
  "final_score": {"home": 3, "away": 1},
  "ai_events": 18,
  "veo_events": 20,
  "accuracy": 91.2,
  "processing_stats": {
    "compression_ratio": 68.5,
    "clips_processed": 360,
    "total_time_minutes": 52
  },
  "events": [
    {
      "timestamp": "36:39",
      "type": "SHOT_ON_GOAL",
      "team": "home",
      "ai_confidence": 0.94,
      "description": "Player #10 takes shot from penalty area - SAVED"
    }
  ]
}
```

### Processing Statistics
```json
{
  "compression_stats": {
    "overall_compression_ratio": 68.5,
    "compression_speed_clips_per_second": 12.3,
    "total_original_size_mb": 2450.0,
    "total_compressed_size_mb": 771.5
  }
}
```

## 🎯 Goals

- **Fast**: Optimized pipeline completes in ~50 minutes
- **Efficient**: Stream copying + parallel processing + smart compression
- **Accurate**: Compare AI vs established Veo platform
- **Self-contained**: Everything for a match in one folder
- **Web-ready**: JSON formatted for website consumption
- **Scalable**: Process multiple matches efficiently

## 🔧 Requirements

- Python 3.8+
- FFmpeg (video processing)
- Gemini AI API key
- Dependencies: `google-generativeai`, `python-dotenv`, `opencv-python`

## 💡 Key Improvements

### From bball Pipeline
- **Ultra-fast clipping**: Stream copying instead of re-encoding
- **Parallel processing**: ThreadPoolExecutor for all video operations
- **Batch API calls**: Rate limiting with smart delays
- **Optimized prompts**: Plain text responses for reliability
- **Compression pipeline**: API-optimized video format

### Football-Specific
- **Event Detection**: Goals, shots, tackles, passes, fouls, set pieces
- **Field Position**: Penalty area, attacking third, center circle
- **Team Analysis**: Jersey colors, player movements
- **Match Context**: Timeline integration with Veo ground truth

---

**URL → Complete Football Analysis in ~50 Minutes! ⚽🤖** 
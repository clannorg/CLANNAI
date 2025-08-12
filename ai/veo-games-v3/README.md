# VEO Games v3 - Clean MEGA Pipeline

**Clean, simplified pipeline using Gemini MEGA analyzer**

## Pipeline Flow

1. **`1_fetch_veo.py`** - Download match metadata from VEO
2. **`2_download_video.py`** - Download video file  
3. **`3_make_clips.py`** - Split video into 15-second clips
4. **`mega_analyzer.py`** - 🧠 **MEGA GEMINI** (replaces steps 4-11 from v2)
   - Analyzes all clips in one context-aware call
   - Generates events, tactical analysis, accuracy metrics
5. **`10_s3_uploader.py`** - Upload all outputs to S3
6. **`12_write_metadata.py`** - Generate match metadata JSON

## Key Outputs

- `web_events_array.json` - Events for webapp UI
- `11_tactical_analysis.json` - Tactical insights  
- `mega_analysis.json` - Complete analysis
- `match_metadata.json` - Game metadata for dashboard
- `s3_locations.json` - S3 upload URLs

## Usage

```bash
cd /Users/thomasbradley/CLANNAI/ai/veo-games-v3/pipeline

# Run full pipeline
python3 1_fetch_veo.py <veo-url>
python3 2_download_video.py <match-id>  
python3 3_make_clips.py <match-id>
python3 mega_analyzer.py <match-id>
python3 10_s3_uploader.py <match-id>
python3 12_write_metadata.py <match-id>
```

## Difference from v2

- **v2**: 14-step pipeline with many manual validation scripts
- **v3**: 6-step pipeline with single MEGA analyzer doing the heavy lifting
- **Cleaner**: No mixed pipelines, no confusion about which ran
- **Same outputs**: Compatible with existing webapp
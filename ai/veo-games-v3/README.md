# VEO Games v3 - Clean MEGA Pipeline

**Clean, simplified pipeline using Gemini MEGA analyzer**

## Pipeline Flow

1. **`1_fetch_veo.py`** - Download match metadata from VEO
2. **`2_download_video.py`** - Download video file  
3. **`3_make_clips.py`** - Split video into 15-second clips
4. **`mega_analyzer.py`** - 🧠 **MEGA GEMINI** (replaces steps 4-11 from v2)
   - Analyzes all clips in one context-aware call
   - Outputs natural language analysis in plain text files
5. **`format_for_webapp.py`** - 📊 **WEBAPP FORMATTER** 
   - Converts mega analyzer plain text outputs to webapp JSON formats
   - Generates web_events_array.json, 11_tactical_analysis.json
6. **`10_s3_uploader.py`** - Upload all outputs to S3
7. **`12_write_metadata.py`** - Generate match metadata JSON

## Key Outputs

**Plain text (from mega analyzer):**
- `mega_events.txt` - Natural language event descriptions
- `mega_tactical.txt` - Tactical analysis in plain text
- `mega_summary.txt` - Match overview and context

**JSON (from formatter):**
- `web_events_array.json` - Events for webapp UI
- `11_tactical_analysis.json` - Tactical insights  
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
python3 format_for_webapp.py <match-id>
python3 10_s3_uploader.py <match-id>
python3 12_write_metadata.py <match-id>
```

## Difference from v2

- **v2**: 14-step pipeline with many manual validation scripts
- **v3**: 6-step pipeline with single MEGA analyzer doing the heavy lifting
- **Cleaner**: No mixed pipelines, no confusion about which ran
- **Same outputs**: Compatible with existing webapp
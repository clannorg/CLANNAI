# Pipeline Scripts

This directory contains all the processing scripts for the VEO Games V5 analysis pipeline.

## 🔄 Script Execution Order

### Phase 1: Setup & Data Collection
```bash
1.0_webid.py          # Link to website game (run first for uploads)
1.1_fetch_veo.py      # Fetch VEO match data
1.2_download_video.py # Download match video
1.3_setup_teams.py    # Configure teams and jersey colors
```

### Phase 2: Analysis Generation
```bash
1.4_make_clips.py         # Extract video clips
1.5_analyze_clips.py      # AI analysis of clips
1.6_synthesis.py          # Create complete timeline
2.5_events_synthesizer.py # Generate match narrative with VEO validation
```

### Phase 3: Web Integration
```bash
3.1_format_webapp.py      # Format for web display
3.2_tactical_formatter.py # Create tactical analysis JSON
3.5_s3_uploader.py        # Upload to S3 cloud storage
3.7_api_upload.py         # Push to website database
```

### Utilities
```bash
3.4_check_db_contents.py  # Verify database contents
3.6_upload_to_db.py       # Direct DB upload (deprecated)
```

## 🚀 Quick Commands

### Full Analysis (New Match)
```bash
python3 1.1_fetch_veo.py <veo-url>
python3 1.2_download_video.py <match-id>
python3 1.3_setup_teams.py <match-id>
python3 1.4_make_clips.py <match-id>
python3 1.5_analyze_clips.py <match-id>
python3 1.6_synthesis.py <match-id>
python3 2.5_events_synthesizer.py <match-id>
python3 3.1_format_webapp.py <match-id>
python3 3.2_tactical_formatter.py <match-id>
python3 1.0_webid.py <match-id>
python3 3.5_s3_uploader.py <match-id>
python3 3.7_api_upload.py <match-id> --no-auth --base-url http://localhost:3002
```

### Upload Only (Analysis Complete)
```bash
python3 1.0_webid.py <match-id>
python3 3.5_s3_uploader.py <match-id>
python3 3.7_api_upload.py <match-id> --no-auth --base-url http://localhost:3002
```

### Verify Upload
```bash
python3 3.4_check_db_contents.py <match-id>
```

## 📝 Script Details

Each script is self-contained and includes:
- Command-line argument parsing
- Error handling and validation
- Progress indicators
- Output file generation

All scripts follow the naming convention: `<phase>.<step>_<description>.py`

## 🔧 Configuration

Scripts read configuration from:
- Environment variables (API keys, database URLs)
- Generated config files (team_config.json)
- VEO ground truth data (1_veo_ground_truth.json)

## 📊 Output Structure

Each script generates numbered output files matching its script number:
- `1.3_setup_teams.py` → `1_team_config.json`
- `3.1_format_webapp.py` → `3.1_web_events_array.json`
- `3.2_tactical_formatter.py` → `3.2_tactical_analysis.json`

This ensures clear traceability from script to output file.

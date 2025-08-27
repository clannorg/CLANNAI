# VEO Games V5 Pipeline

**Complete Football Match Analysis System** - From VEO URL to Website Integration

## 🎯 Overview

The VEO Games V5 pipeline is a comprehensive football match analysis system that:
- Fetches match data from VEO platform
- Generates AI-powered tactical analysis using Gemini
- Validates events against VEO ground truth
- Formats data for web application display
- Automatically uploads to S3 and website database

## 🏗️ Architecture

```
VEO Match URL → Video Download → Clip Analysis → Event Synthesis → Web Integration
     ↓              ↓              ↓              ↓              ↓
  1.1_fetch_veo  1.2_download   1.4_make_clips  2.5_events    3.1_format_webapp
                    ↓              ↓           synthesizer        ↓
                1.3_setup_teams  1.5_analyze     ↓           3.2_tactical
                    ↓            clips         1.6_synthesis  formatter
                1.0_webid.py        ↓              ↓              ↓
                    ↓          Complete Timeline  ↓         3.5_s3_uploader
                Link to Website     ↓              ↓              ↓
                                   AI Analysis    ↓         3.7_api_upload
                                                 ↓              ↓
                                            Website Ready   Database Updated
```

## 📋 Prerequisites

### Environment Setup
```bash
conda activate hooper-ai
pip install -r requirements.txt
```

### Required Environment Variables
```bash
export GEMINI_API_KEY="your_gemini_api_key"
export DATABASE_URL="postgresql://user:pass@host:port/db"
```

### AWS S3 Configuration
- AWS credentials configured (`aws configure`)
- S3 bucket: `end-nov-webapp-clann`
- Region: `eu-west-1`

## 🚀 Quick Start

### Complete Analysis Workflow
```bash
# 1. Setup match and teams
python3 1.1_fetch_veo.py <veo-match-url>
python3 1.2_download_video.py <match-id>
python3 1.3_setup_teams.py <match-id>

# 2. Generate analysis
python3 1.4_make_clips.py <match-id>
python3 1.5_analyze_clips.py <match-id>
python3 1.6_synthesis.py <match-id>
python3 2.5_events_synthesizer.py <match-id>

# 3. Format for web
python3 3.1_format_webapp.py <match-id>
python3 3.2_tactical_formatter.py <match-id>

# 4. Upload to website
python3 1.0_webid.py <match-id>           # Link to existing game
python3 3.5_s3_uploader.py <match-id>     # Upload to S3
python3 3.7_api_upload.py <match-id> --no-auth --base-url http://localhost:3002
```

### Quick Upload (Analysis Already Done)
```bash
python3 1.0_webid.py <match-id>
python3 3.5_s3_uploader.py <match-id>
python3 3.7_api_upload.py <match-id> --no-auth --base-url http://localhost:3002
```

## 📁 Pipeline Scripts

### Phase 1: Data Collection
- **`1.0_webid.py`** - Link pipeline match to website game ID
- **`1.1_fetch_veo.py`** - Fetch match metadata from VEO
- **`1.2_download_video.py`** - Download match video
- **`1.3_setup_teams.py`** - Configure team information and jersey colors

### Phase 2: Analysis Generation  
- **`1.4_make_clips.py`** - Extract video clips from match
- **`1.5_analyze_clips.py`** - AI analysis of individual clips
- **`1.6_synthesis.py`** - Synthesize clips into complete timeline
- **`2.5_events_synthesizer.py`** - Generate comprehensive match narrative with VEO validation

### Phase 3: Web Integration
- **`3.1_format_webapp.py`** - Format events for web application
- **`3.2_tactical_formatter.py`** - Create rich tactical analysis JSON
- **`3.5_s3_uploader.py`** - Upload all files to S3 cloud storage
- **`3.7_api_upload.py`** - Push analysis to website via API

### Utilities
- **`3.4_check_db_contents.py`** - Verify database contents
- **`3.6_upload_to_db.py`** - Direct database upload (deprecated - use 3.7)

## 📊 Output Files

### Generated Analysis Files
```
outputs/<match-id>/
├── 1_team_config.json              # Team setup and jersey colors
├── 1_veo_ground_truth.json         # VEO verified events
├── 1.6_complete_timeline.txt       # Full match timeline
├── 2.5_mega_events.txt            # Comprehensive event narrative
├── 2.5_mega_tactical.txt          # Tactical insights
├── 2.5_mega_summary.txt           # Match summary
├── 3.1_web_events_array.json     # Events formatted for website
├── 3.1_match_metadata.json       # Match metadata
├── 3.2_tactical_analysis.json    # Rich tactical analysis
├── 3.5_s3_locations.json         # S3 upload manifest
├── website_game_id.txt            # Linked website game ID
└── 4_clip_descriptions/           # Individual clip analyses
```

## 🔧 Key Features

### VEO Ground Truth Validation
- Only counts goals/events verified by VEO
- Prevents AI hallucinations
- Ensures accurate match statistics

### Team Attribution System
- Maps jersey colors to team names
- Handles complex kit combinations
- Consistent team identification throughout analysis

### Rich Tactical Analysis
- Formation analysis
- Player movement patterns
- Key tactical moments
- Strategic insights

### Automated Web Integration
- S3 cloud storage
- Database updates via API
- No manual upload required
- Test endpoints for development

## 🌐 Website Integration

### API Endpoints Used
- **Events**: `/api/games/:id/upload-analysis-file-test`
- **Metadata**: `/api/games/:id/upload-metadata-test`  
- **Tactical**: `/api/games/:id/upload-tactical-test`

### Database Schema
- **`ai_analysis`** - Events JSON array
- **`tactical_analysis`** - Tactical insights JSON
- **`metadata`** - Match metadata and S3 file locations
- **`metadata_url`** - Direct metadata file URL

## 🐛 Troubleshooting

### Common Issues

**Missing VEO Data**
```bash
# Check VEO ground truth file exists
ls outputs/<match-id>/1_veo_ground_truth.json
```

**API Upload Failures**
```bash
# Check backend is running on correct port
lsof -i :3002

# Verify game ID linking
python3 3.4_check_db_contents.py <match-id>
```

**S3 Upload Issues**
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify S3 bucket access
aws s3 ls s3://end-nov-webapp-clann/
```

### Debug Commands
```bash
# Check pipeline output
python3 3.4_check_db_contents.py <match-id>

# Verify S3 uploads
cat outputs/<match-id>/3.5_s3_core_locations.json

# Test API connectivity
curl http://localhost:3002/api/health
```

## 📈 Performance

### Typical Processing Times
- **Video Download**: 2-5 minutes
- **Clip Generation**: 5-10 minutes  
- **AI Analysis**: 15-30 minutes
- **Web Upload**: 30 seconds

### Resource Requirements
- **Storage**: ~2GB per match (video + clips)
- **Memory**: 4GB+ recommended
- **API Calls**: ~200 Gemini requests per match

## 🔒 Security

### API Keys
- Store in environment variables
- Never commit to version control
- Use separate keys for dev/prod

### Database Access
- Company role required for uploads
- Test endpoints for development
- Authentication tokens for production

## 📝 Development

### Adding New Analysis Types
1. Create analysis script in pipeline/
2. Add output format to OUTPUT_FORMATS.md
3. Update S3 uploader to include new files
4. Add API endpoint if needed

### Modifying Team Detection
- Update `1.3_setup_teams.py`
- Modify jersey color mapping
- Test with various kit combinations

## 🎯 Future Enhancements

- [ ] Real-time analysis streaming
- [ ] Multi-camera angle support
- [ ] Player tracking integration
- [ ] Advanced tactical visualizations
- [ ] Automated highlight generation

## 📞 Support

For issues or questions:
1. Check troubleshooting section
2. Verify all prerequisites are met
3. Check pipeline logs for errors
4. Ensure VEO ground truth data is available

---

**Built with ❤️ for football tactical analysis**
# VM Auto-Upload Setup Guide

## 🔧 One-Time Setup

### 1. Set API Token on VM
```bash
# Add to your VM's ~/.bashrc or ~/.zshrc
export CLANNAI_API_TOKEN="your_company_api_token_here"

# Or create a .env file in the pipeline directory
echo "CLANNAI_API_TOKEN=your_token_here" > /home/ubuntu/CLANNAI/ai/veo-games-v4/pipeline/.env
```

### 2. Install Required Python Package
```bash
conda activate hooper-ai
pip install requests
```

### 3. Update API Endpoint (if needed)
Edit `3.3_auto_upload.py` line 15:
```python
self.api_base = "https://your-domain.com/api"  # Update with your actual domain
```

## 🚀 Usage

### New Workflow (Automated)
```bash
cd /home/ubuntu/CLANNAI/ai/veo-games-v4/pipeline
conda activate hooper-ai

# Run full pipeline
python3 1.1_fetch_veo.py "https://app.veo.co/matches/your-match-url/"
python3 1.2_download_video.py <match-id>
python3 1.3_setup_match.py <match-id>
python3 1.4_make_clips.py <match-id>
python3 1.5_analyze_clips.py <match-id>
python3 1.6_synthesis.py <match-id>
python3 2.1_mega_analyzer.py <match-id>
python3 2.2_format_for_webapp.py <match-id>
python3 3.1_write_metadata.py <match-id>
python3 3.2_s3_uploader.py <match-id>

# NEW: Interactive upload to website
python3 3.3_auto_upload.py <match-id>
```

### What the Auto-Upload Does
1. **Fetches your recent games** from the website
2. **Shows interactive menu** with game titles and status
3. **You select** which game to upload to (or create new)
4. **Automatically uploads** all analysis files to the database
5. **Confirms success** with direct link to view the game

### Example Output
```
🎮 CLANNAI - Game Selection
========================
📋 Select a game to upload analysis to:

[1] Cookstown Youth vs Bourneview YM (Created: 2 hours ago) [EMPTY]
[2] East London Ballers Match (Created: 1 day ago) [HAS DATA] 
[3] Green Island FC Analysis (Created: 3 days ago) [HAS DATA]

[N] Create new game instead
[Q] Quit

Enter your choice (1-3, N, Q): 1

📤 Uploading analysis to game 09e614b8...
📊 Uploading events data...
✅ Events uploaded successfully
🧠 Uploading tactical analysis...
✅ Tactical analysis uploaded successfully
🎬 Updating video URL...
✅ Game metadata updated successfully

🎉 SUCCESS!
📊 Analysis uploaded to game: 09e614b8...
🌐 View at: https://clannai.com/games/09e614b8-6d5a-4abe-9ad8-c3180a1d56e4
```

## 🔒 Security Notes

- **API Token**: Keep your token secure, don't commit to git
- **Company Role**: Script requires company-level permissions
- **HTTPS**: All API calls use secure HTTPS connections

## 🐛 Troubleshooting

### "CLANNAI_API_TOKEN environment variable not set"
```bash
# Check if token is set
echo $CLANNAI_API_TOKEN

# Set it temporarily
export CLANNAI_API_TOKEN="your_token_here"
```

### "Failed to fetch games: 401"
- Your API token is invalid or expired
- Get a new token from the website settings

### "Network error fetching games"
- Check internet connection on VM
- Verify API endpoint URL is correct
- Check if website is accessible from VM

### "File not found" errors
- Make sure you've run the full pipeline first
- Check that `s3_locations.json` exists in outputs directory
- Verify S3 upload completed successfully


#!/bin/bash
set -e
source ~/.bashrc
conda activate hooper-ai

# Get latest match ID (we already ran step 1)
MATCH_ID=$(ls -t ../data/*/1_veo_ground_truth.json | head -1 | xargs dirname | xargs basename)
echo "🎯 Processing match: $MATCH_ID"
python 2_download_video.py "$MATCH_ID"
python 3_generate_clips.py "$MATCH_ID"
python 4_simple_clip_analyzer.py "$MATCH_ID"
python 5_synthesis.py "$MATCH_ID"
python 6_goals_shots_validator.py "$MATCH_ID"
python 7_accuracy_evaluator.py "$MATCH_ID"
python 8_tactical_analyst.py "$MATCH_ID"
python 9_convert_to_web_format.py "$MATCH_ID"
python 10_s3_uploader.py "$MATCH_ID"
python 11_simple_s3_urls.py "$MATCH_ID"
python 12_complete_s3_list.py "$MATCH_ID"
echo "🎉 DONE! Check ../data/$MATCH_ID/ for files"

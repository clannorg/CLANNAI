#!/bin/bash

echo "🏀 BASKETBALL EVENTS ANALYSIS PIPELINE"
echo "======================================"
echo "Choose your analysis:"
echo "1) Compressed Analysis (640x480)"
echo "2) High-Quality Analysis (1920x1080) - RECOMMENDED"
echo "3) Player Profiling"
echo "4) Player Tracking"
echo "5) Accuracy Evaluation"
echo "6) Full High-Quality Pipeline"
echo "7) Full Compressed Pipeline"
echo ""
read -p "Enter your choice (1-7): " choice

case $choice in
    1)
        echo "Running compressed analysis..."
        python 1_game_events/events_clip_analyzer.py
        python 1_game_events/events_synthesis.py
        python 1_game_events/basketball_json_converter.py
        ;;
    2)
        echo "Running high-quality analysis..."
        python 1_game_events/events_clip_analyzer_hq.py
        python 1_game_events/events_synthesis.py
        python 1_game_events/basketball_json_converter.py
        ;;
    3)
        echo "Running player profiling..."
        python 2_player_profiling/player_clip_analyzer.py
        python 2_player_profiling/player_synthesis.py
        ;;
    4)
        echo "Running player tracking..."
        python 3_player_analysis/tracking_clip_analyzer.py
        python 3_player_analysis/tracking_synthesis.py
        ;;
    5)
        echo "Running accuracy evaluation..."
        python 1.5_accuracy_eval/accuracy_evaluation.py
        python 1.5_accuracy_eval/llm_accuracy_evaluator.py
        ;;
    6)
        echo "Running full high-quality pipeline..."
        python 1_game_events/events_clip_analyzer_hq.py && python 1_game_events/events_synthesis.py && python 1_game_events/basketball_json_converter.py
        ;;
    7)
        echo "Running full compressed pipeline..."
        python 1_game_events/events_clip_analyzer.py && python 1_game_events/events_synthesis.py && python 1_game_events/basketball_json_converter.py
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "✅ Analysis complete!"
echo "📁 Check output files in synthesis_output/" 
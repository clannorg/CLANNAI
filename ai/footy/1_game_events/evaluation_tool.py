#!/usr/bin/env python3
"""
Event Evaluation Tool
Compares the synthesized event timeline with manual annotations to assess accuracy
and saves a detailed comparison log.
"""

import csv
import json
from pathlib import Path
import logging
import argparse
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
# Time window (in seconds) to consider an event a match
TIME_TOLERANCE = 10.0
# Events from manual annotations that should not be included in accuracy reports
NON_EVALUABLE_EVENTS = {'intro', 'walk', 'wave', 'end', 'fulltime'}
# ---

class EvaluationTool:
    """
    Compares AI-generated event timeline with manual annotations (ground truth),
    calculates accuracy, and generates a detailed log.
    """

    def __init__(self, manual_annotations_path: Path, synthesized_timeline_path: Path, output_log_dir: Path):
        """
        Initialize the evaluation tool.
        """
        if not manual_annotations_path.exists():
            raise FileNotFoundError(f"Manual annotations file not found at: {manual_annotations_path}")
        if not synthesized_timeline_path.exists():
            raise FileNotFoundError(f"Synthesized timeline file not found at: {synthesized_timeline_path}")

        self.manual_annotations_path = manual_annotations_path
        self.synthesized_timeline_path = synthesized_timeline_path
        self.output_log_dir = output_log_dir
        self.output_log_dir.mkdir(parents=True, exist_ok=True)
        
        self.manual_events = []
        self.synthesized_events = []
        self.event_types_to_evaluate = []

    def load_manual_annotations(self):
        """
        Loads and parses manual annotations. Goals/Saves are also treated as Shots.
        """
        logger.info(f"Loading manual annotations from {self.manual_annotations_path}...")
        
        original_events = []
        with open(self.manual_annotations_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    timestamp_str = row.get('Timestamp', '0;0')
                    parts = timestamp_str.split(';')
                    
                    if len(parts) == 3:
                        h, m, s = map(int, parts)
                        absolute_time = float(h * 3600 + m * 60 + s)
                    elif len(parts) == 2:
                        m, s = map(int, parts)
                        absolute_time = float(m * 60 + s)
                    else:
                        raise ValueError("Invalid timestamp format")

                    original_events.append({
                        'time': absolute_time,
                        'raw_timestamp': timestamp_str,
                        'label': row.get('Label', 'N/A').strip().lower().replace('!', ''),
                        'description': row.get('Description', '').strip()
                    })
                except (ValueError, TypeError) as e:
                    logger.warning(f"Could not parse row: {row}. Error: {e}")
        
        # Now create the final list, adding implied shots
        self.manual_events = []
        for event in original_events:
            self.manual_events.append(event)
            # If it's a goal or a save, also add a corresponding 'shot' event
            if event['label'] in ['goal', 'save']:
                implied_shot = event.copy()
                implied_shot['label'] = 'shot'
                implied_shot['description'] = f"(Implied from {event['label'].capitalize()})"
                self.manual_events.append(implied_shot)

        # Add goal side information
        for event in self.manual_events:
            desc = event['description'].lower()
            if 'left' in desc:
                event['side'] = 'left'
            elif 'right' in desc:
                event['side'] = 'right'
            else:
                event['side'] = None

        self.manual_events.sort(key=lambda x: x['time'])
        
        # Dynamically determine which event types to evaluate from the data
        all_labels = set(e['label'] for e in self.manual_events)
        self.event_types_to_evaluate = sorted(list(all_labels - NON_EVALUABLE_EVENTS))
        
        logger.info(f"Loaded {len(self.manual_events)} manual events for comparison (including implied shots).")
        logger.info(f"Will evaluate the following event types: {self.event_types_to_evaluate}")
        
    def load_synthesized_events(self):
        """
        Loads events from the synthesized timeline JSON file.
        """
        logger.info(f"Loading synthesized events from {self.synthesized_timeline_path}...")
        with open(self.synthesized_timeline_path, 'r') as f:
            data = json.load(f)
            self.synthesized_events = data.get("events", [])
        logger.info(f"Loaded {len(self.synthesized_events)} synthesized events.")

    def _is_match(self, manual_event: dict, synth_event: dict) -> bool:
        """
        Checks if a synthesized event matches a manual event based on time and flexible label logic.
        """
        manual_label = manual_event['label']
        if manual_label not in self.event_types_to_evaluate:
            return False

        # 1. Check time tolerance
        if not (abs(manual_event['time'] - synth_event['absolute_time']) <= TIME_TOLERANCE):
            return False

        # 2. Check event type with more flexibility
        synth_type = synth_event.get('event_type', '')
        synth_text = synth_event.get('event_text', '').lower()

        # 3. Check for side/direction if specified in manual data
        manual_side = manual_event.get('side')
        if manual_side and manual_side not in synth_text:
            return False

        # Handle special cases first
        if manual_label == 'shot':
            # A 'shot' is a shot that is NOT a save.
            return 'shot' in synth_type and 'save' not in synth_type and 'save' not in synth_text
        
        if manual_label == 'save':
            # A 'save' can be described in the type or in the text of a shot.
            return 'save' in synth_type or ('shot' in synth_type and 'save' in synth_text)

        # Generic case for all other labels (including 'goal')
        return manual_label in synth_type

    def run_evaluation(self):
        """
        Executes the main evaluation logic, calculates scores, and saves logs.
        """
        self.load_manual_annotations()
        self.load_synthesized_events()

        if not self.manual_events:
            logger.error("No manual events were loaded. Aborting evaluation.")
            return

        stats = {
            'true_positives': {event_type: 0 for event_type in self.event_types_to_evaluate},
            'false_negatives': {event_type: 0 for event_type in self.event_types_to_evaluate},
            'false_positives': {event_type: 0 for event_type in self.event_types_to_evaluate},
            'total_manual': {event_type: 0 for event_type in self.event_types_to_evaluate}
        }
        comparison_log_lines = []
        unmatched_synth_events = list(self.synthesized_events)

        # --- Pass 1: Find True Positives and False Negatives ---
        for manual_event in self.manual_events:
            label = manual_event['label']
            is_evaluable = label in self.event_types_to_evaluate
            
            if is_evaluable:
                stats['total_manual'][label] += 1

            match_found_in_synth = None
            for synth_event in unmatched_synth_events:
                if self._is_match(manual_event, synth_event):
                    match_found_in_synth = synth_event
                    break

            if is_evaluable:
                if match_found_in_synth:
                    stats['true_positives'][label] += 1
                    unmatched_synth_events.remove(match_found_in_synth)
                else:
                    stats['false_negatives'][label] += 1
            
            # --- Logging for every manual event ---
            side_info = f" ({manual_event.get('side')})" if manual_event.get('side') else ""
            comparison_log_lines.append(f"--- MANUAL EVENT: {manual_event['label'].upper()}{side_info} @ {manual_event['raw_timestamp']} ({manual_event['time']:.2f}s) ---")
            if manual_event['description']:
                comparison_log_lines.append(f"  Description: {manual_event['description']}")

            # Add the match decision to the log
            match_status = bool(match_found_in_synth)
            comparison_log_lines.append(f"  Match Decision: {match_status}")

            nearby_events = [se for se in self.synthesized_events if abs(manual_event['time'] - se['absolute_time']) <= TIME_TOLERANCE]
            comparison_log_lines.append("  Nearby AI Events:")
            if nearby_events:
                for se in nearby_events:
                    comparison_log_lines.append(f"  - {se['absolute_time']:.2f}s: [{se['event_type']}] {se['event_text']}")
            else:
                comparison_log_lines.append("    >> No AI-generated events found within the time window.")
            comparison_log_lines.append("-" * 60)

        # --- Pass 2: Find False Positives from remaining AI events ---
        for synth_event in unmatched_synth_events:
            synth_type = synth_event.get('event_type', '')
            synth_text = synth_event.get('event_text', '').lower()
            fp_type = None

            # Prioritize specific events first to avoid misclassifying (e.g., a save as a shot)
            if 'goal' in synth_type:
                fp_type = 'goal'
            elif 'save' in synth_type or ('shot' in synth_type and 'save' in synth_text):
                fp_type = 'save'
            elif 'shot' in synth_type:
                fp_type = 'shot'
            else:
                # Generic check for other event types discovered from manual annotations
                for event_type in self.event_types_to_evaluate:
                    if event_type in synth_type:
                        fp_type = event_type
                        break # Take the first match
            
            if fp_type and fp_type in self.event_types_to_evaluate:
                stats['false_positives'][fp_type] += 1

        self._print_accuracy_report(stats)
        self._save_log_file(comparison_log_lines, stats)

    def _print_accuracy_report(self, stats: dict):
        print("\n" + "="*50)
        print("📊 ACCURACY EVALUATION REPORT")
        print("="*50 + "\n")

        for event_type in self.event_types_to_evaluate:
            tp = stats['true_positives'][event_type]
            fn = stats['false_negatives'][event_type]
            fp = stats['false_positives'][event_type]
            total = stats['total_manual'][event_type]

            recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
            precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
            
            print(f"--- {event_type.upper()} ---")
            print(f"  Recall:    {recall:.2f}% ({tp}/{total} detected)")
            print(f"  Precision: {precision:.2f}% ({tp} correct / {tp+fp} total AI detections)")
            print(f"  (TP: {tp}, FP: {fp}, FN: {fn})")

        print("\n" + "="*50)

    def _save_log_file(self, log_lines: list, stats: dict):
        log_path = self.output_log_dir / "evaluation_log.txt"
        logger.info(f"Saving detailed evaluation log to {log_path}")

        with open(log_path, 'w') as f:
            f.write("="*60 + "\n")
            f.write("AI vs. Manual Annotation - Detailed Comparison Log\n")
            f.write("="*60 + "\n\n")

            f.write("--- ACCURACY SUMMARY ---\n")
            for event_type in self.event_types_to_evaluate:
                 tp = stats['true_positives'][event_type]
                 fn = stats['false_negatives'][event_type]
                 fp = stats['false_positives'][event_type]
                 total = stats['total_manual'][event_type]
                 recall = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0
                 precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
                 f.write(f"{event_type.upper()}: Recall={recall:.1f}%, Precision={precision:.1f}%\n")
            f.write("\n" + "="*60 + "\n\n")
            
            f.write("\n".join(log_lines))

        print(f"✅ Log file saved successfully.")
        
        # Save stats to JSON as well
        stats_path = self.output_log_dir / "evaluation_stats.json"
        try:
            with open(stats_path, 'w') as f:
                json.dump(stats, f, indent=2)
            logger.info(f"💾 Statistics JSON saved to: {stats_path}")
        except Exception as e:
            logger.error(f"❌ Failed to save statistics JSON: {e}")

def find_latest_run_timestamp(synthesis_game_dir: Path) -> str:
    """Finds the timestamp of the latest run in a game's synthesis directory."""
    timestamps = [d.name for d in synthesis_game_dir.iterdir() if d.is_dir()]
    if not timestamps:
        return None
    return sorted(timestamps)[-1]

def generate_summary_report(logs_base_dir: Path):
    """Scans all evaluation logs and generates a summary report."""
    logger.info(f"🔍 Generating overall evaluation summary from logs in: {logs_base_dir}")

    # Find the anchor timestamp from the latest run in any game directory
    all_run_dirs = [d for d in logs_base_dir.glob("*/*") if d.is_dir()]
    if not all_run_dirs:
        logger.error("No evaluation runs found to summarize.")
        return

    try:
        latest_run_dir = max(all_run_dirs, key=lambda d: d.name)
        anchor_timestamp_str = latest_run_dir.name
        anchor_timestamp_dt = datetime.strptime(anchor_timestamp_str, "%Y-%m-%d_%H-%M-%S")
    except (ValueError, TypeError):
        logger.error(f"Could not determine a valid latest run from directories like '{latest_run_dir.name}'")
        return

    time_window = timedelta(minutes=15)
    logger.info(f"Anchor run for summary is {anchor_timestamp_str}. Looking for runs within a {time_window} window.")

    all_stats = {}
    game_dirs = [d for d in logs_base_dir.iterdir() if d.is_dir()]

    for game_dir in game_dirs:
        # Find all runs for this game that are within the time window of the anchor
        valid_runs_in_window = []
        for run_dir in game_dir.iterdir():
            if not run_dir.is_dir():
                continue
            try:
                run_dt = datetime.strptime(run_dir.name, "%Y-%m-%d_%H-%M-%S")
                if abs(anchor_timestamp_dt - run_dt) <= time_window:
                    valid_runs_in_window.append(run_dir)
            except ValueError:
                continue # Ignore non-timestamp directories
        
        if not valid_runs_in_window:
            logger.warning(f"No runs found for game {game_dir.name} within the latest run window.")
            continue
        
        # Of the valid runs, find the latest one and its stats file
        latest_valid_run_dir = max(valid_runs_in_window, key=lambda d: d.name)
        stats_file = latest_valid_run_dir / "evaluation_stats.json"
        
        if stats_file.exists():
            with open(stats_file, 'r') as f:
                stats = json.load(f)
            all_stats[game_dir.name] = stats
            logger.info(f"Found stats for {game_dir.name} (run: {latest_valid_run_dir.name})")
        else:
            logger.warning(f"No stats file found for run {latest_valid_run_dir.name} in {game_dir.name}")

    if not all_stats:
        logger.error("No evaluation stats found within the time window to generate a summary.")
        return

    report_lines = []
    report_lines.append("="*80)
    report_lines.append("📊 OVERALL EVALUATION SUMMARY REPORT")
    report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("="*80 + "\n")

    # Dynamically discover all event types from the collected stats
    all_event_types = set()
    for stats in all_stats.values():
        all_event_types.update(stats['true_positives'].keys())
    
    sorted_event_types = sorted(list(all_event_types))

    overall_stats = {
        'true_positives': {event_type: 0 for event_type in sorted_event_types},
        'false_negatives': {event_type: 0 for event_type in sorted_event_types},
        'false_positives': {event_type: 0 for event_type in sorted_event_types},
        'total_manual': {event_type: 0 for event_type in sorted_event_types}
    }
    
    report_lines.append("--- INDIVIDUAL GAME PERFORMANCE (LATEST RUN) ---")
    for game_name, stats in sorted(all_stats.items()):
        report_lines.append(f"\nGame: {game_name}")
        for event_type in sorted_event_types:
            tp = stats['true_positives'].get(event_type, 0)
            fn = stats['false_negatives'].get(event_type, 0)
            fp = stats['false_positives'].get(event_type, 0)
            total = stats['total_manual'].get(event_type, 0)
            
            overall_stats['true_positives'][event_type] += tp
            overall_stats['false_negatives'][event_type] += fn
            overall_stats['false_positives'][event_type] += fp
            overall_stats['total_manual'][event_type] += total

            recall = (tp / total) * 100 if total > 0 else 0
            precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
            report_lines.append(f"  - {event_type.upper():<5}: Recall: {recall:5.1f}%, Precision: {precision:5.1f}%  (TP:{tp}, FP:{fp}, FN:{fn})")

    report_lines.append("\n" + "="*80)
    report_lines.append("\n--- OVERALL AGGREGATE PERFORMANCE ---")
    total_games = len(all_stats)
    report_lines.append(f"(Aggregated across {total_games} games)\n")
    for event_type in sorted_event_types:
        tp = overall_stats['true_positives'][event_type]
        fn = overall_stats['false_negatives'][event_type]
        fp = overall_stats['false_positives'][event_type]
        total = overall_stats['total_manual'][event_type]

        recall = (tp / total) * 100 if total > 0 else 0
        precision = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0
        report_lines.append(f"--- {event_type.upper()} ---")
        report_lines.append(f"  Overall Recall:    {recall:.2f}% ({tp}/{total} detected)")
        report_lines.append(f"  Overall Precision: {precision:.2f}% ({tp} correct / {tp+fp} total AI detections)")
        report_lines.append(f"  (Total TP: {tp}, Total FP: {fp}, Total FN: {fn})")
        report_lines.append("")
    report_lines.append("="*80)

    summary_text = "\n".join(report_lines)
    print(summary_text)

    summary_filename = f"summary_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    summary_path = logs_base_dir / summary_filename
    with open(summary_path, 'w') as f:
        f.write(summary_text)
    logger.info(f"✅ Summary report saved to: {summary_path}")

def main():
    """Main function to run the evaluation tool."""
    parser = argparse.ArgumentParser(description="Compares AI-generated events with manual annotations or summarizes previous evaluations.")
    parser.add_argument("--summarize", action="store_true", help="Generate a summary report of the latest evaluation for all games.")
    parser.add_argument("--game_name", help="The name of the game to evaluate (e.g., Game298_0601). Required unless --summarize is used.")
    parser.add_argument("--run_timestamp", help="Optional: Specify a run timestamp. If omitted, the latest run will be used.")
    args = parser.parse_args()

    script_dir = Path(__file__).parent
    logs_base_dir = script_dir / "evaluation_logs"

    if args.summarize:
        generate_summary_report(logs_base_dir)
        return

    if not args.game_name:
        parser.error("Argument --game_name is required unless --summarize is used.")
    
    game_name = args.game_name
    
    # Correct path for manual annotations using the new naming convention
    manual_annotations_filename = f"manual_annotations_{game_name}.csv"
    manual_annotations_path = script_dir.parent / "data" / game_name / manual_annotations_filename
    
    # Determine the synthesis path
    synthesis_game_dir = script_dir / "synthesis" / game_name
    if not synthesis_game_dir.exists():
        logger.error(f"Synthesis directory for {game_name} not found at: {synthesis_game_dir}")
        return

    run_timestamp = args.run_timestamp
    if not run_timestamp:
        logger.info("No run timestamp provided, finding the latest run...")
        run_timestamp = find_latest_run_timestamp(synthesis_game_dir)
        if not run_timestamp:
            logger.error(f"No completed synthesis runs found for {game_name}.")
            return
        logger.info(f"Using latest run: {run_timestamp}")

    synthesized_timeline_path = synthesis_game_dir / run_timestamp / "events_timeline.json"
    log_output_dir = script_dir / "evaluation_logs" / game_name / run_timestamp

    print(f"⚽ Football AI Evaluation Tool for {game_name} ⚽")
    print(f"Comparing AI timeline against manual data using tolerance: +/- {TIME_TOLERANCE}s")
    print(f"  - Manual Data: {manual_annotations_path}")
    print(f"  - AI Timeline: {synthesized_timeline_path}")

    try:
        tool = EvaluationTool(manual_annotations_path, synthesized_timeline_path, log_output_dir)
        tool.run_evaluation()
    except FileNotFoundError as e:
        logger.error(f"Setup Error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main() 
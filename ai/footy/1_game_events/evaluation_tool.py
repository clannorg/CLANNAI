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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# --- Configuration ---
# Time window (in seconds) to consider an event a match
TIME_TOLERANCE = 2.0
# The event types we want to formally evaluate for accuracy scores
EVENT_TYPES_TO_EVALUATE = ['goal', 'shot', 'save']
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
        self.output_log_dir.mkdir(exist_ok=True)
        
        self.manual_events = []
        self.synthesized_events = []

    def load_manual_annotations(self):
        """
        Loads and parses all manual annotations from the CSV file.
        """
        logger.info(f"Loading manual annotations from {self.manual_annotations_path}...")
        
        with open(self.manual_annotations_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    timestamp_str = row.get('Timestamp', '0;0')
                    minutes, seconds = map(int, timestamp_str.split(';'))
                    absolute_time = float(minutes * 60 + seconds)
                    
                    self.manual_events.append({
                        'time': absolute_time,
                        'raw_timestamp': timestamp_str,
                        'label': row.get('Label', 'N/A').strip().lower().replace('!', ''),
                        'description': row.get('Description', '').strip()
                    })
                except (ValueError, TypeError) as e:
                    logger.warning(f"Could not parse row: {row}. Error: {e}")

        self.manual_events.sort(key=lambda x: x['time'])
        logger.info(f"Loaded {len(self.manual_events)} manual events for comparison.")
        
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
        Checks if a synthesized event matches a manual event based on time and label logic.
        """
        manual_label = manual_event['label']
        if manual_label not in EVENT_TYPES_TO_EVALUATE:
            return False

        if not (abs(manual_event['time'] - synth_event['absolute_time']) <= TIME_TOLERANCE):
            return False

        synth_type = synth_event.get('event_type', '')
        synth_text = synth_event.get('event_text', '').lower()

        if manual_label == 'goal' and synth_type == 'goals':
            return True
        if manual_label == 'shot' and synth_type == 'shots' and 'save' not in synth_text:
            return True
        if manual_label == 'save' and (synth_type == 'shots' and 'save' in synth_text or synth_type == 'saves'): # Future-proofing
            return True
            
        return False

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
            'true_positives': {event_type: 0 for event_type in EVENT_TYPES_TO_EVALUATE},
            'false_negatives': {event_type: 0 for event_type in EVENT_TYPES_TO_EVALUATE},
            'false_positives': {event_type: 0 for event_type in EVENT_TYPES_TO_EVALUATE},
            'total_manual': {event_type: 0 for event_type in EVENT_TYPES_TO_EVALUATE}
        }
        comparison_log_lines = []
        unmatched_synth_events = list(self.synthesized_events)

        # --- Pass 1: Find True Positives and False Negatives ---
        for manual_event in self.manual_events:
            label = manual_event['label']
            is_evaluable = label in EVENT_TYPES_TO_EVALUATE
            
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
            comparison_log_lines.append(f"--- MANUAL EVENT: {manual_event['label'].upper()} @ {manual_event['raw_timestamp']} ({manual_event['time']:.2f}s) ---")
            if manual_event['description']:
                comparison_log_lines.append(f"  Description: {manual_event['description']}")

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

            if synth_type == 'goals':
                fp_type = 'goal'
            elif synth_type == 'shots':
                if 'save' in synth_text:
                    fp_type = 'save'
                else:
                    fp_type = 'shot'
            
            if fp_type and fp_type in EVENT_TYPES_TO_EVALUATE:
                stats['false_positives'][fp_type] += 1

        self._print_accuracy_report(stats)
        self._save_log_file(comparison_log_lines, stats)

    def _print_accuracy_report(self, stats: dict):
        print("\n" + "="*50)
        print("📊 ACCURACY EVALUATION REPORT")
        print("="*50 + "\n")

        for event_type in EVENT_TYPES_TO_EVALUATE:
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
            for event_type in EVENT_TYPES_TO_EVALUATE:
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

def main():
    """Main function to run the evaluation tool."""
    script_dir = Path(__file__).parent
    
    manual_annotations_path = script_dir.parent / "Game298_0601" / "manual_annotations.csv"
    synthesized_timeline_path = script_dir / "synthesis" / "events_timeline.json"
    log_output_dir = script_dir / "evaluation_logs"

    print("⚽ Football AI Evaluation Tool ⚽")
    print(f"Comparing AI timeline against manual data using tolerance: +/- {TIME_TOLERANCE}s")

    try:
        tool = EvaluationTool(manual_annotations_path, synthesized_timeline_path, log_output_dir)
        tool.run_evaluation()
    except FileNotFoundError as e:
        logger.error(f"Setup Error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)


if __name__ == "__main__":
    main() 
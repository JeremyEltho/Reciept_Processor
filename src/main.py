import sys
import os
import glob
from controller.receipt_controller import handle_single_receipt, handle_event_receipts

RESULTS_SINGLE = os.path.join(os.path.dirname(__file__), '../results/single')
RESULTS_EVENTS = os.path.join(os.path.dirname(__file__), '../results/events')
RESULTS_BATCH = os.path.join(os.path.dirname(__file__), '../results/batch')

os.makedirs(RESULTS_SINGLE, exist_ok=True)
os.makedirs(RESULTS_EVENTS, exist_ok=True)
os.makedirs(RESULTS_BATCH, exist_ok=True)

HELP_TEXT = """
CLUB TREASURER EXPENSE PROCESSOR
===================================

USAGE MODES:

Single Receipt:
  python main.py receipt.png
  → Generates: results/single/receipt_reimbursement_summary.txt

Event Processing:
  python main.py --event "FSAE Competition Michigan" receipt1.png receipt2.png
  → Generates: results/events/Event_YYYYMMDD_HHMMSS_expenses.csv + summary.txt

Batch Processing:
  python main.py --batch folder_with_receipts/
  → Processes all images in folder, uses folder name as event

FEATURES:
• Auto-categorizes expenses (food, tools, travel, fees, etc.)
• Flags items needing approval (>$100, questionable expenses)
• Exports finance-ready CSV files
• Generates treasurer summary reports
• Quality checks for incomplete receipts

PERFECT FOR: FSAE, Robotics, Student Organizations, Club Treasurers
"""

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print(HELP_TEXT)
        sys.exit(0)
    if sys.argv[1] == "--event":
        if len(sys.argv) < 4:
            print("Error: Event mode requires event name and at least one receipt")
            sys.exit(1)
        event_name = sys.argv[2]
        image_paths = sys.argv[3:]
        for path in image_paths:
            if not os.path.exists(path):
                print(f"Error: File '{path}' not found.")
                sys.exit(1)
        handle_event_receipts(event_name, image_paths, RESULTS_EVENTS)
    elif sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("Error: Batch mode requires a folder path")
            sys.exit(1)
        folder_path = sys.argv[2]
        if not os.path.exists(folder_path):
            print(f"Error: Folder '{folder_path}' not found.")
            sys.exit(1)
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.tiff', '*.bmp']
        image_paths = []
        for ext in image_extensions:
            image_paths.extend(glob.glob(os.path.join(folder_path, ext)))
            image_paths.extend(glob.glob(os.path.join(folder_path, ext.upper())))
        if not image_paths:
            print(f"No image files found in '{folder_path}'")
            sys.exit(1)
        event_name = os.path.basename(folder_path.rstrip('/'))
        handle_event_receipts(event_name, image_paths, RESULTS_BATCH)
    else:
        path = sys.argv[1]
        if not os.path.exists(path):
            print(f"Error: File '{path}' not found.")
            sys.exit(1)
        handle_single_receipt(path, RESULTS_SINGLE)

if __name__ == "__main__":
    main()

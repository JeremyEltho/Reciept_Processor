import os
from datetime import datetime
from model.receipt_model import process_single_receipt, process_event_receipts, export_to_csv
from model.summary_model import generate_summary_report
from view.receipt_view import format_single_receipt_summary, save_text_file

def handle_single_receipt(path, results_dir):
    receipt_data = process_single_receipt(path)
    if not receipt_data:
        print("Warning: Could not process receipt.")
        return
    base_name = os.path.splitext(os.path.basename(path))[0]
    output_filename = os.path.join(results_dir, f"{base_name}_reimbursement_summary.txt")
    summary = format_single_receipt_summary(receipt_data)
    save_text_file(output_filename, summary)
    print(summary)

def handle_event_receipts(event_name, image_paths, results_dir):
    receipts_data = process_event_receipts(image_paths, event_name)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_name = event_name.replace(' ', '_').replace('/', '_')
    csv_file = os.path.join(results_dir, f"{base_name}_{timestamp}_expenses.csv")
    export_to_csv(receipts_data, csv_file)
    print(f"\n CSV exported: {csv_file}")
    report = generate_summary_report(receipts_data)
    report_file = os.path.join(results_dir, f"{base_name}_{timestamp}_summary.txt")
    save_text_file(report_file, report)
    print(f"✅Summary report: {report_file}")
    print(report)

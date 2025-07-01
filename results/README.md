# Results Directory

This folder contains all generated outputs from the Club Treasurer Expense Processor.

## Folder Structure

### `/single/`
Contains individual receipt processing results:
- `*_reimbursement_summary.txt` - Text summaries for single receipts

### `/events/`
Contains event-based processing results:
- `*_expenses.csv` - Finance-ready CSV exports for events
- `*_summary.txt` - Comprehensive event summary reports

### `/batch/`
Contains batch processing results:
- `*_batch_expenses.csv` - CSV exports for folder-based processing
- `*_batch_summary.txt` - Summary reports for batch operations

## File Naming Convention

- **Single**: `{receipt_name}_reimbursement_summary.txt`
- **Event**: `{event_name}_{timestamp}_expenses.csv` and `{event_name}_{timestamp}_summary.txt`
- **Batch**: `{folder_name}_{timestamp}_batch_expenses.csv` and `{folder_name}_{timestamp}_batch_summary.txt`

## CSV Format

The CSV files are designed for direct submission to finance offices and include:
- Event, File Name, Merchant, Date, Location
- Item, Amount, Category, Justification
- Needs Approval, Approval Reason, Receipt Total

Perfect for club treasurers managing expense reimbursements!

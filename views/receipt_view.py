"""
View components for formatting and displaying receipt data.
"""

import csv


class ReceiptFormatter:
    """Handles formatting of receipt data for different output formats."""
    
    def format_single_receipt_summary(self, receipt_data: dict) -> str:
        """Format a single receipt's data into a readable summary."""
        summary = f"""=== BUSINESS EXPENSE SUMMARY ===

MERCHANT: {receipt_data.get('merchant', 'N/A')} | DATE: {receipt_data.get('date', 'N/A')} | LOCATION: {receipt_data.get('location', 'N/A')}

LINE ITEMS:
"""
        for item in receipt_data.get('line_items', []):
            approval_note = f" [NEEDS APPROVAL: {item.get('approval_reason', 'Reason not specified')}]" if item.get('needs_approval') else ""
            summary += f"• {item.get('item', 'N/A'):<40} | ${item.get('amount', '0.00'):>7} | {item.get('category', 'Uncategorized')} | Justification: {item.get('justification', 'N/A')}{approval_note}\n"
        
        summary += f"""
TOTALS:
Subtotal: ${receipt_data.get('subtotal', '0.00')}
Tax:      ${receipt_data.get('tax', '0.00')}
TOTAL:    ${receipt_data.get('receipt_total', '0.00')}

RECEIPT QUALITY: {receipt_data.get('completeness_score', 'N/A')}
"""
        
        if receipt_data.get('flags'):
            summary += "\nFLAGS:\n"
            for flag in receipt_data['flags']:
                summary += f"- {flag}\n"
        
        return summary


class CSVExporter:
    """Handles CSV export functionality."""
    
    def export_to_csv(self, receipts_data: list[dict], output_file: str):
        """Export receipt data to CSV format."""
        fieldnames = [
            'Event', 'File Name', 'Merchant', 'Date', 'Location', 
            'Item', 'Amount', 'Category', 'Justification', 
            'Needs Approval', 'Approval Reason', 'Receipt Total'
        ]
        
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for receipt in receipts_data:
                for item in receipt.get('line_items', []):
                    writer.writerow({
                        'Event': receipt.get('event_name', ''),
                        'File Name': receipt.get('file_name', ''),
                        'Merchant': receipt.get('merchant', ''),
                        'Date': receipt.get('date', ''),
                        'Location': receipt.get('location', ''),
                        'Item': item.get('item', ''),
                        'Amount': item.get('amount', ''),
                        'Category': item.get('category', ''),
                        'Justification': item.get('justification', ''),
                        'Needs Approval': item.get('needs_approval', False),
                        'Approval Reason': item.get('approval_reason', ''),
                        'Receipt Total': receipt.get('receipt_total', '')
                    })


class FileHandler:
    """Handles file operations for saving outputs."""
    
    def save_text_file(self, filename: str, content: str):
        """Save text content to a file."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Saved: {filename}")

import sys
import os
import csv
import json
import glob
from datetime import datetime
from PIL import Image
import pytesseract
import google.generativeai as genai
import argparse
from pathlib import Path

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCC88P2ZrbzMgUcchPgmJXYD7cOCACQTkw')
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def generate_reimbursement_summary(raw_text, event_name=None):
    prompt = f"""You are a club treasurer's expense analysis assistant. Analyze this receipt for a student organization (FSAE, robotics, etc.).

RECEIPT TEXT:
{raw_text}

INSTRUCTIONS:
1. Extract ALL line items with prices
2. Identify merchant, date, location, and receipt total
3. Categorize each expense using CLUB-SPECIFIC categories
4. Flag any issues or items needing approval
5. Return data in JSON format for easy processing

FORMAT YOUR RESPONSE AS VALID JSON:
{{
    "merchant": "Vendor Name",
    "date": "MM/DD/YYYY or 'Not Available'",
    "location": "City, State or 'Not Available'", 
    "receipt_total": "XX.XX",
    "subtotal": "XX.XX",
    "tax": "XX.XX",
    "line_items": [
        {{
            "item": "Item Description",
            "amount": "XX.XX",
            "category": "Category Name",
            "justification": "Why this is a valid club expense",
            "needs_approval": true/false,
            "approval_reason": "Reason if needs approval"
        }}
    ],
    "flags": [
        "Any issues: missing total, unclear items, personal expenses, etc."
    ],
    "completeness_score": "A-F grade for receipt quality"
}}

**CLUB EXPENSE CATEGORIES:**
- Competition Food (team meals during events/travel)
- Tools & Equipment (hardware, parts, manufacturing supplies)
- Travel & Lodging (gas, flights, hotels for competitions)
- Registration Fees (competition entries, memberships)
- Materials & Consumables (raw materials, fasteners, fluids)
- Software & Subscriptions (CAD, analysis tools, cloud services)
- Team Building & Recruitment (social events, recruitment materials)
- Office Supplies (printing, stationery, organization materials)
- Training & Education (courses, books, certifications)
- Personal - Not Reimbursable (clearly personal items)

**APPROVAL FLAGS** (mark needs_approval=true if):
- Single item over $100
- Personal/questionable expenses
- Alcohol purchases
- Items without clear business purpose
- Missing or unclear receipts

Be precise with amounts and realistic about what clubs can reimburse."""
    
    response = model.generate_content(prompt)
    return response.text

def parse_receipt_json(json_text):
    """Parse the JSON response from AI, handling potential formatting issues."""
    try:
        # Clean up the response to extract just the JSON part
        start = json_text.find('{')
        end = json_text.rfind('}') + 1
        if start != -1 and end > start:
            clean_json = json_text[start:end]
            return json.loads(clean_json)
        else:
            raise ValueError("No valid JSON found in response")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        return None

def process_single_receipt(image_path, event_name=None):
    """Process a single receipt and return structured data."""
    text = extract_text_from_image(image_path)
    if not text.strip():
        return None
    
    ai_response = generate_reimbursement_summary(text, event_name)
    receipt_data = parse_receipt_json(ai_response)
    
    if receipt_data:
        receipt_data['file_name'] = os.path.basename(image_path)
        receipt_data['event_name'] = event_name or 'General'
        receipt_data['processed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return receipt_data

def export_to_csv(receipts_data, output_file):
    """Export receipt data to CSV for finance submission."""
    fieldnames = [
        'Event', 'File Name', 'Merchant', 'Date', 'Location', 
        'Item', 'Amount', 'Category', 'Justification', 
        'Needs Approval', 'Approval Reason', 'Receipt Total'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for receipt in receipts_data:
            if not receipt:
                continue
                
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

def generate_summary_report(receipts_data):
    """Generate a comprehensive summary report for the treasurer."""
    total_spent = 0
    category_totals = {}
    vendor_totals = {}
    flagged_receipts = []
    approval_items = []
    
    for receipt in receipts_data:
        if not receipt:
            continue
            
        # Track flagged receipts
        if receipt.get('flags'):
            flagged_receipts.append({
                'file': receipt.get('file_name', ''),
                'flags': receipt.get('flags', []),
                'score': receipt.get('completeness_score', 'N/A')
            })
        
        # Process line items
        for item in receipt.get('line_items', []):
            try:
                amount = float(item.get('amount', '0').replace('$', ''))
                total_spent += amount
                
                # Category totals
                category = item.get('category', 'Unknown')
                category_totals[category] = category_totals.get(category, 0) + amount
                
                # Vendor totals
                vendor = receipt.get('merchant', 'Unknown')
                vendor_totals[vendor] = vendor_totals.get(vendor, 0) + amount
                
                # Items needing approval
                if item.get('needs_approval'):
                    approval_items.append({
                        'item': item.get('item', ''),
                        'amount': amount,
                        'reason': item.get('approval_reason', ''),
                        'file': receipt.get('file_name', '')
                    })
                    
            except (ValueError, AttributeError):
                continue
    
    # Generate report
    report = f"""
=== CLUB EXPENSE SUMMARY REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 FINANCIAL OVERVIEW:
Total Amount: ${total_spent:.2f}
Number of Receipts: {len([r for r in receipts_data if r])}
Number of Line Items: {sum(len(r.get('line_items', [])) for r in receipts_data if r)}

💰 SPENDING BY CATEGORY:
"""
    
    # Sort categories by spending
    for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / total_spent * 100) if total_spent > 0 else 0
        report += f"  {category}: ${amount:.2f} ({percentage:.1f}%)\n"
    
    report += f"\n🏪 TOP VENDORS:\n"
    # Sort vendors by spending
    for vendor, amount in sorted(vendor_totals.items(), key=lambda x: x[1], reverse=True)[:5]:
        report += f"  {vendor}: ${amount:.2f}\n"
    
    if approval_items:
        report += f"\n⚠️  ITEMS REQUIRING APPROVAL ({len(approval_items)}):\n"
        for item in approval_items:
            report += f"  • {item['item']} - ${item['amount']:.2f} ({item['reason']})\n"
            report += f"    File: {item['file']}\n"
    
    if flagged_receipts:
        report += f"\n🚩 FLAGGED RECEIPTS ({len(flagged_receipts)}):\n"
        for receipt in flagged_receipts:
            report += f"  • {receipt['file']} (Score: {receipt['score']})\n"
            for flag in receipt['flags']:
                report += f"    - {flag}\n"
    
    report += f"\n✅ RECOMMENDATIONS:\n"
    if total_spent > 500:
        report += "  • High total spending - ensure all receipts are properly justified\n"
    if len(approval_items) > 0:
        report += f"  • {len(approval_items)} items need treasurer/advisor approval before submission\n"
    if len(flagged_receipts) > 0:
        report += f"  • {len(flagged_receipts)} receipts have quality issues - review before submitting\n"
    
    report += "  • Export to CSV for easy finance office submission\n"
    report += "  • Keep original receipt images as backup documentation\n"
    
    return report

def process_event_receipts(image_paths, event_name):
    """Process multiple receipts for a single event."""
    print(f"Processing {len(image_paths)} receipts for event: {event_name}")
    receipts_data = []
    
    for i, path in enumerate(image_paths, 1):
        print(f"  Processing receipt {i}/{len(image_paths)}: {os.path.basename(path)}")
        try:
            receipt_data = process_single_receipt(path, event_name)
            receipts_data.append(receipt_data)
        except Exception as e:
            print(f"    Error processing {path}: {e}")
            receipts_data.append(None)
    
    return receipts_data

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print("""
🏆 CLUB TREASURER EXPENSE PROCESSOR
===================================

USAGE MODES:

📄 Single Receipt:
  python check.py receipt.png
  → Generates: receipt_reimbursement_summary.txt

🎯 Event Processing:
  python check.py --event "FSAE Competition Michigan" receipt1.png receipt2.png receipt3.png
  → Generates: Event_YYYYMMDD_HHMMSS_expenses.csv + summary.txt

📁 Batch Processing:
  python check.py --batch folder_with_receipts/
  → Processes all images in folder, uses folder name as event

FEATURES:
• Auto-categorizes expenses (food, tools, travel, fees, etc.)
• Flags items needing approval (>$100, questionable expenses)
• Exports finance-ready CSV files
• Generates treasurer summary reports
• Quality checks for incomplete receipts

PERFECT FOR: FSAE, Robotics, Student Organizations, Club Treasurers
        """)
        sys.exit(0)

    # Handle different modes
    if sys.argv[1] == "--event":
        if len(sys.argv) < 4:
            print("Error: Event mode requires event name and at least one receipt")
            sys.exit(1)
        
        event_name = sys.argv[2]
        image_paths = sys.argv[3:]
        
        # Validate all files exist
        for path in image_paths:
            if not os.path.exists(path):
                print(f"Error: File '{path}' not found.")
                sys.exit(1)
        
        try:
            receipts_data = process_event_receipts(image_paths, event_name)
            
            # Generate outputs
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = event_name.replace(' ', '_').replace('/', '_')
            
            # CSV export
            csv_file = f"{base_name}_{timestamp}_expenses.csv"
            export_to_csv(receipts_data, csv_file)
            print(f"\n✅ CSV exported: {csv_file}")
            
            # Summary report
            report = generate_summary_report(receipts_data)
            report_file = f"{base_name}_{timestamp}_summary.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ Summary report: {report_file}")
            
            # Display summary
            print(report)
            
        except Exception as e:
            print(f"Error processing event receipts: {e}")
            sys.exit(1)
    
    elif sys.argv[1] == "--batch":
        if len(sys.argv) < 3:
            print("Error: Batch mode requires a folder path")
            sys.exit(1)
        
        folder_path = sys.argv[2]
        if not os.path.exists(folder_path):
            print(f"Error: Folder '{folder_path}' not found.")
            sys.exit(1)
        
        # Find all image files in folder
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.tiff', '*.bmp']
        image_paths = []
        for ext in image_extensions:
            image_paths.extend(glob.glob(os.path.join(folder_path, ext)))
            image_paths.extend(glob.glob(os.path.join(folder_path, ext.upper())))
        
        if not image_paths:
            print(f"No image files found in '{folder_path}'")
            sys.exit(1)
        
        # Use folder name as event name
        event_name = os.path.basename(folder_path.rstrip('/'))
        
        try:
            receipts_data = process_event_receipts(image_paths, event_name)
            
            # Generate outputs
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            base_name = event_name.replace(' ', '_').replace('/', '_')
            
            # CSV export
            csv_file = f"{base_name}_{timestamp}_batch_expenses.csv"
            export_to_csv(receipts_data, csv_file)
            print(f"\n✅ CSV exported: {csv_file}")
            
            # Summary report
            report = generate_summary_report(receipts_data)
            report_file = f"{base_name}_{timestamp}_batch_summary.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ Summary report: {report_file}")
            
            # Display summary
            print(report)
            
        except Exception as e:
            print(f"Error processing batch receipts: {e}")
            sys.exit(1)
    
    else:
        # Single receipt mode (original functionality)
        path = sys.argv[1]
        
        if not os.path.exists(path):
            print(f"Error: File '{path}' not found.")
            sys.exit(1)
        
        try:
            receipt_data = process_single_receipt(path)
            
            if not receipt_data:
                print("Warning: Could not process receipt.")
                sys.exit(1)
            
            # Generate text summary (original format for compatibility)
            base_name = os.path.splitext(os.path.basename(path))[0]
            output_filename = f"{base_name}_reimbursement_summary.txt"
            
            # Create readable summary
            summary = f"""=== REIMBURSEMENT SUMMARY ===

**MERCHANT:** {receipt_data.get('merchant', 'N/A')} | **DATE:** {receipt_data.get('date', 'N/A')} | **LOCATION:** {receipt_data.get('location', 'N/A')}

**LINE ITEMS:**
"""
            
            for item in receipt_data.get('line_items', []):
                approval_note = f" [NEEDS APPROVAL: {item.get('approval_reason', 'High value')}]" if item.get('needs_approval') else ""
                summary += f"• {item.get('item', 'N/A')} - ${item.get('amount', '0.00')} → **{item.get('category', 'Unknown')}** - {item.get('justification', 'N/A')}{approval_note}\n"
            
            summary += f"""
**TOTALS:**
Subtotal: ${receipt_data.get('subtotal', '0.00')}
Tax: ${receipt_data.get('tax', '0.00')}
**TOTAL: ${receipt_data.get('receipt_total', '0.00')}**

**RECEIPT QUALITY:** {receipt_data.get('completeness_score', 'N/A')}
"""
            
            if receipt_data.get('flags'):
                summary += "\n**FLAGS:**\n"
                for flag in receipt_data.get('flags', []):
                    summary += f"⚠️  {flag}\n"
            
            # Save to file
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            print(f"Reimbursement summary saved to: {output_filename}")
            print(summary)
            
        except Exception as e:
            print(f"Error processing receipt: {e}")
            sys.exit(1)

#!/usr/bin/env python3
"""
Club Treasurer Receipt Processor - Unified Implementation
Processes receipt images using OCR and AI for expense categorization and reimbursement summaries.
VERSION 2.1 - Enhanced, Secure, and Refactored
"""

import os
import sys
import json
import csv
import argparse
import glob
import re
from datetime import datetime
from PIL import Image
import pytesseract
import google.generativeai as genai

# Try to import OpenCV, provide instructions if it's missing
try:
    import cv2
except ImportError:
    print("OpenCV library not found. It is required for enhanced OCR.")
    print("Please install it by running: pip install opencv-python")
    sys.exit(1)

# --- CONFIGURATION ---

def configure_gemini():
    """Configures the Gemini AI model and ensures API key is present."""
    api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCC88P2ZrbzMgUcchPgmJXYD7cOCACQTkw')
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        print("Please set this environment variable with your API key and try again.")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")

model = configure_gemini()

# --- CORE PROCESSING FUNCTIONS ---

def extract_text_from_image(image_path: str) -> str:
    """
    Extract text from receipt image using OCR with OpenCV pre-processing for better accuracy.
    """
    try:
        # 1. Read the image with OpenCV for pre-processing
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Could not read image file: {image_path}")

        # 2. Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # 3. Apply adaptive thresholding to create a clean, binary image.
        # This is very effective for receipts with uneven lighting.
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                       cv2.THRESH_BINARY, 11, 2)

        # 4. Use Tesseract on the pre-processed image for better OCR results.
        # --psm 6 assumes a single uniform block of text, which is often good for receipts.
        custom_config = r'--oem 3 --psm 6'
        text = pytesseract.image_to_string(binary, config=custom_config)
        
        if not text.strip():
            print(f"Warning: OCR returned no text for {image_path}. The image might be blank or unreadable.")
        return text
    except Exception as e:
        print(f"Error during OCR pre-processing for {image_path}: {e}")
        # Fallback to the simpler method if OpenCV processing fails
        try:
            print("Attempting fallback OCR method...")
            return pytesseract.image_to_string(Image.open(image_path))
        except Exception as e2:
            print(f"Fallback OCR also failed: {e2}")
            return ""

def generate_reimbursement_summary(raw_text: str, event_name: str = None) -> str:
    """Use AI to analyze receipt text and generate structured expense data with an improved prompt."""
    event_context = f"This receipt is for the club event: '{event_name}'." if event_name else ""
    
    prompt = f"""You are an expert AI assistant for a student engineering club treasurer (e.g., FSAE, Robotics). Your task is to analyze OCR text from a receipt and convert it into a structured JSON format.

**CONTEXT:**
- The club can only reimburse expenses directly related to its projects.
- The OCR text is automatically generated and may contain errors, formatting issues, or jumbled lines. Do your best to interpret the messy text.
{event_context}

**INSTRUCTIONS:**
1.  **Analyze the Entire Text:** Carefully read the provided OCR text to identify the merchant, date, and line items.
2.  **Extract Key Information:**
    - `merchant`: The name of the store or vendor.
    - `date`: The transaction date in "YYYY-MM-DD" format. If unavailable, use "Not Available".
    - `location`: City and State, if present. Otherwise, "Not Available".
    - `receipt_total`, `subtotal`, `tax`: Extract these values precisely as numbers in string format (e.g., "123.45"). If a value is missing, use "0.00".
3.  **Process Line Items:**
    - Extract EVERY SINGLE item purchased with its price.
    - `item`: The description of the item.
    - `amount`: The price of the item as a number in a string (e.g., "19.99").
    - `category`: Assign a category from this specific list: **["Food & Beverage", "Tools & Equipment", "Raw Materials", "Software & Subscriptions", "Competition Fees", "Travel & Lodging", "Office Supplies", "Miscellaneous"]**.
    - `justification`: Briefly explain why this item is a valid expense for the club. Be specific (e.g., "Food for team during a late-night work session," or "Aluminum stock for manufacturing chassis parts.").
    - `needs_approval`: Set to `true` if the item is unusual, a personal item (like clothing), alcohol, or costs more than $75. Otherwise, `false`.
    - `approval_reason`: If `needs_approval` is true, state why (e.g., "High-value item", "Potential personal expense").
4.  **Add Flags:**
    - Create a list of strings in the `flags` field for any major problems, such as "Receipt total does not match sum of line items", "Potentially personal items found", or "Date is missing". **Do not** flag store numbers or transaction IDs.
5.  **Assess Quality:**
    - `completeness_score`: Give an A-F grade based on how clear and complete the receipt is. (A=perfect, C=readable but missing info, F=unreadable).

**OCR TEXT TO ANALYZE:**
Use code with caution.
Python
{raw_text}
Generated code
**REQUIRED OUTPUT FORMAT:**
Your entire response MUST be a single, valid JSON object. Do not include any text, explanations, or markdown formatting outside of the JSON structure itself.
"""
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"An error occurred during the API call: {e}")
        return "" # Return empty string on failure

def parse_receipt_json(json_text: str) -> dict | None:
    """Parse AI response and robustly extract JSON data using regex."""
    if not json_text:
        return None
    
    # Regex to find a JSON object, even if it's wrapped in markdown
    match = re.search(r"```json\s*(\{.*?\})\s*```", json_text, re.DOTALL)
    if not match:
        match = re.search(r"(\{.*\})", json_text, re.DOTALL)

    if match:
        json_str = match.group(1)
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON: {e}")
            print(f"--- Received malformed JSON string ---\n{json_str}\n------------------------------------")
            return None
    else:
        print("Error: No valid JSON object found in the AI response.")
        print(f"--- Full AI Response ---\n{json_text}\n--------------------------")
        return None

def process_single_receipt(image_path: str, event_name: str = None) -> dict | None:
    """Process a single receipt image and return structured data."""
    print(f"  -> Reading and processing image: {os.path.basename(image_path)}")
    text = extract_text_from_image(image_path)
    if not text.strip():
        return None
    
    print("  -> Sending to AI for analysis...")
    ai_response = generate_reimbursement_summary(text, event_name)
    receipt_data = parse_receipt_json(ai_response)
    
    if receipt_data:
        receipt_data['file_name'] = os.path.basename(image_path)
        receipt_data['event_name'] = event_name or 'General'
        receipt_data['processed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print("  -> Successfully parsed AI response.")
    else:
        print("  -> Failed to parse AI response.")
        
    return receipt_data

# --- REPORTING AND EXPORTING FUNCTIONS ---

def format_single_receipt_summary(receipt_data: dict) -> str:
    """Format a single receipt's data into a readable summary."""
    summary = f"""=== REIMBURSEMENT SUMMARY ===

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

def save_text_file(filename: str, content: str):
    """Save text content to a file."""
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved: {filename}")

def process_event_receipts(image_paths: list[str], event_name: str) -> list[dict]:
    """Process multiple receipts for an event and show progress."""
    receipts_data = []
    total_receipts = len(image_paths)
    print(f"\nProcessing {total_receipts} receipts for event: '{event_name}'")
    
    for i, path in enumerate(image_paths, 1):
        print(f"\n--- Processing receipt {i}/{total_receipts} ---")
        try:
            receipt_data = process_single_receipt(path, event_name)
            receipts_data.append(receipt_data)
        except Exception as e:
            print(f"FATAL ERROR processing {path}: {e}")
            receipts_data.append(None) # Add a placeholder for failed processing
    
    return [r for r in receipts_data if r is not None]

def export_to_csv(receipts_data: list[dict], output_file: str):
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

def generate_summary_report(receipts_data: list[dict]) -> str:
    """Generate a comprehensive summary report for multiple receipts."""
    total_spent = 0
    category_totals = {}
    vendor_totals = {}
    flagged_receipts = []
    approval_items = []
    
    for receipt in receipts_data:
        if receipt.get('flags'):
            flagged_receipts.append({
                'file': receipt.get('file_name', ''),
                'flags': receipt.get('flags', []),
                'score': receipt.get('completeness_score', 'N/A')
            })
            
        for item in receipt.get('line_items', []):
            try:
                amount = float(item.get('amount', '0').replace('$', ''))
                total_spent += amount
                
                category = item.get('category', 'Miscellaneous')
                category_totals[category] = category_totals.get(category, 0) + amount
                
                vendor = receipt.get('merchant', 'Unknown Vendor')
                vendor_totals[vendor] = vendor_totals.get(vendor, 0) + amount
                
                if item.get('needs_approval'):
                    approval_items.append({
                        'item': item.get('item', ''),
                        'amount': amount,
                        'reason': item.get('approval_reason', ''),
                        'file': receipt.get('file_name', '')
                    })
            except (ValueError, AttributeError):
                continue
    
    report = f"""=== CLUB EXPENSE SUMMARY REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FINANCIAL OVERVIEW:
Total Amount Submitted: ${total_spent:.2f}
Number of Receipts Processed: {len(receipts_data)}
Number of Line Items: {sum(len(r.get('line_items', [])) for r in receipts_data)}

SPENDING BY CATEGORY:
"""
    
    for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / total_spent * 100) if total_spent > 0 else 0
        report += f"  - {category:<25} ${amount:>8.2f} ({percentage:.1f}%)\n"
    
    report += f"\nTOP VENDORS:\n"
    for vendor, amount in sorted(vendor_totals.items(), key=lambda x: x[1], reverse=True)[:5]:
        report += f"  - {vendor:<25} ${amount:>8.2f}\n"
    
    if approval_items:
        report += f"\nITEMS REQUIRING APPROVAL ({len(approval_items)}):\n"
        for item in approval_items:
            report += f"  - {item['item']} - ${item['amount']:.2f} ({item['reason']}) | File: {item['file']}\n"
    
    if flagged_receipts:
        report += f"\nFLAGGED RECEIPTS ({len(flagged_receipts)}):\n"
        for receipt in flagged_receipts:
            report += f"  - {receipt['file']} (Score: {receipt['score']})\n"
            for flag in receipt['flags']:
                report += f"    - {flag}\n"
    
    report += f"\nRECOMMENDATIONS:\n"
    report += "  - Review the generated CSV file for accuracy before submitting.\n"
    if approval_items:
        report += f"  - Seek treasurer/advisor sign-off for the {len(approval_items)} item(s) requiring approval.\n"
    if flagged_receipts:
        report += f"  - Check the original images for the {len(flagged_receipts)} flagged receipt(s) to clarify issues.\n"
    
    return report

# --- MAIN EXECUTION LOGIC ---

def ensure_results_folders():
    """Create results folders if they don't exist."""
    for folder in ['results/single', 'results/events', 'results/batch']:
        os.makedirs(folder, exist_ok=True)

def process_and_generate_reports(image_paths: list[str], event_name: str, output_folder: str):
    """Refactored logic to process images and generate both CSV and summary reports."""
    if not image_paths:
        print(f"No images found for processing.")
        return
        
    receipts_data = process_event_receipts(image_paths, event_name)
    if not receipts_data:
        print("\nProcessing complete. No receipts were successfully analyzed.")
        return

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    event_safe = re.sub(r'[^a-zA-Z0-9_-]', '_', event_name)
    base_filename = f"{event_safe}_{timestamp}"
    
    # Export CSV
    csv_filename = os.path.join(output_folder, f"{base_filename}_expenses.csv")
    export_to_csv(receipts_data, csv_filename)
    print(f"\nCSV report exported: {csv_filename}")

    # Generate and save summary report
    summary_report = generate_summary_report(receipts_data)
    summary_filename = os.path.join(output_folder, f"{base_filename}_summary.txt")
    save_text_file(summary_filename, summary_report)
    print(f"Summary report generated: {summary_filename}")
    
    # Print summary to console
    print("\n" + "="*50)
    print(summary_report)
    print("="*50 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Club Treasurer Receipt Processor v2.1',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
MODES OF OPERATION:

Single Receipt: Processes one image and prints the summary.
  python3 receipt_processor.py receipt.png

Event Processing: Processes multiple specified images for an event.
  python3 receipt_processor.py --event "FSAE Michigan Comp" receipt1.jpg receipt2.png

Batch Processing: Processes all images in a folder, using the folder name as the event.
  python3 receipt_processor.py --batch ./competition_receipts/

REQUIREMENTS:
- Python 3
- Tesseract OCR engine installed on your system
- A GEMINI_API_KEY set as an environment variable
"""
    )
    
    parser.add_argument('images', nargs='*', help='One or more receipt image files to process.')
    parser.add_argument('--event', help='An event name to associate with multiple receipts.')
    parser.add_argument('--batch', help='Path to a folder containing receipt images to process as a batch.')
    
    args = parser.parse_args()
    
    if not args.images and not args.batch:
        parser.print_help()
        sys.exit(1)
    
    ensure_results_folders()
    
    if args.batch:
        folder_path = args.batch
        if not os.path.isdir(folder_path):
            print(f"Error: Batch folder '{folder_path}' not found.")
            return
        
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.tiff', '*.bmp']
        image_files = []
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(folder_path, ext)))
        
        event_name = os.path.basename(os.path.normpath(folder_path))
        process_and_generate_reports(image_files, event_name, 'results/batch')

    elif args.event:
        if not args.images:
            print("Error: Please specify at least one image file for --event mode.")
            return
        process_and_generate_reports(args.images, args.event, 'results/events')
        
    else: # Single receipt mode
        if len(args.images) != 1:
            print("Error: Single receipt mode requires exactly one image file.")
            return
        
        image_path = args.images[0]
        if not os.path.exists(image_path):
            print(f"Error: File '{image_path}' not found.")
            return
            
        receipt_data = process_single_receipt(image_path)
        if receipt_data:
            summary = format_single_receipt_summary(receipt_data)
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            summary_filename = f"results/single/{base_name}_summary.txt"
            save_text_file(summary_filename, summary)
            print("\n" + summary)
        else:
            print("Could not process the receipt.")

if __name__ == "__main__":
    main()
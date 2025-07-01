"""
Receipt data model and core processing logic.
"""

import os
import sys
import json
import re
from datetime import datetime
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class ReceiptProcessor:
    """Core receipt processing model."""
    
    def __init__(self):
        self.model = self._configure_gemini()
    
    def _configure_gemini(self):
        """Configure the Gemini model and ensure API key is present."""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("Error: GEMINI_API_KEY environment variable not set.")
            print("Please copy .env.example to .env and set your API key.")
            sys.exit(1)
            sys.exit(1)
        
        genai.configure(api_key=api_key)
        return genai.GenerativeModel("gemini-1.5-flash")
    
    def analyze_receipt_image(self, image_path: str, event_name: str = None) -> str:
        """Analyze a receipt image and generate structured data."""
        try:
            image = Image.open(image_path)
        except FileNotFoundError:
            print(f"Error: Image file not found at {image_path}")
            return ""
        except Exception as e:
            print(f"Error opening image {image_path}: {e}")
            return ""

        event_context = f"This receipt is for the business event: '{event_name}'." if event_name else ""
        
        prompt = f"""You are an expert financial processor for a business organization. Your task is to analyze the provided receipt IMAGE and convert it into a structured JSON format.

**CONTEXT:**
- You are looking directly at a photo of a receipt. Use your vision capabilities to read all text, including logos and layouts, to understand the contents.
- The business can only reimburse expenses directly related to its operations.
{event_context}

**INSTRUCTIONS:**
1.  **Analyze the Image:** Carefully read all text in the image to identify the merchant, date, and line items.
2.  **Extract Key Information:**
    - `merchant`: The name of the store or vendor. Find it near the top.
    - `date`: The transaction date in "YYYY-MM-DD" format. If unavailable, use "Not Available".
    - `location`: City and State, if present. Otherwise, "Not Available".
    - `receipt_total`, `subtotal`, `tax`: Extract these values precisely as numbers in string format (e.g., "123.45"). If a value is missing, use "0.00".
3.  **Process Line Items:**
    - Extract EVERY SINGLE item purchased with its price.
    - `item`: The description of the item.
    - `amount`: The price of the item as a number in a string (e.g., "19.99").
    - `category`: Assign a category from this specific list: **["Food & Beverage", "Tools & Equipment", "Raw Materials", "Software & Subscriptions", "Event Fees", "Travel & Lodging", "Office Supplies", "Miscellaneous"]**.
    - `justification`: Briefly explain why this item is a valid expense for the business. Be specific (e.g., "Office supplies for daily operations," or "Materials for product development.").
    - `needs_approval`: Set to `true` if the item is unusual, a personal item (like clothing), alcohol, or costs more than $75. Otherwise, `false`.
    - `approval_reason`: If `needs_approval` is true, state why (e.g., "High-value item", "Potential personal expense").
4.  **Add Flags:**
    - Create a list of strings in the `flags` field for any major problems, such as "Receipt total does not match sum of line items", "Potentially personal items found", or "Date is missing". **Do not** flag store numbers or transaction IDs.
5.  **Assess Quality:**
    - `completeness_score`: Give an A-F grade based on how clear and complete the receipt image is. (A=perfect, C=readable but missing info, F=unreadable).

**REQUIRED OUTPUT FORMAT:**
Your entire response MUST be a single, valid JSON object. Do not include any text, explanations, or markdown formatting outside of the JSON structure itself.
"""
        try:
            response = self.model.generate_content([prompt, image])
            return response.text
        except Exception as e:
            print(f"An error occurred during the API call: {e}")
            return ""
    
    def parse_receipt_json(self, json_text: str) -> dict | None:
        """Parse response and robustly extract JSON data using regex."""
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
            print("Error: No valid JSON object found in the response.")
            print(f"--- Full Response ---\n{json_text}\n--------------------------")
            return None
    
    def process_single_receipt(self, image_path: str, event_name: str = None) -> dict | None:
        """Process a single receipt image and return structured data."""
        print(f"  -> Analyzing image: {os.path.basename(image_path)}")
        response = self.analyze_receipt_image(image_path, event_name)
        
        if not response:
            print("  -> Analysis failed.")
            return None

        receipt_data = self.parse_receipt_json(response)
        
        if receipt_data:
            receipt_data['file_name'] = os.path.basename(image_path)
            receipt_data['event_name'] = event_name or 'General'
            receipt_data['processed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("  -> Successfully parsed response.")
        else:
            print("  -> Failed to parse response.")
            
        return receipt_data
    
    def process_event_receipts(self, image_paths: list[str], event_name: str) -> list[dict]:
        """Process multiple receipts for an event and show progress."""
        receipts_data = []
        total_receipts = len(image_paths)
        print(f"\nProcessing {total_receipts} receipts for event: '{event_name}'")
        
        for i, path in enumerate(image_paths, 1):
            print(f"\n--- Processing receipt {i}/{total_receipts} ---")
            try:
                receipt_data = self.process_single_receipt(path, event_name)
                receipts_data.append(receipt_data)
            except Exception as e:
                print(f"FATAL ERROR processing {path}: {e}")
                receipts_data.append(None)
        
        return [r for r in receipts_data if r is not None]


class ReportGenerator:
    """Handles report generation and data analysis."""
    
    def generate_summary_report(self, receipts_data: list[dict]) -> str:
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
        
        report = f"""=== BUSINESS EXPENSE SUMMARY REPORT ===
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
            report += f"  - Seek financial manager/supervisor sign-off for the {len(approval_items)} item(s) requiring approval.\n"
        if flagged_receipts:
            report += f"  - Check the original images for the {len(flagged_receipts)} flagged receipt(s) to clarify issues.\n"
        
        return report

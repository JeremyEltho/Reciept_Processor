import os
import json
import csv
from datetime import datetime
from PIL import Image
import pytesseract
import google.generativeai as genai

def configure_gemini():
    api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCC88P2ZrbzMgUcchPgmJXYD7cOCACQTkw')
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-1.5-flash")

model = configure_gemini()

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

def generate_reimbursement_summary(raw_text, event_name=None):
    prompt = f"""You are a club treasurer's expense analysis assistant. Analyze this receipt for a student organization (FSAE, robotics, etc.).\n\nRECEIPT TEXT:\n{raw_text}\n\nINSTRUCTIONS:\n1. Extract ALL line items with prices\n2. Identify merchant, date, location, and receipt total\n3. Categorize each expense using CLUB-SPECIFIC categories\n4. Flag any issues or items needing approval\n5. Return data in JSON format for easy processing\n\nFORMAT YOUR RESPONSE AS VALID JSON:\n{{\n    \"merchant\": \"Vendor Name\",\n    \"date\": \"MM/DD/YYYY or 'Not Available'\",\n    \"location\": \"City, State or 'Not Available'\", \n    \"receipt_total\": \"XX.XX\",\n    \"subtotal\": \"XX.XX\",\n    \"tax\": \"XX.XX\",\n    \"line_items\": [\n        {{\n            \"item\": \"Item Description\",\n            \"amount\": \"XX.XX\",\n            \"category\": \"Category Name\",\n            \"justification\": \"Why this is a valid club expense\",\n            \"needs_approval\": true/false,\n            \"approval_reason\": \"Reason if needs approval\"\n        }}\n    ],\n    \"flags\": [\n        \"Any issues: missing total, unclear items, personal expenses, etc.\"\n    ],\n    \"completeness_score\": \"A-F grade for receipt quality\"\n}}\n\nBe precise with amounts and realistic about what clubs can reimburse."""
    response = model.generate_content(prompt)
    return response.text

def parse_receipt_json(json_text):
    try:
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

def process_event_receipts(image_paths, event_name):
    receipts_data = []
    for path in image_paths:
        try:
            receipt_data = process_single_receipt(path, event_name)
            receipts_data.append(receipt_data)
        except Exception as e:
            print(f"Error processing {path}: {e}")
            receipts_data.append(None)
    return receipts_data

def export_to_csv(receipts_data, output_file):
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

def format_single_receipt_summary(receipt_data):
    base_name = receipt_data.get('file_name', 'receipt')
    summary = f"""=== REIMBURSEMENT SUMMARY ===\n\nMERCHANT: {receipt_data.get('merchant', 'N/A')} | DATE: {receipt_data.get('date', 'N/A')} | LOCATION: {receipt_data.get('location', 'N/A')}\n\nLINE ITEMS:\n"""
    for item in receipt_data.get('line_items', []):
        approval_note = f" [NEEDS APPROVAL: {item.get('approval_reason', 'High value')}]" if item.get('needs_approval') else ""
        summary += f"• {item.get('item', 'N/A')} - ${item.get('amount', '0.00')} → {item.get('category', 'Unknown')} - {item.get('justification', 'N/A')}{approval_note}\n"
    summary += f"""\nTOTALS:\nSubtotal: ${receipt_data.get('subtotal', '0.00')}\nTax: ${receipt_data.get('tax', '0.00')}\nTOTAL: ${receipt_data.get('receipt_total', '0.00')}\n\nRECEIPT QUALITY: {receipt_data.get('completeness_score', 'N/A')}\n"""
    if receipt_data.get('flags'):
        summary += "\nFLAGS:\n"
        for flag in receipt_data.get('flags', []):
            summary += f"- {flag}\n"
    return summary

def save_text_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Saved: {filename}")

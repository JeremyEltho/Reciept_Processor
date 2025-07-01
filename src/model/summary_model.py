from datetime import datetime

def generate_summary_report(receipts_data):
    total_spent = 0
    category_totals = {}
    vendor_totals = {}
    flagged_receipts = []
    approval_items = []
    for receipt in receipts_data:
        if not receipt:
            continue
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
                category = item.get('category', 'Unknown')
                category_totals[category] = category_totals.get(category, 0) + amount
                vendor = receipt.get('merchant', 'Unknown')
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
    report = f"""
=== CLUB EXPENSE SUMMARY REPORT ===
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

FINANCIAL OVERVIEW:
Total Amount: ${total_spent:.2f}
Number of Receipts: {len([r for r in receipts_data if r])}
Number of Line Items: {sum(len(r.get('line_items', [])) for r in receipts_data if r)}

SPENDING BY CATEGORY:
"""
    for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / total_spent * 100) if total_spent > 0 else 0
        report += f"  {category}: ${amount:.2f} ({percentage:.1f}%)\n"
    report += f"\nTOP VENDORS:\n"
    for vendor, amount in sorted(vendor_totals.items(), key=lambda x: x[1], reverse=True)[:5]:
        report += f"  {vendor}: ${amount:.2f}\n"
    if approval_items:
        report += f"\nITEMS REQUIRING APPROVAL ({len(approval_items)}):\n"
        for item in approval_items:
            report += f"  • {item['item']} - ${item['amount']:.2f} ({item['reason']})\n"
            report += f"    File: {item['file']}\n"
    if flagged_receipts:
        report += f"\nFLAGGED RECEIPTS ({len(flagged_receipts)}):\n"
        for receipt in flagged_receipts:
            report += f"  • {receipt['file']} (Score: {receipt['score']})\n"
            for flag in receipt['flags']:
                report += f"    - {flag}\n"
    report += f"\nRECOMMENDATIONS:\n"
    if total_spent > 500:
        report += "  • High total spending - ensure all receipts are properly justified\n"
    if len(approval_items) > 0:
        report += f"  • {len(approval_items)} items need treasurer/advisor approval before submission\n"
    if len(flagged_receipts) > 0:
        report += f"  • {len(flagged_receipts)} receipts have quality issues - review before submitting\n"
    report += "  • Export to CSV for easy finance office submission\n"
    report += "  • Keep original receipt images as backup documentation\n"
    return report

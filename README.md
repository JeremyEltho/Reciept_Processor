# 🏆 Club Treasurer Expense Processor

A comprehensive receipt processing tool designed specifically for student organizations like FSAE teams, robotics clubs, and other student groups. Automatically categorizes expenses, flags issues, and generates finance-ready reports.

## 📁 Project Structure

```
sedai_pet_project/
├── src/                          # Source code
│   ├── check.py                  # Main application
│   └── requirements.txt          # Python dependencies
├── test_data/                    # Test receipt images
│   └── receipts/                 # Sample receipt files
├── results/                      # Generated outputs
│   ├── single/                   # Single receipt summaries
│   ├── events/                   # Event processing results
│   └── batch/                    # Batch processing results
└── README.md                     # This file
```

## 🚀 Features

### 🏷️ **Smart Categorization**
- **Competition Food** (team meals during events/travel)
- **Tools & Equipment** (hardware, parts, manufacturing supplies)
- **Travel & Lodging** (gas, flights, hotels for competitions)
- **Registration Fees** (competition entries, memberships)
- **Materials & Consumables** (raw materials, fasteners, fluids)
- **Software & Subscriptions** (CAD, analysis tools, cloud services)
- **Team Building & Recruitment** (social events, recruitment materials)
- **Office Supplies** (printing, stationery, organization materials)
- **Training & Education** (courses, books, certifications)

### 📊 **Processing Modes**
1. **Single Receipt**: Process individual receipts
2. **Event Processing**: Group multiple receipts for a single event
3. **Batch Processing**: Process entire folders of receipts

### 🚩 **Quality Control**
- Receipt quality scoring (A-F grades)
- Automatic flagging for missing information
- Approval requirements for high-value items (>$100)
- Detection of questionable expenses

### 📈 **Finance-Ready Outputs**
- CSV exports for finance office submission
- Comprehensive treasurer summary reports
- Category breakdowns with spending percentages
- Top vendor analysis
- Approval queue management

## 📋 Usage

### Prerequisites
```bash
cd src/
pip install -r requirements.txt
```

Note: Requires Tesseract OCR to be installed on your system.

### Single Receipt Processing
```bash
python src/check.py test_data/receipts/receipt_home_depot.png
```
**Output**: `receipt_home_depot_reimbursement_summary.txt`

### Event Processing
```bash
python src/check.py --event "FSAE Competition Michigan" test_data/receipts/receipt_*.png
```
**Output**: 
- `Event_YYYYMMDD_HHMMSS_expenses.csv`
- `Event_YYYYMMDD_HHMMSS_summary.txt`

### Batch Processing
```bash
python src/check.py --batch test_data/receipts/
```
**Output**:
- `FolderName_YYYYMMDD_HHMMSS_batch_expenses.csv`
- `FolderName_YYYYMMDD_HHMMSS_batch_summary.txt`

### Help
```bash
python src/check.py --help
```

## 📊 Sample Output

### CSV Export Format
| Event | File Name | Merchant | Date | Location | Item | Amount | Category | Justification | Needs Approval | Receipt Total |
|-------|-----------|----------|------|----------|------|--------|----------|---------------|----------------|---------------|
| FSAE Michigan | receipt_home_depot.png | Home Depot | 06/30/2025 | Detroit, MI | Screwdriver Set | 14.99 | Tools & Equipment | Essential hand tool for vehicle maintenance | false | 27.63 |

### Summary Report Features
- 📊 Financial overview (total spending, receipt counts)
- 💰 Category breakdowns with percentages
- 🏪 Top vendor analysis
- ⚠️ Items requiring approval
- 🚩 Flagged receipts with quality issues
- ✅ Actionable recommendations

## 🎯 Perfect For
- **FSAE Teams** organizing competition expenses
- **Robotics Clubs** tracking tool and material purchases
- **Student Organizations** managing event and operational costs
- **Club Treasurers** preparing expense reports for submission

## 🔧 Technical Details
- **OCR**: Uses Tesseract for text extraction from receipt images
- **AI**: Leverages Google Gemini for intelligent expense categorization
- **Formats**: Supports PNG, JPG, JPEG, TIFF, BMP image formats
- **Export**: CSV and TXT file generation
- **Processing**: JSON-based structured data handling

## 📝 Security Note
The script includes a fallback API key for testing. For production use, set the `GEMINI_API_KEY` environment variable with your own API key.

## 🤝 Contributing
This tool was designed to make club treasurers' lives easier. Feel free to customize categories and approval thresholds for your organization's specific needs.

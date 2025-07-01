# Test Data

This folder contains sample receipt images for testing the Club Treasurer Expense Processor.

## Receipt Files

- `receipt_home_depot.png` - Tools & equipment purchase
- `receipt_office_depot.png` - Office supplies purchase  
- `receipt_tacobell.png` - Food expense
- `receipt_uber.png` - Transportation expense
- `receipt_airbnb.png` - Lodging expense
- `sample_receipt.png` - General test receipt
- `sample_receipt2.png` - Duplicate test receipt

## Usage

These files are used for testing the three processing modes:

### Single Receipt
```bash
python ../src/check.py receipts/receipt_home_depot.png
```

### Event Processing
```bash
python ../src/check.py --event "Test Event" receipts/receipt_*.png
```

### Batch Processing
```bash
python ../src/check.py --batch receipts/
```

All test results will be saved to the appropriate folders in the `../results/` directory.

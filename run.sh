#!/bin/bash

# Create results folders if they don't exist
mkdir -p results/{single,events,batch}

# Clean results folders before each run
find results/ -type f -name "*.txt" -delete
find results/ -type f -name "*.csv" -delete

# Run the unified receipt processor
python receipt_processor.py "$@"

echo ""
echo "Results saved to:"
echo "   Single receipts: results/single/"
echo "   Event processing: results/events/"
echo "   Batch processing: results/batch/"
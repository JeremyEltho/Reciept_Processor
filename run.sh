#!/bin/bash
# Club Treasurer Expense Processor - Run Script (MVC)
# Usage: ./run.sh [arguments]

# Clean results folders before each run
rm -f results/single/* results/events/* results/batch/*

cd "$(dirname "$0")/src"
python main.py "$@"

cd ..
echo ""
echo "Results saved to:"
echo "   Single receipts: results/single/"
echo "   Event processing: results/events/"  
echo "   Batch processing: results/batch/"

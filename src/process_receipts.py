#!/usr/bin/env python3
"""
Club Treasurer Expense Processor

A comprehensive tool for processing receipts and generating expense reports
specifically designed for student organizations like FSAE teams, robotics clubs, etc.

Usage:
    python process_receipts.py receipt.png                    # Single receipt
    python process_receipts.py --event "Event" receipt1.png   # Event processing  
    python process_receipts.py --batch folder/                # Batch processing
    python process_receipts.py --help                         # Show help

Author: AI Assistant for Club Treasurers
"""

import sys
import os
import csv
import json
import glob
from datetime import datetime
from pathlib import Path

# Add the parent directory to path for imports if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from PIL import Image
    import pytesseract
    import google.generativeai as genai
except ImportError as e:
    print(f"Missing required dependency: {e}")
    print("Please install requirements: pip install -r requirements.txt")
    sys.exit(1)

# Configuration
RESULTS_DIR = Path(__file__).parent.parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)
(RESULTS_DIR / "single").mkdir(exist_ok=True)
(RESULTS_DIR / "events").mkdir(exist_ok=True)
(RESULTS_DIR / "batch").mkdir(exist_ok=True)

# Configure Gemini
api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyCC88P2ZrbzMgUcchPgmJXYD7cOCACQTkw')
genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-1.5-flash")

# Rest of the code stays the same...
# (The functions from check.py would be copied here)

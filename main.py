#!/usr/bin/env python3
"""
Business Receipt Processor
Processes receipt images for business expense tracking and reporting.
"""

import argparse
import sys
from dotenv import load_dotenv
from controllers.receipt_controller import ReceiptController

# Load environment variables from .env file
load_dotenv()


def main():
    parser = argparse.ArgumentParser(
        description='Business Receipt Processor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
MODES OF OPERATION:

Single Receipt: Processes one image and prints the summary.
  python3 receipt_processor.py receipt.png

Event Processing: Processes multiple specified images for an event.
  python3 receipt_processor.py --event "Q1 Team Meeting" receipt1.jpg receipt2.png

Batch Processing: Processes all images in a folder, using the folder name as the event.
  python3 receipt_processor.py --batch ./business_receipts/

REQUIREMENTS:
- Python 3
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
    
    controller = ReceiptController()
    controller.ensure_results_folders()
    
    if args.batch:
        controller.process_batch_folder(args.batch)
    elif args.event:
        if not args.images:
            print("Error: Please specify at least one image file for --event mode.")
            return
        controller.process_event_images(args.images, args.event)
    else:  # Single receipt mode
        if len(args.images) != 1:
            print("Error: Single receipt mode requires exactly one image file.")
            return
        controller.process_single_image_with_output(args.images[0])


if __name__ == "__main__":
    main()

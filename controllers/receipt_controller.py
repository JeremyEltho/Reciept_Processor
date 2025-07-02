"""
Controller for receipt processing operations.
Coordinates between model and view components.
"""

import os
import glob
import re
from datetime import datetime

from models.receipt_model import ReceiptProcessor, ReportGenerator
from models.rag_model import ReceiptRAG
from views.receipt_view import ReceiptFormatter, CSVExporter, FileHandler


class ReceiptController:
    """Main controller for receipt processing operations."""
    
    def __init__(self):
        self.processor = ReceiptProcessor()
        self.report_generator = ReportGenerator()
        self.formatter = ReceiptFormatter()
        self.csv_exporter = CSVExporter()
        self.file_handler = FileHandler()
        self.rag = ReceiptRAG()
    
    def process_single_receipt(self, image_path: str, event_name: str = None) -> dict | None:
        """Process a single receipt and return the data."""
        return self.processor.process_single_receipt(image_path, event_name)
    
    def format_single_receipt_summary(self, receipt_data: dict) -> str:
        """Format a single receipt summary."""
        return self.formatter.format_single_receipt_summary(receipt_data)
    
    def save_text_file(self, filename: str, content: str):
        """Save text content to a file."""
        self.file_handler.save_text_file(filename, content)
    
    def ensure_results_folders(self):
        """Create results folders if they don't exist."""
        for folder in ['results/single', 'results/events', 'results/batch']:
            os.makedirs(folder, exist_ok=True)
    
    def process_and_generate_reports(self, image_paths: list[str], event_name: str, output_folder: str):
        """Process images and generate both CSV and summary reports."""
        if not image_paths:
            print(f"No images found for processing.")
            return
            
        receipts_data = self.processor.process_event_receipts(image_paths, event_name)
        if not receipts_data:
            print("\nProcessing complete. No receipts were successfully analyzed.")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        event_safe = re.sub(r'[^a-zA-Z0-9_-]', '_', event_name)
        base_filename = f"{event_safe}_{timestamp}"
        
        # Export CSV
        csv_filename = os.path.join(output_folder, f"{base_filename}_expenses.csv")
        self.csv_exporter.export_to_csv(receipts_data, csv_filename)
        print(f"\nCSV report exported: {csv_filename}")

        # Generate and save summary report
        summary_report = self.report_generator.generate_summary_report(receipts_data)
        summary_filename = os.path.join(output_folder, f"{base_filename}_summary.txt")
        self.file_handler.save_text_file(summary_filename, summary_report)
        print(f"Summary report generated: {summary_filename}")
        
        # Print summary to console
        print("\n" + "="*50)
        print(summary_report)
        print("="*50 + "\n")
    
    def process_batch_folder(self, folder_path: str):
        """Process all images in a folder as a batch."""
        if not os.path.isdir(folder_path):
            print(f"Error: Batch folder '{folder_path}' not found.")
            return
        
        image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.tiff', '*.bmp']
        image_files = []
        for ext in image_extensions:
            image_files.extend(glob.glob(os.path.join(folder_path, ext)))
        
        event_name = os.path.basename(os.path.normpath(folder_path))
        self.process_and_generate_reports(image_files, event_name, 'results/batch')
    
    def process_event_images(self, image_paths: list[str], event_name: str):
        """Process multiple images for a specific event."""
        self.process_and_generate_reports(image_paths, event_name, 'results/events')
    
    def process_single_image_with_output(self, image_path: str):
        """Process a single image and save the summary to file."""
        if not os.path.exists(image_path):
            print(f"Error: File '{image_path}' not found.")
            return
            
        receipt_data = self.process_single_receipt(image_path)
        if receipt_data:
            summary = self.format_single_receipt_summary(receipt_data)
            base_name = os.path.splitext(os.path.basename(image_path))[0]
            summary_filename = f"results/single/{base_name}_summary.txt"
            self.save_text_file(summary_filename, summary)
            print("\n" + summary)
        else:
            print("Could not process the receipt.")
    
    def load_receipt_for_questions(self, receipt_data: dict):
        """Load receipt data into RAG system for questions."""
        self.rag.load_receipt_context(receipt_data)
    
    def ask_receipt_question(self, question: str) -> str:
        """Ask a question about the loaded receipt."""
        return self.rag.ask_question(question)
    
    def get_suggested_questions(self) -> list:
        """Get suggested questions for the current receipt."""
        return self.rag.get_suggested_questions()

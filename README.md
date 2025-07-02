# Business Receipt Processor

A web-based receipt processing system that analyzes receipt images using computer vision to extract structured expense data. Built with Python, Flask, and Google's Gemini AI for automated receipt parsing.

## Features

- **Web Interface**: Upload and process receipts through a clean web interface
- **Command Line Interface**: Process single receipts, events, or batch folders
- **Smart Categorization**: Automatically categorizes expenses by type
- **Approval Workflow**: Flags items that need management approval
- **Multiple Export Formats**: CSV exports and text summaries
- **Image Format Support**: PNG, JPG, JPEG, TIFF, BMP
- **RAG Chatbot**: Ask questions about processed receipts using AI

## Quick Start

1. **Install and setup:**
```bash
pip install -r requirements.txt && cp .env.example .env
```

2. **Edit `.env` file and add your API key:**
```bash
# Edit the .env file and replace 'your_gemini_api_key_here' with your actual key
```

3. **Start the application:**
```bash
cd web && python app.py
```

4. **Open your browser to:** `http://localhost:5002`

## Setup

1. **Install Dependencies**
```bash
pip install -r requirements.txt
```

2. **Configure Environment**
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

3. **Run Web Interface**
```bash
cd web
python app.py
```

4. **Run Both Frontend and Backend (Recommended)**
```bash
# In one terminal - start the web server
cd web && python app.py &

# The web interface will be available at http://localhost:5000
# Backend processing happens automatically when you upload files
```

5. **Or Use CLI Only**
```bash
python main.py receipt.png
```

## Project Structure

```
business-receipt-processor/
├── controllers/          # Business logic controllers
├── models/              # Data models and AI processing
├── views/               # Output formatting and file handling
├── web/                 # Flask web application
│   ├── templates/       # HTML templates
│   └── uploads/         # File upload directory
├── main.py             # CLI entry point
└── requirements.txt    # Python dependencies
```

## Usage

### Web Interface (Recommended)
1. Start the application: `cd web && python app.py`
2. Navigate to `http://localhost:5002`
3. Upload a receipt image
4. View processed results and download summary
5. **NEW**: Ask questions about your receipt using the chatbot!

### CLI Options
- Single receipt: `python main.py receipt.png`
- Event processing: `python main.py --event "Team Meeting" receipt1.jpg receipt2.png`
- Batch processing: `python main.py --batch ./receipts_folder/`

## Output

The system generates:
- **CSV files**: Structured data for accounting systems
- **Text summaries**: Human-readable expense reports
- **Approval flags**: Items requiring management review

## Categories

Expenses are automatically categorized into:
- Food & Beverage
- Tools & Equipment
- Raw Materials
- Software & Subscriptions
- Event Fees
- Travel & Lodging
- Office Supplies
- Miscellaneous
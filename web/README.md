# Web Interface Documentation

## Flask App Features

- **Receipt Upload**: Supports PNG receipt uploads via web form
- **Real-time Processing**: OCR and AI categorization happens immediately
- **Results Display**: Shows formatted summary directly in browser
- **Download Option**: Provides TXT file download of results

## Usage

1. Start the server: `cd web && python app.py`
2. Open browser to `http://127.0.0.1:5000`
3. Upload a PNG receipt file
4. View results and download summary

## Configuration

- Upload folder: `web/uploads/`
- Results folder: `web/results/`
- Supported formats: PNG only
- Debug mode: Enabled by default

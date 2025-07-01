import os
import sys
from flask import Flask, request, render_template, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add parent directory to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from controllers.receipt_controller import ReceiptController

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
RESULTS_FOLDER = os.path.join(os.path.dirname(__file__), 'results')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tiff', 'bmp'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

# Initialize controller
controller = ReceiptController()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No selected file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # Process receipt
            receipt_data = controller.process_single_receipt(filepath)
            if not receipt_data:
                return render_template('index.html', error='Could not process receipt')
            summary = controller.format_single_receipt_summary(receipt_data)
            result_filename = filename.rsplit('.', 1)[0] + '_summary.txt'
            result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
            controller.save_text_file(result_path, summary)
            return render_template('index.html', summary=summary, download_link=url_for('download_file', filename=result_filename))
        else:
            return render_template('index.html', error='Invalid file type. Supported formats: PNG, JPG, JPEG, TIFF, BMP')
    return render_template('index.html')

@app.route('/results/<filename>')
def download_file(filename):
    return send_from_directory(app.config['RESULTS_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)

import os
import sys
from flask import Flask, request, render_template, send_from_directory, redirect, url_for, jsonify, session
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
app.secret_key = 'receipt_processor_secret_key_2025'  # For session management

# Initialize controller
controller = ReceiptController()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        print("POST request received")
        print("Files in request:", request.files)
        
        if 'file' not in request.files:
            print("No file part in request")
            return render_template('index.html', error='No file part')
        
        file = request.files['file']
        print(f"File object: {file}")
        print(f"Filename: '{file.filename}'")
        
        if file.filename == '':
            print("Empty filename")
            return render_template('index.html', error='No file selected')
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"Saving file to: {filepath}")
            file.save(filepath)
            
            try:
                # Process receipt
                print("Processing receipt...")
                receipt_data = controller.process_single_receipt(filepath)
                print(f"Receipt data: {receipt_data}")
                
                if not receipt_data:
                    return render_template('index.html', error='Could not process receipt - check API key')
                
                # Load receipt data for RAG questions
                controller.load_receipt_for_questions(receipt_data)
                session['has_receipt'] = True
                
                summary = controller.format_single_receipt_summary(receipt_data)
                result_filename = filename.rsplit('.', 1)[0] + '_summary.txt'
                result_path = os.path.join(app.config['RESULTS_FOLDER'], result_filename)
                controller.save_text_file(result_path, summary)
                
                # Get suggested questions
                suggested_questions = controller.get_suggested_questions()
                
                return render_template('index.html', 
                                     summary=summary, 
                                     download_link=url_for('download_file', filename=result_filename),
                                     suggested_questions=suggested_questions,
                                     show_chat=True)
            except Exception as e:
                print(f"Error processing receipt: {e}")
                return render_template('index.html', error=f'Error processing receipt: {str(e)}')
        else:
            print("Invalid file type")
            return render_template('index.html', error='Invalid file type. Supported formats: PNG, JPG, JPEG, TIFF, BMP')
    
    return render_template('index.html')

@app.route('/results/<filename>')
def download_file(filename):
    return send_from_directory(app.config['RESULTS_FOLDER'], filename, as_attachment=True)

@app.route('/ask_question', methods=['POST'])
def ask_question():
    """Handle chatbot questions about the receipt."""
    if not session.get('has_receipt'):
        return jsonify({'error': 'No receipt data loaded. Please upload a receipt first.'})
    
    data = request.get_json()
    question = data.get('question', '').strip()
    
    if not question:
        return jsonify({'error': 'Please enter a question.'})
    
    try:
        answer = controller.ask_receipt_question(question)
        return jsonify({'answer': answer})
    except Exception as e:
        return jsonify({'error': f'Error processing question: {str(e)}'})

@app.route('/suggested_questions')
def get_suggested_questions():
    """Get suggested questions for the current receipt."""
    if not session.get('has_receipt'):
        return jsonify({'questions': []})
    
    try:
        questions = controller.get_suggested_questions()
        return jsonify({'questions': questions})
    except Exception as e:
        return jsonify({'questions': [], 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5002)

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv
from parser.file_reader import read_file
from parser.llm import parseResume , generateDescription
from tqdm import tqdm 
from pathlib import Path
from dotenv import load_dotenv

app = Flask(__name__)

CORS(app, origins=["http://localhost:5173"])  


UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    text = read_file(filepath)

    if not text or text.strip() == "":
        return jsonify({"error": "Failed to extract text from the resume"}), 500

    try:
        print("🧠 Extracting resume info...")
        print("📊 sections:", text)
        result = parseResume(text)
        return result, 200
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        return jsonify({"error": "Internal error while parsing resume"}), 500

@app.route('/generateDes', methods=['POST'])
def description():
    try:
        data = request.json
        # Ensure data is not None and contains expected keys
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400
        
        if 'job_summary' not in data:
            return jsonify({"error": "Missing 'job_title' or 'job_summary' in request"}), 400

        job_summary = data.get('job_summary', 'Default Summary')
        output = generateDescription(job_summary)
        print(output)
        # Corrected: jsonify the dictionary, and return the status code separately
        return jsonify({"job_description": output}), 200

    except Exception as e:
        # It's good practice to log the full exception for debugging
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True , port = 5050)
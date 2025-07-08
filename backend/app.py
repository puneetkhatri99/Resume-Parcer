from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from parser.file_reader import read_file
from parser.extractor import extract_resume_info, extract_skills_section
from tqdm import tqdm 


# Initialize Flask app
app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"])  # Adjust for your frontend port

# Uploads folder
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}

def allowed_file(filename):
    return os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_resume():
    print("🚨 Frontend hit /upload endpoint!")
    if 'resume' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['resume']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Unsupported file type"}), 400
    print(f"📥 Received file: {file.filename}")

    # Save the uploaded file
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    print("📄 Reading file...")
    # Extract raw text
    text = read_file(filepath)
    if not text or text.strip() == "":
        return jsonify({"error": "Failed to extract text from the resume"}), 500

    # Extract structured data
    try:
        print("🧠 Extracting resume info...")
        for _ in tqdm(range(15), desc="Parsing", ncols=75):
            pass
        result = extract_resume_info(text)
        print("✅ Done parsing!")
        # print("📊 sections:", text)
        return jsonify(result), 200
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        return jsonify({"error": "Internal error while parsing resume"}), 500

if __name__ == '__main__':
    app.run(debug=True)
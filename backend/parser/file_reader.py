import pdfplumber
from docx import Document
import os

def read_file(path):
    ext = os.path.splitext(path)[-1].lower()
    try:
        if ext == ".pdf":
            with pdfplumber.open(path) as pdf:
                return "\n".join(p.extract_text() for p in pdf.pages if p.extract_text())
        elif ext == ".docx":
            doc = Document(path)
            return "\n".join([p.text for p in doc.paragraphs])
        elif ext == ".txt":
            with open(path, 'r') as f:
                return f.read()
        else:
            raise ValueError("Unsupported file type.")
    
    except Exception as e:
        print(f"this format not supported: {e}")
        return None
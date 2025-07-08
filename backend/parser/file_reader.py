import pdfplumber
from docx import Document
from PIL import Image
import pytesseract
import os

def read_file(path):
    ext = os.path.splitext(path)[-1].lower()

    try:
        if ext == ".pdf":
            text = ""
            with pdfplumber.open(path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                    else:
                        # OCR fallback for image-based PDF pages
                        img = page.to_image(resolution=300)
                        pil_image = img.original.convert("L")
                        ocr_text = pytesseract.image_to_string(pil_image)
                        text += ocr_text + "\n"
            return text.strip()

        elif ext == ".docx":
            doc = Document(path)
            return "\n".join([p.text for p in doc.paragraphs])

        elif ext == ".txt":
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()

        elif ext in [".jpg", ".jpeg", ".png"]:
            image = Image.open(path)
            ocr_text = pytesseract.image_to_string(image.convert("L"))  # grayscale improves OCR
            return ocr_text.strip()

        else:
            raise ValueError("Unsupported file type.")

    except Exception as e:
        print(f"❌ Error reading file '{path}': {e}")
        return None
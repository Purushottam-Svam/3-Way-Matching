import pytesseract
pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

from pdf2image import convert_from_path
from PIL import Image
import os

POPPLER_PATH = (
    r"C:\Users\PurushottamKaushik\Documents\Tools\poppler-23.11.0\Library\bin"
)

def ocr_document(file_path):
    text = ""

    if file_path.lower().endswith(".pdf"):
        pages = convert_from_path(file_path, poppler_path=POPPLER_PATH)
        for page in pages:
            text += pytesseract.image_to_string(
                page,
                config= r'--oem 3 --psm 3'
            ) + "\n"
    else:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(
            img,
            config= r'--oem 3 --psm 3'
        )

    return text.strip()

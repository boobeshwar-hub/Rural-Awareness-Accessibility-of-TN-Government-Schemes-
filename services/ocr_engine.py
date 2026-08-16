import os
import re
import datetime
import pytesseract
from PIL import Image, ImageEnhance

# 1. Automatically locate tesseract.exe on Windows
potential_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
    os.path.join(os.environ.get('LOCALAPPDATA', ''), r'Programs\Tesseract-OCR\tesseract.exe'),
    os.path.join(os.environ.get('LOCALAPPDATA', ''), r'Tesseract-OCR\tesseract.exe'),
    r'C:\Tesseract-OCR\tesseract.exe'
]

tesseract_found = False
for path in potential_paths:
    if os.path.isfile(path):
        pytesseract.pytesseract.tesseract_cmd = path
        tesseract_found = True
        print(f"[OCR Engine] Connected to Tesseract at: {path}")
        break

if not tesseract_found:
    print("[OCR Warning] tesseract.exe not found. Please install Tesseract to C:\\Program Files\\Tesseract-OCR")

class DocumentOCREngine:
    @staticmethod
    def preprocess_image(image_path: str) -> Image.Image:
        image = Image.open(image_path)
        gray_image = image.convert('L')
        enhancer = ImageEnhance.Contrast(gray_image)
        return enhancer.enhance(2.0)

    @classmethod
    def parse_document(cls, image_path: str) -> dict:
        extracted_data = {}

        if not os.path.exists(image_path):
            print(f"[OCR Error] Image not found at {image_path}")
            return extracted_data

        try:
            processed_img = cls.preprocess_image(image_path)
            raw_text = pytesseract.image_to_string(processed_img, lang='eng')
            print("\n--- OCR Extracted Raw Text ---")
            print(raw_text)
            print("------------------------------\n")
        except Exception as e:
            print(f"[OCR Execution Error]: {e}")
            raw_text = ""

        if not raw_text:
            return extracted_data

        # 1. Extract Gender (Ration Card / Aadhaar / Income Cert)
        if re.search(r'\b(FEMALE|WOMAN|GIRL|பெண்|செல்வி|திருமதி)\b', raw_text, re.IGNORECASE):
            extracted_data["gender"] = "female"
            extracted_data["is_head_of_family"] = True
        elif re.search(r'\b(MALE|MAN|BOY|ஆண்|திரு)\b', raw_text, re.IGNORECASE):
            extracted_data["gender"] = "male"

        # 2. Extract Annual Household Income
        income_match = re.search(r'(?:Annual\s*Household\s*Income|Annual\s*Income|Income|Rs\.?|₹|வருமானம்)\s*:?\s*(\d+[\d,]*)', raw_text, re.IGNORECASE)
        if income_match:
            clean_income = income_match.group(1).replace(',', '')
            try:
                extracted_data["annual_income"] = int(clean_income)
            except ValueError:
                pass

        # 3. Extract Ration Card Type (PHH / NPHH / AAY)
        card_match = re.search(r'\b(NPHH|PHH|AAY)\b', raw_text, re.IGNORECASE)
        if card_match:
            extracted_data["ration_card_type"] = card_match.group(1).upper()

        # 4. Extract School Education Status (From School TC)
        if re.search(r'Government\s*School|Govt\s*School|Class\s*6\s*to\s*Class\s*12', raw_text, re.IGNORECASE):
            extracted_data["is_govt_school_studied"] = True
            extracted_data["pursuing_higher_education"] = True

        # 5. Extract Age from DOB
        current_year = datetime.datetime.now().year
        dob_match = re.search(r'(?:DOB|Date of Birth)\s*:?\s*\d{2}/\d{2}/(\d{4})', raw_text, re.IGNORECASE)
        if dob_match:
            birth_year = int(dob_match.group(1))
            extracted_data["age"] = current_year - birth_year

        return extracted_data
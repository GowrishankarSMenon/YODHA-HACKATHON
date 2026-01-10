import os
import torch
import pytesseract
import numpy as np
import cv2
from PIL import Image
from typing import Dict, Any, List, Optional, Tuple

# ------------------ CONFIG ------------------
# Set Tesseract path if not in system PATH (Default Windows installation path)
TESSERACT_PATH = os.getenv("TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe")

print(f"🔍 Checking Tesseract at: {TESSERACT_PATH}")
if os.path.exists(TESSERACT_PATH):
    print("✅ Tesseract found! Setting path.")
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
else:
    print("⚠️ Tesseract NOT found at default path. Ensure it's installed or set TESSERACT_PATH environment variable.")

FIELD_LABELS = {
    "patient_name": ["First name", "Name"],
    "surname": ["Surname"],
    "date_of_birth": ["D.O.B", "DOB", "Date of Birth"],
    "gender": ["Sex", "Gender"],
    "address": ["Address"],
    "suburb": ["Suburb"],
    "state": ["State"],
    "phone": ["Phone"],
    "mobile": ["Mobile"],
    "email": ["Email"],
    "occupation": ["Occupation"],
    "appointment_datetime": ["Appointment Date", "Date / Time"],
    "procedure": ["Procedure"],
    "hospital_name": ["Hospital", "Facility"],
    "hospital_address": ["Address"],
    "health_fund": ["Health Fund"],
    "insurance_id": ["Membership No", "Policy No"],
    "gp_name": ["GP", "General Practitioner"],
    "referrer": ["Referrer"],
    "comments": ["Comments"],
    "diagnosis": ["Diagnosis"]
}

class LayoutLMv3Engine:
    """Spacial-aware OCR engine for medical registration forms."""
    
    @staticmethod
    def ocr_with_boxes(image: Image.Image) -> Tuple[List[str], List[List[int]]]:
        """Perform OCR and extract word bounding boxes."""
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)

        words, boxes = [], []
        h, w = img.shape[:2]

        for i in range(len(data["text"])):
            txt = data["text"][i].strip()
            if not txt:
                continue

            # Bounding box coordinates: [x_min, y_min, x_max, y_max] normalized to 1000x1000
            x, y, bw, bh = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
            bbox = [
                int(1000 * x / w),
                int(1000 * y / h),
                int(1000 * (x + bw) / w),
                int(1000 * (y + bh) / h),
            ]

            words.append(txt)
            boxes.append(bbox)

        return words, boxes

    @staticmethod
    def _same_row(a: List[int], b: List[int], tol: int = 25) -> bool:
        """Check if two boxes are on the same vertical row."""
        return abs(a[1] - b[1]) < tol

    @staticmethod
    def _is_right_of(a: List[int], b: List[int]) -> bool:
        """Check if box A is to the right of box B."""
        return a[0] > b[2]

    @staticmethod
    def extract_by_layout(words: List[str], boxes: List[List[int]]) -> Dict[str, Any]:
        """Extract fields deterministically using spatial anchoring."""
        results = {k: None for k in FIELD_LABELS}

        for field, labels in FIELD_LABELS.items():
            for i, word in enumerate(words):
                for label in labels:
                    if label.lower() in word.lower():
                        label_box = boxes[i]
                        candidates = []

                        # Look for words on the same row, to the right of the label
                        for j in range(len(words)):
                            if LayoutLMv3Engine._same_row(boxes[j], label_box) and \
                               LayoutLMv3Engine._is_right_of(boxes[j], label_box):
                                candidates.append((boxes[j][0], words[j]))

                        # Sort candidates by x-coordinate and join them
                        candidates = sorted(candidates, key=lambda x: x[0])
                        if candidates:
                            # Heuristic: Take up to 6 words to the right
                            results[field] = " ".join([c[1] for c in candidates[:8]]).strip()
                        break
                if results[field]: break

        return results

    @staticmethod
    def process_image(image: Image.Image) -> Dict[str, Any]:
        """Full pipeline for spatial extraction."""
        # words, boxes normalization happens inside ocr_with_boxes
        words, boxes = LayoutLMv3Engine.ocr_with_boxes(image)
        
        # Determine structured fields via layout anchoring
        structured_data = LayoutLMv3Engine.extract_by_layout(words, boxes)
        
        # Include full OCR text for redundancy/LLM context
        structured_data["_raw_ocr"] = " ".join(words)
        
        return structured_data

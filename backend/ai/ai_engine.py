import torch
import numpy as np
import cv2
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# ================================================================
# LOAD TrOCR MODEL
# ================================================================
MODEL_NAME = "microsoft/trocr-small-handwritten"

processor = TrOCRProcessor.from_pretrained(MODEL_NAME)
model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME)

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)
model.eval()

# ================================================================
# OCR UTILITIES
# ================================================================
def segment_lines(pil_image: Image.Image):
    gray = np.array(pil_image.convert("L"))
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    sobel = cv2.Sobel(blurred, cv2.CV_8U, 0, 1, ksize=3)
    _, binary = cv2.threshold(
        sobel, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (150, 5))
    dilated = cv2.dilate(binary, kernel, iterations=2)

    contours, _ = cv2.findContours(
        dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1])

    lines = []
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        cropped = pil_image.crop(
            (0, max(0, y - 5), pil_image.width, y + h + 5)
        )
        lines.append(cropped)

    return lines


def preprocess_for_trocr(img: Image.Image):
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    denoise = cv2.fastNlMeansDenoising(gray, h=25)

    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoise)

    return Image.fromarray(enhanced).convert("RGB")


def ocr_line(img: Image.Image) -> str:
    inputs = processor(
        images=img, return_tensors="pt"
    ).pixel_values.to(device)

    ids = model.generate(inputs, max_new_tokens=80)
    text = processor.batch_decode(
        ids, skip_special_tokens=True
    )[0].strip()

    return text


def ocr_page(pil_image: Image.Image):
    results = []
    line_images = segment_lines(pil_image)

    for line_img in line_images:
        processed = preprocess_for_trocr(line_img)
        text = ocr_line(processed)
        if text:
            results.append(text)

    return results

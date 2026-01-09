import torch
import numpy as np
import cv2
from PIL import Image
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from typing import List, Tuple

# ================================================================
# LOAD TrOCR MODEL (LAZY LOADING)
# ================================================================
MODEL_NAME = "microsoft/trocr-small-handwritten"

# Lazy loading - only load when first needed
processor = None
model = None
device = None

def _load_model():
    """Load TrOCR model lazily (only when first needed)."""
    global processor, model, device
    
    if model is not None:
        return  # Already loaded
    
    print("📥 Loading TrOCR model (this may take a moment)...")
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    
    processor = TrOCRProcessor.from_pretrained(MODEL_NAME)
    model = VisionEncoderDecoderModel.from_pretrained(MODEL_NAME)
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model.to(device)
    model.eval()
    print("✅ TrOCR model loaded successfully!")

# ================================================================
# IMPROVED OCR UTILITIES
# ================================================================

def adaptive_binarization(gray_image: np.ndarray) -> np.ndarray:
    """Better binarization using adaptive thresholding"""
    # Apply adaptive thresholding for better handling of varying lighting
    binary = cv2.adaptiveThreshold(
        gray_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 21, 10
    )
    return binary


def remove_noise(binary_image: np.ndarray) -> np.ndarray:
    """Remove small noise components"""
    # Morphological opening to remove noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    cleaned = cv2.morphologyEx(binary_image, cv2.MORPH_OPEN, kernel)
    return cleaned


def detect_skew(gray_image: np.ndarray) -> float:
    """Detect skew angle of the document"""
    # Binarize
    _, binary = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Find coordinates of all white pixels
    coords = np.column_stack(np.where(binary > 0))
    
    # Fit a minimum area rectangle
    if len(coords) > 0:
        rect = cv2.minAreaRect(coords)
        angle = rect[-1]
        
        # Normalize angle
        if angle < -45:
            angle = 90 + angle
        elif angle > 45:
            angle = angle - 90
            
        return angle
    return 0


def deskew_image(image: Image.Image) -> Image.Image:
    """Correct skew/rotation in the image"""
    gray = np.array(image.convert("L"))
    angle = detect_skew(gray)
    
    # Only deskew if angle is significant
    if abs(angle) > 0.5:
        (h, w) = gray.shape
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            np.array(image), M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        return Image.fromarray(rotated)
    
    return image


def segment_lines_improved(pil_image: Image.Image) -> List[Tuple[Image.Image, int]]:
    """Improved line segmentation with better filtering"""
    gray = np.array(pil_image.convert("L"))
    
    # Adaptive binarization
    binary = adaptive_binarization(gray)
    
    # Remove noise
    cleaned = remove_noise(binary)
    
    # Horizontal projection profile
    horizontal_projection = np.sum(cleaned, axis=1)
    
    # Find line boundaries using projection profile
    threshold = np.max(horizontal_projection) * 0.1
    in_line = False
    line_boundaries = []
    start = 0
    
    for i, val in enumerate(horizontal_projection):
        if val > threshold and not in_line:
            start = i
            in_line = True
        elif val <= threshold and in_line:
            if i - start > 10:  # Minimum line height
                line_boundaries.append((start, i))
            in_line = False
    
    # If still in a line at the end
    if in_line and len(horizontal_projection) - start > 10:
        line_boundaries.append((start, len(horizontal_projection)))
    
    # Extract line images with padding
    lines = []
    for start, end in line_boundaries:
        padding = 10
        y1 = max(0, start - padding)
        y2 = min(pil_image.height, end + padding)
        
        cropped = pil_image.crop((0, y1, pil_image.width, y2))
        
        # Filter out very small or very large lines
        if cropped.height > 15 and cropped.height < pil_image.height * 0.5:
            lines.append((cropped, start))  # Keep y-position for ordering
    
    return lines


def preprocess_for_trocr_improved(img: Image.Image) -> Image.Image:
    """Enhanced preprocessing for better OCR accuracy"""
    # Convert to grayscale
    gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
    
    # Resize if too small (TrOCR works better with certain sizes)
    h, w = gray.shape
    if h < 32:
        scale = 32 / h
        new_h, new_w = int(h * scale), int(w * scale)
        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    
    # Denoise with optimized parameters
    denoised = cv2.fastNlMeansDenoising(gray, None, h=20, templateWindowSize=7, searchWindowSize=21)
    
    # CLAHE for contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    # Sharpen the image
    kernel_sharpen = np.array([[-1,-1,-1],
                               [-1, 9,-1],
                               [-1,-1,-1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel_sharpen)
    
    # Normalize brightness and contrast
    normalized = cv2.normalize(sharpened, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)
    
    return Image.fromarray(normalized).convert("RGB")


def ocr_line_with_confidence(img: Image.Image) -> Tuple[str, float]:
    """OCR with confidence score estimation"""
    _load_model()  # Ensure model is loaded
    
    inputs = processor(images=img, return_tensors="pt").pixel_values.to(device)
    
    # Generate with beam search for better results
    with torch.no_grad():
        outputs = model.generate(
            inputs,
            max_new_tokens=80,
            num_beams=5,  # Beam search for better quality
            early_stopping=True,
            output_scores=True,
            return_dict_in_generate=True
        )
    
    ids = outputs.sequences
    text = processor.batch_decode(ids, skip_special_tokens=True)[0].strip()
    
    # Estimate confidence from sequence scores if available
    confidence = 1.0
    if hasattr(outputs, 'sequences_scores'):
        confidence = float(torch.exp(outputs.sequences_scores[0]))
    
    return text, confidence


def merge_broken_lines(lines: List[str]) -> List[str]:
    """Merge lines that were incorrectly split"""
    if not lines:
        return lines
    
    merged = []
    current = lines[0]
    
    for i in range(1, len(lines)):
        # If current line doesn't end with punctuation and next line doesn't start with capital
        if (current and not current[-1] in '.!?:;,' and 
            lines[i] and len(lines[i]) > 0 and 
            lines[i][0].islower()):
            current += " " + lines[i]
        else:
            merged.append(current)
            current = lines[i]
    
    merged.append(current)
    return merged


def ocr_page_improved(pil_image: Image.Image, min_confidence: float = 0.3) -> dict:
    """
    Improved OCR with preprocessing and confidence filtering
    
    Args:
        pil_image: Input PIL Image
        min_confidence: Minimum confidence threshold (0-1)
    
    Returns:
        Dictionary with 'lines', 'full_text', and 'metadata'
    """
    # Step 1: Deskew the image
    deskewed = deskew_image(pil_image)
    
    # Step 2: Segment lines with improved algorithm
    line_data = segment_lines_improved(deskewed)
    
    # Step 3: Process each line
    results = []
    low_confidence_lines = []
    
    for line_img, y_pos in line_data:
        # Preprocess
        processed = preprocess_for_trocr_improved(line_img)
        
        # OCR with confidence
        text, confidence = ocr_line_with_confidence(processed)
        
        if text:
            results.append({
                'text': text,
                'confidence': confidence,
                'y_position': y_pos
            })
            
            if confidence < min_confidence:
                low_confidence_lines.append(text)
    
    # Sort by y-position to maintain reading order
    results.sort(key=lambda x: x['y_position'])
    
    # Extract just the text
    text_lines = [r['text'] for r in results]
    
    # Optional: merge broken lines
    merged_lines = merge_broken_lines(text_lines)
    
    return {
        'lines': merged_lines,
        'full_text': '\n'.join(merged_lines),
        'raw_lines': text_lines,
        'metadata': {
            'total_lines': len(results),
            'avg_confidence': np.mean([r['confidence'] for r in results]) if results else 0,
            'low_confidence_count': len(low_confidence_lines)
        }
    }


# ================================================================
# CONVENIENCE FUNCTION (backwards compatible)
# ================================================================
def ocr_page(pil_image: Image.Image) -> List[str]:
    """Backwards compatible function that returns just the lines"""
    result = ocr_page_improved(pil_image)
    return result['lines']
# src/ocr/_gemini_bridge.py   ← should be in .gitignore
import os
from google import genai
from PIL import Image


def gemini_vision_ocr(image: Image.Image) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable not set!")

    print("→ Making real Gemini API call")

    model = genai.GenerativeModel("gemini-1.5-flash")  # change to 2.0-flash if available

    prompt = """
This is a handwritten Malayalam medical/OPD note.

1. Carefully read and understand the handwritten Malayalam text in the image.
2. First, rewrite the content in clear, correct and natural Malayalam text.
3. Then provide a simple English summary of what the note says.
4. Extract the following fields if present:
   - Symptoms
   - Diagnosis
   - Medicines prescribed
   - Doctor's instructions / advice

Be accurate with Malayalam spelling and conjunct characters.
If any part is unclear, write "unclear" in that section.
"""

    try:
        response = model.generate_content([prompt, image])
        return response.text
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}")
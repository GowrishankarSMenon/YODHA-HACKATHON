import os
from PIL import Image
from google import genai

def main(image_path: str):
    if not os.path.exists(image_path):
        print("❌ Image not found:", image_path)
        return

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY not set in environment")
        return

    print("🧠 Initializing Gemini client...")
    client = genai.Client(api_key=api_key)

    print("📤 Loading image...")
    img = Image.open(image_path)

    prompt = """
This is a handwritten Malayalam medical/OPD note.

1. Carefully read and understand the handwritten Malayalam text in the image.
2. First, rewrite the content in clear Malayalam text (as best as you can).
3. Then summarize in simple English what happened.
4. Extract and list:
   - Symptoms
   - Diagnosis
   - Medicines
   - Doctor instructions

If something is unclear or unreadable, explicitly say "unclear".
"""

    print("🚀 Sending to Gemini Vision...")

    response = client.models.generate_content(
        model="models/gemini-2.5-flash",   # ✅ use this
        contents=[prompt, img],
    )

    print("\n================ GEMINI OUTPUT ================\n")
    print(response.text)
    print("\n=============================================\n")

if __name__ == "__main__":
    main("ml1.png")   # change path if needed

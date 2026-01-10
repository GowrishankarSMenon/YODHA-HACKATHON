# Malayalam Handwritten Character Recognizer

This document provides details and usage instructions for the **Malayalam Handwritten Character Recognizer** model, a pre-trained Keras model designed to identify handwritten Malayalam characters and digits.

## 📦 Model Details

- **Hugging Face Repository**: [shankarz/malayalam-character-recognizer](https://huggingface.co/shankarz/malayalam-character-recognizer)
- **Framework**: Keras / TensorFlow
- **Format**: `.h5` and `.keras`
- **Total Size**: ~16.6 MB

### Files and Versions
- `model.keras` (8.31 MB): The latest Keras format for the model weights and architecture.
- `model.h5` (8.31 MB): Legacy HDF5 format for compatibility with older Keras versions.
- `classes.csv`: Mapping of model output indices to actual Malayalam characters.
- `README.md`: Basic description of the model.

---

## 🚀 How to Use

### 1. Prerequisites
Ensure you have TensorFlow and Keras installed:
```bash
pip install tensorflow pandas pillow
```

### 2. Implementation Script
Here is a basic example of how to load the model and make predictions:

```python
import tensorflow as tf
import pandas as pd
import numpy as np
from PIL import Image

# 1. Load the model
model = tf.keras.models.load_model('model.keras')

# 2. Load classes (mapping)
classes_df = pd.read_csv('classes.csv')
class_names = classes_df['class_name'].tolist()

# 3. Preprocess Image
def preprocess_image(image_path):
    # Requirements: Grayscale, specific size (usually 32x32 or 64x64 for character OCR)
    # Note: Check the original model training specs for exact input dimensions
    img = Image.open(image_path).convert('L')
    img = img.resize((32, 32)) # Replace with model's expected input size
    img_array = np.array(img) / 255.0
    img_array = img_array.reshape(1, 32, 32, 1) # Assumes (batch, h, w, channels)
    return img_array

# 4. Predict
image_data = preprocess_image('path_to_handwritten_character.png')
predictions = model.predict(image_data)
predicted_class_idx = np.argmax(predictions)
print(f"Predicted Character: {class_names[predicted_class_idx]}")
```

---

## 🎯 Use Case in MedScan AI

In the context of the **MedScan AI** project, this model can be used to improve the extraction of handwritten Malayalam data in clinical documents, such as:
- **Patient Names** written in Malayalam.
- **Vitals** or numbers written in Malayalam script.
- **Clinical Comments** (as seen in the [attached example](test-images/mal.jpeg)).

### Integration Strategy
1. **Segmentation**: Use OpenCV to segment individual handwritten characters from the "Comments" or "Name" sections of the medical form.
2. **Recognition**: Pass each segment to this character recognizer model.
3. **LLM Refinement**: Use a Large Language Model (like Groq Qwen) to reconstruct the predicted characters into meaningful medical terms or names, correcting any individual character errors.

---

## 🤝 Contribution & License
This model is provided by **shankarz** on Hugging Face. For contributions or specific license details, please refer to the original repository.

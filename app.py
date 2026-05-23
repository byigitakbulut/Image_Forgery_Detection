"""
Main application module for the Image Forgery Detection API.
Provides endpoints for health checking and image manipulation detection.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os

# Import the helper function for in-memory ELA generation
from src.utils import generate_ela_in_memory
from src.opencv_detector import detect_copy_move_in_memory

# Suppress TensorFlow logging outputs for cleaner terminal
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

app = FastAPI(title="Image Forgery Detection API")

# Configure CORS permissions for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the model path based on the directory structure
MODEL_PATH = 'models/two_stream_forgery_model.keras'

# Attempt to load the pre-trained Keras model
try:
    model = tf.keras.models.load_model(MODEL_PATH)
except Exception as e:
    print(f"Critical Error: Model could not be loaded. Path: {MODEL_PATH}, Error: {e}")


@app.post("/predict")
async def predict_forgery(file: UploadFile = File(...)):
    """
    Processes an uploaded image to predict whether it has been tampered with.

    Parameters
    ----------
    file : UploadFile
        The image file uploaded by the user. Supported formats are JPEG and PNG.

    Returns
    -------
    dict
        A JSON object containing the status, filename, prediction result
        ("Tampered" or "Authentic"), and confidence scores.

    Raises
    ------
    HTTPException
        If the file format is unsupported (400) or a processing error occurs (500).
    """

    # Validate file extension
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only JPEG and PNG formats are allowed."
        )

    try:
        # Read file contents and convert to RGB format
        contents = await file.read()
        img_rgb = Image.open(io.BytesIO(contents)).convert('RGB')

        # Generate the ELA (Error Level Analysis) image
        img_ela = generate_ela_in_memory(img_rgb)

        # Resize images to match the expected input dimensions of the model
        img_rgb = img_rgb.resize((128, 128))
        img_ela = img_ela.resize((128, 128))

        # Normalize pixel values and expand dimensions for batch prediction
        arr_rgb = np.expand_dims(np.array(img_rgb) / 255.0, axis=0)
        arr_ela = np.expand_dims(np.array(img_ela) / 255.0, axis=0)

        # Perform inference using the dual-stream model
        prediction = model.predict({'rgb_input': arr_rgb, 'ela_input': arr_ela}, verbose=0)
        score = float(prediction[0][0])

        # Determine the final prediction based on a 0.5 threshold
        is_tampered = score > 0.5
        confidence = score if is_tampered else (1 - score)

        return {
            "status": "success",
            "filename": file.filename,
            "prediction": "Tampered" if is_tampered else "Authentic",
            "confidence_score": round(confidence * 100, 2),
            "raw_score": round(score, 4)
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during image processing: {str(e)}"
        )


@app.post("/predict/copy-move")
async def predict_copy_move(file: UploadFile = File(...), algorithm: str = "SIFT"):
    """
    OpenCV searches for copy-move (copy-paste) forgery on the incoming image.
    """
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Only JPEG and PNG formats are allowed."
        )

    try:
        contents = await file.read()

        # Sends image bytes directly to the function in memory
        result = detect_copy_move_in_memory(image_bytes=contents, algorithm=algorithm)

        # Return results as JSON
        return {
            "status": "success",
            "filename": file.filename,
            "data": result
        }

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during OpenCV processing: {str(e)}"
        )


@app.get("/")
def health_check():
    """
    Health check endpoint to verify the API status.

    Returns
    -------
    dict
        A JSON object indicating the API's operational status and model availability.
    """
    return {"status": "API is active", "model_loaded": True}
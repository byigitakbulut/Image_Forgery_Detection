from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os

# Yardımcı fonksiyonu modül olarak içeri aktar
from src.utils import generate_ela_in_memory

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

app = FastAPI(title="Image Forgery Detection API")

# Frontend için CORS izinleri
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Klasör yapısına göre model yolu
MODEL_PATH = 'models/two_stream_forgery_model.keras'

try:
    model = tf.keras.models.load_model(MODEL_PATH)
except Exception as e:
    print(f"Kritik Hata: Model yüklenemedi. Yol: {MODEL_PATH}, Hata: {e}")

@app.post("/predict")
async def predict_forgery(file: UploadFile = File(...)):
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Sadece JPEG veya PNG formatları desteklenmektedir.")
    
    try:
        contents = await file.read()
        img_rgb = Image.open(io.BytesIO(contents)).convert('RGB')
        
        img_ela = generate_ela_in_memory(img_rgb)
        
        img_rgb = img_rgb.resize((128, 128))
        img_ela = img_ela.resize((128, 128))
        
        arr_rgb = np.expand_dims(np.array(img_rgb) / 255.0, axis=0)
        arr_ela = np.expand_dims(np.array(img_ela) / 255.0, axis=0)
        
        prediction = model.predict({'rgb_input': arr_rgb, 'ela_input': arr_ela}, verbose=0)
        score = float(prediction[0][0])
        
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
        raise HTTPException(status_code=500, detail=f"İşlem sırasında sunucu hatası: {str(e)}")

@app.get("/")
def health_check():
    return {"status": "API aktif", "model_loaded": True}
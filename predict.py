import sys
import json
import tensorflow as tf
import numpy as np
from PIL import Image
import os
from datetime import datetime

# Load model
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model/saved_model')

try:
    model = tf.saved_model.load(MODEL_PATH)
    print("Model berhasil dimuat", file=sys.stderr)
    
    # Cek signature model
    print("\nModel signatures:", file=sys.stderr)
    print(model.signatures, file=sys.stderr)
    
    # Cek input shape
    print("\nInput shape:", file=sys.stderr)
    print(model.signatures['serving_default'].inputs[0].shape, file=sys.stderr)
    
    # Cek output shape
    print("\nOutput shape:", file=sys.stderr)
    print(model.signatures['serving_default'].outputs[0].shape, file=sys.stderr)
    
except Exception as e:
    print(json.dumps({"error": f"Gagal memuat model: {str(e)}"}))
    sys.exit(1)

# Daftar kelas penyakit yang sesuai dengan model
CLASS_NAMES = [
    "Bacterial Spot",
    "Cercospora Leaf Spot",
    "Curl Virus",
    "Healthy Leaf",
    "Nutrition Deficiency",
    "White spot"
]

def preprocess_image(image_path):
    try:
        # Baca gambar
        img = Image.open(image_path)
        
        # Konversi ke RGB jika gambar dalam format lain
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize gambar
        img = img.resize((224, 224))
        
        # Konversi ke array dan normalisasi
        img_array = np.array(img)
        img_array = img_array.astype(np.float32) / 255.0
        
        # Tambahkan batch dimension
        img_array = np.expand_dims(img_array, axis=0)
        
        return img_array
    except Exception as e:
        raise Exception(f"Error dalam preprocessing gambar: {str(e)}")

def predict(image_path):
    try:
        # Validasi file
        if not os.path.exists(image_path):
            raise Exception("File gambar tidak ditemukan")
            
        # Preprocess gambar
        processed_image = preprocess_image(image_path)
        
        # Lakukan prediksi menggunakan serving_default signature
        predictions = model.signatures['serving_default'](inputs=processed_image)
        
        # Debug: print raw predictions
        print("\nRaw predictions:", file=sys.stderr)
        print(predictions, file=sys.stderr)
        
        # Ambil output dari predictions
        predictions = predictions['output_0'].numpy()
        
        # Debug: print predictions shape
        print("\nPredictions shape:", file=sys.stderr)
        print(predictions.shape, file=sys.stderr)
        
        # Ambil prediksi dengan confidence tertinggi
        prediction = np.argmax(predictions[0])
        confidence = float(predictions[0][prediction])
        
        # Debug: print prediction index and confidence
        print(f"\nPrediction index: {prediction}", file=sys.stderr)
        print(f"Confidence: {confidence}", file=sys.stderr)
        
        # Terapkan threshold confidence
        if confidence < 0.5:
            predicted_class = "Tidak dikenali"
        else:
            predicted_class = CLASS_NAMES[prediction]
        
        # Buat hasil prediksi
        result = {
            "prediction": predicted_class,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        
        print(json.dumps(result))
        sys.exit(0)
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
        print(json.dumps(error_result))
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Image path argument required"}))
        sys.exit(1)
        
    image_path = sys.argv[1]
    predict(image_path) 
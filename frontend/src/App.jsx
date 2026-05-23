import { useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import "./App.css";

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [activeTab, setActiveTab] = useState("dl"); // 'dl' (Derin Öğrenme) veya 'cv' (OpenCV Copy-Move)
  const [dlResult, setDlResult] = useState(null);
  const [cvResult, setCvResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleImage = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setSelectedImage(file);
    setPreview(URL.createObjectURL(file));
    setDlResult(null);
    setCvResult(null);
  };

  const analyzeImage = async () => {
    if (!selectedImage) {
      alert("Lütfen önce bir resim seçin.");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append("file", selectedImage);

    try {
      if (activeTab === "dl") {
        // 1. Derin Öğrenme Analiz Endpoint'i
        const response = await fetch("http://localhost:8000/predict", {
          method: "POST",
          body: formData,
        });

        const data = await response.json();
        if (response.ok) {
          const confidence = Number(data.confidence_score.toFixed(2));
          let chartData = data.prediction === "Tampered" 
            ? [{ name: "Shoplu", value: confidence }, { name: "Orijinal", value: 100 - confidence }]
            : [{ name: "Orijinal", value: 100 - confidence }, { name: "Shoplu", value: confidence }];

          setDlResult({
            prediction: data.prediction,
            confidence,
            chartData,
          });
        } else {
          alert(`Hata: ${data.detail || "Analiz başarısız oldu."}`);
        }
      } else {
        // 2. Yeni Eklenen OpenCV Copy-Move Endpoint'i
        const response = await fetch("http://localhost:8000/predict/copy-move?algorithm=SIFT", {
          method: "POST",
          body: formData,
        });

        const resData = await response.json();
        if (response.ok) {
          setCvResult(resData.data);
        } else {
          alert(`Hata: ${resData.detail || "OpenCV analizi başarısız oldu."}`);
        }
      }
    } catch (error) {
      console.error(error);
      alert("Backend bağlantısında hata oluştu.");
    } finally {
      setLoading(false);
    }
  };

  const COLORS = ["#7c3aed", "#9ca3af"];

  return (
    <div className="container">
      <h1>Image Forgery Detection</h1>

      {/* Tercih Butonları (Yöntem Seçimi) */}
      <div className="tab-container">
        <button 
          className={`tab-btn ${activeTab === "dl" ? "active" : ""}`} 
          onClick={() => {
            setActiveTab("dl");
            setDlResult(null);
            setCvResult(null);
          }}
        >
          Derin Öğrenme Modeli
        </button>
        <button 
          className={`tab-btn ${activeTab === "cv" ? "active" : ""}`} 
          onClick={() => {
            setActiveTab("cv");
            setDlResult(null);
            setCvResult(null);
          }}
        >
          OpenCV (Copy-Move)
        </button>
      </div>

      <div className="upload-box">
        <input
          type="file"
          accept="image/png, image/jpeg, image/jpg"
          onChange={handleImage}
        />
        <p className="main-text">Lütfen test edilecek resmi buraya bırakın</p>
        <p className="sub-text">Desteklenen formatlar: JPG, PNG, JPEG</p>
      </div>

      {preview && !dlResult && !cvResult && (
        <img src={preview} alt="preview" className="preview-image" />
      )}

      <button className="analyze-btn" onClick={analyzeImage} disabled={loading}>
        {loading ? "Analiz Ediliyor..." : "Analiz Et"}
      </button>

      {/* DERİN ÖĞRENME SONUÇ KARTI */}
      {activeTab === "dl" && dlResult && (
        <div className="result-container">
          <h2>Analiz Sonucu (Derin Öğrenme)</h2>
          <div className="result-text">
            <span>Sonuç: <strong>{dlResult.prediction === "Authentic" ? "Orijinal" : "Shoplu"}</strong></span>
            <span>Güven: <strong>%{dlResult.confidence}</strong></span>
          </div>
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie data={dlResult.chartData} cx="50%" cy="50%" outerRadius={120} dataKey="value" label>
                {dlResult.chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* OPENCV COPY-MOVE SONUÇ KARTI */}
      {activeTab === "cv" && cvResult && (
        <div className="result-container">
          <h2>Analiz Sonucu (Copy-Move)</h2>
          <div className="result-text">
            <span>Yöntem: <strong>{cvResult.algorithm}</strong></span>
            <span>Eşleşme Sayısı: <strong>{cvResult.match_count}</strong></span>
          </div>
          <div className="result-status-text">
            Durum: <strong style={{ color: cvResult.is_tampered ? "#f87171" : "#4ade80" }}>
              {cvResult.is_tampered ? "Manipülasyon Tespit Edildi (Shoplu)" : "Güvenli (Orijinal)"}
            </strong>
          </div>
          
          {cvResult.result_image_base64 ? (
            <div className="cv-image-wrapper">
              <p className="image-label">Eşleşen Anahtar Noktalar Haritası:</p>
              <img 
                src={`data:image/jpeg;base64,${cvResult.result_image_base64}`} 
                alt="Copy-Move Analiz Sonucu" 
                className="preview-image result-cv-img" 
              />
            </div>
          ) : (
            <p className="info-message">{cvResult.message}</p>
          )}
        </div>
      )}
    </div>
  );
}

export default App;
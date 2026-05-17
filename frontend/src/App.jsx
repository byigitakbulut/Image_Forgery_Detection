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
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleImage = (e) => {
    const file = e.target.files[0];

    if (!file) return;

    setSelectedImage(file);
    setPreview(URL.createObjectURL(file));
    setResult(null);
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
      const response = await fetch("http://localhost:8000/predict", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      console.log(data);

      const confidence = Number(data.confidence_score.toFixed(2));

      let chartData;

      if (data.prediction === "Tampered") {
        chartData = [
          { name: "Shoplu", value: confidence },
          { name: "Orijinal", value: 100 - confidence },
        ];
      } else {
          chartData = [
            { name: "Orijinal", value: 100 - confidence },
            { name: "Shoplu", value: confidence },
      ];
      }

      setResult({
        prediction: data.prediction,
        confidence,
        chartData,
      });
    } catch (error) {
      console.error(error);
      alert("Backend bağlantısında hata oluştu.");
    }

    setLoading(false);
  };

  const COLORS = ["#7c3aed", "#9ca3af"];

  return (
    <div className="container">
      <h1>Image Forgery Detection</h1>

      <div className="upload-box">
        <input
          type="file"
          accept="image/png, image/jpeg, image/jpg"
          onChange={handleImage}
        />

        <p className="main-text">
          Lütfen test edilecek resmi buraya bırakın
        </p>

        <p className="sub-text">
          Desteklenen formatlar: JPG, PNG, JPEG
        </p>
      </div>

      {preview && (
        <img src={preview} alt="preview" className="preview-image" />
      )}

      <button className="analyze-btn" onClick={analyzeImage}>
        {loading ? "Analiz Ediliyor..." : "Analiz Et"}
      </button>

      {result && (
        <div className="result-container">
          <h2>Analiz Sonucu</h2>

          <div className="result-text">
            <span>
              Sonuç:
              <strong> {result.prediction === "Authentic" ? "Orijinal" : "Shoplu"}</strong>
            </span>

            <span>
              Güven:
              <strong> %{result.confidence}</strong>
            </span>
          </div>

          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={result.chartData}
                cx="50%"
                cy="50%"
                outerRadius={120}
                dataKey="value"
                label
              >
                {result.chartData.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>

              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

export default App;
# Image Forgery Detection

Bu proje, dijital görseller üzerindeki manipülasyonları (splicing, copy-move, retouching vb.) tespit etmek amacıyla geliştirilmiş bir görüntü işleme ve makine öğrenmesi ardışık düzenidir (pipeline). Görsellerdeki piksel seviyesi anomalileri ve gözle görülmeyen tutarsızlıkları analiz ederek, fotoğrafın orijinal olup olmadığını değerlendirir.

## Temel Özellikler

* **Piksel Seviyesi Analiz:** Copy-move (kopyala-yapıştır) ve splicing (farklı görselleri birleştirme) sahteciliklerinin tespiti.
* **Işık ve Renk Tutarsızlığı Tespiti:** Manipüle edilmiş bölgelerdeki ten rengi uyuşmazlıkları, gölge hataları ve ışık kaynağı tutarsızlıklarının analizi.
* **Hata Seviyesi Analizi (Error Level Analysis - ELA):** JPEG sıkıştırma oranlarındaki farklılıkları kullanarak sonradan eklenen veya değiştirilen piksellerin vurgulanması.
* **Makine Öğrenmesi Entegrasyonu:** Çıkarılan özniteliklerin (özelliklerin) sınıflandırma modelleri ile değerlendirilmesi.

## Kullanılan Teknolojiler

* **Dil:** Python 3.9+
* **Görüntü İşleme:** OpenCV, scikit-image, PIL
* **Makine Öğrenmesi / Derin Öğrenme:** TensorFlow, scikit-learn
* **Veri Manipülasyonu:** NumPy, pandas

## Kurulum

Projeyi yerel ortamında çalıştırmak için aşağıdaki adımları izleyebilirsin.

1.  **Depoyu Klonlayın:**
    ```bash
    git clone https://github.com/byigitakbulut/Image_Forgery_Detection
    cd image-forgery-detection
    ```

2.  **Proje Dizinine Girin:**
    ```bash
    cd image-forgery-detection
    ```

3.  **Docker Konteynerini Başlatın:**
    ```bash
    docker-compose up --build
    ```

## Kullanım

Tek bir görsel üzerinde sahtecilik tespiti yapmak için CLI (Komut Satırı Arayüzü) üzerinden aşağıdaki komutu çalıştırabilirsiniz:

```bash
python main.py --image "test_images/sample_image.jpg"
```

## Parametreler

* --image veya -i: Analiz edilecek görselin dosya yolu.
* --method veya -m: Kullanılacak analiz yöntemi (örn. ela, color_analysis, cnn). Varsayılan: all.
* --output veya -o: Analiz sonuçlarının kaydedileceği dizin.

## Klasör Yapısı

```text
├── data/                   # Eğitim ve test veri setleri
├── models/                 # Eğitilmiş makine öğrenmesi/derin öğrenme modelleri (.pth, .pkl vb.)
├── src/
│   ├── preprocessing/      # Görsel önişleme, ELA filtreleme
│   ├── feature_extraction/ # Işık/renk analizi ve öznitelik çıkarımı modülleri
│   └── classification/     # Model tahminleme ve sınıflandırma betikleri
├── test_images/            # Test amaçlı örnek görseller
├── main.py                 # Ana çalıştırma dosyası
├── requirements.txt        # Bağımlılıklar
└── README.md
```

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Daha fazla bilgi için lisans dosyasına göz atabilirsiniz.


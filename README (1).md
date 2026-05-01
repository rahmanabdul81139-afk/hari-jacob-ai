# 🌾 AgriSense AI — Smart Irrigation & Crop Recommendation System

## 📁 Project Structure
```
agrisense_project/
├── app.py                       ← Main Streamlit application
├── arduino_bridge.py            ← Arduino serial communication
├── crop_training.ipynb          ← Google Colab training notebook
├── requirements.txt             ← Python dependencies
├── README.md                    ← This file
├── agrisense_rf_model.pkl       ← (Generate from Colab)
└── agrisense_label_encoder.pkl  ← (Generate from Colab)
```

---

## ⚡ Quick Start (No Model Needed)

The app runs in **rule-based fallback mode** even without .pkl files.

```bash
cd agrisense_project
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## 🤖 Train the ML Model (Recommended)

1. Go to [colab.research.google.com](https://colab.research.google.com)
2. Click **File → Upload notebook** → upload `crop_training.ipynb`
3. Click **Runtime → Run all**
4. Download the two `.pkl` files when prompted
5. Place both files in your `agrisense_project/` folder
6. Restart the Streamlit app — it will auto-detect the model ✅

---

## 🎙️ Voice Input Setup

Voice input supports **English** and **Tamil**.

### Install PyAudio (required for microphone):

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
pip install SpeechRecognition
```

**Mac:**
```bash
brew install portaudio
pip install pyaudio SpeechRecognition
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install SpeechRecognition
```

### How to use voice:
1. Open sidebar → select Language (English / Tamil)
2. Click **🎙️ Speak Now**
3. Say: *"Temperature 32, soil moisture 45, rainfall 800"*
4. The app extracts numbers from your speech

> **Note:** If microphone is unavailable, the app continues normally with sliders.

---

## 🔌 Arduino Integration

Run the bridge in a separate terminal:
```bash
python arduino_bridge.py
```

Supports COM3, COM4 (Windows) and /dev/ttyUSB0, /dev/ttyACM0 (Linux/Mac).
Runs in simulation mode if no Arduino is connected.

---

## 📊 App Pages

| Page | Features |
|------|----------|
| 📊 Dashboard | Sensor metrics, crop recommendation with image, irrigation status |
| 🌱 Crop AI | Detailed crop analysis, probability chart, growing conditions |
| 🧪 Soil Health | Moisture gauge, pH meter, NPK bars, soil type profile |
| 💧 Irrigation | Water decision card, pump controls, weekly schedule, SMS alerts |
| 💰 Profit Calculator | Per-acre profit by region, comparison chart, best crop highlight |

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | `pip install -r requirements.txt` |
| Sliders not updating | Refresh browser page |
| Voice not working | Check PyAudio installation above |
| Images not loading | Check internet connection (loads from Wikimedia) |
| Model not found | App runs in fallback mode — works fine without .pkl files |

---

## 🎥 Demo Instructions (Saturday)

1. Launch: `streamlit run app.py`
2. Show all 5 pages by clicking sidebar navigation
3. Move sliders — crop recommendation updates in real time
4. Demonstrate voice input (English or Tamil)
5. Show profit calculator with different regions and farm sizes
6. Highlight that app works without internet for core features

---

*Built with ❤️ using Streamlit, scikit-learn, and Plotly*

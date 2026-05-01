import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import os
import json
import re
import requests
from io import BytesIO

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AgriSense AI",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── STYLING ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 { font-family: 'Playfair Display', serif; }

.main { background: #0d1f0f; }
.block-container { padding: 1.5rem 2rem; }

/* Cards */
.metric-card {
    background: linear-gradient(135deg, #1a3a1e 0%, #0f2312 100%);
    border: 1px solid #2d6a35;
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.metric-card .label { font-size: 0.75rem; color: #7fc97f; letter-spacing: 1px; text-transform: uppercase; }
.metric-card .value { font-size: 1.8rem; font-weight: 700; color: #e8f5e9; margin: 0.2rem 0; }
.metric-card .unit  { font-size: 0.8rem; color: #81c784; }

/* Status badges */
.badge-water-now { background: #ff5252; color: white; border-radius: 20px; padding: 4px 14px; font-size: 0.82rem; font-weight: 600; }
.badge-wait      { background: #4caf50; color: white; border-radius: 20px; padding: 4px 14px; font-size: 0.82rem; font-weight: 600; }
.badge-water-soon{ background: #ff9800; color: white; border-radius: 20px; padding: 4px 14px; font-size: 0.82rem; font-weight: 600; }

/* Crop card */
.crop-card {
    background: linear-gradient(135deg, #1b3d20 0%, #0a1f0d 100%);
    border: 1px solid #388e3c;
    border-radius: 20px;
    padding: 1.5rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.crop-card h2 { color: #a5d6a7; margin: 0.5rem 0; font-size: 1.6rem; }
.crop-card .confidence { color: #81c784; font-size: 0.9rem; }

/* Progress bars */
.prob-row { display: flex; align-items: center; margin: 6px 0; gap: 10px; }
.prob-label { width: 100px; color: #a5d6a7; font-size: 0.85rem; }
.prob-bar-bg { flex: 1; background: #1b3d20; border-radius: 8px; height: 10px; overflow: hidden; }
.prob-bar-fill { height: 100%; border-radius: 8px; background: linear-gradient(90deg, #43a047, #a5d6a7); }
.prob-pct { width: 45px; color: #c8e6c9; font-size: 0.82rem; text-align: right; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #0a1a0c !important;
    border-right: 1px solid #2d6a35;
}
section[data-testid="stSidebar"] .stSlider > div { color: #a5d6a7; }

/* Dividers */
hr { border-color: #2d6a35; }

/* Tables */
.stDataFrame { border-radius: 12px; overflow: hidden; }

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #2e7d32, #43a047) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(67,160,71,0.4) !important;
}

.big-title { font-family: 'Playfair Display', serif; color: #a5d6a7; font-size: 2.2rem; margin: 0; }
.sub-title  { color: #558b2f; font-size: 0.95rem; margin-top: 0.2rem; }
</style>
""", unsafe_allow_html=True)

# ─── CROP DATA ────────────────────────────────────────────────────────────────
CROP_IMAGES = {
    "rice":      "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/A_green_ear_of_rice_01.jpg/400px-A_green_ear_of_rice_01.jpg",
    "wheat":     "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Vehn%C3%A4pelto_6.jpg/400px-Vehn%C3%A4pelto_6.jpg",
    "sugarcane": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Sugarcane_field.jpg/400px-Sugarcane_field.jpg",
    "cotton":    "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/CottonPlant.JPG/400px-CottonPlant.JPG",
    "groundnut": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/43/Peanut_clusters_on_a_white_background.jpg/400px-Peanut_clusters_on_a_white_background.jpg",
}
CROP_EMOJI = {"rice":"🌾","wheat":"🌿","sugarcane":"🎋","cotton":"🌸","groundnut":"🥜"}

CROP_INFO = {
    "rice":      {"season":"Kharif (Jun-Nov)", "water":"High (1200-2000mm)", "days":120, "temp":"22-30°C", "profit_per_acre":{"Tamil Nadu":18000,"Maharashtra":15000,"Punjab":20000,"Andhra Pradesh":17000,"Uttar Pradesh":14000}},
    "wheat":     {"season":"Rabi (Nov-Apr)",   "water":"Medium (450-650mm)","days":120, "temp":"15-25°C", "profit_per_acre":{"Tamil Nadu":12000,"Maharashtra":13000,"Punjab":22000,"Andhra Pradesh":11000,"Uttar Pradesh":19000}},
    "sugarcane": {"season":"Year-round",        "water":"High (1500-2500mm)","days":365,"temp":"24-38°C", "profit_per_acre":{"Tamil Nadu":45000,"Maharashtra":50000,"Punjab":35000,"Andhra Pradesh":42000,"Uttar Pradesh":48000}},
    "cotton":    {"season":"Kharif (May-Nov)", "water":"Medium (700-1200mm)","days":180,"temp":"20-35°C", "profit_per_acre":{"Tamil Nadu":25000,"Maharashtra":22000,"Punjab":20000,"Andhra Pradesh":28000,"Uttar Pradesh":18000}},
    "groundnut": {"season":"Kharif/Rabi",      "water":"Low (500-700mm)",   "days":120, "temp":"25-30°C", "profit_per_acre":{"Tamil Nadu":20000,"Maharashtra":18000,"Punjab":15000,"Andhra Pradesh":22000,"Uttar Pradesh":14000}},
}

# ─── MODEL LOADING ────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    try:
        import joblib
        model = joblib.load("agrisense_rf_model.pkl")
        le    = joblib.load("agrisense_label_encoder.pkl")
        return model, le, True
    except Exception:
        return None, None, False

model, label_encoder, model_loaded = load_model()

# ─── RULE-BASED FALLBACK ──────────────────────────────────────────────────────
def rule_based_predict(temp, humidity, rainfall, soil_moisture, soil_ph, nitrogen, phosphorus, potassium):
    scores = {c: 0.0 for c in CROP_INFO}
    # Temperature
    if 22 <= temp <= 30:  scores["rice"]      += 2
    if 15 <= temp <= 25:  scores["wheat"]     += 2
    if 24 <= temp <= 38:  scores["sugarcane"] += 2
    if 20 <= temp <= 35:  scores["cotton"]    += 2
    if 25 <= temp <= 30:  scores["groundnut"] += 2
    # Rainfall
    if rainfall > 1200:   scores["rice"]      += 2
    if rainfall < 700:    scores["wheat"]     += 2
    if rainfall > 1500:   scores["sugarcane"] += 2
    if rainfall > 700:    scores["cotton"]    += 1
    if rainfall < 800:    scores["groundnut"] += 2
    # Humidity
    if humidity > 75:     scores["rice"]      += 1
    if humidity < 60:     scores["wheat"]     += 1
    if humidity > 70:     scores["sugarcane"] += 1
    # Moisture
    if soil_moisture > 60: scores["rice"]     += 1
    if soil_moisture < 40: scores["groundnut"]+= 1
    # pH
    if 5.5 <= soil_ph <= 6.5: scores["rice"]  += 1
    if 6.0 <= soil_ph <= 7.5: scores["wheat"] += 1
    if 6.0 <= soil_ph <= 7.0: scores["sugarcane"] += 1

    total = sum(scores.values()) or 1
    probs = {c: v/total for c, v in scores.items()}
    best  = max(probs, key=probs.get)
    return best, probs

def predict_crop(temp, humidity, rainfall, soil_moisture, soil_ph, nitrogen, phosphorus, potassium):
    features = np.array([[temp, humidity, rainfall, soil_moisture, soil_ph, nitrogen, phosphorus, potassium]])
    if model_loaded and model is not None:
        try:
            proba = model.predict_proba(features)[0]
            classes = label_encoder.classes_
            probs = {c: float(p) for c, p in zip(classes, proba)}
            best  = label_encoder.inverse_transform(model.predict(features))[0]
            return best, probs
        except Exception:
            pass
    return rule_based_predict(temp, humidity, rainfall, soil_moisture, soil_ph, nitrogen, phosphorus, potassium)

def irrigation_status(soil_moisture, rainfall):
    if soil_moisture < 30 or rainfall < 50:
        return "🚨 Water Now", "badge-water-now"
    elif soil_moisture < 55:
        return "⏰ Water Soon", "badge-water-soon"
    else:
        return "✅ Wait", "badge-wait"

def safe_image(url, fallback_emoji, width=None):
    try:
        if width:
            st.image(url, width=width)
        else:
            st.image(url, use_column_width=True)
    except Exception:
        st.markdown(f"<div style='font-size:5rem;text-align:center'>{fallback_emoji}</div>", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌾 AgriSense AI")
    st.markdown("---")

    page = st.radio("Navigate", ["📊 Dashboard", "🌱 Crop AI", "🧪 Soil Health", "💧 Irrigation", "💰 Profit Calculator"], label_visibility="collapsed")
    st.markdown("---")
    st.markdown("### 🎛️ Sensor Inputs")

    temp          = st.slider("🌡️ Temperature (°C)",    10,  45, 28)
    humidity      = st.slider("💧 Humidity (%)",          20, 100, 72)
    rainfall      = st.slider("🌧️ Rainfall (mm)",          0,2500, 800)
    soil_moisture = st.slider("🌱 Soil Moisture (%)",      0, 100, 45)
    soil_ph       = st.slider("⚗️ Soil pH",              4.0, 9.0, 6.5, step=0.1)
    nitrogen      = st.slider("🔵 Nitrogen (kg/ha)",       0, 200, 90)
    phosphorus    = st.slider("🟠 Phosphorus (kg/ha)",     0, 200, 45)
    potassium     = st.slider("🟣 Potassium (kg/ha)",      0, 200, 60)

    st.markdown("---")
    # Voice Input Section
    st.markdown("### 🎤 Voice Input")
    voice_lang = st.selectbox("Language", ["English", "Tamil"])
    if st.button("🎙️ Speak Now"):
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                st.info("🎙️ Listening... Speak now!")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            lang_code = "ta-IN" if voice_lang == "Tamil" else "en-IN"
            text = recognizer.recognize_google(audio, language=lang_code)
            st.success(f"Heard: {text}")
            # Extract numbers
            nums = re.findall(r'\d+(?:\.\d+)?', text)
            if nums:
                st.info(f"Extracted values: {nums}")
        except ImportError:
            st.warning("⚠️ Install SpeechRecognition:\n`pip install SpeechRecognition pyaudio`")
        except Exception as e:
            st.warning(f"Voice error: Try again. ({type(e).__name__})")

    if not model_loaded:
        st.warning("⚠️ Running in fallback mode (no .pkl files found)")
    else:
        st.success("✅ ML Model loaded")

# ─── PREDICTION ───────────────────────────────────────────────────────────────
best_crop, crop_probs = predict_crop(temp, humidity, rainfall, soil_moisture, soil_ph, nitrogen, phosphorus, potassium)
irr_status, irr_badge = irrigation_status(soil_moisture, rainfall)
confidence = crop_probs.get(best_crop, 0.0) * 100

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1: DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    st.markdown('<p class="big-title">🌾 AgriSense AI Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Real-time smart irrigation & crop intelligence</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="metric-card">
            <div class="label">🌡️ Temperature</div>
            <div class="value">{temp}°</div>
            <div class="unit">Celsius</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="metric-card">
            <div class="label">💧 Humidity</div>
            <div class="value">{humidity}%</div>
            <div class="unit">Relative</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="metric-card">
            <div class="label">🌧️ Rainfall</div>
            <div class="value">{rainfall}</div>
            <div class="unit">mm</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="metric-card">
            <div class="label">🌱 Soil Moisture</div>
            <div class="value">{soil_moisture}%</div>
            <div class="unit">Volumetric</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown('<div class="crop-card">', unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:#7fc97f;margin:0'>🌾 Recommended Crop</h3>", unsafe_allow_html=True)
        safe_image(CROP_IMAGES.get(best_crop, ""), CROP_EMOJI.get(best_crop, "🌱"), width=260)
        st.markdown(f"<h2 style='color:#a5d6a7;font-size:1.8rem;text-align:center'>{best_crop.upper()}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;color:#81c784'>Confidence: {confidence:.1f}%</p>", unsafe_allow_html=True)
        st.progress(confidence / 100)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f"<div class='label'>💧 Irrigation Status</div>", unsafe_allow_html=True)
        st.markdown(f"<br><span class='{irr_badge}' style='font-size:1.3rem;padding:8px 24px'>{irr_status}</span>", unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"<div class='label'>⚗️ Soil pH</div><div class='value'>{soil_ph}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='label' style='margin-top:1rem'>🔵 N | 🟠 P | 🟣 K</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='color:#e8f5e9;font-size:1.2rem;font-weight:600'>{nitrogen} | {phosphorus} | {potassium} kg/ha</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # Crop probability mini-bars
        st.markdown("**Crop Probabilities**")
        sorted_probs = sorted(crop_probs.items(), key=lambda x: x[1], reverse=True)
        bars_html = ""
        for crop, prob in sorted_probs:
            pct = prob * 100
            bars_html += f"""<div class='prob-row'>
                <span class='prob-label'>{CROP_EMOJI.get(crop,'🌱')} {crop}</span>
                <div class='prob-bar-bg'><div class='prob-bar-fill' style='width:{pct:.0f}%'></div></div>
                <span class='prob-pct'>{pct:.0f}%</span></div>"""
        st.markdown(bars_html, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2: CROP AI
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🌱 Crop AI":
    st.markdown('<p class="big-title">🌱 Crop Intelligence</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns([1, 1.6])
    with col1:
        safe_image(CROP_IMAGES.get(best_crop, ""), CROP_EMOJI.get(best_crop, "🌱"))
        st.markdown(f"<h2 style='color:#a5d6a7;text-align:center'>{best_crop.upper()}</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='color:#81c784;text-align:center'>Confidence: <b>{confidence:.1f}%</b></p>", unsafe_allow_html=True)

    with col2:
        info = CROP_INFO.get(best_crop, {})
        st.markdown("### 🧠 Why This Crop?")
        reasons = []
        if 22 <= temp <= 35:
            reasons.append(f"✅ Temperature **{temp}°C** is suitable for {best_crop}")
        if rainfall > 500:
            reasons.append(f"✅ Rainfall **{rainfall}mm** meets water requirements")
        if 5.5 <= soil_ph <= 7.5:
            reasons.append(f"✅ Soil pH **{soil_ph}** is in optimal range")
        if soil_moisture > 30:
            reasons.append(f"✅ Soil moisture **{soil_moisture}%** is adequate")
        if not reasons:
            reasons.append(f"⚠️ Conditions are marginal — consider improving inputs")
        for r in reasons:
            st.markdown(r)

        st.markdown("---")
        st.markdown("### 📋 Growing Conditions")
        df_info = pd.DataFrame({
            "Parameter": ["Season", "Water Requirement", "Days to Harvest", "Optimal Temp"],
            "Value": [info.get("season","—"), info.get("water","—"), str(info.get("days","—"))+" days", info.get("temp","—")]
        })
        st.dataframe(df_info, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("### 📊 All Crop Probabilities")
    sorted_probs = sorted(crop_probs.items(), key=lambda x: x[1], reverse=True)
    fig = go.Figure(go.Bar(
        x=[c.capitalize() for c, _ in sorted_probs],
        y=[p*100 for _, p in sorted_probs],
        marker_color=["#43a047" if c == best_crop else "#2d6a35" for c, _ in sorted_probs],
        text=[f"{p*100:.1f}%" for _, p in sorted_probs],
        textposition="outside"
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#a5d6a7", yaxis_title="Probability (%)",
        xaxis=dict(color="#a5d6a7"), yaxis=dict(color="#a5d6a7", gridcolor="#2d6a35"),
        margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3: SOIL HEALTH
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🧪 Soil Health":
    st.markdown('<p class="big-title">🧪 Soil Health Monitor</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    # Moisture gauge
    with col1:
        st.markdown("#### 💧 Soil Moisture Gauge")
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=soil_moisture,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Moisture %", 'font': {'color': '#a5d6a7'}},
            gauge={
                'axis': {'range': [0, 100], 'tickcolor': '#a5d6a7'},
                'bar': {'color': '#43a047'},
                'bgcolor': '#1b3d20',
                'steps': [
                    {'range': [0, 30], 'color': '#b71c1c'},
                    {'range': [30, 60], 'color': '#f57f17'},
                    {'range': [60, 100], 'color': '#1b5e20'}],
                'threshold': {'line': {'color': "#a5d6a7", 'width': 3}, 'value': soil_moisture}
            },
            number={'font': {'color': '#a5d6a7'}}
        ))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=250, margin=dict(t=40,b=10,l=10,r=10))
        st.plotly_chart(fig, use_container_width=True)

    # pH meter
    with col2:
        st.markdown("#### ⚗️ Soil pH Meter")
        if soil_ph < 6.0:
            ph_label, ph_color = "Acidic 🔴", "#ef5350"
            ph_advice = "Add lime to increase pH"
        elif soil_ph > 7.5:
            ph_label, ph_color = "Alkaline 🔵", "#42a5f5"
            ph_advice = "Add sulfur to decrease pH"
        else:
            ph_label, ph_color = "Neutral ✅", "#66bb6a"
            ph_advice = "pH is in ideal range"

        fig2 = go.Figure(go.Indicator(
            mode="gauge+number",
            value=soil_ph,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "pH Level", 'font': {'color': '#a5d6a7'}},
            gauge={
                'axis': {'range': [4, 9], 'tickcolor': '#a5d6a7'},
                'bar': {'color': ph_color},
                'bgcolor': '#1b3d20',
                'steps': [
                    {'range': [4, 6], 'color': '#b71c1c'},
                    {'range': [6, 7.5], 'color': '#1b5e20'},
                    {'range': [7.5, 9], 'color': '#0d47a1'}],
            },
            number={'font': {'color': '#a5d6a7'}}
        ))
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=250, margin=dict(t=40,b=10,l=10,r=10))
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown(f"**Status:** <span style='color:{ph_color}'>{ph_label}</span>", unsafe_allow_html=True)
        st.caption(ph_advice)

    # NPK
    with col3:
        st.markdown("#### 🧬 NPK Levels")
        npk_data = {"Nitrogen": nitrogen, "Phosphorus": phosphorus, "Potassium": potassium}
        for nutrient, val in npk_data.items():
            pct = min(val / 200, 1.0)
            color = "#43a047" if pct > 0.5 else "#ff9800" if pct > 0.25 else "#ef5350"
            st.markdown(f"**{nutrient}** — {val} kg/ha")
            fig3 = go.Figure(go.Bar(x=[val], y=[""], orientation="h",
                marker_color=color, text=[f"{val}"], textposition="outside"))
            fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=60, margin=dict(t=0,b=0,l=0,r=60),
                xaxis=dict(range=[0,200], color="#a5d6a7", gridcolor="#2d6a35"),
                yaxis=dict(showticklabels=False), font_color="#a5d6a7")
            st.plotly_chart(fig3, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🗺️ Soil Type Profile")
    soil_type = st.selectbox("Select Soil Type", ["Alluvial", "Black (Regur)", "Red Laterite", "Sandy Loam", "Clay"])
    soil_profiles = {
        "Alluvial":       {"Texture":"Fine-loamy","Drainage":"Good","Fertility":"High","Best Crops":"Rice, Wheat"},
        "Black (Regur)":  {"Texture":"Heavy Clay","Drainage":"Poor","Fertility":"High","Best Crops":"Cotton, Sugarcane"},
        "Red Laterite":   {"Texture":"Coarse","Drainage":"Excellent","Fertility":"Low","Best Crops":"Groundnut, Millets"},
        "Sandy Loam":     {"Texture":"Light","Drainage":"Very Good","Fertility":"Medium","Best Crops":"Groundnut, Vegetables"},
        "Clay":           {"Texture":"Fine","Drainage":"Poor","Fertility":"High","Best Crops":"Rice, Sugarcane"},
    }
    df_soil = pd.DataFrame(list(soil_profiles[soil_type].items()), columns=["Property","Value"])
    st.dataframe(df_soil, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4: IRRIGATION
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💧 Irrigation":
    st.markdown('<p class="big-title">💧 Irrigation Control</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns([1,1.2])

    with col1:
        st.markdown("### 🚦 Water Decision")
        color_map = {"badge-water-now": "#ff5252", "badge-wait": "#4caf50", "badge-water-soon": "#ff9800"}
        irr_color = color_map.get(irr_badge, "#4caf50")
        st.markdown(f"""<div style="background:{irr_color}22;border:2px solid {irr_color};border-radius:16px;padding:1.5rem;text-align:center">
            <div style="font-size:2.5rem">{irr_status}</div>
            <p style="color:#c8e6c9;margin:0.5rem 0">Soil moisture: {soil_moisture}% | Rainfall: {rainfall}mm</p>
        </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🔧 Manual Pump Control")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("💧 Turn Pump ON"):
                st.success("✅ Pump turned ON!")
        with c2:
            if st.button("🛑 Turn Pump OFF"):
                st.info("🛑 Pump turned OFF")

        st.markdown("---")
        st.markdown("### 📱 SMS Alerts (Twilio)")
        phone = st.text_input("Phone number (e.g. +91XXXXXXXXXX)")
        if st.button("📤 Send Test Alert"):
            if phone:
                st.info("⚠️ Twilio credentials required. Add TWILIO_SID, TWILIO_TOKEN, TWILIO_FROM to environment to enable SMS.")
            else:
                st.warning("Enter a phone number first.")

    with col2:
        st.markdown("### 📅 Weekly Watering Schedule")
        days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        schedule_data = []
        base_moisture = soil_moisture
        for i, day in enumerate(days):
            projected = max(0, min(100, base_moisture + np.random.randint(-5, 10)))
            decision = "Water" if projected < 40 else "Skip" if projected > 65 else "Monitor"
            amount = "25 min" if decision == "Water" else "—"
            schedule_data.append({"Day": day, "Projected Moisture": f"{projected:.0f}%", "Action": decision, "Duration": amount})
            base_moisture = projected
        df_sched = pd.DataFrame(schedule_data)
        st.dataframe(df_sched, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5: PROFIT CALCULATOR
# ══════════════════════════════════════════════════════════════════════════════
elif page == "💰 Profit Calculator":
    st.markdown('<p class="big-title">💰 Profit Calculator</p>', unsafe_allow_html=True)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        farm_size = st.slider("🏡 Farm Size (acres)", 1, 100, 10)
    with col2:
        region = st.selectbox("📍 Region", ["Tamil Nadu","Maharashtra","Punjab","Andhra Pradesh","Uttar Pradesh"])

    st.markdown("---")

    profit_rows = []
    best_profit_crop = max(CROP_INFO.keys(), key=lambda c: CROP_INFO[c]["profit_per_acre"].get(region, 0))

    cols = st.columns(len(CROP_INFO))
    for idx, (crop, info) in enumerate(CROP_INFO.items()):
        ppa = info["profit_per_acre"].get(region, 15000)
        total = ppa * farm_size
        is_best = (crop == best_profit_crop)
        profit_rows.append({"Crop": crop.capitalize(), "Per Acre (₹)": f"₹{ppa:,}", "Total (₹)": f"₹{total:,}"})

        with cols[idx]:
            border_color = "#ffd600" if is_best else "#2d6a35"
            badge = "⭐ BEST" if is_best else ""
            st.markdown(f"""<div style="background:{'#1a3a00' if is_best else '#1a3a1e'};border:2px solid {border_color};border-radius:16px;padding:1rem;text-align:center;margin-bottom:1rem">
                <div style="font-size:0.8rem;color:{'#ffd600' if is_best else '#7fc97f'};font-weight:700">{badge}</div>
                <div style="font-size:1.1rem;color:#a5d6a7;font-weight:700">{crop.upper()}</div>
                <div style="color:#c8e6c9;margin:0.5rem 0">₹{ppa:,}/acre</div>
                <div style="font-size:1.4rem;font-weight:700;color:{'#ffd600' if is_best else '#e8f5e9'}">₹{total:,}</div>
                <div style="font-size:0.75rem;color:#81c784">{farm_size} acres</div>
            </div>""", unsafe_allow_html=True)
            safe_image(CROP_IMAGES.get(crop,""), CROP_EMOJI.get(crop,"🌱"), width=130)

    st.markdown("---")
    st.markdown("### 📊 Profit Comparison Chart")
    crops_list = list(CROP_INFO.keys())
    profits    = [CROP_INFO[c]["profit_per_acre"].get(region,0)*farm_size for c in crops_list]
    fig = go.Figure(go.Bar(
        x=[c.capitalize() for c in crops_list],
        y=profits,
        marker_color=["#ffd600" if c == best_profit_crop else "#43a047" for c in crops_list],
        text=[f"₹{p:,}" for p in profits],
        textposition="outside"
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font_color="#a5d6a7", yaxis_title="Total Profit (₹)",
        xaxis=dict(color="#a5d6a7"), yaxis=dict(color="#a5d6a7", gridcolor="#2d6a35"),
        margin=dict(t=30,b=20)
    )
    st.plotly_chart(fig, use_container_width=True)

    df_summary = pd.DataFrame(profit_rows)
    st.markdown("### 📋 Summary Table")
    st.dataframe(df_summary, use_container_width=True, hide_index=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("<p style='text-align:center;color:#558b2f;font-size:0.8rem'>🌾 AgriSense AI | Smart Irrigation & Crop Intelligence | Built with Streamlit</p>", unsafe_allow_html=True)

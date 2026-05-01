import streamlit as st
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt

# ✅ SAFE Plotly import (prevents crash)
try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except:
    PLOTLY_AVAILABLE = False

st.set_page_config(page_title="AI Smart Agriculture", layout="centered")

st.title("🌱 AI Smart Agriculture Decision System")

# ✅ Load Dataset safely
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Crop_recommendation.csv")
        return df
    except:
        return None

data = load_data()

if data is None:
    st.error("❌ Dataset not found. Make sure 'Crop_recommendation.csv' is in the same folder.")
    st.stop()

st.success("✅ Dataset Loaded Successfully")

# ✅ Prepare Model
X = data.drop("label", axis=1)
y = data["label"]

model = RandomForestClassifier()
model.fit(X, y)

accuracy = model.score(X, y)
st.info(f"📊 Model Accuracy: {round(accuracy*100,2)}%")

# ✅ User Inputs
st.subheader("🧪 Enter Soil & Environmental Data")

col1, col2 = st.columns(2)

with col1:
    N = st.number_input("Nitrogen (N)", min_value=0.0)
    P = st.number_input("Phosphorus (P)", min_value=0.0)
    K = st.number_input("Potassium (K)", min_value=0.0)
    temp = st.number_input("Temperature (°C)", min_value=0.0)

with col2:
    humidity = st.number_input("Humidity (%)", min_value=0.0)
    ph = st.number_input("pH Value", min_value=0.0)
    rainfall = st.number_input("Rainfall (mm)", min_value=0.0)

# ✅ Prediction
if st.button("🚀 Analyze & Recommend"):

    input_data = [[N, P, K, temp, humidity, ph, rainfall]]

    try:
        prediction = model.predict(input_data)[0]
        probs = model.predict_proba(input_data)[0]
        classes = model.classes_

        st.success(f"🌾 Best Crop: {prediction}")

        # 🧠 Top 3
        st.subheader("🧠 Top 3 Recommendations")
        top3_idx = np.argsort(probs)[-3:][::-1]

        for i in top3_idx:
            st.write(f"{classes[i]} → {round(probs[i]*100,2)}%")

        # 💰 Profit
        st.subheader("💰 Profit Estimation")

        market_price = {
            "rice": 20, "wheat": 18, "maize": 22,
            "cotton": 60, "sugarcane": 5,
            "banana": 25, "mango": 50
        }

        yield_estimate = rainfall * 0.8 + temp * 2
        price = market_price.get(prediction, 15)
        profit = yield_estimate * price

        st.success(f"Estimated Profit: ₹ {round(profit,2)}")

        # 📊 Visualization
        st.subheader("📊 Soil & Climate Analysis")

        values = [N, P, K, temp, humidity, ph, rainfall]
        labels = ["N","P","K","Temp","Humidity","pH","Rainfall"]

        # ✅ Use Plotly if available
        if PLOTLY_AVAILABLE:
            fig = go.Figure([go.Bar(x=labels, y=values)])
            st.plotly_chart(fig, use_container_width=True)
        else:
            fig, ax = plt.subplots()
            ax.bar(labels, values)
            st.pyplot(fig)

        # 🌱 Soil Insight
        st.subheader("🌱 Soil Health Insight")

        if ph < 5.5:
            st.warning("Soil is acidic. Add lime.")
        elif ph > 7.5:
            st.warning("Soil is alkaline. Add organic matter.")
        else:
            st.success("Soil pH is optimal.")

        # 🤖 AI Explanation
        st.subheader("🤖 AI Recommendation")

        st.write(f"""
        Based on soil nutrients and climate conditions, the system recommends **{prediction}**.

        The model analyzed multiple environmental factors and ranked crops using probability scores.

        This ensures better decision-making and improved agricultural productivity.
        """)

    except Exception as e:
        st.error(f"❌ Error: {e}")

# ✅ Debug Info
with st.expander("⚙️ Debug Info"):
    st.write("Dataset Shape:", data.shape)
    st.write("Columns:", list(data.columns))

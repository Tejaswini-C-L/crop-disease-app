import streamlit as st
from PIL import Image
import numpy as np
from tensorflow.keras.models import load_model
import json

st.set_page_config(page_title="Crop Disease Detection", layout="centered")

st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}

.big-card {
    padding: 20px;
    border-radius: 12px;
    background-color: white;
    box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.title {
    font-size: 26px;
    font-weight: bold;
    color: #2c3e50;
}

.sub {
    font-size: 18px;
    color: #555;
}

.small {
    font-size: 15px;
    color: #777;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD MODEL ----------------
model = load_model("crop_model_final.keras")

with open("class_names.json", "r") as f:
    class_names = json.load(f)

# ---------------- FUNCTIONS ----------------

def predict_image(img):
    img = img.resize((224,224))
    img_array = np.array(img)/255.0
    img_array = np.expand_dims(img_array, axis=0)

    pred = model.predict(img_array)
    class_idx = np.argmax(pred)
    confidence = np.max(pred)

    return class_names[class_idx], confidence


def get_severity(conf):
    if conf < 0.6:
        return "Early Stage"
    elif conf < 0.85:
        return "Moderate"
    else:
        return "Severe"


def analyze_weather(temp, humidity, rainfall):
    report = {
        "risk_level": "Low",
        "factors": [],
        "summary": ""
    }

    score = 0

    # HIGH IMPACT
    if humidity > 80:
        report["factors"].append("🔴 High humidity strongly promotes fungal disease")
        score += 2

    if rainfall > 100:
        report["factors"].append("🔴 Excess rainfall increases disease spread")
        score += 2

    # MODERATE IMPACT
    if temp > 32:
        report["factors"].append("🟠 High temperature causes plant stress")
        score += 2

    # LOW IMPACT
    elif temp > 28:
        report["factors"].append("🟡 Slightly high temperature")
        score += 1

    # -------- FIXED RISK LOGIC --------
    if score >= 4:
        report["risk_level"] = "High"
        report["summary"] = "⚠️ High chance of disease due to weather conditions"
    elif score >= 2:
        report["risk_level"] = "Moderate"
        report["summary"] = "⚠️ Some weather conditions may contribute to disease"
    elif score == 1:
        report["risk_level"] = "Low"
        report["summary"] = "⚠️ Minor weather stress detected"
    else:
        report["risk_level"] = "Low"
        report["summary"] = "✅ Weather conditions are safe"

    # No factors case
    if not report["factors"]:
        report["factors"].append("✅ No significant weather risks")

    return report

# ---------------- SOLUTIONS ----------------

solutions = {
    "maize_blight": {"fertilizer":"Nitrogen-rich","treatment":"Fungicide spray","prevention":"Resistant seeds"},
    "maize_common_rust": {"fertilizer":"Potassium-rich","treatment":"Foliar fungicide","prevention":"Proper spacing"},
    "maize_gray_leaf_spot": {"fertilizer":"Balanced NPK","treatment":"Strobilurin fungicide","prevention":"Crop rotation"},
    "maize_healthy": {"fertilizer":"Balanced nutrients","treatment":"None","prevention":"Regular care"},

    "potato_early_blight": {"fertilizer":"Nitrogen + Potassium","treatment":"Chlorothalonil","prevention":"Avoid wet leaves"},
    "potato_late_blight": {"fertilizer":"NPK","treatment":"Copper fungicide","prevention":"Avoid waterlogging"},
    "potato_healthy": {"fertilizer":"Balanced fertilizer","treatment":"None","prevention":"Soil health"},

    "tomato_early_blight": {"fertilizer":"Nitrogen + Potassium","treatment":"Chlorothalonil","prevention":"Avoid wet leaves"},
    "tomato_late_blight": {"fertilizer":"Balanced fertilizer","treatment":"Copper fungicide","prevention":"Good airflow"},
    "tomato_healthy": {"fertilizer":"Organic compost","treatment":"None","prevention":"Regular care"}
}

# ---------------- UI ----------------

st.markdown("<h1 style='text-align:center;color:#0F5904'>🌿 Crop Disease Detection System</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:grey;'>AI-powered plant health analysis</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("Upload Leaf Image", type=["jpg","png","jpeg"])

temp = st.number_input("Temperature (°C)", 0, 50, 30)
humidity = st.number_input("Humidity (%)", 0, 100, 80)
rainfall = st.number_input("Rainfall (mm)", 0, 500, 100)

# ---------------- MAIN LOGIC ----------------

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, caption="Uploaded Image", use_column_width=True)

    disease, conf = predict_image(img)
    severity = get_severity(conf)
    weather = analyze_weather(temp, humidity, rainfall)

    solution = solutions.get(disease, {
        "fertilizer":"General fertilizer",
        "treatment":"Consult expert",
        "prevention":"Maintain crop care"
    })

    # 🔥 BIG HEADING
    st.markdown("### 📊 Results")

if "healthy" in disease:
    status = "✅ Healthy"
else:
    status = severity

st.markdown(f"""
<div class="big-card">
    <div class="title">Disease: {disease.replace('_',' ').title()}</div>
    <div class="sub">Confidence: {round(conf,3)}</div>
    <div class="sub">Status: {status}</div>
</div>
""", unsafe_allow_html=True)

# ✅ FIX HERE
if "healthy" in disease:
    st.markdown("**Status:** ✅ Plant is Healthy")
else:
    st.markdown(f"**Severity:** {severity}")
    # 🔥 BIG HEADING
    st.markdown("### 🌦️ Weather Analysis")

color = "#2ecc71"  # green
if weather["risk_level"] == "Moderate":
    color = "#f39c12"
elif weather["risk_level"] == "High":
    color = "#e74c3c"

factors_html = "".join([f"<li>{f}</li>" for f in weather["factors"]])

st.markdown(f"""
<div class="big-card">
    <div class="title">Risk Level: <span style="color:{color};">{weather['risk_level']}</span></div>
    <div class="sub">{weather['summary']}</div>
    <br>
    <div class="small"><b>Contributing Factors:</b></div>
    <ul class="small">
        {factors_html}
    </ul>
</div>
""", unsafe_allow_html=True)
    # 🔥 BIG HEADING
st.markdown("### 🌱 Solution")

if "healthy" in disease:
    st.success("✅ No treatment needed. Maintain current care.")
else:
    st.markdown(f"""
    <div class="big-card">
        <div class="sub"><b>Fertilizer:</b> {solution['fertilizer']}</div>
        <div class="sub"><b>Treatment:</b> {solution['treatment']}</div>
        <div class="sub"><b>Prevention:</b> {solution['prevention']}</div>
    </div>
    """, unsafe_allow_html=True)
# 🌲 VanDoot: Multi-Tier Forest Intelligence System

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge.svg)](https://vandootproject-hnud4i4hdhbpdc6wovxbkx.streamlit.app)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![Logic](https://img.shields.io/badge/Logic-Sensor%20Fusion-green)

**VanDoot** is an integrated IoT ecosystem designed for real-time forest threat detection. It solves the "False Alarm" problem in remote monitoring by using a **Multi-Sensor Fusion** strategy—verifying visual AI detections with environmental data to provide 100% reliable alerts.

---

## 🛰️ Live Deployment
Check out the live AI Analytical Dashboard here:  
🚀 **[VanDoot Cloud Interface](https://vandootproject-hnud4i4hdhbpdc6wovxbkx.streamlit.app)**

---

## 🛠️ The VanDoot Pipeline (Repository Map)

This project is organized according to the flow of data. Follow the pipeline to understand the logic:

### 1️⃣ Phase 1: Edge Vision (The Sentry)
*Located in `/esp32`*
* **On-Device AI**: `esp32_ai_camera.ino` runs a quantized **MobileNetV1** model directly on the ESP32-CAM.
* **Task**: Detects **Fire, Humans, or Animals** at the source to minimize data transmission.
* **Optimization**: The model is converted to a C++ byte array (`model_data.cc`) for low-memory execution.

### 2️⃣ Phase 2: Sensor Fusion (The Judge)
*Located in `/random_forest`*
* **The "Judge" Logic**: The camera can be fooled (e.g., a red sunset looks like fire). Our **Random Forest model** (`vandoot_judge.pkl`) resolves these conflicts.
* **Decision Logic**:
    * `Vision(Fire)` + `Smoke(Low)` = **SAFE** (System overrides the camera).
    * `Vision(Human)` + `Audio(High)` = **POACHER** (Detects chainsaw/logging noise).

### 3️⃣ Phase 3: Cloud Analytics (The Dashboard)
*Located in `streamlit_app.py`*
* **Data Processing**: Processes the `logs/events.txt` bridge file.
* **Generative AI**: Integrates **Gemini AI** to transform raw logs into "Ecological Intelligence Reports," summarizing long-term threat patterns in plain English.

---

## 📂 Project Structure
* **`data_generation/`**: Simulators like `generate_realistic_logs.py` used to stress-test the system with 180 days of activity.
* **`esp32/`**: Hardware firmware and TinyML training scripts.
* **`random_forest/`**: Training pipeline for the fusion logic.
* **`logs/`**: The central data hub where sensors record raw event data.

---

## 🚀 Quick Start (Local Simulation)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your Gemini API Key
export GOOGLE_API_KEY='your_api_key_here'

# 3. Launch the full pipeline
python data_generation/generate_realistic_logs.py && streamlit run streamlit_app.py

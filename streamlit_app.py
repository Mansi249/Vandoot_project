import streamlit as st
from google import genai
from collections import Counter
import os

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)

st.title("🌲 VanDoot AI Forest Monitoring System")

st.write(
"""
Upload **forest monitoring logs** collected from an edge AI camera.

Gemini 3 will analyze:
- wildlife activity
- human intrusion
- fire risks

and generate an **AI ecological intelligence report**.
"""
)

# ---------- DEMO LOG SECTION ----------

st.subheader("📁 Demo Log File")

with open("logs/events.txt", "r") as f:
    demo_log = f.read()

st.download_button(
    label="Download Sample Log File",
    data=demo_log,
    file_name="events.txt",
    mime="text/plain"
)

use_demo = st.button("Use Demo Log")

uploaded_file = st.file_uploader("Upload events.txt log file")

# ---------- SELECT SOURCE OF LOGS ----------

if uploaded_file is not None:
    lines = uploaded_file.read().decode().splitlines()

elif use_demo:
    lines = demo_log.splitlines()

else:
    lines = None


# ---------- PROCESS LOGS ----------

if lines is not None:

    events = []
    human_times = []
    fire_times = []

    for line in lines:

        parts = line.strip().split()

        if len(parts) < 4:
            continue

        timestamp = parts[0] + " " + parts[1]
        event = parts[2]

        events.append(event)

        if event == "human":
            human_times.append(timestamp)

        if event == "fire":
            fire_times.append(timestamp)

    counts = Counter(events)

    st.subheader("📊 Log Summary")

    st.write(f"Animal detections: {counts.get('animal',0)}")
    st.write(f"Human detections: {counts.get('human',0)}")
    st.write(f"Fire detections: {counts.get('fire',0)}")
    st.write(f"Empty frames: {counts.get('empty',0)}")

    st.subheader("📄 Log Preview")
    st.code("\n".join(lines[:10]))

    summary = f"""
    You are analyzing six months of forest monitoring data collected from
    an AI wildlife camera system.

    Event statistics:

    Animal detections: {counts.get("animal",0)}
    Human detections: {counts.get("human",0)}
    Fire detections: {counts.get("fire",0)}
    Empty frames: {counts.get("empty",0)}

    Example human detection times:
    {human_times[:5]}

    Example fire detection times:
    {fire_times[:5]}

    Generate a forest monitoring intelligence report explaining:

    - wildlife behavior patterns
    - possible human intrusion
    - potential wildfire risks
    """

    if st.button("🔍 Analyze with Gemini 3"):

        with st.spinner("Gemini is analyzing forest activity..."):

            try:

                response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=summary
                )

                st.subheader("🌍 AI Forest Intelligence Report")

                st.write(response.text)

            except Exception as e:

                st.error(f"Gemini API error: {e}")

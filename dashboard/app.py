import streamlit as st
import requests
import plotly.graph_objects as go

# Ensure API URL matches the Docker network
API_URL = "http://api:8000/api"

st.set_page_config(page_title="HawkEye Traffic AI", layout="wide", page_icon="🚔")

st.title("🚔 HawkEye Traffic AI Command Center")
st.markdown("Powered by **Smart Enforcement Validation Engine (SEVE)**")

# Fetch Data
try:
    response = requests.get(f"{API_URL}/analytics")
    data = response.json()
except Exception as e:
    st.error("API Offline. Please ensure Docker containers are running.")
    st.stop()

# --- Top Metrics Row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Vehicles Processed", data.get("total_processed", 0))
col2.metric("Triple Riding Flags", data.get("triple_riding", 0))
col3.metric("Helmet Violations", data.get("helmet_non_compliance", 0))

# THIS IS THE WINNING METRIC
col4.metric(
    "False Fines Suppressed by SEVE", 
    data.get("seve_suppressed_fines", 0), 
    delta="Rescued by Contextual AI", 
    delta_color="normal"
)

st.markdown("---")

# --- Interactive Upload & Evaluation Section ---
st.subheader("Live Intersection Feed (Upload Evidence)")

upload_col, result_col = st.columns([1, 2])

with upload_col:
    uploaded_file = st.file_uploader("Upload Traffic Camera Frame", type=['jpg', 'jpeg', 'png'])
    if uploaded_file is not None:
        if st.button("Run SEVE Evaluation"):
            with st.spinner("Analyzing environment, tracking vectors, and running SEVE checks..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "image/jpeg")}
                upload_res = requests.post(f"{API_URL}/upload", files=files)
                
                if upload_res.status_code == 200:
                    detect_res = requests.get(f"{API_URL}/detect")
                    st.session_state['latest_result'] = detect_res.json()

with result_col:
    if 'latest_result' in st.session_state:
        res = st.session_state['latest_result']
        
        if res.get("status") == "FAILED":
            st.error(f"Image Rejected by EQS: {res.get('message')}")
        else:
            st.success("SEVE Evaluation Complete")
            
            # Display the processed SEVE evidence image (Not the raw upload)
            import os
            evidence_file = res.get("evidence_url")
            if evidence_file and os.path.exists(evidence_file):
                st.image(evidence_file, caption="HawkEye AI Processed Evidence", use_container_width=True)
            else:
                st.image(uploaded_file, caption="Raw Frame (Evidence generation pending)", use_container_width=True)
            
            st.markdown("### SEVE Execution Log")
            st.write(f"**Environment Quality Score (EQS):** {res['environment_quality']['score']}/100 - {res['environment_quality']['reason']}")
            
            if res.get("plates_detected"):
                st.info(f"**Validated Plates:** {', '.join(res['plates_detected'])}")
            
            if res.get("violations"):
                for v in res["violations"]:
                    st.warning(f"🚨 **{v['type']}** (Confidence: {v['confidence']:.2f})")
                    st.caption(f"SEVE Context: {v.get('seve_context', 'N/A')}")
            else:
                st.success("✅ No actionable violations found (or suppressed by SEVE).")
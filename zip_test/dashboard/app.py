import streamlit as st
import requests
import plotly.graph_objects as go

import os
# Support running natively (localhost) or inside docker (api)
API_BASE = os.getenv("API_URL", "http://localhost:8000")
API_URL = f"{API_BASE.rstrip('/')}/api"

st.set_page_config(page_title="HawkEye Traffic AI", layout="wide", page_icon="🚔")

st.title("🚔 HawkEye Traffic AI Command Center")
st.markdown("Powered by **Smart Enforcement Validation Engine (SEVE)**")

# Fetch Data
try:
    response = requests.get(f"{API_URL}/analytics")
    if response.status_code == 200:
        data = response.json()
    else:
        data = {}
        st.warning("Could not fetch analytics data.")
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
    uploaded_files = st.file_uploader("Upload Evidence Photos", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
    if uploaded_files:
        if st.button("Run SEVE Evaluation"):
            with st.spinner("Analyzing environment, running SEVE checks, and extracting OCR..."):
                st.session_state['results'] = []
                for uploaded_file in uploaded_files:
                    # Single image process for each file
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "image/jpeg")}
                    upload_res = requests.post(f"{API_URL}/upload", files=files)
                    if upload_res.status_code == 200:
                        # Call the specific detection route for the uploaded file if we could pass name, but detect() grabs latest
                        # We need an endpoint to process a specific file to avoid race conditions.
                        # Wait, /detect grabs the latest file. If we upload one by one and detect, it's fine.
                        detect_res = requests.get(f"{API_URL}/detect")
                        st.session_state['results'].append({
                            'upload': uploaded_file,
                            'data': detect_res.json()
                        })

with result_col:
    if 'results' in st.session_state and st.session_state['results']:
        for idx, result_item in enumerate(st.session_state['results']):
            res = result_item['data']
            upload = result_item['upload']
            
            st.markdown(f"### Result {idx + 1}: {upload.name}")
            
            if res.get("status") == "FAILED":
                st.error(f"Image Rejected by EQS: {res.get('message')}")
            else:
                st.success("SEVE Evaluation Complete")
                
                # Display the processed SEVE evidence image
                import os
                evidence_file = res.get("evidence_url")
                if evidence_file and os.path.exists(evidence_file):
                    st.image(evidence_file, caption=f"Processed: {upload.name}", use_container_width=True)
                else:
                    st.image(upload, caption="Raw Frame", use_container_width=True)
                
                st.write(f"**Environment Quality Score (EQS):** {res['environment_quality']['score']}/100 - {res['environment_quality']['reason']}")
                
                if res.get("plates_detected"):
                    st.info(f"**Validated Plates:** {', '.join(res['plates_detected'])}")
                
                if res.get("violations"):
                    for v in res["violations"]:
                        st.warning(f"🚨 **{v['type']}** (Confidence: {v['confidence']:.2f})")
                        st.caption(f"SEVE Context: {v.get('seve_context', 'N/A')}")
                else:
                    st.success("✅ No actionable violations found (or suppressed by SEVE).")
            
            st.markdown("---")

# --- Investigation Section ---
st.subheader("Intelligence & Investigations")
inv_col1, inv_col2 = st.columns(2)

with inv_col1:
    st.markdown("### 🔍 Search by License Plate")
    plate_query = st.text_input("Enter Plate Number (e.g. KA01AB1234)")
    if st.button("Search History") and plate_query:
        try:
            search_res = requests.get(f"{API_URL}/violations/search/{plate_query}")
            if search_res.status_code == 200:
                records = search_res.json().get("records", [])
                if records:
                    st.success(f"Found {len(records)} records for {plate_query.upper()}")
                    for r in records:
                        st.info(f"Date: {r.get('created_at')} - Violations: {len(r.get('violations', []))}")
                else:
                    st.warning("No records found.")
        except Exception as e:
            st.error("Search failed.")

with inv_col2:
    st.markdown("### ⚠️ Top 10 Repeat Offenders")
    if st.button("Load Repeat Offenders"):
        try:
            ro_res = requests.get(f"{API_URL}/analytics/repeat_offenders")
            if ro_res.status_code == 200:
                offenders = ro_res.json()
                if offenders:
                    for o in offenders:
                        st.error(f"**{o['plate']}**: {o['count']} Violations")
                else:
                    st.success("No repeat offenders found.")
        except Exception as e:
            st.error("Failed to load repeat offenders.")
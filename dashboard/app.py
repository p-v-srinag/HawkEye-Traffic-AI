import streamlit as st
import requests


st.set_page_config(
    page_title="HawkEye Traffic AI",
    layout="wide"
)

st.title(
    "🚔 HawkEye Traffic AI"
)

response = requests.get(
    "http://localhost:8000/api/analytics"
)

data = response.json()

st.metric(
    "Total Records",
    data["total_records"]
)

st.metric(
    "Triple Riding",
    data["triple_riding"]
)
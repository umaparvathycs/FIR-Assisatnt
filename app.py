import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# 1. Setup the API Key
# For local testing, replace the line below with: genai.configure(api_key="PASTE_YOUR_KEY_HERE")
# For GitHub/Streamlit Cloud, we use 'Secrets' for safety:
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    st.error("Please set the GOOGLE_API_KEY in Streamlit Secrets!")

model = genai.GenerativeModel('gemini-1.5-flash')

st.title("⚖️ AI FIR Drafting Assistant")

# --- Initialize Chat ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- User Input ---
if prompt := st.chat_input("Tell me what happened..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- Get AI Response (Cloud Version) ---
    with st.chat_message("assistant"):
        full_prompt = f"System: You are a Kerala Police Assistant. Ask for Date, Time, Location, and Item one by one. Once you have all, generate a formal FIR using BNS Section 303. Context: {st.session_state.messages}"
        response = model.generate_content(full_prompt)
        reply = response.text
        st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})

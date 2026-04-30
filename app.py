import streamlit as st
import google.generativeai as genai
from fpdf import FPDF

# --- 1. SETUP ---
st.set_page_config(page_title="AI FIR Assistant", page_icon="⚖️")

# Use st.secrets for the API Key (set this up in Streamlit Cloud dashboard)
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except:
    st.error("Error: GOOGLE_API_KEY not found in Streamlit Secrets.")
    st.stop()

model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. UI HEADER ---
st.title("⚖️ AI FIR Drafting Assistant")
st.markdown("##### Kerala Police Interactive Reporting Tool (Academic Project)")

# --- 3. CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a Kerala Police Assistant. Help the user draft an FIR for theft (BNS Section 303). Ask for: Date/Time, Location, and Item Details one by one. Once you have all, generate a formal FIR draft."}
    ]

# Display chat history
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Tell me what happened..."):
    # Add user message to state
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate AI Response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            # We send the history so the AI remembers previous answers
            response = model.generate_content(str(st.session_state.messages))
            reply = response.text
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

    # --- 4. PDF DOWNLOAD ---
    # Only show button if the AI has generated a formal report
    if "FIR" in reply.upper() or "BNS" in reply.upper():
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        # Clean text for PDF compatibility
        clean_text = reply.encode('latin-1', 'replace').decode('latin-1')
        pdf.multi_cell(0, 10, txt=clean_text)
        
        pdf_file = "FIR_Draft.pdf"
        pdf.output(pdf_file)
        
        with open(pdf_file, "rb") as f:
            st.download_button("📥 Download FIR PDF", f, file_name="FIR_Draft.pdf")

# Sidebar
with st.sidebar:
    st.info("Built with Google Gemini & Streamlit")
    st.warning("For project purposes only.")

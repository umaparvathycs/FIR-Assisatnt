import streamlit as st
import google.generativeai as genai
import json
import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FIR Assistant | Kerala Police",
    page_icon="🚔",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS styling ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@400;600;700&family=Noto+Serif+Malayalam&family=Source+Sans+3:wght@300;400;600&display=swap');

/* Reset & Base */
html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
}

/* Background */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1b2a 50%, #0a1628 100%);
    min-height: 100vh;
}

/* Header Banner */
.header-banner {
    background: linear-gradient(90deg, #1a3a5c 0%, #0d2137 40%, #1a3a5c 100%);
    border-bottom: 3px solid #c8a84b;
    padding: 1.2rem 2rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
    border-radius: 0 0 12px 12px;
}
.header-title {
    font-family: 'Rajdhani', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 2px;
    margin: 0;
    line-height: 1.1;
}
.header-sub {
    font-family: 'Noto Serif Malayalam', serif;
    font-size: 0.85rem;
    color: #c8a84b;
    margin: 0;
}
.badge {
    background: #c8a84b;
    color: #0a0e1a;
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    font-size: 2.5rem;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    border: 3px solid #fff;
    box-shadow: 0 0 20px rgba(200,168,75,0.4);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1f33 0%, #091526 100%) !important;
    border-right: 2px solid #1e3a5c !important;
}
section[data-testid="stSidebar"] * {
    color: #cdd8e6 !important;
}
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stRadio label {
    color: #8aaccc !important;
    font-size: 0.8rem !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
}

/* Cards */
.info-card {
    background: rgba(13, 33, 55, 0.85);
    border: 1px solid #1e3a5c;
    border-left: 4px solid #c8a84b;
    border-radius: 8px;
    padding: 1rem 1.2rem;
    margin-bottom: 1rem;
}
.info-card h4 {
    color: #c8a84b;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin: 0 0 0.3rem 0;
}
.info-card p {
    color: #9ab3cc;
    font-size: 0.85rem;
    margin: 0;
    line-height: 1.5;
}

/* Chat container */
.chat-area {
    background: rgba(8, 18, 30, 0.7);
    border: 1px solid #1e3a5c;
    border-radius: 12px;
    padding: 1.5rem;
    min-height: 400px;
    max-height: 520px;
    overflow-y: auto;
}

/* Message bubbles */
.msg-user {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 1rem;
}
.msg-user .bubble {
    background: linear-gradient(135deg, #1a4a8a 0%, #0f3060 100%);
    border: 1px solid #2a6abf;
    color: #e8f0ff;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 4px 18px;
    max-width: 72%;
    font-size: 0.9rem;
    line-height: 1.55;
    box-shadow: 0 2px 12px rgba(26,74,138,0.3);
}
.msg-bot {
    display: flex;
    justify-content: flex-start;
    margin-bottom: 1rem;
    gap: 0.7rem;
}
.bot-avatar {
    background: #c8a84b;
    color: #0a0e1a;
    font-weight: 700;
    font-size: 0.75rem;
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    font-family: 'Rajdhani', sans-serif;
}
.msg-bot .bubble {
    background: rgba(20, 40, 65, 0.95);
    border: 1px solid #2a4a6a;
    color: #d0e4f7;
    padding: 0.75rem 1.1rem;
    border-radius: 18px 18px 18px 4px;
    max-width: 75%;
    font-size: 0.9rem;
    line-height: 1.6;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
}

/* FIR Preview */
.fir-preview {
    background: #fafaf5;
    border: 2px solid #c8a84b;
    border-radius: 8px;
    padding: 1.5rem;
    color: #1a1a1a;
    font-family: 'Times New Roman', serif;
}
.fir-preview h2 { text-align: center; color: #0a0e1a; font-size: 1.2rem; margin: 0 0 0.2rem; }
.fir-preview h3 { text-align: center; color: #1a3a5c; font-size: 1rem; margin: 0 0 1rem; }
.fir-preview .field { margin-bottom: 0.6rem; font-size: 0.88rem; }
.fir-preview .field strong { color: #1a3a5c; }
.fir-preview .divider { border-top: 1px solid #ccc; margin: 0.8rem 0; }

/* Section headers */
.section-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #c8a84b;
    margin-bottom: 0.5rem;
}

/* Button overrides */
.stButton > button {
    background: linear-gradient(135deg, #c8a84b 0%, #a8882a 100%) !important;
    color: #0a0e1a !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    letter-spacing: 1.5px !important;
    border: none !important;
    border-radius: 6px !important;
    padding: 0.5rem 1.5rem !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #ddb85a 0%, #c8a84b 100%) !important;
    box-shadow: 0 4px 16px rgba(200,168,75,0.35) !important;
    transform: translateY(-1px) !important;
}

/* Input fields */
.stTextArea textarea, .stTextInput input {
    background: rgba(13, 33, 55, 0.9) !important;
    border: 1px solid #2a4a6a !important;
    color: #d0e4f7 !important;
    border-radius: 6px !important;
    font-family: 'Source Sans 3', sans-serif !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #c8a84b !important;
    box-shadow: 0 0 0 2px rgba(200,168,75,0.2) !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: rgba(13, 33, 55, 0.9) !important;
    border: 1px solid #2a4a6a !important;
    color: #d0e4f7 !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: rgba(10,14,26,0.5); }
::-webkit-scrollbar-thumb { background: #2a4a6a; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #c8a84b; }

/* Download button */
.stDownloadButton > button {
    background: linear-gradient(135deg, #1a4a8a 0%, #0f3060 100%) !important;
    color: #ffffff !important;
    border: 1px solid #2a6abf !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
}
.stDownloadButton > button:hover {
    background: linear-gradient(135deg, #2a5a9a 0%, #1a4070 100%) !important;
    box-shadow: 0 4px 16px rgba(26,74,138,0.4) !important;
    transform: translateY(-1px) !important;
}

/* Status chip */
.status-chip {
    display: inline-block;
    background: rgba(200,168,75,0.15);
    border: 1px solid rgba(200,168,75,0.4);
    color: #c8a84b;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 0.15rem 0.6rem;
    border-radius: 20px;
    margin-left: 0.5rem;
}

/* Hide Streamlit branding */
#MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── State ──────────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "fir_data" not in st.session_state:
    st.session_state.fir_data = {}
if "fir_ready" not in st.session_state:
    st.session_state.fir_ready = False
if "language" not in st.session_state:
    st.session_state.language = "English"
if "user_type" not in st.session_state:
    st.session_state.user_type = "Citizen"

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:1rem 0 0.5rem;'>
        <div style='font-family:Rajdhani,sans-serif; font-size:1.3rem; font-weight:700;
                    color:#c8a84b; letter-spacing:3px;'>⚖️ FIR ASSIST</div>
        <div style='font-size:0.72rem; color:#5a7a9a; letter-spacing:1px; margin-top:0.2rem;'>
            KERALA POLICE SYSTEM
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown('<div class="section-label">🔑 Gemini API Key</div>', unsafe_allow_html=True)
    api_key_input = st.text_input(
        "",
        type="password",
        placeholder="Enter your Gemini API key...",
        label_visibility="collapsed",
        key="gemini_api_key_input",
    )
    if api_key_input:
        st.session_state["gemini_api_key"] = api_key_input
        st.markdown('<div style="color:#22c55e; font-size:0.75rem; margin-top:0.2rem;">✅ Key saved for this session</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="color:#8aaccc; font-size:0.72rem; margin-top:0.2rem;">'
            'Or set <code>GEMINI_API_KEY</code> as env variable / Streamlit secret</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown('<div class="section-label">Interface Language</div>', unsafe_allow_html=True)
    lang = st.radio("", ["English", "Malayalam / മലയാളം"], index=0, label_visibility="collapsed")
    st.session_state.language = "Malayalam" if "Malayalam" in lang else "English"

    st.markdown('<div class="section-label" style="margin-top:1rem;">User Role</div>', unsafe_allow_html=True)
    user_type = st.selectbox("", ["Citizen", "Police Officer"], label_visibility="collapsed")
    st.session_state.user_type = user_type

    st.divider()

    st.markdown("""
    <div class="info-card">
        <h4>📋 Supported Cases</h4>
        <p>
        • Theft / Petty theft<br>
        • Vehicle theft / Missing<br>
        • Chain snatching<br>
        • Burglary / House break-in<br>
        • Mobile / Wallet lost<br>
        • Property damage<br>
        • Trespassing<br>
        • Eve-teasing / Harassment
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.fir_ready:
        st.markdown("""
        <div class="info-card" style="border-left-color:#22c55e;">
            <h4>✅ FIR Status</h4>
            <p>Draft ready — scroll down to preview & download</p>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🔄 New FIR", use_container_width=True):
        st.session_state.messages = []
        st.session_state.fir_data = {}
        st.session_state.fir_ready = False
        st.rerun()

# ── Header ─────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-banner">
    <div class="badge">🚔</div>
    <div>
        <p class="header-title">FIR DRAFTING ASSISTANT</p>
        <p class="header-sub">Kerala Police — ഒന്നാം വിവര റിപ്പോർട്ട് സഹായി</p>
    </div>
    <div style="margin-left:auto; text-align:right;">
        <div style="font-family:Rajdhani,sans-serif; font-size:0.75rem; color:#8aaccc; letter-spacing:1px;">
            SECURED SYSTEM
        </div>
        <div style="font-family:Rajdhani,sans-serif; font-size:1rem; font-weight:700; color:#c8a84b;">
            KERALA STATE POLICE
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Layout ─────────────────────────────────────────────────────────────────
col_chat, col_preview = st.columns([1.1, 0.9], gap="large")

# ── SYSTEM PROMPT ───────────────────────────────────────────────────────────
def build_system_prompt():
    lang = st.session_state.language
    role = st.session_state.user_type
    lang_instruction = (
        "Respond ONLY in Malayalam (മലയാളം). Use simple, clear Malayalam throughout."
        if lang == "Malayalam"
        else "Respond in clear English."
    )
    role_context = (
        "The user is a police officer. They may provide technical details. Use official police terminology."
        if role == "Police Officer"
        else "The user is a citizen/complainant. Use simple, empathetic language. Guide them step by step."
    )
    return f"""You are an official FIR (First Information Report) Drafting Assistant for Kerala Police.

{lang_instruction}
{role_context}

Your job: Conversationally collect all required information and draft a formal FIR.

SUPPORTED CASE TYPES ONLY:
- Theft (regular, petty, chain snatching)
- Vehicle theft / Missing vehicle
- Burglary / House break-in
- Lost items (mobile phone, wallet, documents)
- Property damage / vandalism
- Trespassing
- Eve-teasing / Public harassment

WORKFLOW:
1. Greet the user warmly. Ask what happened briefly.
2. Identify the case type from their description.
3. Collect info via friendly questions (one or two at a time):
   - Complainant full name
   - Age and gender
   - Address
   - Phone number
   - Date and time of incident
   - Place/location of incident
   - Detailed description of what happened
   - Items stolen or damaged (with values if applicable)
   - Suspect description (if any)
   - Witnesses (if any)
   - Any evidence or CCTV available
4. Once you have all info, tell the user you have enough to draft the FIR and ask for confirmation.
5. When confirmed, output ONLY a valid JSON block (no markdown fences, no extra text) in this exact format:

{{"fir_number": "auto", "date_of_filing": "auto", "police_station": "Complainant's local station", "district": "Kerala", "case_type": "...", "ipc_sections": "...", "complainant_name": "...", "complainant_age": "...", "complainant_gender": "...", "complainant_address": "...", "complainant_phone": "...", "incident_date": "...", "incident_time": "...", "incident_location": "...", "incident_description": "...", "items_lost": "...", "suspect_description": "...", "witnesses": "...", "evidence": "...", "officer_name": "..."}}

IPC sections to use:
- Theft → 379 IPC
- Burglary → 457 IPC
- Chain snatching → 379A IPC
- Damage to property → 427 IPC
- Trespassing → 447 IPC
- Eve-teasing → 354A IPC
- Lost vehicle → 379 IPC
- Lost documents/mobile → File as lost property report

IMPORTANT: Do not handle violent crimes, murder, fraud, cybercrime — politely redirect those to the nearest police station.
"""

# ── Gemini API setup ────────────────────────────────────────────────────────
def get_gemini_key() -> str:
    # 1. Streamlit secrets (recommended for deployment)
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    # 2. Environment variable
    key = os.environ.get("GEMINI_API_KEY", "")
    if key:
        return key
    # 3. Sidebar manual input (fallback)
    return st.session_state.get("gemini_api_key", "")

# ── Gemini API call ──────────────────────────────────────────────────────────
def chat_with_gemini(user_input: str) -> str:
    api_key = get_gemini_key()
    if not api_key:
        return "⚠️ Gemini API key not found. Please enter your API key in the sidebar."

    genai.configure(api_key=api_key)

    # Build Gemini chat history (role must be user or model)
    history = []
    for m in st.session_state.messages:
        role = "model" if m["role"] == "assistant" else "user"
        history.append({"role": role, "parts": [m["content"]]})

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=build_system_prompt(),
    )
    chat = model.start_chat(history=history)
    response = chat.send_message(user_input)
    return response.text

# ── Extract JSON from response ──────────────────────────────────────────────
def extract_fir_json(text: str):
    import re
    match = re.search(r'\{[\s\S]+\}', text)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            return None
    return None

# ── PDF Generation ──────────────────────────────────────────────────────────
def generate_fir_pdf(fir: dict) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=55, leftMargin=55,
        topMargin=60, bottomMargin=55,
    )

    styles = getSampleStyleSheet()
    gold = colors.HexColor("#8B6914")
    navy = colors.HexColor("#0a1628")
    dark = colors.HexColor("#1a1a2e")

    title_style = ParagraphStyle("Title", fontName="Helvetica-Bold", fontSize=14,
                                  alignment=TA_CENTER, textColor=navy, spaceAfter=2)
    sub_style = ParagraphStyle("Sub", fontName="Helvetica", fontSize=10,
                                alignment=TA_CENTER, textColor=colors.HexColor("#3a3a6a"), spaceAfter=2)
    heading_style = ParagraphStyle("Heading", fontName="Helvetica-Bold", fontSize=10,
                                    textColor=gold, spaceAfter=4, spaceBefore=8,
                                    leading=14)
    body_style = ParagraphStyle("Body", fontName="Helvetica", fontSize=9.5,
                                 textColor=dark, spaceAfter=3, leading=14)
    label_style = ParagraphStyle("Label", fontName="Helvetica-Bold", fontSize=9.5,
                                  textColor=colors.HexColor("#2a3a6a"), spaceAfter=2)

    story = []
    now = datetime.now()
    fir_num = f"FIR/{now.strftime('%Y')}/{now.strftime('%m%d%H%M')}"

    # ── Header ──
    story.append(Paragraph("KERALA POLICE", title_style))
    story.append(Paragraph("FIRST INFORMATION REPORT (FIR)", title_style))
    story.append(Paragraph("Under Section 154 Cr.P.C.", sub_style))
    story.append(HRFlowable(width="100%", thickness=2, color=gold, spaceAfter=8))

    # ── FIR Meta Table ──
    meta_data = [
        ["FIR Number:", fir_num, "Date of Filing:", now.strftime("%d/%m/%Y")],
        ["Police Station:", fir.get("police_station", "—"), "Time:", now.strftime("%I:%M %p")],
        ["District:", fir.get("district", "Kerala"), "State:", "Kerala"],
    ]
    meta_table = Table(meta_data, colWidths=[1.2*inch, 2.1*inch, 1.2*inch, 1.5*inch])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#2a3a6a")),
        ("TEXTCOLOR", (2,0), (2,-1), colors.HexColor("#2a3a6a")),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor("#f0f4ff"), colors.white]),
        ("BOX", (0,0), (-1,-1), 0.8, gold),
        ("INNERGRID", (0,0), (-1,-1), 0.3, colors.lightgrey),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # ── Case Info ──
    story.append(HRFlowable(width="100%", thickness=0.5, color=gold, spaceAfter=4))
    story.append(Paragraph("CASE INFORMATION", heading_style))

    case_rows = [
        ["Case Type:", fir.get("case_type", "—")],
        ["IPC Sections:", fir.get("ipc_sections", "—")],
    ]
    case_table = Table(case_rows, colWidths=[1.8*inch, 4.2*inch])
    case_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (1,0), (1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 9.5),
        ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#2a3a6a")),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor("#fffbf0"), colors.white]),
        ("BOX", (0,0), (-1,-1), 0.5, colors.lightgrey),
        ("INNERGRID", (0,0), (-1,-1), 0.3, colors.HexColor("#e8e8e8")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(case_table)
    story.append(Spacer(1, 8))

    # ── Complainant ──
    story.append(HRFlowable(width="100%", thickness=0.5, color=gold, spaceAfter=4))
    story.append(Paragraph("COMPLAINANT DETAILS", heading_style))

    comp_rows = [
        ["Name:", fir.get("complainant_name", "—"), "Age:", fir.get("complainant_age", "—")],
        ["Gender:", fir.get("complainant_gender", "—"), "Phone:", fir.get("complainant_phone", "—")],
        ["Address:", fir.get("complainant_address", "—"), "", ""],
    ]
    comp_table = Table(comp_rows, colWidths=[1.2*inch, 2.2*inch, 0.8*inch, 1.8*inch])
    comp_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTNAME", (1,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 9.5),
        ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#2a3a6a")),
        ("TEXTCOLOR", (2,0), (2,-1), colors.HexColor("#2a3a6a")),
        ("SPAN", (1,2), (3,2)),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor("#f0f8ff"), colors.white, colors.HexColor("#f0f8ff")]),
        ("BOX", (0,0), (-1,-1), 0.5, colors.lightgrey),
        ("INNERGRID", (0,0), (-1,-1), 0.3, colors.HexColor("#e8e8e8")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 8))

    # ── Incident Details ──
    story.append(HRFlowable(width="100%", thickness=0.5, color=gold, spaceAfter=4))
    story.append(Paragraph("INCIDENT DETAILS", heading_style))

    inc_meta = [
        ["Date of Incident:", fir.get("incident_date", "—"), "Time:", fir.get("incident_time", "—")],
        ["Location:", fir.get("incident_location", "—"), "", ""],
    ]
    inc_table = Table(inc_meta, colWidths=[1.5*inch, 2.2*inch, 0.8*inch, 1.5*inch])
    inc_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
        ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
        ("FONTNAME", (1,0), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 9.5),
        ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#2a3a6a")),
        ("TEXTCOLOR", (2,0), (2,-1), colors.HexColor("#2a3a6a")),
        ("SPAN", (1,1), (3,1)),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor("#fff8f0"), colors.white]),
        ("BOX", (0,0), (-1,-1), 0.5, colors.lightgrey),
        ("INNERGRID", (0,0), (-1,-1), 0.3, colors.HexColor("#e8e8e8")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(inc_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph("Description of Incident:", label_style))
    story.append(Paragraph(fir.get("incident_description", "—"), body_style))
    story.append(Spacer(1, 6))

    if fir.get("items_lost") and fir.get("items_lost") != "—":
        story.append(Paragraph("Items Lost / Stolen:", label_style))
        story.append(Paragraph(fir.get("items_lost"), body_style))
        story.append(Spacer(1, 4))

    if fir.get("suspect_description") and fir.get("suspect_description") not in ["—", "None", "Unknown"]:
        story.append(Paragraph("Suspect Description:", label_style))
        story.append(Paragraph(fir.get("suspect_description"), body_style))
        story.append(Spacer(1, 4))

    if fir.get("witnesses") and fir.get("witnesses") not in ["—", "None", "No witnesses"]:
        story.append(Paragraph("Witnesses:", label_style))
        story.append(Paragraph(fir.get("witnesses"), body_style))
        story.append(Spacer(1, 4))

    if fir.get("evidence") and fir.get("evidence") not in ["—", "None"]:
        story.append(Paragraph("Evidence / CCTV:", label_style))
        story.append(Paragraph(fir.get("evidence"), body_style))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=1, color=gold, spaceAfter=10))

    # ── Signatures ──
    sig_data = [
        ["Complainant's Signature", "Receiving Officer's Signature"],
        ["\n\n________________________", "\n\n________________________"],
        [fir.get("complainant_name", "Complainant"),
         fir.get("officer_name", "Officer-in-Charge")],
        ["Date: " + now.strftime("%d/%m/%Y"), "Date: " + now.strftime("%d/%m/%Y")],
    ]
    sig_table = Table(sig_data, colWidths=[3*inch, 3*inch])
    sig_table.setStyle(TableStyle([
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME", (0,2), (-1,-1), "Helvetica"),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#2a3a6a")),
        ("TOPPADDING", (0,0), (-1,-1), 3),
        ("BOTTOMPADDING", (0,0), (-1,-1), 3),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 12))

    story.append(Paragraph(
        "This is a computer-generated FIR draft. It must be verified, signed, and stamped by an authorized police officer to be legally valid.",
        ParagraphStyle("Footer", fontName="Helvetica", fontSize=7.5, alignment=TA_CENTER,
                        textColor=colors.grey, leading=11)
    ))

    doc.build(story)
    return buffer.getvalue()

# ── Chat Column ─────────────────────────────────────────────────────────────
with col_chat:
    st.markdown(f"""
    <div style="display:flex; align-items:center; margin-bottom:1rem;">
        <div class="section-label" style="margin:0;">Chat Interface</div>
        <span class="status-chip">
            {'🟡 MALAYALAM' if st.session_state.language == 'Malayalam' else '🟢 ENGLISH'}
        </span>
        <span class="status-chip" style="background:rgba(26,74,138,0.2); border-color:rgba(26,74,138,0.5); color:#5a9af0;">
            {'🚔 OFFICER' if st.session_state.user_type == 'Police Officer' else '👤 CITIZEN'}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Display messages
    chat_html = '<div class="chat-area" id="chat-scroll">'

    if not st.session_state.messages:
        if st.session_state.language == "Malayalam":
            welcome = "നമസ്കാരം! ഞാൻ Kerala Police FIR Drafting Assistant ആണ്. നിങ്ങൾക്ക് FIR ഫയൽ ചെയ്യാൻ സഹായിക്കാൻ ഞാൻ ഇവിടെ ഉണ്ട്. എന്ത് പ്രശ്നം ഉണ്ടായി? ദയവായി വിശദമായി പറയൂ."
        else:
            welcome = "Welcome to the Kerala Police FIR Drafting Assistant. I'm here to help you file a First Information Report. Please tell me — what happened? Describe the incident briefly and I'll guide you through the process."
        chat_html += f'''
        <div class="msg-bot">
            <div class="bot-avatar">FIR</div>
            <div class="bubble">{welcome}</div>
        </div>'''

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            chat_html += f'<div class="msg-user"><div class="bubble">{msg["content"]}</div></div>'
        else:
            display_text = msg["content"]
            if extract_fir_json(display_text):
                display_text = "✅ FIR draft is ready! Please review it on the right and download the PDF."
            chat_html += f'''
            <div class="msg-bot">
                <div class="bot-avatar">FIR</div>
                <div class="bubble">{display_text}</div>
            </div>'''

    chat_html += '</div>'
    st.markdown(chat_html, unsafe_allow_html=True)

    # Auto-scroll JS
    st.markdown("""
    <script>
    const el = document.getElementById('chat-scroll');
    if(el) el.scrollTop = el.scrollHeight;
    </script>
    """, unsafe_allow_html=True)

    # Input area
    st.markdown('<div class="section-label" style="margin-top:1rem;">Your Message</div>', unsafe_allow_html=True)
    placeholder_text = (
        "ഇവിടെ ടൈപ്പ് ചെയ്യൂ..." if st.session_state.language == "Malayalam"
        else "Type your message here..."
    )
    user_input = st.text_area("", placeholder=placeholder_text, height=90, label_visibility="collapsed", key="user_input")

    send_col, _ = st.columns([1, 3])
    with send_col:
        send_btn = st.button("▶ SEND", use_container_width=True)

    if send_btn and user_input.strip():
        with st.spinner("Drafting response..."):
            response = chat_with_gemini(user_input.strip())
            st.session_state.messages.append({"role": "user", "content": user_input.strip()})
            st.session_state.messages.append({"role": "assistant", "content": response})

            fir_json = extract_fir_json(response)
            if fir_json:
                st.session_state.fir_data = fir_json
                st.session_state.fir_ready = True
        st.rerun()

# ── Preview Column ────────────────────────────────────────────────────────────
with col_preview:
    st.markdown('<div class="section-label">FIR Preview & Download</div>', unsafe_allow_html=True)

    if st.session_state.fir_ready and st.session_state.fir_data:
        fir = st.session_state.fir_data
        now = datetime.now()
        fir_num = f"FIR/{now.strftime('%Y')}/{now.strftime('%m%d%H%M')}"

        preview_html = f"""
        <div class="fir-preview">
            <h2>KERALA POLICE</h2>
            <h3>FIRST INFORMATION REPORT (FIR)</h3>
            <div class="divider"></div>
            <div class="field"><strong>FIR No.:</strong> {fir_num} &nbsp;|&nbsp; <strong>Date:</strong> {now.strftime('%d/%m/%Y')}</div>
            <div class="field"><strong>Police Station:</strong> {fir.get('police_station','—')}, {fir.get('district','Kerala')}</div>
            <div class="divider"></div>
            <div class="field"><strong>Case Type:</strong> {fir.get('case_type','—')}</div>
            <div class="field"><strong>IPC Sections:</strong> {fir.get('ipc_sections','—')}</div>
            <div class="divider"></div>
            <div class="field"><strong>Complainant:</strong> {fir.get('complainant_name','—')}</div>
            <div class="field"><strong>Age / Gender:</strong> {fir.get('complainant_age','—')} / {fir.get('complainant_gender','—')}</div>
            <div class="field"><strong>Address:</strong> {fir.get('complainant_address','—')}</div>
            <div class="field"><strong>Phone:</strong> {fir.get('complainant_phone','—')}</div>
            <div class="divider"></div>
            <div class="field"><strong>Incident Date:</strong> {fir.get('incident_date','—')} at {fir.get('incident_time','—')}</div>
            <div class="field"><strong>Location:</strong> {fir.get('incident_location','—')}</div>
            <div class="field" style="margin-top:0.5rem;"><strong>Description:</strong><br>{fir.get('incident_description','—')}</div>
            {'<div class="field"><strong>Items Lost:</strong> ' + fir.get('items_lost','') + '</div>' if fir.get('items_lost') and fir.get('items_lost') not in ['—','None'] else ''}
            {'<div class="field"><strong>Suspect:</strong> ' + fir.get('suspect_description','') + '</div>' if fir.get('suspect_description') and fir.get('suspect_description') not in ['—','None','Unknown'] else ''}
            <div class="divider"></div>
            <div class="field" style="font-size:0.78rem; color:#666; font-style:italic;">
                ⚠️ Draft only — must be signed and stamped by an authorized officer to be legally valid.
            </div>
        </div>
        """
        st.markdown(preview_html, unsafe_allow_html=True)

        st.markdown('<div style="margin-top:1rem;"></div>', unsafe_allow_html=True)
        pdf_bytes = generate_fir_pdf(fir)
        st.download_button(
            label="⬇  DOWNLOAD FIR AS PDF",
            data=pdf_bytes,
            file_name=f"FIR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.markdown("""
        <div style="
            background: rgba(13,33,55,0.6);
            border: 1px dashed #2a4a6a;
            border-radius: 12px;
            padding: 3rem 2rem;
            text-align: center;
            min-height: 400px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        ">
            <div style="font-size:3rem; margin-bottom:1rem;">📄</div>
            <div style="font-family:Rajdhani,sans-serif; font-size:1.1rem; font-weight:700;
                        color:#c8a84b; letter-spacing:2px; margin-bottom:0.5rem;">FIR PREVIEW</div>
            <div style="color:#5a7a9a; font-size:0.85rem; max-width:240px; line-height:1.6;">
                Your FIR draft will appear here once the chatbot collects all necessary information.
            </div>
            <div style="margin-top:2rem; display:flex; flex-direction:column; gap:0.5rem; text-align:left; max-width:260px;">
                <div style="color:#4a6a8a; font-size:0.78rem;">
                    <span style="color:#c8a84b;">◉</span> &nbsp;Describe your case in the chat
                </div>
                <div style="color:#4a6a8a; font-size:0.78rem;">
                    <span style="color:#c8a84b;">◉</span> &nbsp;Answer the assistant's questions
                </div>
                <div style="color:#4a6a8a; font-size:0.78rem;">
                    <span style="color:#c8a84b;">◉</span> &nbsp;Confirm to generate FIR
                </div>
                <div style="color:#4a6a8a; font-size:0.78rem;">
                    <span style="color:#c8a84b;">◉</span> &nbsp;Download as PDF
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Footer ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:2rem 0 1rem; border-top:1px solid #1e3a5c; margin-top:2rem;">
    <div style="font-family:Rajdhani,sans-serif; font-size:0.72rem; color:#3a5a7a; letter-spacing:2px;">
        KERALA STATE POLICE &nbsp;|&nbsp; FIR ASSIST SYSTEM &nbsp;|&nbsp; FOR OFFICIAL USE
    </div>
    <div style="font-size:0.68rem; color:#2a3a4a; margin-top:0.3rem;">
        Emergency: 100 &nbsp;|&nbsp; Women Helpline: 1091 &nbsp;|&nbsp; Kerala Police: 0471-2721547
    </div>
</div>
""", unsafe_allow_html=True)

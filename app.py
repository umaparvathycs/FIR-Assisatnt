import streamlit as st
import requests
import json
import re
import random
from datetime import datetime
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kerala Police FIR Assistant",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Malayalam:wght@400;600&display=swap');

html, body, [class*="css"] { font-family: 'Noto Sans Malayalam', sans-serif; }

.header-banner {
    background: linear-gradient(135deg, #0d1f3c 0%, #1a3a6b 60%, #2a5298 100%);
    color: white;
    padding: 24px 32px 16px;
    border-radius: 12px;
    margin-bottom: 8px;
}
.gold-bar {
    height: 4px;
    background: linear-gradient(90deg, transparent, #c8a227, #e8c547, #c8a227, transparent);
    border-radius: 2px;
    margin-bottom: 20px;
}
.chat-user {
    background: #1a3a6b;
    color: white;
    padding: 10px 14px;
    border-radius: 16px 16px 4px 16px;
    margin: 6px 0;
    margin-left: 20%;
    font-size: 14px;
    line-height: 1.5;
}
.chat-ai {
    background: #f0f4fa;
    color: #111;
    padding: 10px 14px;
    border-radius: 16px 16px 16px 4px;
    margin: 6px 0;
    margin-right: 20%;
    font-size: 14px;
    line-height: 1.5;
    border: 1px solid #d0dae8;
}
.fir-ready-badge {
    background: #22753b;
    color: white;
    padding: 3px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
}
.info-box {
    background: #fff8e1;
    border: 1px solid #f0c040;
    border-radius: 8px;
    padding: 12px 14px;
    font-size: 13px;
    color: #7a5a00;
    margin-top: 10px;
}
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert Kerala Police FIR (First Information Report) assistant.
You help both citizens and police officers draft accurate FIRs in English and Malayalam.

RULES:
1. Detect the user's language (English or Malayalam) and respond in that same language.
2. Only handle minor cases: theft, petty theft, pickpocketing, mobile/phone theft, vehicle theft,
   lost property, minor assault, trespassing, vandalism, mischief, cheating/fraud (small scale),
   harassment, missing persons (initial report).
3. For serious crimes (murder, rape, terrorism, kidnapping), politely refuse and redirect to
   the nearest police station.
4. Gather these FIR fields through natural conversation:
   complainant_name, complainant_age, complainant_address, complainant_phone,
   incident_date, incident_time, incident_location, case_type,
   incident_description, accused_description, witnesses,
   property_details, estimated_value, ipc_sections.
5. When you have ENOUGH information to draft a FIR, output ONLY this JSON block (no extra text before/after):
   |||JSON_START|||
   {
     "fir_ready": true,
     "fields": {
       "complainant_name": "",
       "complainant_age": "",
       "complainant_address": "",
       "complainant_phone": "",
       "incident_date": "",
       "incident_time": "",
       "incident_location": "",
       "case_type": "",
       "incident_description": "",
       "accused_description": "",
       "witnesses": "",
       "property_details": "",
       "estimated_value": "",
       "ipc_sections": ""
     },
     "message": "Your friendly response telling the user the FIR is ready"
   }
   |||JSON_END|||
6. If you still need more details, respond conversationally (no JSON).
7. IPC sections reference:
   Theft → Section 379 IPC
   Robbery → Section 392 IPC
   Vehicle theft → Section 379 IPC
   Cheating → Section 420 IPC
   Trespassing → Section 447 IPC
   Assault → Section 323/324 IPC
   Mischief → Section 426/427 IPC
   Harassment → Section 354/509 IPC
   Lost property → No IPC (civil complaint)
8. Be empathetic, professional, and clear."""

TRANSLATIONS = {
    "en": {
        "title": "Kerala Police FIR Assistant",
        "subtitle": "AI-Powered First Information Report Generator",
        "tagline": "For Citizens & Police Officers | English & Malayalam",
        "role_label": "I am a:",
        "citizen": "Citizen / Complainant",
        "officer": "Police Officer",
        "placeholder": "Describe your complaint in English or Malayalam...",
        "send": "Send",
        "new_fir": "New FIR",
        "download": "Download FIR (PDF)",
        "fir_preview": "FIR Preview",
        "how_to": "How to use",
        "supported": "Supported Cases",
        "warning": "⚠️ This tool generates draft FIRs. Always submit through official police channels.",
        "welcome": "Welcome! Please describe your complaint and I will help you draft an FIR. You can type in English or Malayalam.",
    },
    "ml": {
        "title": "കേരള പോലീസ് FIR സഹായി",
        "subtitle": "AI ഉപയോഗിച്ച് FIR തയ്യാറാക്കൽ",
        "tagline": "പൗരന്മാർക്കും പോലീസ് ഓഫീസർക്കും | ഇംഗ്ലീഷ്, മലയാളം",
        "role_label": "ഞാൻ ഒരു:",
        "citizen": "പൗരൻ / പരാതിക്കാരൻ",
        "officer": "പോലീസ് ഓഫീസർ",
        "placeholder": "നിങ്ങളുടെ പരാതി ഇംഗ്ലീഷിലോ മലയാളത്തിലോ വിവരിക്കുക...",
        "send": "അയക്കുക",
        "new_fir": "പുതിയ FIR",
        "download": "FIR ഡൗൺലോഡ് (PDF)",
        "fir_preview": "FIR പ്രിവ്യൂ",
        "how_to": "ഉപയോഗ നിർദ്ദേശം",
        "supported": "കേസ് തരങ്ങൾ",
        "warning": "⚠️ ഇത് ഒരു ഡ്രാഫ്റ്റ് FIR ആണ്. ഔദ്യോഗിക ചാനലുകൾ വഴി സമർപ്പിക്കുക.",
        "welcome": "സ്വാഗതം! നിങ്ങളുടെ പരാതി വിവരിക്കൂ, FIR തയ്യാറാക്കാൻ ഞാൻ സഹായിക്കാം.",
    }
}

CASE_TYPES = [
    "Theft / മോഷണം",
    "Vehicle Theft / വാഹന മോഷണം",
    "Mobile Theft / ഫോൺ മോഷണം",
    "Cheating / ചതി",
    "Trespassing / കടന്നുകയറ്റം",
    "Minor Assault / ആക്രമണം",
    "Vandalism / നാശം",
    "Harassment / ഉപദ്രവം",
    "Lost Property / നഷ്ടപ്പെട്ട വസ്തു",
]

QUICK_PROMPTS_EN = [
    "My phone was stolen from my bag",
    "Someone stole my bike",
    "I was cheated of money",
    "My wallet was pickpocketed",
]
QUICK_PROMPTS_ML = [
    "എന്റെ ഫോൺ ബാഗിൽ നിന്ന് മോഷ്ടിക്കപ്പെട്ടു",
    "എന്റെ ബൈക്ക് മോഷ്ടിക്കപ്പെട്ടു",
    "എന്നെ പണം തട്ടിപ്പ് ചെയ്തു",
]

# ── Session state ─────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "messages": [],          # display messages {"role","content"}
        "history": [],            # API history
        "fir_data": None,
        "lang": "en",
        "role": "citizen",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Helpers ───────────────────────────────────────────────────────────────────
def gen_fir_no():
    now = datetime.now()
    return f"KL-{now.year}/{now.month:02d}/{random.randint(1000,9999)}"

def call_claude(history, role, lang):
    import os
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        api_key = "AIzaSyCj7FQWH1369QGdZvhAGyhi4Tx5yjYaAi4"
        st.stop()

    system = SYSTEM_PROMPT + f"\n\nUser role: {'Police Officer' if role == 'officer' else 'Citizen/Complainant'}. Interface language: {lang}."

    # Build contents for Gemini REST API
    contents = []
    # Add system as first user message
    for msg in history:
        contents.append({
            "role": "user" if msg["role"] == "user" else "model",
            "parts": [{"text": msg["content"]}]
        })

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": contents,
        "generationConfig": {"maxOutputTokens": 1000}
    }
    resp = requests.post(url, json=payload, timeout=30)
    if resp.status_code != 200:
        st.error(f"❌ Gemini API error {resp.status_code}: Check your API key in Secrets.")
        st.stop()
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]

def parse_response(raw):
    if "|||JSON_START|||" in raw:
        m = re.search(r"\|\|\|JSON_START\|\|\|([\s\S]*?)\|\|\|JSON_END\|\|\|", raw)
        if m:
            try:
                data = json.loads(m.group(1).strip())
                if data.get("fir_ready"):
                    return data.get("message", "Your FIR is ready!"), data
            except Exception:
                pass
    return raw, None

def reset():
    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.fir_data = None

# ── PDF Generator ─────────────────────────────────────────────────────────────
def generate_pdf(fir_data) -> bytes:
    buf = BytesIO()
    f = fir_data["fields"]
    fir_no = gen_fir_no()
    now = datetime.now()

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )

    navy = colors.HexColor("#1a3a6b")
    gold = colors.HexColor("#c8a227")
    light_blue = colors.HexColor("#e8f0fb")
    red = colors.HexColor("#cc0000")

    styles = getSampleStyleSheet()
    center_bold = ParagraphStyle("cb", parent=styles["Normal"],
        alignment=TA_CENTER, fontName="Helvetica-Bold")
    center_small = ParagraphStyle("cs", parent=styles["Normal"],
        alignment=TA_CENTER, fontSize=9, textColor=colors.HexColor("#555"))
    field_label = ParagraphStyle("fl", parent=styles["Normal"],
        fontSize=8, textColor=colors.HexColor("#666"),
        fontName="Helvetica-Bold", spaceAfter=1)
    field_value = ParagraphStyle("fv", parent=styles["Normal"],
        fontSize=11, spaceAfter=4)
    section_head = ParagraphStyle("sh", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=10,
        textColor=navy, spaceBefore=8, spaceAfter=4)
    desc_style = ParagraphStyle("ds", parent=styles["Normal"],
        fontSize=11, leading=16, alignment=TA_JUSTIFY)

    story = []

    # Header
    story.append(Paragraph("KERALA POLICE DEPARTMENT", ParagraphStyle(
        "hdr", parent=styles["Normal"], alignment=TA_CENTER,
        fontName="Helvetica-Bold", fontSize=15, textColor=navy)))
    story.append(Paragraph("കേരള പോലീസ് വകുപ്പ്", ParagraphStyle(
        "hdr2", parent=styles["Normal"], alignment=TA_CENTER,
        fontSize=10, textColor=colors.HexColor("#555"))))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=3, color=navy))
    story.append(HRFlowable(width="100%", thickness=1, color=gold, spaceAfter=4))
    story.append(Paragraph("FIRST INFORMATION REPORT", ParagraphStyle(
        "fir", parent=styles["Normal"], alignment=TA_CENTER,
        fontName="Helvetica-Bold", fontSize=18, textColor=red)))
    story.append(Paragraph("ഒന്നാം വിവര റിപ്പോർട്ട്", ParagraphStyle(
        "fir2", parent=styles["Normal"], alignment=TA_CENTER,
        fontSize=10, textColor=colors.HexColor("#888"), spaceAfter=6)))
    story.append(HRFlowable(width="100%", thickness=1, color=gold, spaceAfter=6))

    # FIR meta row
    meta_data = [
        [Paragraph(f"<b>FIR No:</b> {fir_no}", styles["Normal"]),
         Paragraph(f"<b>Date:</b> {now.strftime('%d %B %Y')}", styles["Normal"]),
         Paragraph(f"<b>Time:</b> {now.strftime('%I:%M %p')}", styles["Normal"]),
         Paragraph(f"<b>Type:</b> {f.get('case_type','Complaint')}", styles["Normal"])],
    ]
    meta_table = Table(meta_data, colWidths=[4.2*cm, 4.2*cm, 3.5*cm, 4.5*cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), light_blue),
        ("BOX", (0,0), (-1,-1), 0.5, navy),
        ("INNERGRID", (0,0), (-1,-1), 0.3, colors.HexColor("#aaa")),
        ("FONTSIZE", (0,0), (-1,-1), 9),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 8))

    # Warning
    warn_data = [["⚠  This is a computer-generated draft FIR. Must be verified and signed by an authorized Police Officer."]]
    warn_table = Table(warn_data, colWidths=[16.2*cm])
    warn_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#fff8e1")),
        ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#f0c040")),
        ("FONTSIZE", (0,0), (-1,-1), 8),
        ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#856404")),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(warn_table)
    story.append(Spacer(1, 10))

    def section(title):
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#ccc"), spaceBefore=6))
        story.append(Paragraph(title, section_head))

    def two_col(rows):
        data = []
        for i in range(0, len(rows), 2):
            pair = rows[i:i+2]
            row = []
            for label, value in pair:
                row.append(Paragraph(f'<font size="8" color="#666"><b>{label}</b></font><br/>{value or "—"}', field_value))
            while len(row) < 2:
                row.append(Paragraph("", field_value))
            data.append(row)
        t = Table(data, colWidths=[8*cm, 8*cm])
        t.setStyle(TableStyle([
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("TOPPADDING", (0,0), (-1,-1), 2),
            ("BOTTOMPADDING", (0,0), (-1,-1), 2),
            ("LEFTPADDING", (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(t)

    # Complainant
    section("COMPLAINANT DETAILS / പരാതിക്കാരന്റെ വിവരങ്ങൾ")
    two_col([
        ("Name / പേര്", f.get("complainant_name", "")),
        ("Age / പ്രായം", f.get("complainant_age", "")),
        ("Phone / ഫോൺ", f.get("complainant_phone", "")),
        ("Address / വിലാസം", f.get("complainant_address", "")),
    ])

    # Incident
    section("INCIDENT DETAILS / സംഭവ വിവരങ്ങൾ")
    two_col([
        ("Date / തീയതി", f.get("incident_date", "")),
        ("Time / സമയം", f.get("incident_time", "")),
        ("Location / സ്ഥലം", f.get("incident_location", "")),
        ("Case Type / കേസ് തരം", f.get("case_type", "")),
    ])

    # Description
    section("COMPLAINT DESCRIPTION / പരാതി വിവരണം")
    desc_box_data = [[Paragraph(f.get("incident_description", "—"), desc_style)]]
    desc_box = Table(desc_box_data, colWidths=[16.2*cm])
    desc_box.setStyle(TableStyle([
        ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#aaa")),
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#fafafa")),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
    ]))
    story.append(desc_box)

    # Accused
    if f.get("accused_description"):
        section("ACCUSED DESCRIPTION / പ്രതി വിവരണം")
        story.append(Paragraph(f.get("accused_description"), desc_style))

    # Property
    if f.get("property_details"):
        section("PROPERTY DETAILS / സ്വത്ത് വിവരങ്ങൾ")
        prop_text = f.get("property_details", "")
        if f.get("estimated_value"):
            prop_text += f" | Estimated Value: Rs. {f.get('estimated_value')}"
        story.append(Paragraph(prop_text, desc_style))

    # Witnesses
    if f.get("witnesses"):
        section("WITNESSES / സാക്ഷികൾ")
        story.append(Paragraph(f.get("witnesses"), desc_style))

    # IPC Sections
    section("APPLICABLE IPC SECTIONS / ബാധകമായ IPC വകുപ്പുകൾ")
    ipc_raw = f.get("ipc_sections", "")
    sections_list = [s.strip() for s in ipc_raw.split(",") if s.strip()]
    if sections_list:
        ipc_data = [[Paragraph(f"<b>{s}</b>", ParagraphStyle("ipc", parent=styles["Normal"],
            textColor=colors.white, fontSize=10, alignment=TA_CENTER)) for s in sections_list]]
        widths = [16.2/len(sections_list)*cm] * len(sections_list)
        ipc_t = Table(ipc_data, colWidths=widths)
        ipc_t.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,-1), navy),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(ipc_t)
    else:
        story.append(Paragraph("—", desc_style))

    # Signatures
    story.append(Spacer(1, 24))
    sig_data = [
        [Paragraph("", styles["Normal"]),
         Paragraph("", styles["Normal"]),
         Paragraph("", styles["Normal"])],
        [Paragraph("Complainant's Signature<br/>പരാതിക്കാരന്റെ ഒപ്പ്",
            ParagraphStyle("sig", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9)),
         Paragraph("Investigating Officer<br/>അന്വേഷണ ഓഫീസർ",
            ParagraphStyle("sig", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9)),
         Paragraph("Station House Officer<br/>SHO ഒപ്പ് & സീൽ",
            ParagraphStyle("sig", parent=styles["Normal"], alignment=TA_CENTER, fontSize=9))],
    ]
    sig_table = Table(sig_data, colWidths=[5.4*cm, 5.4*cm, 5.4*cm])
    sig_table.setStyle(TableStyle([
        ("TOPPADDING", (0,1), (-1,1), 6),
        ("LINEABOVE", (0,1), (-1,1), 0.8, colors.black),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
    ]))
    story.append(sig_table)

    # Footer
    story.append(Spacer(1, 12))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#ccc")))
    story.append(Paragraph(
        f"Generated by Kerala Police FIR Assistant | AI-Assisted Draft | {now.strftime('%d %B %Y')} | "
        "This document requires official verification before submission.",
        ParagraphStyle("footer", parent=styles["Normal"],
            alignment=TA_CENTER, fontSize=8, textColor=colors.HexColor("#888"), spaceBefore=6)
    ))

    doc.build(story)
    return buf.getvalue()

# ── Sidebar ───────────────────────────────────────────────────────────────────
t = TRANSLATIONS[st.session_state.lang]

with st.sidebar:
    st.markdown("### 🌐 Language / ഭാഷ")
    lang_col1, lang_col2 = st.columns(2)
    with lang_col1:
        if st.button("English", use_container_width=True,
                     type="primary" if st.session_state.lang == "en" else "secondary"):
            st.session_state.lang = "en"
            st.rerun()
    with lang_col2:
        if st.button("മലയാളം", use_container_width=True,
                     type="primary" if st.session_state.lang == "ml" else "secondary"):
            st.session_state.lang = "ml"
            st.rerun()

    st.markdown("---")
    st.markdown(f"### 👤 {t['role_label']}")
    role_choice = st.radio(
        "", [t["citizen"], t["officer"]],
        key="role_radio", label_visibility="collapsed"
    )
    st.session_state.role = "citizen" if role_choice == t["citizen"] else "officer"

    st.markdown("---")
    st.markdown(f"### 📋 {t['how_to']}")
    st.markdown("""
1. **Select** your role above
2. **Describe** what happened
3. **Answer** the AI's questions
4. **Download** your FIR as PDF
""")

    st.markdown(f"### 📌 {t['supported']}")
    for c in CASE_TYPES:
        st.markdown(f"• {c}")

    st.markdown("---")
    st.markdown(f'<div class="info-box">{t["warning"]}</div>', unsafe_allow_html=True)

# ── Main header ───────────────────────────────────────────────────────────────
t = TRANSLATIONS[st.session_state.lang]

st.markdown(f"""
<div class="header-banner">
  <div style="display:flex; align-items:center; gap:16px;">
    <div style="font-size:42px;">⚖️</div>
    <div>
      <div style="font-size:22px; font-weight:700;">{t['title']}</div>
      <div style="font-size:13px; color:#c8d8f0; margin-top:2px;">{t['subtitle']}</div>
      <div style="font-size:12px; color:#c8a227; margin-top:3px; font-weight:600;">{t['tagline']}</div>
    </div>
  </div>
</div>
<div class="gold-bar"></div>
""", unsafe_allow_html=True)

# ── Layout ────────────────────────────────────────────────────────────────────
col_chat, col_preview = st.columns([3, 2])

with col_chat:
    st.markdown("#### 💬 FIR Chat Assistant")

    # Quick prompts
    if not st.session_state.messages:
        st.markdown("**Quick start — tap a prompt:**")
        prompts = QUICK_PROMPTS_EN if st.session_state.lang == "en" else QUICK_PROMPTS_ML
        q_cols = st.columns(2)
        for i, p in enumerate(prompts):
            with q_cols[i % 2]:
                if st.button(p, key=f"qp_{i}", use_container_width=True):
                    st.session_state.messages.append({"role": "user", "content": p})
                    st.session_state.history.append({"role": "user", "content": p})
                    with st.spinner(t.get("thinking", "Thinking...")):
                        raw = call_claude(st.session_state.history, st.session_state.role, st.session_state.lang)
                    msg, fir = parse_response(raw)
                    st.session_state.messages.append({"role": "assistant", "content": msg})
                    st.session_state.history.append({"role": "assistant", "content": raw})
                    if fir:
                        st.session_state.fir_data = fir
                    st.rerun()

    # Chat history
    chat_container = st.container(height=400)
    with chat_container:
        if not st.session_state.messages:
            st.info(t["welcome"])
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-user">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                content = msg["content"]
                fir_badge = ' <span class="fir-ready-badge">✓ FIR Ready</span>' if st.session_state.fir_data and msg == st.session_state.messages[-1] else ""
                st.markdown(f'<div class="chat-ai">{content}{fir_badge}</div>', unsafe_allow_html=True)

    # Input
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_area(
            "Your message", placeholder=t["placeholder"],
            label_visibility="collapsed", height=80
        )
        send_col, reset_col = st.columns([3, 1])
        with send_col:
            submitted = st.form_submit_button(f"▶ {t['send']}", use_container_width=True, type="primary")
        with reset_col:
            reset_btn = st.form_submit_button(f"🔄 {t['new_fir']}", use_container_width=True)

    if reset_btn:
        reset()
        st.rerun()

    if submitted and user_input.strip():
        st.session_state.messages.append({"role": "user", "content": user_input.strip()})
        st.session_state.history.append({"role": "user", "content": user_input.strip()})
        with st.spinner("⏳ " + t.get("thinking", "Preparing your FIR...")):
            raw = call_claude(st.session_state.history, st.session_state.role, st.session_state.lang)
        msg, fir = parse_response(raw)
        st.session_state.messages.append({"role": "assistant", "content": msg})
        st.session_state.history.append({"role": "assistant", "content": raw})
        if fir:
            st.session_state.fir_data = fir
        st.rerun()

# ── FIR Preview ───────────────────────────────────────────────────────────────
with col_preview:
    st.markdown(f"#### 📄 {t['fir_preview']}")

    if st.session_state.fir_data:
        f = st.session_state.fir_data["fields"]
        fir_no = gen_fir_no()

        st.markdown(f"""
        <div style="background:#1a3a6b; color:white; padding:12px 16px; border-radius:10px 10px 0 0; text-align:center;">
            <div style="font-size:11px; letter-spacing:2px; color:#c8d8f0;">KERALA POLICE DEPARTMENT</div>
            <div style="font-size:15px; font-weight:700; margin-top:2px;">FIRST INFORMATION REPORT</div>
            <div style="font-size:10px; color:#c8a227; margin-top:2px; font-weight:600;">FIR No: {fir_no}</div>
        </div>
        """, unsafe_allow_html=True)

        def fir_row(label, value):
            if value:
                st.markdown(f"""
                <div style="margin-bottom:8px;">
                  <div style="font-size:10px; font-weight:700; color:#666; text-transform:uppercase; letter-spacing:0.5px;">{label}</div>
                  <div style="font-size:13px; color:#111; border-bottom:1px dotted #bbb; padding-bottom:2px;">{value}</div>
                </div>""", unsafe_allow_html=True)

        with st.container():
            st.markdown('<div style="background:white; border:1px solid #1a3a6b; border-top:none; border-radius:0 0 10px 10px; padding:14px 16px;">', unsafe_allow_html=True)
            col1, col2 = st.columns(2)
            with col1:
                fir_row("Name / പേര്", f.get("complainant_name"))
                fir_row("Phone / ഫോൺ", f.get("complainant_phone"))
                fir_row("Date / തീയതി", f.get("incident_date"))
            with col2:
                fir_row("Age / പ്രായം", f.get("complainant_age"))
                fir_row("Case Type / കേസ്", f.get("case_type"))
                fir_row("Time / സമയം", f.get("incident_time"))
            fir_row("Address / വിലാസം", f.get("complainant_address"))
            fir_row("Location / സ്ഥലം", f.get("incident_location"))
            fir_row("Description / വിവരണം", f.get("incident_description"))
            if f.get("accused_description"):
                fir_row("Accused / പ്രതി", f.get("accused_description"))
            if f.get("property_details"):
                val = f.get("property_details","")
                if f.get("estimated_value"):
                    val += f" (₹{f.get('estimated_value')})"
                fir_row("Property / സ്വത്ത്", val)
            if f.get("ipc_sections"):
                st.markdown(f"""
                <div style="margin-top:8px;">
                  <div style="font-size:10px; font-weight:700; color:#666; text-transform:uppercase; letter-spacing:0.5px;">IPC Sections</div>
                  <div style="margin-top:4px;">
                  {"".join(f'<span style="background:#1a3a6b; color:white; font-size:11px; padding:3px 8px; border-radius:4px; margin-right:4px;">{s.strip()}</span>' for s in f.get("ipc_sections","").split(",") if s.strip())}
                  </div>
                </div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Download button
        pdf_bytes = generate_pdf(st.session_state.fir_data)
        st.download_button(
            label=f"⬇ {t['download']}",
            data=pdf_bytes,
            file_name=f"FIR_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )
    else:
        st.markdown("""
        <div style="background:#f8f9fb; border:1px dashed #ccd; border-radius:10px; padding:32px 20px; text-align:center; color:#888;">
            <div style="font-size:36px; margin-bottom:10px;">📋</div>
            <div style="font-size:14px;">Your FIR preview will appear here once the AI has gathered enough information.</div>
            <div style="font-size:12px; margin-top:8px;">Start chatting on the left to begin →</div>
        </div>
        """, unsafe_allow_html=True)

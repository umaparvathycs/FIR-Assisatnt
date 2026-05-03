# 🚔 Kerala Police — FIR Drafting Assistant (Gemini Edition)

An AI-powered Streamlit web app that helps citizens and police officers draft First Information Reports (FIRs) through a conversational chatbot. Powered by **Google Gemini API**. Supports both **English** and **Malayalam**.

---

## Features
- 🤖 AI chatbot (Gemini 1.5 Flash) collects case info conversationally
- 📋 Supports petty theft, burglary, vehicle theft, chain snatching, property damage, eve-teasing, lost items
- 🌐 Bilingual: English & Malayalam (മലയാളം)
- 👮 Two modes: Citizen and Police Officer
- 📄 Downloadable PDF FIR with official formatting
- 🎨 Kerala Police themed UI

---

## Setup & Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set your Gemini API Key (choose one method)

**Method A — Environment variable (recommended):**
```bash
# Linux/Mac
export GEMINI_API_KEY="your_gemini_api_key_here"

# Windows CMD
set GEMINI_API_KEY=your_gemini_api_key_here

# Windows PowerShell
$env:GEMINI_API_KEY="your_gemini_api_key_here"
```

**Method B — Streamlit secrets (for deployment):**
Create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your_gemini_api_key_here"
```

**Method C — Sidebar input (easiest for testing):**
Just paste your key directly in the sidebar after launching the app.

### 3. Run the app
```bash
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

> Get a free Gemini API key at: https://aistudio.google.com/app/apikey

---

## Usage

1. **Enter API Key** — paste in sidebar (or set env variable)
2. **Select Language** — English or Malayalam
3. **Select Role** — Citizen or Police Officer
4. **Chat** — describe your case to the AI assistant
5. **Answer Questions** — the bot asks for required details one by one
6. **Confirm** — once all info is collected, confirm to generate FIR
7. **Download PDF** — click the download button to save the official FIR

---

## Supported Case Types
| Case | IPC Section |
|------|------------|
| Theft | 379 |
| Burglary / House break-in | 457 |
| Chain snatching | 379A |
| Vehicle theft | 379 |
| Property damage | 427 |
| Trespassing | 447 |
| Eve-teasing / Harassment | 354A |
| Lost property | — |

---

## Emergency Contacts
- **Police Emergency**: 100
- **Women Helpline**: 1091
- **Kerala Police HQ**: 0471-2721547

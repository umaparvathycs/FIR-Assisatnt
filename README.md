# Kerala Police FIR Assistant 🚔⚖️

An AI-powered bilingual (English + Malayalam) FIR drafting tool built with Streamlit and Claude AI.

## Features
- 💬 Bilingual AI chatbot (English & Malayalam)
- 👤 Separate flows for Citizens and Police Officers
- 📋 Auto-detects case type & applies correct IPC sections
- 📄 Live FIR preview
- ⬇️ Downloadable PDF with official formatting
- 🔒 Handles: Theft, Vehicle Theft, Mobile Theft, Cheating, Assault, Harassment & more

## Run Locally

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set your Anthropic API key:
   ```
   export ANTHROPIC_API_KEY=your_key_here
   ```

3. Run:
   ```
   streamlit run app.py
   ```

## Deploy on Streamlit Cloud (Free)

1. Push this folder to a **GitHub repository**
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → select your repo → set `app.py` as main file
4. Go to **Settings → Secrets** and add:
   ```
   ANTHROPIC_API_KEY = "your_key_here"
   ```
5. Click **Deploy** — you get a public link like `https://yourapp.streamlit.app`

## Supported Cases
- Theft / മോഷണം (IPC 379)
- Vehicle Theft / വാഹന മോഷണം (IPC 379)
- Mobile Theft / ഫോൺ മോഷണം (IPC 379)
- Cheating / ചതി (IPC 420)
- Trespassing / കടന്നുകയറ്റം (IPC 447)
- Minor Assault / ആക്രമണം (IPC 323/324)
- Vandalism / നാശം (IPC 426/427)
- Harassment / ഉപദ്രവം (IPC 354/509)
- Lost Property / നഷ്ടപ്പെട്ട വസ്തു (Civil Report)

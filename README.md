# 🕵️‍♂️ CyberUstad AI

Ek **funny, roasting wala Cyber Security Ustad** — jo tumhein chat
karte karte **Red Team** aur **Blue Team** ka A-to-Z sikhaye, wo bhi
gehrai (depth) ke saath, mazaak aur halke phulke taanon ke sath. 😂🔥

Built with **Python + Streamlit + Google Gemini API (free tier)**.

---

## ✨ Features

- 💬 Real chat-message jaisa interface (Streamlit `st.chat_message` + streaming replies)
- 😂 Funny + roasting persona — jitna tang karega utna he sikhayega
- 🎯 Red Team, Blue Team, ya dono choose karne ka option
- 📚 Beginner se Advanced tak level select karo
- 🔥 Roast Intensity slider (1 = halka mazaak, 3 = full ustad mode)
- 🆓 Google Gemini free-tier API key ke sath kaam karta hai
- 🔐 API key sidebar mein ya `.streamlit/secrets.toml` mein daal sakte ho

---

## 📁 Project Structure

```
cyber-ustad-ai/
├── app.py                          # Main Streamlit app
├── core/
│   ├── __init__.py
│   ├── gemini_client.py            # Gemini API wrapper + streaming + error handling
│   └── persona.py                  # CyberUstad ki personality / system prompt
├── .streamlit/
│   └── secrets.toml.example        # API key save karne ka template
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## 🚀 Local Setup

### 1. Repo clone karo
```bash
git clone https://github.com/<your-username>/cyber-ustad-ai.git
cd cyber-ustad-ai
```

### 2. Virtual environment banao (recommended)
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Dependencies install karo
```bash
pip install -r requirements.txt
```

### 4. Free Gemini API Key lo
1. Jao: https://aistudio.google.com/app/apikey
2. Google account se login karo
3. "Create API Key" pe click karo — ye **free** hai
4. Key copy kar lo

### 5. API key set karo (2 tareeqay)

**Option A — Sidebar (sabse aasan, temporary):**
App run karo aur sidebar mein directly key paste kar do.

**Option B — Permanent (secrets.toml):**
```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```
Phir `.streamlit/secrets.toml` khol kar apni key daal do. Ye file
`.gitignore` mein hai, GitHub pe push nahi hogi.

### 6. App run karo
```bash
streamlit run app.py
```
Browser mein `http://localhost:8501` khul jayega.

---

## ☁️ Free Deployment (Streamlit Community Cloud)

1. Ye repo apne GitHub account pe push karo
2. Jao: https://share.streamlit.io
3. "New app" -> apna repo select karo -> `app.py` ko main file batao
4. **Settings -> Secrets** mein jaake ye add karo:
   ```toml
   GEMINI_API_KEY = "your-key-here"
   ```
5. Deploy pe click karo — bas ho gaya, live link mil jayegi 🎉

---

## 🧠 Persona Customize Karna

Sara personality/character `core/persona.py` mein hai. Agar roast
ka andaaz change karna ho, ya syllabus (topics) add/remove karne
hon, bas `build_system_prompt()` function edit kar do — baqi app
apne aap adjust ho jayega.

---

## ⚠️ Responsible Use / Disclaimer

Ye tool **sirf educational purposes** ke liye hai:
- CyberUstad sirf concepts, methodology, aur defense sikhata hai
- Ye kisi real target ke against working exploit code ya malware
  generate nahi karta
- Bug bounty / pentesting hamesha **authorized scope** mein hi karo,
  jo qanoon aur rules follow kare

---

## 🛣️ Roadmap (aage ki plans)

- [ ] Multi-language support (pure English mode toggle)
- [ ] Progress tracker — kitne topics cover ho chuke
- [ ] Practice quiz mode (MCQs Red/Blue Team pe)
- [ ] Export chat as PDF notes
- [ ] Voice mode (text-to-speech ustad ki awaaz mein)

Pull requests welcome! 🤝

---

## 📜 License

MIT License — jo chahe use karo, modify karo, seekhne ke liye share karo.

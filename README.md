# 🏛️ TN Welfare Scheme Matcher (NH-S11)
> **Rural Awareness and Accessibility of Tamil Nadu Government Schemes**

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![OCR](https://img.shields.io/badge/OCR-Tesseract-orange.svg)](https://github.com/tesseract-ocr/tesseract)
[![Speech](https://img.shields.io/badge/Speech-Web_Speech_API_%2B_gTTS-success.svg)](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
[![UI](https://img.shields.io/badge/UI-Tailwind_CSS-38B2AC.svg)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📌 Problem Statement & Innovation Gap
Existing e-governance portals (such as e-Sevai and TNeGA) rely heavily on text-heavy forms, requiring formal literacy, digital navigation skills, and manual document verification. 

**Our Solution:** A low-friction, voice-first Tamil web application that accepts spoken Tamil queries or scanned document photos (Smart Ration Card, Aadhaar Card, Income Certificate) and dynamically evaluates eligibility across **29+ Tamil Nadu and Central Government welfare schemes**.

---

## ✨ Key Features

* 🎙️ **Voice-First Tamil Assistant:** Built-in Tamil Speech Recognition (`ta-IN`) and Text-to-Speech (`gTTS`) audio responses for low-literacy rural citizens.
* 📄 **Document OCR Parameter Extraction:** Optical Character Recognition powered by `pytesseract` and Regular Expressions to auto-extract Gender, Age (from DOB), Annual Income, and Ration Card Type (`PHH`/`NPHH`).
* ⚖️ **Dynamic Scheme Matching Engine:** Rule evaluation engine matching multi-parameter criteria (income thresholds, age limits, school type, landholding acres).
* 📚 **Schemes Master Directory (`/schemes`):** Interactive, searchable catalog with category filter tabs covering Students, Women Empowerment, Farmers, Healthcare, and Pensions.
* 📍 **GPS-Enabled e-Sevai Locator:** 1-click geolocation routing to nearby physical Arasu e-Sevai centers across all 38 districts of Tamil Nadu.

---

## 🛠️ Technology Stack

| Layer | Technologies Used |
| :--- | :--- |
| **Backend Framework** | Python 3.10+, FastAPI, Uvicorn, Pydantic |
| **OCR & Computer Vision** | Tesseract OCR (`pytesseract`), Pillow (PIL), Python `re` |
| **Speech Processing** | Web Speech API (`webkitSpeechRecognition` - `ta-IN`), `gTTS` |
| **Frontend UI** | HTML5, JavaScript (ES6+ `fetch`), Tailwind CSS, FontAwesome |
| **Database** | Structured JSON Knowledge Base (`data/schemes.json`) |

---

## 📂 Project Directory Layout

```text
tn-welfare-scheme-matcher/
├── data/
│   └── schemes.json            # 29+ TN & Central welfare schemes database
├── services/
│   ├── __init__.py
│   ├── ocr_engine.py           # Tesseract OCR & regex parameter parser
│   ├── scheme_matcher.py       # Eligibility rule matching engine
│   └── speech_engine.py        # Tamil TTS audio synthesizer (gTTS)
├── static/
│   ├── app.js                  # Frontend client logic & Speech API handlers
│   ├── style.css               # Responsive stylesheet
│   └── response.mp3            # Synthesized Tamil audio output
├── templates/
│   ├── index.html              # Main voice & OCR matching interface
│   └── schemes.html            # Complete welfare schemes directory page
├── app.py                      # FastAPI server & REST API routes
├── requirements.txt            # Python dependencies
└── README.md

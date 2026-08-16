import os
import json
import shutil
import traceback
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services.ocr_engine import DocumentOCREngine
from services.scheme_matcher import SchemeMatcher
from services.speech_engine import SpeechEngine

# 1. Initialize FastAPI Application
app = FastAPI(title="TN Rural Scheme Matcher API")

# 2. Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure runtime directories exist
os.makedirs("static", exist_ok=True)
os.makedirs("temp", exist_ok=True)

# 3. Mount Static Directory (for CSS, JS, and Generated Audio)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 4. Root Route: Serve Home Matcher Page (index.html)
@app.get("/")
async def serve_home():
    if os.path.exists("templates/index.html"):
        return FileResponse("templates/index.html")
    return FileResponse("static/index.html")

# 5. Route: Serve Full Schemes Directory Page (schemes.html)
@app.get("/schemes")
async def serve_schemes_page():
    if os.path.exists("templates/schemes.html"):
        return FileResponse("templates/schemes.html")
    return FileResponse("static/schemes.html")

# Suppress favicon 404 log
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)

# Initialize Scheme Matcher Engine
matcher = SchemeMatcher()

# 6. Dynamic Citizen Profile Model (Defaults to None)
class CitizenProfile(BaseModel):
    gender: Optional[str] = None
    age: Optional[int] = None
    annual_income: Optional[int] = None
    ration_card_type: Optional[str] = None
    is_head_of_family: Optional[bool] = None
    is_govt_school_studied: Optional[bool] = None
    pursuing_higher_education: Optional[bool] = None
    is_agricultural_laborer: Optional[bool] = None
    is_landholding_farmer: Optional[bool] = None
    is_differently_abled: Optional[bool] = None
    is_widow: Optional[bool] = None
    is_pregnant: Optional[bool] = None

# 7. Scheme Matching API Endpoint
@app.post("/api/match-schemes")
def match_schemes(profile: CitizenProfile):
    try:
        # Compatible with both Pydantic v1 (.dict()) and v2 (.model_dump())
        profile_data = profile.model_dump() if hasattr(profile, "model_dump") else profile.dict()
        
        # Check if the user has provided any data via Voice, OCR, or Form
        has_data = any(val is not None for val in profile_data.values())
        if not has_data:
            return {
                "status": "empty",
                "matched_count": 0,
                "schemes": [],
                "text_summary_ta": "தயவுசெய்து உங்கள் தகவல்களைக் குரல் மூலமாகவோ அல்லது ஆவணத்தைப் பதிவேற்றுவதன் மூலமாகவோ வழங்கவும்.",
                "audio_url": None
            }

        # Evaluate eligibility rules
        results = matcher.evaluate_household(profile_data)
        
        if results:
            names_ta = " , ".join([s["scheme_name_ta"] for s in results])
            speech_text = f"நீங்கள் {len(results)} திட்டங்களுக்குத் தகுதியானவர். அவை: {names_ta}."
        else:
            speech_text = "மன்னிக்கவும், உங்கள் தகவல்களுக்குப் பொருத்தமான திட்டங்கள் எதுவும் கண்டறியப்படவில்லை."

        # Generate Tamil TTS Audio
        audio_file = SpeechEngine.generate_tamil_audio(speech_text, "static/response.mp3")
        audio_url = "/static/response.mp3" if audio_file and os.path.exists("static/response.mp3") else None

        return {
            "status": "success",
            "matched_count": len(results),
            "schemes": results,
            "text_summary_ta": speech_text,
            "audio_url": audio_url
        }
    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

# 8. Document OCR Scan Endpoint
@app.post("/api/ocr-scan")
async def ocr_scan(file: UploadFile = File(...)):
    temp_path = os.path.join("temp", file.filename)
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        extracted_params = DocumentOCREngine.parse_document(temp_path)

        return {
            "status": "success",
            "extracted_data": extracted_params
        }
    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": str(e)}
    finally:
        # Cleanup temporary uploaded file
        if os.path.exists(temp_path):
            os.remove(temp_path)

# 9. API Endpoint: Get All Schemes from data/schemes.json
@app.get("/api/all-schemes")
def get_all_schemes():
    try:
        json_path = "data/schemes.json"
        if not os.path.exists(json_path):
            json_path = os.path.join(os.path.dirname(__file__), "data", "schemes.json")
            
        with open(json_path, "r", encoding="utf-8") as f:
            schemes_data = json.load(f)

        return {
            "status": "success",
            "total_count": len(schemes_data),
            "schemes": schemes_data
        }
    except Exception as e:
        traceback.print_exc()
        return {"status": "error", "message": str(e)}

# 10. Server Entry Point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True)
# checkin.py
from fastapi import APIRouter
from pydantic import BaseModel
# --- UPDATED: Import the new function ---
from gemini import get_all_gemini_responses, check_for_crisis

from database import get_db, save_db

router = APIRouter()

class CheckIn(BaseModel):
    emotion: str
    energy: int
    social: str
    context: list[str]
    thoughts: str

@router.post("/checkin")
def create_checkin(checkin: CheckIn):
    
    # --- UPDATED: AI-Powered Safety Check ---
    # 1. First, classify the user's thoughts for a potential crisis.
    classification = check_for_crisis(checkin.thoughts)

    # 2. If a crisis is detected, redirect immediately.
    if "crisis" in classification:
        return {
            "status": "crisis_detected",
            "message": "It sounds like you need immediate help. We will connect you to professional resources."
        }
    
    # 3. If the message is safe, proceed to get the creative recommendations.
    gemini_recommendations = get_all_gemini_responses(checkin.model_dump())

    music_map = {
        "Nature Sounds": "./sounds/1.mp3",
        "Piano Melodies": "./sounds/2.mp3",
        "Ocean Waves": "./sounds/3.mp3",
        "Upbeat Folk": "./sounds/4.mp3",
        "Chillwave": "./sounds/5.mp3",
        "default":"./sounds/111.mp3"
    }
    
    music_phrase_from_ai = gemini_recommendations.get("music_phrase", "Calm Music")
    music_url = music_map.get(music_phrase_from_ai, "./sounds/111.mp3")
    
    gemini_recommendations["music_url"] = music_url
    gemini_recommendations["status"] = "success"

    db = get_db()
    db.append({"checkin_data": checkin.model_dump(), "ai_response": gemini_recommendations})
    save_db(db)

    return gemini_recommendations

# chat.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Union
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')  
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def get_chat_response(history: list):
    """
    Handles the chat logic using a more robust two-call method.
    """
    try:
        # --- Task 1: Safety Classification ---
        last_user_message = history[-1]['text']
        safety_prompt = f"""
        Analyze the following user message. Classify it as either "crisis" or "safe".
        Respond with only a single word: either "crisis" or "safe".

        User Message: "{last_user_message}"
        Classification:
        """
        safety_response = model.generate_content(safety_prompt)
        classification = safety_response.text.strip().lower()

        # If a crisis is detected, stop immediately.
        if "crisis" in classification:
            return {"status": "crisis", "response_text": ""}

        # --- Task 2: Generate Conversational Response (only if safe) ---
        gemini_history = []
        for message in history:
            role = 'model' if message['sender'] == 'ai' else 'user'
            gemini_history.append({'role': role, 'parts': [message['text']]})
        
        chat = model.start_chat(history=gemini_history[:-1]) # History without the latest user message
        
        conversation_response = chat.send_message(gemini_history[-1]['parts'])
        
        return {"status": "safe", "response_text": conversation_response.text.strip()}

    except Exception as e:
        print(f"An error occurred in get_chat_response: {e}")
        return {"status": "safe", "response_text": "I'm having a little trouble thinking right now. Could you please say that again?"}

# ===================================================================
# 2. API Endpoint Logic (No changes here)
# ===================================================================

router = APIRouter()

class Message(BaseModel):
    id: Union[int, str]
    text: str
    sender: str

class ChatPayload(BaseModel):
    messages: List[Message]

@router.post("/chat")
def handle_chat(payload: ChatPayload):
    history = [msg.dict() for msg in payload.messages]
    
    ai_response = get_chat_response(history)
    
    if ai_response.get("status") == "crisis":
        return { "status": "crisis_detected" }

    ai_text = ai_response.get("response_text", "I'm not sure what to say. Could you rephrase?")
    
    return {
        "status": "success",
        "message": {
            "id": "ai-" + str(payload.messages[-1].id),
            "sender": "ai",
            "text": ai_text
        }
    }
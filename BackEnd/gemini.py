# services/gemini.py
import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY') 
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-flash-latest')


def check_for_crisis(text_to_analyze: str):
    """
    Uses a focused prompt to classify text as 'crisis' or 'safe'.
    Returns the classification as a string.
    """
    prompt = f"""
    Analyze the following user message. Classify it as either "crisis" or "safe".
    A "crisis" involves any mention of self-harm, suicide, or severe, urgent distress.
    Respond with only a single word: either "crisis" or "safe".

    User Message: "{text_to_analyze}"
    Classification:
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip().lower()
    except Exception as e:
        print(f"Error during crisis check: {e}")
        return "safe" # Default to safe if the API fails


def get_all_gemini_responses(checkin_data):
    """
    Sends a single, structured prompt to Gemini and expects a JSON response
    with a comprehensive set of recommendations.
    """
    approved_music_phrases = [
        "Nature Sounds",
        "Piano Melodies",
        "Ocean Waves",
        "Upbeat Folk",
        "Chillwave"
    ]
    
    # --- UPDATED: This is the new, more advanced prompt ---
    prompt = f"""
    You are Sahaara, a kind, wise, and empathetic mental wellness companion. A user has just completed a check-in.
    
    User Data:
    - Emotion: {checkin_data['emotion']}
    - Energy: {checkin_data['energy']} out of 100
    - Social connection: {checkin_data['social']}
    - Context: {', '.join(checkin_data['context']) if checkin_data['context'] else 'none'}
    - Thoughts: {checkin_data['thoughts']}
    
    Your task is to generate a personalized response based on this data. The response must be a single, valid JSON object.
    
    First, think step-by-step to identify the user's core emotional challenge.
    Then, find a compelling, true story about a real person (historical figure, artist, scientist, etc.) who overcame a similar challenge.

    Finally, generate the following JSON keys:
    
    1. "recommendations_line": A brief, actionable line that tells the user to check out the activities that might help.
    2. "chat_welcome": A welcoming, encouraging line for the start of a chat.
    3. "story_heading": A short, engaging title for the true story you've chosen.
    4. "story_text": The concise (max 100 words) true story, structured to show the person's struggle and their moment of perseverance.
    5. "story_reflection": A single, powerful sentence that connects the story's lesson directly to the user's current feelings or situation.
    6. "music_phrase": Choose one of the following phrases to recommend music: {', '.join(approved_music_phrases)}.
    
    Do not include any other text, explanations, or formatting outside of the JSON object.
    """
    
    try:
        response = model.generate_content(prompt)
        cleaned_text = response.text.strip().replace('```json\n', '').replace('```', '')
        return json.loads(cleaned_text)
    except Exception as e:
        print(f"Error getting or parsing Gemini response: {e}")
        # --- UPDATED: Fallback response now includes the new 'story_reflection' key ---
        return {
            "recommendations_line": "It sounds like you're carrying a heavy load today. Here are a few things that might help.",
            "chat_welcome": "I'm here for you. Let's talk about what's on your mind.",
            "story_heading": "The Persistent Inventor",
            "story_text": "Thomas Edison's teachers said he was 'too stupid to learn anything.' He was fired from his first two jobs. As an inventor, he made 1,000 unsuccessful attempts at inventing the light bulb. But he never gave up, and eventually succeeded, changing the world.",
            "story_reflection": "Just like Edison, remember that every attempt, even those that don't work out, is a step toward your own brilliant breakthrough.",
            "music_phrase": "Ocean Waves",
        }
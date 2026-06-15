import os
import pandas as pd
from flask import Flask, request, jsonify
from google import genai
from google.genai import types

# 1. DEFINE APP FIRST so Vercel finds it immediately
app = Flask(__name__)

# 2. SETUP SECURE ENVIRONMENT VARIABLE
# This pulls your real key from Vercel's secure settings, not your code!
API_KEY = os.environ.get("GEMINI_API_KEY")

# Global Variables
excel_database_content = ""
client = None
config = None

# 3. WRAP STARTUP LOGIC IN A TRY/EXCEPT SO DEPLOYMENT DOESN'T CRASH
try:
    # Load Excel File safely
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    EXCEL_FILE = os.path.join(BASE_DIR, "events_data.xlsx")
    
    if os.path.exists(EXCEL_FILE):
        df = pd.read_excel(EXCEL_FILE)
        for _, row in df.iterrows():
            excel_database_content += f"- Event: {row['event name']} | Department: {row['department']} | Date: {row['date']} | Venue: {row['venue']}\n"
    else:
        excel_database_content = "Warning: events_data.xlsx not found."

    # Initialize AI ONLY if a real API key is detected in Vercel
    if API_KEY:
        client = genai.Client(api_key=API_KEY)
        
        system_instruction = f"""
        You are an expert Event Management AI Assistant.
        Here is the exact live records sheet data stored right now:
        
        {excel_database_content}
        
        Strict Operating Instructions:
        1. Base all answers strictly on the dataset rows supplied above.
        2. If an event is not explicitly found, say "We don't have that specific event cataloged."
        3. Keep answers brief, accurate, and professional.
        """
        
        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.1 
        )
        
except Exception as e:
    print(f"Startup Error: {e}")

# ==============================================================================
# 4. WEB ROUTES
# ==============================================================================
@app.route('/', methods=['GET'])
def home():
    if not API_KEY:
        return jsonify({"status": "Almost ready! Add GEMINI_API_KEY to your Vercel Environment Variables."})
    return jsonify({"status": "Event Chatbot API is running online and connected to Gemini!"})

@app.route('/chat', methods=['POST'])
def chat():
    if not client:
        return jsonify({"error": "AI Client not initialized. Check your Vercel Environment Variables."}), 500
        
    try:
        data = request.get_json()
        user_message = data.get("message")
        
        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        chat_session = client.chats.create(model="gemini-2.5-flash", config=config)
        response = chat_session.send_message(user_message)
        
        return jsonify({"reply": response.text})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
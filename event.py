import os
import sys
import pandas as pd
from google import genai
from google.genai import types

# ==============================================================================
# 1. READ EXCEL DATASET (100 ENTRIES)
# ==============================================================================
EXCEL_FILE = "events_data.xlsx"

def load_dataset_context():
    """Reads your custom 100-row Excel dataset and formats it for the AI model."""
    try:
        # Load the spreadsheet data
        df = pd.read_excel(EXCEL_FILE)
        
        # Verify required structural headers are present
        required_headers = ['event name', 'venue', 'date', 'department']
        for header in required_headers:
            if header not in df.columns:
                print(f"❌ Error: Your Excel sheet is missing the column header: '{header}'")
                sys.exit(1)
                
        # Parse spreadsheet rows out into clean text rows
        context_string = ""
        for _, row in df.iterrows():
            context_string += f"- Event: {row['event name']} | Department: {row['department']} | Date: {row['date']} | Venue: {row['venue']}\n"
            
        return context_string
        
    except FileNotFoundError:
        print(f"❌ Error: Cannot find file '{EXCEL_FILE}' in this folder.")
        print("Please ensure you download the generated Excel sheet and save it next to chatbot.py.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error compiling spreadsheet records: {e}")
        sys.exit(1)

# Compile context logs right before initializing backend services
excel_database_content = load_dataset_context()

# ==============================================================================
# 2. INJECT DATA TO SYSTEM PROMPTS & AUTHENTICATE
# ==============================================================================
# Your provided API key is hardcoded below:
API_KEY = "PASTE_YOUR_API_KEY_HERE"
try:
    client = genai.Client(api_key=API_KEY)
    
    # Configure the system rules using our formatted spreadsheet contents
    system_instruction = f"""
    You are an expert Event Management AI Assistant. You have access to our entire internal 100-event Excel schedule matrix.
    Here is the exact live records sheet data stored right now:
    
    {excel_database_content}
    
    Strict Operating Instructions:
    1. Base all answers strictly on the dataset rows supplied above.
    2. If an event is not explicitly found in the data, reply: "We don't have that specific event cataloged in our system rules."
    3. You can group things. For example, if someone asks: "What events are the Computer Science department hosting?", look through the dataset and list out every event where Department is "Computer Science".
    4. Keep answers brief, accurate, and professional.
    """
    
    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=0.1 # Very low temperature ensures it reads data facts without guessing
    )
    
    chat = client.chats.create(model="gemini-2.5-flash", config=config)
except Exception as e:
    print(f"❌ Connection Error: {e}")
    sys.exit(1)

# ==============================================================================
# 3. INTERACTIVE CONSOLE EXECUTION LOOP
# ==============================================================================
print("\n" + "="*70)
print(f"📅 AI Chatbot Connected! Successfully loaded 100 event listings from {EXCEL_FILE}")
print("Type your questions below. Type 'exit' to terminate.")
print("="*70 + "\n")

while True:
    try:
        user_input = input("You: ")
        
        if user_input.strip().lower() in ['exit', 'quit']:
            print("\n🤖 AI Assistant: Session closed cleanly. Goodbye!")
            break
            
        if not user_input.strip():
            continue
            
        response = chat.send_message(user_input)
        print(f"\nAI Assistant: {response.text}")
        print("-" * 70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n🤖 AI Assistant: Goodbye!")
        break
    except Exception as e:
        print(f"\n❌ Error processing prompt: {e}\n")
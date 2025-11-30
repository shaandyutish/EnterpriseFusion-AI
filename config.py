import os
from dotenv import load_dotenv

load_dotenv()

# Replace with your actual Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDqkqUjVaZrq47dP69RoKWcwwwHD94ixB4")
GOOGLE_GENAI_MODEL = "gemini-2.0-flash-exp"

DB_PATH = "enterprise_fusion.db"
LOG_PATH = "agent_logs.jsonl"

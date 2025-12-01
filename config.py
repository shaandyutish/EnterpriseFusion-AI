# config.py
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load variables from .env in project root
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print("CONFIG GEMINI KEY PREFIX:", api_key[:8] if api_key else None)

genai.configure(api_key=api_key)

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "data", "enterprise_fusion.db")

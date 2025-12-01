import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging

# Load .env
load_dotenv()

# --- Gemini API key ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY not set – live Gemini will not work")

# --- Database path for SQLite ---
DB_PATH = os.getenv("DB_PATH", "enterprise_fusion.db")

# --- Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("enterprise_fusion")

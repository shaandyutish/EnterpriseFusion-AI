import google.generativeai as genai
from tools.data_tools import ingest_csv, query_unified_store
from config import GEMINI_API_KEY, GOOGLE_GENAI_MODEL

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GOOGLE_GENAI_MODEL)

def data_hub_agent(source_data):
    """Data Hub Agent - ingests and normalizes data"""
    prompt = f"""
    You are Data Hub Agent. Process this incoming data source:
    
    Source: {source_data}
    
    Tasks:
    1. Identify data type (CSV, JSON, API)
    2. Call ingest_csv() if CSV
    3. Return confirmation with record count
    
    Available tools: ingest_csv(), query_unified_store()
    """
    
    response = model.generate_content(prompt)
    return response.text

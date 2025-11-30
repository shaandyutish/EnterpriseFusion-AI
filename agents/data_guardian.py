import google.generativeai as genai
import pandas as pd
import numpy as np
from tools.data_tools import query_unified_store
from config import GEMINI_API_KEY, GOOGLE_GENAI_MODEL

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GOOGLE_GENAI_MODEL)

def data_guardian_agent(source_id=None):
    """Data Guardian Agent - validates and cleans data"""
    
    # Query recent data
    if source_id:
        query = f"SELECT * FROM unified_data WHERE source_id='{source_id}' ORDER BY ingested_at DESC LIMIT 100"
    else:
        query = "SELECT * FROM unified_data ORDER BY ingested_at DESC LIMIT 100"
    
    raw_data = query_unified_store(query)
    
    if not raw_data:
        return {"status": "no_data", "quality_score": 0.0}
    
    # Simple validation rules
    issues = []
    df = pd.DataFrame(raw_data)
    
    # Check for missing values
    missing_rate = df.isnull().mean().mean()
    if missing_rate > 0.1:
        issues.append(f"High missing data: {missing_rate:.1%}")
    
    # Check duplicates
    dup_rate = df.duplicated().mean()
    if dup_rate > 0.05:
        issues.append(f"High duplicates: {dup_rate:.1%}")
    
    # Outlier detection (simple)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    outlier_score = 0
    if len(numeric_cols) > 0:
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).mean()
            outlier_score += outliers
    
    quality_score = max(0, 1 - (missing_rate * 0.4 + dup_rate * 0.3 + outlier_score * 0.3))
    
    prompt = f"""
    You are Data Guardian Agent. Review this data quality report:
    
    Issues: {issues}
    Quality Score: {quality_score:.2f}
    Sample data: {raw_data[:3]}
    
    Tasks:
    1. Prioritize data cleaning actions
    2. Suggest schema improvements
    3. Flag critical issues requiring human review
    
    Respond as JSON:
    {{
        "quality_score": {quality_score},
        "issues": [...],
        "actions": [...],
        "human_review_needed": boolean
    }}
    """
    
    response = model.generate_content(prompt)
    
    return {
        "quality_score": quality_score,
        "issues": issues,
        "actions": [
            "Fill missing values with defaults",
            "Remove duplicates by primary key",
            "Cap numeric outliers at 3σ"
        ],
        "human_review_needed": quality_score < 0.7,
        "records_checked": len(raw_data)
    }

import google.generativeai as genai
import pandas as pd
from tools.workflow_tools import analyze_logs, suggest_automation
from config import GEMINI_API_KEY, GOOGLE_GENAI_MODEL

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GOOGLE_GENAI_MODEL)

def workflow_auditor_agent(period_days=7):
    """Workflow Auditor Agent - detects bottlenecks and suggests fixes"""
    analysis = analyze_logs(period_days)
    
    prompt = f"""
    You are Workflow Auditor Agent. Analyze these workflow metrics:
    
    Analysis: {analysis}
    
    Tasks:
    1. Identify top 3 bottlenecks (high failure_rate > 0.3 OR high avg_duration > 20s)
    2. Call suggest_automation() for each bottleneck process_id
    3. Generate prioritized fix recommendations
    4. Estimate time savings after fixes
    
    Available tools: suggest_automation(workflow_id)
    
    Respond in JSON format:
    {{
        "bottlenecks": [...],
        "recommendations": [...],
        "estimated_savings_hours": number
    }}
    """
    
    response = model.generate_content(prompt)
    
    # Parse response as JSON (simplified)
    bottlenecks = analysis['bottlenecks'][:3]
    recommendations = []
    for bottleneck in bottlenecks:
        fix = suggest_automation(bottleneck['process_id'])
        recommendations.append({
            'process_id': bottleneck['process_id'],
            'issue': f"{bottleneck['step_name']}: {bottleneck['failure_rate']:.1%} failure",
            'fix': fix
        })
    
    return {
        'bottlenecks': bottlenecks,
        'recommendations': recommendations,
        'estimated_savings_hours': len(bottlenecks) * 5,  # 5h per fix
        'analysis': analysis
    }

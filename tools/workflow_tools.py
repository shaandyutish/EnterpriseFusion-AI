import pandas as pd
from config import DB_PATH

def analyze_logs(period_days=7):
    """Analyze workflow performance"""
    df = pd.read_csv('data/workflows.csv')
    high_fail = df[df['failure_rate'] > 0.3]
    bottlenecks = high_fail[['process_id', 'step_name', 'failure_rate']].to_dict('records')
    return {
        'total_workflows': len(df),
        'bottlenecks': bottlenecks,
        'avg_failure_rate': df['failure_rate'].mean()
    }

def suggest_automation(workflow_id):
    """Suggest automation fixes"""
    suggestions = {
        'WF002': 'Implement payment retry with exponential backoff',
        'WF004': 'Deploy AI ticket classification agent',
        'WF005': 'Use parallel data ingestion pipelines'
    }
    return suggestions.get(workflow_id, 'Review manual steps for automation')

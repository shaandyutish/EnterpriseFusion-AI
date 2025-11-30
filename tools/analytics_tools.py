import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

def generate_weekly_report():
    """Generate support analytics report"""
    tickets = pd.read_csv('data/tickets.csv')
    
    metrics = {
        'total_tickets': len(tickets),
        'auto_resolved_rate': (len(tickets[tickets['resolution'] == 'auto_resolved']) / len(tickets)) * 100,
        'avg_response_time': tickets['response_time'].mean(),
        'high_priority': len(tickets[tickets['priority'] == 'high'])
    }
    
    # Create chart
    plt.figure(figsize=(10, 6))
    tickets['priority'].value_counts().plot(kind='bar')
    plt.title('Ticket Priority Distribution')
    plt.ylabel('Count')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_url = base64.b64encode(buf.read()).decode()
    
    return {'metrics': metrics, 'chart_url': f"data:image/png;base64,{chart_url}"}

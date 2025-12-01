import pandas as pd
from config import DB_PATH

# tools/workflow_tools.py

def analyze_logs():
    """Return a stubbed log summary for the Workflow Audit demo."""
    return {
        "total_tickets": 1200,
        "avg_resolution_hours": 18,
        "sla_breach_rate": 0.07,
        "top_queues": ["Billing", "Tech Support", "Onboarding"],
        "notes": "Sample data for weekly audit demo, not from real systems.",
    }


def suggest_automation(log_summary):
    """
    Return simple, fixed automation suggestions based on the log summary.

    This implementation does NOT use dicts as dictionary keys, so it avoids
    the 'unhashable type: dict' error and is safe for the demo.
    """
    return {
        "summary": "Weekly audit completed for sample enterprise workflows.",
        "bottlenecks": [
            {
                "name": "Manual ticket triage",
                "impact": "Adds 4–6 hours delay for about 35% of new tickets.",
            },
            {
                "name": "Billing escalation queue",
                "impact": "High-priority payment issues wait more than 8 hours.",
            },
        ],
        "automations": [
            {
                "name": "Auto-route payment issues",
                "description": "Detect 'payment' intent and route directly to Billing L2.",
            },
            {
                "name": "Auto-close resolved FAQs",
                "description": "Automatically close tickets when customers confirm the FAQ answer helped.",
            },
        ],
    }

# orchestrator.py
import json
import pandas as pd

from agents.data_hub_agent import data_hub_agent  # if you use it
from agents.workflow_auditor import workflow_auditor_agent
from agents.data_guardian import data_guardian_agent
from agents.omni_support import omni_support_agent
from tools.analytics_tools import generate_weekly_report


class EnterpriseFusionOrchestrator:
    def __init__(self):
        self.sessions = {}

    def process_ticket(self, ticket_data):
        """Main ticket processing pipeline."""
        ticket_id = ticket_data["id"]
        self.sessions[ticket_id] = {"state": "new"}

        # Route to Omni-Support Agent
        result = omni_support_agent(ticket_data)

        # Log result
        self.log_event(ticket_id, "processed", result)
        return result

    def run_weekly_audit(self):
        """Weekly business intelligence run."""
        audit_result = workflow_auditor_agent()
        report = generate_weekly_report()
        return {"audit": audit_result, "report": report}

    def check_data(self, payload=None):
        """Run data quality / policy checks via Data Guardian."""
        return data_guardian_agent(payload or {})

    def log_event(self, ticket_id, event, data):
        """Observability logging."""
        with open("agent_logs.jsonl", "a", encoding="utf-8") as f:
            f.write(
                json.dumps(
                    {
                        "timestamp": pd.Timestamp.now().isoformat(),
                        "ticket_id": ticket_id,
                        "event": event,
                        "data": data,
                    }
                )
                + "\n"
            )

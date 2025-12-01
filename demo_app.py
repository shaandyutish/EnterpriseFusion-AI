import json
import streamlit as st
import pandas as pd

from agents.omni_support import omni_support_agent
from agents.workflow_auditor import workflow_auditor_agent
from agents.data_guardian import data_guardian_agent
from orchestrator import EnterpriseFusionOrchestrator
from evaluation import run_full_evaluation
from tools.analytics_tools import generate_weekly_report
from tools.data_tools import init_db


# ---------- Page config & intro ----------

st.set_page_config(page_title="EnterpriseFusion-AI", layout="wide")

st.title("EnterpriseFusion-AI 🚀")
st.subheader("Kaggle Agents Intensive Capstone - Enterprise Agents Track")

st.markdown(
    """
    <style>
    .big-font {
        font-size:18px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<p class="big-font">Choose a mode below to explore how EnterpriseFusion-AI transforms enterprise workflows using multiple specialized agents.</p>',
    unsafe_allow_html=True,
)

# Ensure DB exists (no-op if already created)
init_db()

# Create orchestrator (if your constructor differs, adjust accordingly)
orchestrator = EnterpriseFusionOrchestrator()
# ---------- Helper render functions ----------

def show_ticket_demo():
    st.header("💬 Ticket Demo")

    col1, col2 = st.columns(2)

    with col1:
        customer_id = st.text_input("Customer ID", "1001")
        issue_text = st.text_area(
            "Customer Message",
            "My payment failed but money was deducted from my bank account.",
            height=120,
        )
        priority = st.selectbox("Priority", ["Low", "Medium", "High"], index=1)

    with col2:
        channel = st.selectbox("Channel", ["Email", "Chat", "Phone"], index=1)
        product = st.text_input("Product / Plan", "PremiumPlus")
        sla_hours = st.number_input("SLA (hours)", min_value=1, max_value=72, value=24)

    if st.button("Process Ticket"):
        # Build a single payload dict for the orchestrator
        ticket_payload = {
            "id": customer_id,          # or a separate ticket_id if you have one
            "customer_id": customer_id,
            "message": issue_text,
            "priority": priority,
            "channel": channel,
            "product": product,
            "sla_hours": sla_hours,
        }

        with st.spinner("Running omni support agent…"):
            result = orchestrator.process_ticket(ticket_payload)

        st.subheader("Agent Response")
        st.json(result)

def show_audit_demo():
    st.header("📊 Workflow Audit Demo")

    st.write(
        "Run a weekly process audit on sample enterprise workflows to detect "
        "bottlenecks, SLA risks, and automation candidates."
    )

    if st.button("Run Weekly Audit"):
        with st.spinner("Running workflow auditor…"):
            audit_result = orchestrator.run_weekly_audit()

        st.subheader("Audit Summary")
        st.write(audit_result.get("summary", ""))

        st.subheader("Bottlenecks")
        bottlenecks = audit_result.get("bottlenecks", [])
        if bottlenecks:
            for b in bottlenecks:
                st.markdown(f"- **{b.get('name','Unknown')}**: {b.get('impact','')}")
        else:
            st.write("No major bottlenecks detected.")

        st.subheader("Suggested Automations")
        autos = audit_result.get("automations", [])
        if autos:
            for a in autos:
                st.markdown(f"- **{a.get('name','Automation')}** – {a.get('description','')}")
        else:
            st.write("No new automations suggested.")

        st.subheader("Weekly Report JSON")
        st.json(generate_weekly_report())



def show_data_demo():
    st.header("🛡️ Data Demo")

    st.write(
        "Check data quality and policy compliance on a sample dataset using the "
        "Data Guardian agent."
    )

    if st.button("Run Data Quality Check"):
        with st.spinner("Running data guardian…"):
            dq_result = orchestrator.check_data()

        st.subheader("Quality Score")
        st.write(dq_result.get("quality_score", "N/A"))

        st.subheader("Issues")
        issues = dq_result.get("issues", [])
        if issues:
            for issue in issues:
                st.markdown(f"- **{issue.get('type','Issue')}** – {issue.get('detail','')}")
        else:
            st.write("No major issues found.")

        st.subheader("Raw Result")
        st.json(dq_result)


def show_evaluation_demo():
    st.header("📈 Evaluation")

    st.write(
        "Run the full evaluation suite over curated scenarios to compute the "
        "overall performance score."
    )

    if st.button("Run Full Evaluation"):
        with st.spinner("Evaluating agents…"):
            eval_result = run_full_evaluation()

        st.subheader("Overall Score")
        st.write(eval_result.get("overall_score", "N/A"))

        st.subheader("Per-Dimension Scores")
        scores = eval_result.get("scores", {})
        if scores:
            df = pd.DataFrame(
                [{"dimension": k, "score": v} for k, v in scores.items()]
            )
            st.table(df)
        else:
            st.write("No score details available.")

        st.subheader("Evaluation Details")
        st.json(eval_result)


# ---------- Main mode selector (replaces tabs) ----------

mode = st.selectbox(
    "Choose a view",
    [
        "💬 Ticket Demo",
        "📊 Audit Demo",
        "🛡️ Data Demo",
        "📈 Evaluation",
    ],
)

if mode == "💬 Ticket Demo":
    show_ticket_demo()
elif mode == "📊 Audit Demo":
    show_audit_demo()
elif mode == "🛡️ Data Demo":
    show_data_demo()
else:  # "📈 Evaluation"
    show_evaluation_demo()

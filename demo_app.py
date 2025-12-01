import json
import streamlit as st
import pandas as pd

from tools.data_layer import (
    list_tickets_for_customer,
    list_data_quality_runs,
    save_data_quality_run,
)

from agents.omni_support import omni_support_agent
from agents.workflow_auditor import workflow_auditor_agent
from agents.data_guardian import data_guardian_agent
from orchestrator import EnterpriseFusionOrchestrator
from evaluation import run_full_evaluation
from tools.analytics_tools import generate_weekly_report
from tools.data_tools import init_db
from config import logger


# ---------- Page config & intro ----------

st.set_page_config(page_title="EnterpriseFusion-AI", layout="wide")

st.title("EnterpriseFusion-AI 🚀")
st.subheader("Enterprise Workflow Intelligence Platform")

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
    '<p class="big-font">Use the views below to manage support tickets, audit workflows, and monitor data quality using coordinated AI agents.</p>',
    unsafe_allow_html=True,
)

# Ensure DB exists (no-op if already created)
init_db()

# Create orchestrator
orchestrator = EnterpriseFusionOrchestrator()


# ---------- Helper render functions ----------


def show_ticket_view():
    st.header("💬 Ticket Workspace")

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
        ticket_payload = {
            "id": customer_id,
            "customer_id": customer_id,
            "message": issue_text,
            "priority": priority,
            "channel": channel,
            "product": product,
            "sla_hours": sla_hours,
        }

        with st.spinner("Processing ticket with Omni Support Agent…"):
            result = orchestrator.process_ticket(ticket_payload)

        st.subheader("Agent Decision")
        st.json(result)

        cust_id = result.get("customer_id")
        if cust_id:
            st.markdown("### Recent tickets for this customer")
            history = list_tickets_for_customer(cust_id, limit=5)
            if history:
                df = pd.DataFrame(history)
                st.dataframe(df)
            else:
                st.info("No previous tickets found for this customer.")


def show_audit_view():
    st.header("📊 Workflow Audit")

    st.write(
        "Run a weekly workflow audit to detect bottlenecks, SLA risks, and automation opportunities across your operations."
    )

    if st.button("Run Weekly Audit"):
        with st.spinner("Running Workflow Auditor Agent…"):
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
                st.markdown(
                    f"- **{a.get('name','Automation')}** – {a.get('description','')}"
                )
        else:
            st.write("No new automations suggested.")

        st.subheader("Weekly Report JSON")
        st.json(generate_weekly_report())


def show_data_view():
    st.header("🛡️ Data Quality")

    st.write(
        "Upload a CSV dataset to run data quality checks and store each run for monitoring."
    )

    uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
        except Exception as e:
            st.error(f"Could not read CSV: {e}")
            logger.exception("CSV read failed in Data Quality view")
            st.stop()

        st.subheader("Preview")
        st.dataframe(df.head())

        if df.empty:
            st.warning("The uploaded CSV is empty. Nothing to analyze.")
            st.stop()

        row_count = len(df)
        null_counts = df.isna().sum()
        total_nulls = int(null_counts.sum())
        issue_count = total_nulls

        score = max(
            0.0,
            1.0 - (issue_count / max(1, row_count * len(df.columns))),
        )

        result = {
            "columns": list(df.columns),
            "row_count": row_count,
            "null_counts": null_counts.to_dict(),
            "issue_count": issue_count,
            "score": score,
        }

        dataset_name = uploaded_file.name
        uploaded_by = "demo_user"  # later: real user / email

        try:
            save_data_quality_run(
                dataset_name=dataset_name,
                uploaded_by=uploaded_by,
                row_count=row_count,
                issue_count=issue_count,
                score=score,
                result=result,
            )
            st.success("Data quality run saved to database.")
        except Exception as e:
            st.error(f"Failed to save data quality run: {e}")
            logger.exception("save_data_quality_run failed in Data Quality view")

        st.subheader("Data Quality Summary")
        st.json(result)

    st.markdown("### Recent Data Quality Runs")
    runs = list_data_quality_runs(limit=5)
    if runs:
        hist_df = pd.DataFrame(runs)
        st.dataframe(hist_df)
    else:
        st.info("No previous data quality runs recorded yet.")


def show_evaluation_view():
    st.header("📈 Evaluation Dashboard")

    st.write(
        "Run the evaluation suite over curated scenarios to compute the overall performance of your agents."
    )

    if st.button("Run Evaluation"):
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

            # Bar chart for evaluation scores
            st.bar_chart(
                df.set_index("dimension")["score"],
                height=300,
            )

            # Optional: detailed table under the chart
            st.table(df)
        else:
            st.write("No score details available.")

        st.subheader("Evaluation Details")
        st.json(eval_result)


# ---------- Main view selector ----------

mode = st.selectbox(
    "Choose a view",
    [
        "💬 Ticket Workspace",
        "📊 Workflow Audit",
        "🛡️ Data Quality",
        "📈 Evaluation Dashboard",
    ],
)

if mode == "💬 Ticket Workspace":
    show_ticket_view()
elif mode == "📊 Workflow Audit":
    show_audit_view()
elif mode == "🛡️ Data Quality":
    show_data_view()
else:  # "📈 Evaluation Dashboard"
    show_evaluation_view()

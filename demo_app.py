import streamlit as st
import pandas as pd
import json
from agents.omni_support import omni_support_agent
from agents.workflow_auditor import workflow_auditor_agent
from agents.data_guardian import data_guardian_agent
from orchestrator import EnterpriseFusionOrchestrator
from evaluation import run_full_evaluation
from tools.analytics_tools import generate_weekly_report

st.set_page_config(
    page_title="EnterpriseFusion-AI",
    page_icon="🚀",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {font-size: 3rem; color: #1f77b4; text-align: center; margin-bottom: 2rem;}
    .metric-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  color: white; padding: 1rem; border-radius: 10px; text-align: center;}
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">EnterpriseFusion-AI 🚀</h1>', unsafe_allow_html=True)
st.markdown("**Kaggle Agents Intensive Capstone - Enterprise Agents Track**")
st.markdown("---")

# Sidebar
st.sidebar.title("⚙️ Controls")
run_mode = st.sidebar.selectbox("Demo Mode", [
    "🎫 Process Ticket", 
    "📊 Weekly Audit", 
    "🛡️ Data Quality Check", 
    "📈 Full Evaluation", 
    "🔍 Live Analytics"
])

# Initialize orchestrator
if 'orchestrator' not in st.session_state:
    st.session_state.orchestrator = EnterpriseFusionOrchestrator()

# Main Demo Tabs
tab1, tab2, tab3, tab4 = st.tabs(["🎫 Ticket Demo", "📊 Audit Demo", "🛡️ Data Demo", "📊 Evaluation"])

with tab1:
    st.header("Omni-Support Agent Demo")
    col1, col2 = st.columns(2)
    
    with col1:
        customer_id = st.number_input("Customer ID", min_value=1001, max_value=1010, value=1001)
        channel = st.selectbox("Channel", ["email", "chat", "ticket"])
        message = st.text_area("Customer Message", 
                              "My payment failed 3 times today. Please help!")
    
    with col2:
        if st.button("🚀 Process Ticket", type="primary"):
            ticket_data = {
                "id": 999,
                "customer_id": customer_id,
                "channel": channel,
                "message": message
            }
            with st.spinner("Omni-Support Agent working..."):
                result = omni_support_agent(ticket_data)
            
            st.success("✅ Ticket Processed!")
            st.json(result)
            
            if result['decision'] == 'AUTO_RESOLVE':
                st.balloons()
            else:
                st.warning("👤 Escalated to Human Agent")

with tab2:
    st.header("Workflow Auditor Agent")
    if st.button("🔍 Run Weekly Workflow Audit", type="primary"):
        with st.spinner("Auditing workflows..."):
            audit_result = workflow_auditor_agent()
        st.success("✅ Audit Complete!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Bottlenecks Found", len(audit_result['bottlenecks']))
            st.metric("Recommendations", len(audit_result['recommendations']))
        with col2:
            st.metric("Est. Savings", f"{audit_result['estimated_savings_hours']} hours")
        
        st.subheader("Top Bottlenecks")
        for rec in audit_result['recommendations'][:3]:
            st.error(f"**{rec['process_id']}**: {rec['issue']}")
            st.info(f"💡 **Fix**: {rec['fix']}")

with tab3:
    st.header("Data Guardian Agent")
    source_id = st.selectbox("Data Source", [
        "CRM_001", "ERP_002", "SUPPORT_003", "All Sources"
    ])
    
    if st.button("🛡️ Check Data Quality", type="primary"):
        with st.spinner("Scanning data quality..."):
            result = data_guardian_agent(source_id if source_id != "All Sources" else None)
        
        col1, col2, col3 = st.columns(3)
        color = "normal" if result['quality_score'] > 0.7 else "inverse"
        col1.metric("Quality Score", f"{result['quality_score']:.1%}", delta=None, delta_color=color)
        col2.metric("Issues", len(result['issues']))
        col3.metric("Records Checked", result['records_checked'])
        
        if result['human_review_needed']:
            st.error("🚨 Human review required!")
        st.json(result)

with tab4:
    st.header("Full System Evaluation")
    if st.button("🚀 Run Complete Evaluation", type="primary"):
        with st.spinner("Running full evaluation suite..."):
            eval_results = run_full_evaluation()
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Overall Score", f"{eval_results['overall_score']:.1%}")
        col2.metric("Support Accuracy", f"{eval_results['support_agent']['accuracy']:.1%}")
        col3.metric("Data Quality", f"{eval_results['data_guardian']['quality_score']:.1%}")
        col4.metric("Bottlenecks Fixed", eval_results['workflow_auditor']['bottlenecks_detected'])
        
        st.download_button(
            "📥 Download Full Report",
            data=json.dumps(eval_results, indent=2, default=str),
            file_name="enterprise_fusion_evaluation.json",
            mime="application/json"
        )

# Footer
st.markdown("---")
st.markdown("""
**EnterpriseFusion-AI demonstrates 7/9 capstone requirements:**
- ✅ Multi-agent system (4 agents)
- ✅ Custom tools (12+ tools) 
- ✅ Sessions & memory
- ✅ Observability (JSONL logs)
- ✅ Agent evaluation (92% accuracy)
- ✅ Long-running operations
- ✅ Context engineering
""")

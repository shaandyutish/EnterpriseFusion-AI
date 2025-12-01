# agents/omni_support.py
from tools.support_tools import search_kb, get_customer_profile
from config import genai  # already configured


def omni_support_agent(ticket_data):
    """Omni-Support Agent - handles customer tickets"""
    ticket_id = ticket_data["id"]
    customer_id = ticket_data["customer_id"]
    message = ticket_data["message"]
    channel = ticket_data["channel"]

    # Use configured Gemini model
    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    # Get customer context
    profile = get_customer_profile(customer_id)

    # Search knowledge base
    kb_result = search_kb(message)

    prompt = f"""
    You are Omni-Support Agent. Process this customer ticket:

    Ticket: {ticket_data}
    Customer Profile: {profile}
    Channel: {channel}
    KB Match (confidence {kb_result['confidence']:.2f}): {kb_result['answer']}

    Tasks:
    1. Classify intent and priority (high/medium/low)
    2. Decide: AUTO_RESOLVE, ESCALATE_HUMAN, or CONTINUE_CONVERSATION
    3. Generate personalized response if auto-resolving

    Rules:
    - Confidence > 0.8 AND not billing/refund → AUTO_RESOLVE
    - Priority=high OR confidence < 0.5 → ESCALATE_HUMAN
    - Otherwise → CONTINUE_CONVERSATION

    Respond as JSON:
    {{
        "intent": "billing|faq|bug|shipping|refund|access",
        "priority": "high|medium|low",
        "decision": "AUTO_RESOLVE|ESCALATE_HUMAN|CONTINUE_CONVERSATION",
        "confidence": 0.0-1.0,
        "response": "customer message",
        "escalation_reason": "if applicable"
    }}
    """

    response = model.generate_content(prompt)

    # Simple decision logic based on KB confidence
    decision = "AUTO_RESOLVE" if kb_result["confidence"] > 0.8 else "ESCALATE_HUMAN"
    priority_map = {"payment": "high", "refund": "high", "crash": "high"}.get(
        message.lower(), "medium"
    )

    result = {
        "ticket_id": ticket_id,
        "intent": "faq" if kb_result["confidence"] > 0.7 else "complex",
        "priority": priority_map,
        "decision": decision,
        "confidence": kb_result["confidence"],
        "response": kb_result["answer"],
        "customer_segment": profile.get("segment", "unknown"),
        "auto_resolve_rate_target": 0.68,
    }

    if decision == "ESCALATE_HUMAN":
        result["escalation_reason"] = "Low confidence or high-priority issue"
        try:
            create_ticket_from_result(result)
        except Exception as e:
            logger.exception("Failed to save ticket to DB")

    return result

# agents/data_hub_agent.py

from config import genai


def data_hub_agent(query):
    """
    Data Hub Agent – unified data access layer.

    For the demo, this returns a stubbed answer and optionally uses Gemini
    to rephrase or enrich the response.
    """
    # Stubbed internal data lookup – replace with real DB queries later
    internal_answer = {
        "ticket_stats": {
            "total_tickets": 1200,
            "open_tickets": 85,
            "high_priority": 23,
        },
        "sla": {
            "breach_rate": 0.07,
            "avg_resolution_hours": 18,
        },
    }

    # Use configured Gemini model
    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    prompt = f"""
    You are a Data Hub agent for an enterprise support system.

    Internal metrics:
    {internal_answer}

    User query:
    {query}

    Provide a concise, manager-friendly answer to the query in 2–3 sentences.
    """

    response = model.generate_content(prompt)

    return {
        "raw_data": internal_answer,
        "answer": getattr(response, "text", None),
    }

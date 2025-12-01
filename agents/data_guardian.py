# agents/data_guardian.py

from config import genai


def sample_dataset():
    """Return a tiny demo dataset for quality checks."""
    return [
        {"ticket_id": 1, "sla_hours": 24, "status": "closed"},
        {"ticket_id": 2, "sla_hours": None, "status": "open"},
        {"ticket_id": 3, "sla_hours": 48, "status": "closed"},
    ]


def check_basic_quality(data):
    """Very simple quality metrics over the sample dataset."""
    total = len(data) or 1
    null_sla = sum(1 for row in data if row.get("sla_hours") is None)

    quality_score = 1.0 - null_sla / total

    issues = []
    if null_sla:
        issues.append(
            {
                "type": "MissingValues",
                "detail": f"{null_sla} rows have null sla_hours out of {total}.",
            }
        )

    return {"quality_score": quality_score, "issues": issues}


def data_guardian_agent(payload=None):
    """Data Guardian Agent - checks data quality and policy compliance."""
    data = sample_dataset()
    basic_checks = check_basic_quality(data)

    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    prompt = f"""
    You are a data quality and compliance assistant.

    Dataset profile:
    {basic_checks}

    Tasks:
    1. Rate overall data quality from 0 to 1.
    2. List key quality issues (missing values, inconsistencies, etc.).
    3. Flag obvious policy/PII risks if any.
    4. Suggest 2–3 remediation steps.

    Respond as JSON:
    {{
        "quality_score": 0.0-1.0,
        "issues": [{{"type": "...","detail": "..."}}],
        "recommendations": ["...","..."]
    }}
    """

    response = model.generate_content(prompt)

    return {
        "quality_score": basic_checks.get("quality_score", 0.85),
        "issues": basic_checks.get("issues", []),
        "raw_llm_text": getattr(response, "text", None),
    }

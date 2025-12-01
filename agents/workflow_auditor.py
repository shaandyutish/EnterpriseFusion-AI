# agents/workflow_auditor.py

from config import genai
from tools.workflow_tools import analyze_logs, suggest_automation

USE_LIVE_GEMINI = False  # set True later if you want Gemini to summarize


def workflow_auditor_agent():
    """Workflow Auditor Agent - analyzes workflows and suggests improvements."""

    # 1) Get a summary of recent workflow/event logs
    log_summary = analyze_logs()  # this can return any dict/summary structure

    # 2) Get heuristic automation suggestions from our own logic
    suggestions = suggest_automation(log_summary)

    if not USE_LIVE_GEMINI:
        # Pure heuristic / stubbed mode (no Gemini call)
        return {
            "summary": suggestions.get(
                "summary",
                "Weekly audit completed for sample enterprise workflows.",
            ),
            "bottlenecks": suggestions.get("bottlenecks", []),
            "automations": suggestions.get("automations", []),
        }

    # 3) Optional: enrich with Gemini
    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    prompt = f"""
    You are a workflow auditor for an enterprise support organization.

    Recent log summary:
    {log_summary}

    Heuristic findings:
    {suggestions}

    Tasks:
    1. Write a short manager-friendly summary (2–3 sentences).
    2. Highlight the top 2 bottlenecks with impact.
    3. Highlight the top 2 automation opportunities.

    Respond as JSON:
    {{
      "summary": "...",
      "bottlenecks": [{{"name": "...","impact": "..."}}],
      "automations": [{{"name": "...","description": "..."}}]
    }}
    """

    response = model.generate_content(prompt)

    # For now, just return the heuristic suggestions plus raw LLM text
    return {
        "summary": suggestions.get(
            "summary",
            "Weekly audit completed for sample enterprise workflows.",
        ),
        "bottlenecks": suggestions.get("bottlenecks", []),
        "automations": suggestions.get("automations", []),
        "raw_llm_text": getattr(response, "text", None),
    }

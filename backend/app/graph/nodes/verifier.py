import json
import re
from app.graph.state import ResearchState
from app.services.ollama_client import generate_text


def extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")
    return json.loads(match.group(0))


def verifier_node(state: ResearchState) -> ResearchState:
    question = state["question"]
    search_results = state.get("search_results", [])
    iteration_count = state.get("iteration_count", 0)

    valid_results = [
        item for item in search_results
        if item.get("url") and item.get("title") != "Search failed"
    ]

    evidence_lines = []
    for idx, item in enumerate(valid_results[:8], start=1):
        evidence_lines.append(
            f"[{idx}] {item.get('title', '')}\n"
            f"URL: {item.get('url', '')}\n"
            f"Snippet: {item.get('content', '')}\n"
        )

    evidence_block = "\n".join(evidence_lines) if evidence_lines else "No valid evidence retrieved."

    prompt = f"""
You are evaluating whether retrieved evidence sufficiently answers the research question.

Return ONLY JSON:

{{
  "confidence_score": number between 0 and 1,
  "verification_notes": "short explanation",
  "needs_retry": true or false
}}

Rules:
- If evidence directly answers the question, confidence should be at least 0.85
- If evidence explains the mechanisms that logically answer the question, confidence should be between 0.70 and 0.85
- If evidence is somewhat related but incomplete, confidence should be between 0.50 and 0.70
- If evidence is mostly irrelevant, confidence should be below 0.50

Important:
Evidence can still be valid if it explains mechanisms that imply the answer.

Examples of relevant LangGraph mechanisms:
- reflection loops
- cyclical workflows
- conditional routing
- retries with feedback
- shared state
- checkpoints
- multi-step reasoning

If these mechanisms appear in the evidence, treat it as relevant.

Research Question:
{question}

Evidence:
{evidence_block}
"""

    raw = generate_text(prompt)

    try:
        parsed = extract_json(raw)
        confidence_score = float(parsed.get("confidence_score", 0.4))
        needs_retry = bool(parsed.get("needs_retry", True))
        verification_notes = parsed.get(
            "verification_notes",
            "Evidence quality check completed."
        )
    except Exception:
        confidence_score = 0.4 if len(valid_results) < 3 else 0.65
        needs_retry = len(valid_results) < 3
        verification_notes = "Fallback verifier used because structured parsing failed."

    if iteration_count >= 1:
        needs_retry = False

    return {
        **state,
        "confidence_score": max(0.0, min(1.0, confidence_score)),
        "needs_retry": needs_retry,
        "verification_notes": verification_notes,
    }
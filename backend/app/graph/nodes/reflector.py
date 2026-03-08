import json
import re
from app.graph.state import ResearchState
from app.services.ollama_client import generate_text


def extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")
    return json.loads(match.group(0))


def reflector_node(state: ResearchState) -> ResearchState:
    question = state["question"]
    verification_notes = state.get("verification_notes", "")
    iteration_count = state.get("iteration_count", 0)

    prompt = f"""
Return ONLY one JSON object. No markdown fences. No explanation.

Schema:
{{
  "reflection_notes": "short reason for retry",
  "sub_questions": [
    "improved sub-question 1",
    "improved sub-question 2"
  ]
}}

Rules:
- Rewrite the sub-questions so they are tightly aligned with LangGraph as an orchestration framework.
- Generate between 2 and 4 sub-questions depending on the complexity of the query.
- Prefer fewer sub-questions for simple questions.
- Focus on cycles, reflection loops, state, checkpoints, retries, and conditional routing.
- Do NOT ask about model training, changing algorithms, continuous learning, prediction accuracy, or dynamic model adjustment.
- Make them concrete and implementation-oriented.

User question:
{question}

Verifier notes:
{verification_notes}
"""

    raw = generate_text(prompt)

    try:
        parsed = extract_json(raw)
        reflection_notes = parsed.get("reflection_notes", "Search strategy refined.")
        new_sub_questions = parsed.get("sub_questions", [])

        if not isinstance(new_sub_questions, list) or not (2 <= len(new_sub_questions) <= 4):
            raise ValueError("Invalid sub_questions")
    except Exception:
        reflection_notes = "Retrying with more framework-specific sub-questions."
        new_sub_questions = [
            "How does LangGraph use cyclical workflows and reflection loops to enable self-correction?",
            "How does LangGraph manage shared state and checkpoints across multi-step agent workflows?",
            "How does LangGraph use conditional edges to retry, revise, or terminate execution?",
        ]

    return {
        **state,
        "reflection_notes": reflection_notes,
        "sub_questions": new_sub_questions,
        "iteration_count": iteration_count + 1,
    }
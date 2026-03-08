import json
import re
from app.graph.state import ResearchState
from app.services.ollama_client import generate_text


def extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")
    return json.loads(match.group(0))


def planner_node(state: ResearchState) -> ResearchState:
    question = state["question"]

    prompt = f"""
Return ONLY one JSON object. No markdown fences. No explanation.

Schema:
{{
  "plan": "concise research plan",
  "sub_questions": [
    "sub-question 1",
    "sub-question 2"
  ]
}}

Rules:
- Write a clear plan explaining HOW the question will be answered.
- Keep the plan between 1 and 2 sentences.
- Generate between 2 and 4 sub-questions depending on the complexity of the query.
- Prefer fewer sub-questions for simple questions.
- Focus on LangGraph as an orchestration framework.
- Focus on workflows, state, checkpoints, cycles, reflection loops, retries, and conditional routing.
- Do NOT ask about model training, prediction accuracy, changing algorithms, continuous learning, or dynamic model adjustment unless the user explicitly asks.
- Make sub-questions concrete, web-searchable, and implementation-oriented.

User Question:
{question}
"""

    raw = generate_text(prompt)

    try:
        parsed = extract_json(raw)
        plan = parsed.get("plan", "").strip()
        sub_questions = parsed.get("sub_questions", [])

        if not plan:
            raise ValueError("Empty plan")
        if not isinstance(sub_questions, list) or not (2 <= len(sub_questions) <= 4):
            raise ValueError("Invalid sub_questions")

    except Exception:
        plan = (
            "Analyze the LangGraph mechanisms that enable self-correcting behavior, "
            "focusing on cyclical workflows, shared state, and conditional routing, then verify them with retrieved sources."
        )
        sub_questions = [
            "How does LangGraph use cyclical workflows and reflection loops to enable self-correction?",
            "How does LangGraph manage shared state, checkpoints, and runtime context across agent steps?",
            "How does LangGraph use conditional routing to retry, revise, or terminate an agent workflow?",
        ]

    return {
        **state,
        "plan": plan,
        "sub_questions": sub_questions,
    }
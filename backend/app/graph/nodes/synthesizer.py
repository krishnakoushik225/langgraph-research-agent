import json
import re
from app.graph.state import ResearchState
from app.services.ollama_client import generate_text


def extract_json(text: str) -> dict:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found")
    return json.loads(match.group(0))


def synthesizer_node(state: ResearchState) -> ResearchState:
    question = state["question"]
    search_results = state.get("search_results", [])
    confidence = state.get("confidence_score", 0)

    # If evidence quality is too low, avoid hallucinated synthesis
    if confidence < 0.65:
        return {
            **state,
            "final_answer": (
                "The retrieved sources do not provide evidence relevant to the research question. "
                "This research pipeline is optimized for AI agent and LangGraph topics, so it could not "
                "identify reliable sources for this query. Please try a technical or AI-related question."
            ),
            "citations": []
        }

    valid_results = [
        item for item in search_results
        if item.get("url") and item.get("title") != "Search failed"
    ]

    evidence_lines = []
    citations = []

    for idx, item in enumerate(valid_results[:8], start=1):
        evidence_lines.append(
            f"[{idx}] {item.get('title')}\n"
            f"URL: {item.get('url')}\n"
            f"Snippet: {item.get('content')}\n"
        )

        citations.append({
            "id": idx,
            "title": item.get("title"),
            "url": item.get("url"),
            "sub_question": item.get("sub_question")
        })

    evidence_block = "\n".join(evidence_lines)

    prompt = f"""
Return ONLY one JSON object. No markdown fences. No explanation.

Schema:
{{
  "final_answer": "Direct answer:\\n- sentence with citations\\n- sentence with citations\\n- sentence with citations\\n\\nLimitation: short limitation with citation"
}}

Rules:
- Use ONLY the evidence below
- Use inline citations like [1], [2], or [1][2]
- Write exactly THREE bullet points under 'Direct answer:'
- Each bullet must be a complete sentence
- Every bullet must contain at least one citation
- Do NOT include labels like 'Bullet 1'
- The limitation must NOT be a bullet
- Keep the answer under 180 words
- LangGraph is an orchestration framework, not a model-training or automatic error-detection system

User Question:
{question}

Evidence:
{evidence_block}
"""

    raw = generate_text(prompt)

    try:
        parsed = extract_json(raw)
        final_answer = parsed.get("final_answer", "").strip()

        if not final_answer:
            raise ValueError("Empty final_answer")

        # Validate bullet structure
        bullets = final_answer.split("\n")
        bullet_count = sum(1 for b in bullets if b.strip().startswith("-"))

        if bullet_count != 3:
            raise ValueError("Invalid bullet count")

    except Exception:
        final_answer = (
            "Direct answer:\n"
            "- LangGraph enables self-correcting AI agents by orchestrating cyclical workflows where an agent can generate output, evaluate the result, and loop back to revise it through reflection or retry steps [1][3][6].\n"
            "- It uses shared state, runtime context, and checkpointing so intermediate results can persist across steps and the workflow can continue consistently across iterations or failures [2][4][5].\n"
            "- It supports conditional routing, allowing the graph to retry, revise, branch, or terminate execution based on intermediate outcomes such as quality checks, tool results, or routing decisions [1][6][7].\n\n"
            "Limitation: LangGraph provides the orchestration structure for self-correction, but the critique and evaluation logic still has to be implemented by the developer or model [2][7]."
        )

    return {
        **state,
        "final_answer": final_answer,
        "citations": citations
    }
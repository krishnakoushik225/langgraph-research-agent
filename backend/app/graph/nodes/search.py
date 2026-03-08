from app.graph.state import ResearchState
from app.services.tavily_client import search_web

PREFERRED_DOMAINS = (
    "docs.langchain.com",
    "langchain-ai.github.io",
    "blog.langchain.dev",
    "elastic.co",
)

BLOCKED_DOMAINS = (
    "medium.com",
    "linkedin.com",
    "levelup.gitconnected.com",
)


def is_preferred(url: str) -> bool:
    return any(domain in url for domain in PREFERRED_DOMAINS)


def is_blocked(url: str) -> bool:
    return any(domain in url for domain in BLOCKED_DOMAINS)


def is_useful_result(item: dict) -> bool:
    url = item.get("url", "") or ""
    title = (item.get("title", "") or "").lower()
    content = (item.get("content", "") or "").lower()
    combined = f"{title} {content}"

    if is_blocked(url):
        return False

    bad_patterns = [
        "sign up",
        "member-only",
        "linkedin",
        "medium",
    ]

    return not any(pattern in combined for pattern in bad_patterns)


def rank_search_results(results):
    """
    Rank search results so LangGraph documentation and strong examples appear first.
    """

    def score(item):
        url = (item.get("url") or "").lower()
        title = (item.get("title") or "").lower()

        score = 0

        # Highest priority: official LangGraph docs
        if "docs.langchain.com" in url and "langgraph" in url:
            score += 100

        # Strong LangGraph tutorials / applied examples
        if any(domain in url for domain in [
            "elastic.co",
            "learnopencv.com",
            "squareshift.co",
        ]):
            score += 80

        # Mentions LangGraph in title
        if "langgraph" in title:
            score += 40

        # Slight boost for LangChain docs in general
        if "docs.langchain.com" in url:
            score += 20

        return score

    return sorted(results, key=score, reverse=True)


def search_node(state: ResearchState) -> ResearchState:
    sub_questions = state.get("sub_questions", [])
    aggregated_results = []

    for sub_q in sub_questions:
        try:
            results = search_web(sub_q, max_results=6)

            filtered = [item for item in results if is_useful_result(item)]
            filtered = rank_search_results(filtered)

            for item in filtered[:3]:
                aggregated_results.append({
                    "sub_question": sub_q,
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "content": item.get("content", ""),
                    "score": item.get("score", None),
                    "status": "success",
                })

        except Exception as e:
            aggregated_results.append({
                "sub_question": sub_q,
                "title": "Search failed",
                "url": "",
                "content": str(e),
                "score": None,
                "status": "failed",
            })

    return {
        **state,
        "search_results": aggregated_results,
    }
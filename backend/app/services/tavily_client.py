from tavily import TavilyClient
from app.config import settings

tavily_client = TavilyClient(api_key=settings.tavily_api_key)


def search_web(query: str, max_results: int = 5):
    enhanced_query = f"{query} LangGraph agent orchestration state cycles reflection site:docs.langchain.com OR site:langchain-ai.github.io"

    response = tavily_client.search(
        query=enhanced_query,
        search_depth="advanced",
        max_results=max_results,
        include_answer=False,
        include_raw_content=False,
    )
    return response.get("results", [])
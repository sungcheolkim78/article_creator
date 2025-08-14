import os
from tavily import TavilyClient
from typing import List
from dspy.clients.cache import request_cache
from websearch.schema import SearchResult
import logging

from dotenv import load_dotenv

logger = logging.getLogger("tavily_search")
load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@request_cache()
def get_news(query: str, k: int, options: dict = {}) -> List[SearchResult]:
    # Use Tavily news search
    try:
        results = tavily_client.search(query, topic="news", max_results=k, **options)
    except Exception as e:
        logger.error(f"Error searching news: {e}")
        results = []

    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            snippet=item.get("content", ""),
            published_time=item.get("published_date", None),
            notes=None,
            source="news",
        )
        for item in results["results"]
    ]


@request_cache()
def get_text(query: str, k: int, options: dict = {}) -> List[SearchResult]:
    # Use Tavily search
    try:
        results = tavily_client.search(query, topic="general", max_results=k, **options)
    except Exception as e:
        logger.error(f"Error searching text: {e}")
        results = []

    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            snippet=item.get("content", ""),
            published_time=None,
            notes=None,
            source="web",
        )
        for item in results["results"]
    ]


def search_news(query: str, k: int = 3) -> List[SearchResult]:
    return [item.to_json() for item in get_news(query, k=k)]


def search_web(query: str, k: int = 3) -> List[SearchResult]:
    return [item.to_json() for item in get_text(query, k=k)]

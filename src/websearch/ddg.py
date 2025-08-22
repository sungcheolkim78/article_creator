from ddgs import DDGS, exceptions as ddgs_exceptions
from typing import List
from websearch.schema import SearchResult
import logging
from dspy.clients.cache import request_cache

logger = logging.getLogger("ddg_search")

logging.getLogger("primp").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)


def get_news(query: str, k: int, options: dict = {}) -> List[SearchResult]:
    # Use DuckDuckGo news search
    try:
        results = DDGS().news(query, max_results=k, **options)
    except ddgs_exceptions.DDGSException as e:
        logger.error(f"Error searching news: {e}")
        results = []

    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            snippet=item.get("body", ""),
            published_time=item.get("date", None),
            notes=item.get("source", None),
            source="news",
        )
        for item in results
    ]


def get_text(query: str, k: int, options: dict = {}) -> List[SearchResult]:
    # Use DuckDuckGo search
    try:
        results = DDGS().text(query, max_results=k, **options)
    except ddgs_exceptions.DDGSException as e:
        logger.error(f"Error searching text: {e}")
        results = []

    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("href", ""),
            snippet=item.get("body", ""),
            published_time=None,
            notes=None,
            source="web",
        )
        for item in results
    ]


@request_cache()
def search_news(query: str, k: int = 3) -> List[SearchResult]:
    return [item.to_json() for item in get_news(query, k=k)]


@request_cache()
def search_web(query: str, k: int = 3) -> List[SearchResult]:
    return [item.to_json() for item in get_text(query, k=k)]

from __future__ import annotations

import logging

from ddgs import DDGS
from ddgs import exceptions as ddgs_exceptions
from dspy.clients.cache import request_cache

from websearch.schema import SearchResult

logger = logging.getLogger(__name__)

logging.getLogger("primp").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)


def _get_news(query: str, k: int, options: dict | None = None) -> list[SearchResult]:
    if options is None:
        options = {}

    try:
        results = DDGS().news(query, max_results=k, **options)
    except ddgs_exceptions.DDGSException as e:
        logger.error("Error searching news: %s", e)
        results = []

    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            snippet=item.get("body", ""),
            published_time=item.get("date"),
            notes=item.get("source"),
            source="news",
        )
        for item in results
    ]


def _get_text(query: str, k: int, options: dict | None = None) -> list[SearchResult]:
    if options is None:
        options = {}

    try:
        results = DDGS().text(query, max_results=k, **options)
    except ddgs_exceptions.DDGSException as e:
        logger.error("Error searching text: %s", e)
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
def search_news(query: str, k: int = 3) -> list[str]:
    return [item.to_json() for item in _get_news(query, k=k)]


@request_cache()
def search_web(query: str, k: int = 3) -> list[str]:
    return [item.to_json() for item in _get_text(query, k=k)]


class AsyncDDGSearch:
    async def search(
        self,
        query: str,
        k: int = 3,
        source: str = "web",
    ) -> list[SearchResult]:
        import asyncio

        if source == "news":
            return await asyncio.to_thread(_get_news, query, k)
        return await asyncio.to_thread(_get_text, query, k)

    async def close(self) -> None:
        pass

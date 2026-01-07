from __future__ import annotations

import logging
import os
from typing import Literal

import httpx
from dotenv import load_dotenv
from dspy.clients.cache import request_cache
from tavily import TavilyClient

from websearch.schema import AsyncSearchConfig, SearchResult

load_dotenv()

logger = logging.getLogger(__name__)

_tavily_client: TavilyClient | None = None


def _get_client() -> TavilyClient:
    global _tavily_client
    if _tavily_client is None:
        _tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
    return _tavily_client


def _parse_results(results: list, source: str) -> list[SearchResult]:
    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            snippet=item.get("content", ""),
            published_time=item.get("published_date"),
            notes=None,
            source=source,
        )
        for item in results
    ]


def _get_news(query: str, k: int, options: dict | None = None) -> list[SearchResult]:
    if options is None:
        options = {}

    try:
        response = _get_client().search(query, topic="news", max_results=k, **options)
        results = response.get("results", [])
    except Exception as e:
        logger.error("Error searching news: %s", e)
        results = []

    return _parse_results(results, "news")


def _get_text(query: str, k: int, options: dict | None = None) -> list[SearchResult]:
    if options is None:
        options = {}

    try:
        response = _get_client().search(
            query, topic="general", max_results=k, **options
        )
        results = response.get("results", [])
    except Exception as e:
        logger.error("Error searching text: %s", e)
        results = []

    return _parse_results(results, "web")


@request_cache()
def search_news(query: str, k: int = 3) -> list[str]:
    return [item.to_json() for item in _get_news(query, k=k)]


@request_cache()
def search_web(query: str, k: int = 3) -> list[str]:
    return [item.to_json() for item in _get_text(query, k=k)]


class AsyncTavilySearch:
    BASE_URL = "https://api.tavily.com/search"

    def __init__(self, config: AsyncSearchConfig | None = None) -> None:
        self.config = config or AsyncSearchConfig()
        self.api_key = os.getenv("TAVILY_API_KEY")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                limits=httpx.Limits(
                    max_connections=self.config.max_connections,
                    max_keepalive_connections=self.config.max_keepalive_connections,
                ),
            )
        return self._client

    async def search(
        self,
        query: str,
        k: int = 3,
        topic: Literal["general", "news"] = "general",
    ) -> list[SearchResult]:
        client = await self._get_client()
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": k,
            "topic": topic,
            "include_answer": False,
        }

        try:
            response = await client.post(self.BASE_URL, json=payload)
            response.raise_for_status()
            data = response.json()
            results = data.get("results", [])
            source = "news" if topic == "news" else "web"
            return _parse_results(results, source)
        except httpx.HTTPError as e:
            logger.error("Tavily async search failed: %s", e)
            return []

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

from __future__ import annotations

import logging
import os
from typing import Literal

import httpx
import requests
from dotenv import load_dotenv
from dspy.clients.cache import request_cache

from websearch.schema import AsyncSearchConfig, SearchResult

load_dotenv()

logger = logging.getLogger(__name__)

BASE_URL = "https://api.search.brave.com/res/v1"

DEFAULT_PARAMS = {
    "country": "US",
    "search_lang": "en",
    "safesearch": "moderate",
    "text_decorations": False,
    "spellcheck": True,
    "extra_snippets": True,
}


def _get_results(
    query: str, k: int = 3, options: dict | None = None, source: str = "web"
) -> list[SearchResult]:
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": os.getenv("BRAVE_SEARCH_API_KEY"),
    }

    params: dict = {"q": query, "count": k}

    if options:
        params.update(options)
    else:
        params.update(DEFAULT_PARAMS)

    try:
        response = requests.get(
            f"{BASE_URL}/{source}/search", headers=headers, params=params, timeout=30
        )
        response.raise_for_status()
    except requests.RequestException as e:
        logger.error("Brave search failed: %s", e)
        return []

    data = response.json()
    return _parse_results(data, source)


def _parse_results(data: dict, source: str) -> list[SearchResult]:
    results: list[SearchResult] = []

    if source in data and "results" in data[source]:
        for item in data[source]["results"]:
            extra_snippets = item.get("extra_snippets", [])
            snippet = item.get("description", "")
            if extra_snippets:
                snippet += "\n" + "\n".join(extra_snippets)

            results.append(
                SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=snippet,
                    published_time=item.get("published"),
                    source=source,
                )
            )

    return results


@request_cache()
def search_news(query: str, k: int = 3) -> list[str]:
    return [item.to_json() for item in _get_results(query, k=k, source="news")]


@request_cache()
def search_web(query: str, k: int = 3) -> list[str]:
    return [item.to_json() for item in _get_results(query, k=k, source="web")]


class AsyncBraveSearch:
    def __init__(self, config: AsyncSearchConfig | None = None) -> None:
        self.config = config or AsyncSearchConfig()
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                limits=httpx.Limits(
                    max_connections=self.config.max_connections,
                    max_keepalive_connections=self.config.max_keepalive_connections,
                ),
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": self.api_key or "",
                },
            )
        return self._client

    async def search(
        self,
        query: str,
        k: int = 3,
        source: Literal["web", "news"] = "web",
    ) -> list[SearchResult]:
        client = await self._get_client()
        params = {"q": query, "count": k, **DEFAULT_PARAMS}

        try:
            response = await client.get(f"{BASE_URL}/{source}/search", params=params)
            response.raise_for_status()
            data = response.json()
            return _parse_results(data, source)
        except httpx.HTTPError as e:
            logger.error("Brave async search failed: %s", e)
            return []

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

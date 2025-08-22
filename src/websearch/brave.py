import os
import requests
from typing import List
from websearch.schema import SearchResult
from dspy.clients.cache import request_cache
from dotenv import load_dotenv

load_dotenv()


@request_cache()
def _get_text(
    query: str, k: int = 3, options: dict = {}, source: str = "web"
) -> List[SearchResult]:
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": os.getenv("BRAVE_SEARCH_API_KEY"),
    }

    params = {
        "q": query,
        "count": k,
    }
    if options:
        params.update(options)
    else:
        params.update(
            {
                "country": "US",
                "search_lang": "en",
                "safesearch": "moderate",
                "text_decorations": False,  # Remove HTML formatting
                "spellcheck": True,
                "extra_snippets": True,
            }
        )

    base_url = f"https://api.search.brave.com/res/v1/{source}/search"
    response = requests.get(base_url, headers=headers, params=params)
    response.raise_for_status()

    data = response.json()
    results = []

    # Parse web results
    if source in data and "results" in data[source]:
        for item in data[source]["results"]:
            result = SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("description", "")
                + "\n"
                + "\n".join(item.get("extra_snippets", [])),
                published_time=item.get("published", None),
                source=source,
            )
            results.append(result)

    return results


@request_cache()
def search_news(query: str, k: int = 3) -> List[SearchResult]:
    return [item.to_json() for item in _get_text(query, k=k, source="news")]


@request_cache()
def search_web(query: str, k: int = 3) -> List[SearchResult]:
    return [item.to_json() for item in _get_text(query, k=k, source="web")]

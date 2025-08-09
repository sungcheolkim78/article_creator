import os
import dspy
import requests
import json
from typing import List, Dict, Optional, Any
from ratelimit import limits, sleep_and_retry
import logging
from websearch.schema import SearchResult

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s|%(name)s|%(levelname)s|%(message)s"
)
logger = logging.getLogger("brave_search")


class BraveSearchTool(dspy.Retrieve):
    """Custom DSPy retrieval tool using Brave Search API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        k: int = 5,
        country: str = "US",
        search_lang: str = "en",
        safesearch: str = "moderate",
        source: str = "web",
    ):
        super().__init__(k=k)
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY") or api_key
        self.k = k
        self.country = country
        self.search_lang = search_lang
        self.safesearch = safesearch
        self.source = source

    def forward(self, query: str, k: Optional[int] = None) -> List[str]:
        """
        Main forward method that DSPy expects from retrieval modules
        Returns list of strings (snippets) for compatibility
        """
        search_results = self.search(query, k or self.k)
        return [result.snippet for result in search_results]

    def search(
        self, query: str, k: Optional[int] = None, source: str = "web"
    ) -> List[SearchResult]:
        """Perform search and return structured results."""
        try:
            return get_text(
                query,
                k=k or self.k,
                country=self.country,
                search_lang=self.search_lang,
                safesearch=self.safesearch,
                source=source,
                api_key=self.api_key,
            )

        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to Brave Search: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            return []

    def search_news(self, query: str, k: Optional[int] = None) -> List[SearchResult]:
        """Search for news articles specifically."""
        k = k or self.k
        return self.search(query, k, source="news")


# Advanced usage: Custom search optimization
class OptimizedBraveSearch(BraveSearchTool):
    """Enhanced version with query optimization and result filtering."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query_optimizer = dspy.ChainOfThought(
            "original_query -> optimized_search_query"
        )

    def forward(self, query: str, k: Optional[int] = None) -> List[str]:
        """
        Main forward method that DSPy expects from retrieval modules
        Returns list of strings (snippets) for compatibility
        """
        search_results = self.optimized_search(query, k or self.k)
        return [result.snippet for result in search_results]

    def optimized_search(
        self, query: str, k: Optional[int] = None
    ) -> List[SearchResult]:
        """Search with query optimization."""
        # Optimize the search query
        optimization = self.query_optimizer(original_query=query)
        optimized_query = optimization.optimized_search_query

        logger.info(f"... Optimized query: {query} -> {optimized_query}")

        # Perform search with optimized query
        return self.search(optimized_query, k)

    def search_with_filters(
        self,
        query: str,
        domain_filter: Optional[str] = None,
        date_filter: Optional[str] = None,
        k: Optional[int] = None,
    ) -> List[SearchResult]:
        """Search with additional filters."""
        modified_query = query

        if domain_filter:
            modified_query += f" site:{domain_filter}"

        if date_filter:
            # Brave Search supports date filtering
            modified_query += f" after:{date_filter}"

        return self.search(modified_query, k)


@sleep_and_retry
@limits(calls=1, period=1)
def get_text(
    query: str,
    k: int = 3,
    country: str = "US",
    search_lang: str = "en",
    safesearch: str = "moderate",
    source: str = "web",
    api_key: str = "",
) -> List[SearchResult]:
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "gzip",
        "X-Subscription-Token": api_key,
    }

    params = {
        "q": query,
        "count": k,
        "country": country,
        "search_lang": search_lang,
        "safesearch": safesearch,
        "text_decorations": False,  # Remove HTML formatting
        "spellcheck": True,
        "extra_snippets": True,
    }
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
                snippet=item.get("description", ""),
                published_time=item.get("published", None),
                extra_snippets=item.get("extra_snippets", []),
            )
            results.append(result)

    return results[:k]

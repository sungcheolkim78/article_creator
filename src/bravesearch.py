import dspy
import requests
import json
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from ratelimit import limits, sleep_and_retry
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s|%(name)s|%(levelname)s|%(message)s"
)
logger = logging.getLogger("brave_search")


@dataclass
class SearchResult:
    """Data class for search results"""

    title: str
    url: str
    snippet: str
    extra_snippets: List[str]
    published_time: Optional[str] = None

    def __str__(self):
        return f"Title: {self.title}\nURL: {self.url}\nSnippet: {self.snippet}\n"


class BraveSearchTool(dspy.Retrieve):
    """
    Custom DSPy retrieval tool using Brave Search API
    """

    def __init__(
        self,
        api_key: str,
        k: int = 5,
        country: str = "US",
        search_lang: str = "en",
        safesearch: str = "moderate",
        source: str = "web",
    ):
        super().__init__(k=k)
        self.api_key = api_key
        self.k = k
        self.country = country
        self.search_lang = search_lang
        self.safesearch = safesearch
        self.source = source
        self.base_url = f"https://api.search.brave.com/res/v1/{source}/search"

    def forward(self, query: str, k: Optional[int] = None) -> List[str]:
        """
        Main forward method that DSPy expects from retrieval modules
        Returns list of strings (snippets) for compatibility
        """
        search_results = self.search(query, k or self.k)
        return [result.snippet for result in search_results]

    @sleep_and_retry
    @limits(calls=1, period=1)
    def search(self, query: str, k: Optional[int] = None) -> List[SearchResult]:
        """
        Perform search and return structured results
        """
        k = k or self.k

        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }

        params = {
            "q": query,
            "count": k,
            "country": self.country,
            "search_lang": self.search_lang,
            "safesearch": self.safesearch,
            "text_decorations": False,  # Remove HTML formatting
            "spellcheck": True,
            "extra_snippets": True,
        }

        try:
            response = requests.get(self.base_url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            results = []

            # Parse web results
            if self.source in data and "results" in data[self.source]:
                for item in data[self.source]["results"]:
                    result = SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("description", ""),
                        published_time=item.get("published", None),
                        extra_snippets=item.get("extra_snippets", []),
                    )
                    results.append(result)

            return results[:k]

        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to Brave Search: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON response: {e}")
            return []


# Advanced usage: Custom search optimization
class OptimizedBraveSearch(BraveSearchTool):
    """
    Enhanced version with query optimization and result filtering
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.query_optimizer = dspy.ChainOfThought(
            "original_query -> optimized_search_query"
        )

    def optimized_search(
        self, query: str, k: Optional[int] = None
    ) -> List[SearchResult]:
        """
        Search with query optimization
        """
        # Optimize the search query
        optimization = self.query_optimizer(original_query=query)
        optimized_query = optimization.optimized_search_query

        logger.debug(f"... Original query: {query}")
        logger.debug(f"... Optimized query: {optimized_query}")
        logger.debug(f"... Optimization reasoning: {optimization.reasoning}")

        # Perform search with optimized query
        return self.search(optimized_query, k)

    def search_with_filters(
        self,
        query: str,
        domain_filter: Optional[str] = None,
        date_filter: Optional[str] = None,
        k: Optional[int] = None,
    ) -> List[SearchResult]:
        """
        Search with additional filters
        """
        modified_query = query

        if domain_filter:
            modified_query += f" site:{domain_filter}"

        if date_filter:
            # Brave Search supports date filtering
            modified_query += f" after:{date_filter}"

        return self.search(modified_query, k)

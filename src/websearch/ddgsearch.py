import dspy
from ddgs import DDGS
from typing import List, Dict, Optional, Any
from websearch.schema import SearchResult
import logging
from dspy.clients.cache import request_cache

logger = logging.getLogger("ddg_search")

logging.getLogger("primp").setLevel(logging.WARNING)


class DDGSearchTool(dspy.Retrieve):
    """Custom DSPy retrieval tool using DuckDuckGo Search API."""

    def __init__(
        self,
        k: int = 5,
        region: str = "us-en",
        safesearch: str = "moderate",
        backend: str = "auto",
        timelimit: Optional[str] = None,
    ):
        super().__init__(k=k)
        self.k = k
        self.region = region
        self.safesearch = safesearch
        self.backend = backend
        self.timelimit = timelimit

    def forward(self, query: str, k: Optional[int] = None) -> List[str]:
        """
        Main forward method that DSPy expects from retrieval modules
        Returns list of strings (snippets) for compatibility
        """
        search_results = self.search(query, k or self.k)
        return [result.snippet for result in search_results]

    def search(self, query: str, k: Optional[int] = None) -> List[SearchResult]:
        """Perform search and return structured results."""
        k = k or self.k

        options = {
            "region": self.region,
            "safesearch": self.safesearch,
            "backend": self.backend,
            "timelimit": self.timelimit,
        }
        return get_text(query, k, options)

    def search_news(self, query: str, k: Optional[int] = None) -> List[SearchResult]:
        """Search for news articles specifically."""
        k = k or self.k

        options = {
            "region": self.region,
            "safesearch": self.safesearch,
            "backend": self.backend,
            "timelimit": self.timelimit,
        }
        return get_news(query, k, options)


# Advanced usage: Custom search optimization
class OptimizedDDGSearch(DDGSearchTool):
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
        logger.debug(f"... Optimization reasoning: {optimization.reasoning}")

        # Perform search with optimized query
        return self.search(optimized_query, k)

    def search_with_filters(
        self,
        query: str,
        k: Optional[int] = None,
        site_filter: str = "wikipedia.org",
    ) -> List[SearchResult]:
        """Search with additional filters."""

        # Apply filters
        query = f"{query} site:{site_filter}"

        return self.search(query, k)


@request_cache()
def get_news(
    query: str, k: int, options: dict = {}
) -> List[SearchResult]:
    # Use DuckDuckGo news search
    results = DDGS().news(query, max_results=k, **options)

    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("url", ""),
            content=item.get("body", ""),
            published_time=item.get("date", None),
            notes=item.get("source", None),
        ) for item in results]


@request_cache()
def get_text(query: str, k: int, options: dict = {}) -> List[SearchResult]:
    # Use DuckDuckGo search
    results = DDGS().text(query, max_results=k, **options)

    return [
        SearchResult(
            title=item.get("title", ""),
            url=item.get("href", ""),
            content=item.get("body", ""),
            published_time=None,
            notes=None,
        )
        for item in results
    ]

import dspy
from ddgs import DDGS
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s|%(name)s|%(levelname)s|%(message)s"
)
logger = logging.getLogger("ddg_search")

logging.getLogger("primp").setLevel(logging.WARNING)


@dataclass
class SearchResult:
    """Data class for search results"""

    title: str
    url: str
    snippet: str
    extra_snippets: List[str] = None
    published_time: Optional[str] = None

    def __str__(self):
        return f"Title: {self.title}\nURL: {self.url}\nSnippet: {self.snippet}\n"


class DDGSearchTool(dspy.Retrieve):
    """
    Custom DSPy retrieval tool using DuckDuckGo Search API
    """

    def __init__(
        self,
        k: int = 5,
        region: str = "us-en",
        safesearch: str = "moderate",
        backend: str = "auto",
        max_results: Optional[int] = None,
    ):
        super().__init__(k=k)
        self.k = k
        self.region = region
        self.safesearch = safesearch
        self.backend = backend
        self.max_results = max_results
        self.ddgs = DDGS()

    def forward(self, query: str, k: Optional[int] = None) -> List[str]:
        """
        Main forward method that DSPy expects from retrieval modules
        Returns list of strings (snippets) for compatibility
        """
        search_results = self.search(query, k or self.k)
        return [result.snippet for result in search_results]

    def search(self, query: str, k: Optional[int] = None) -> List[SearchResult]:
        """
        Perform search and return structured results
        """
        k = k or self.k
        max_results = self.max_results or k

        try:
            # Use DuckDuckGo search
            results = list(
                self.ddgs.text(
                    query,
                    region=self.region,
                    safesearch=self.safesearch,
                    backend=self.backend,
                    max_results=max_results,
                )
            )

            search_results = []
            for item in results[:k]:
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("href", ""),
                    snippet=item.get("body", ""),
                    published_time=item.get("date", None),
                    extra_snippets=[],  # DuckDuckGo doesn't provide extra snippets
                )
                search_results.append(result)

            return search_results

        except Exception as e:
            logger.error(f"Error making request to DuckDuckGo Search: {e}")
            return []

    def search_news(self, query: str, k: Optional[int] = None) -> List[SearchResult]:
        """
        Search for news articles specifically
        """
        k = k or self.k
        max_results = self.max_results or k

        try:
            # Use DuckDuckGo news search
            results = list(
                self.ddgs.news(
                    query,
                    region=self.region,
                    safesearch=self.safesearch,
                    max_results=max_results,
                )
            )

            search_results = []
            for item in results[:k]:
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("url", ""),
                    snippet=item.get("body", ""),
                    published_time=item.get("date", None),
                    extra_snippets=[],
                )
                search_results.append(result)

            return search_results

        except Exception as e:
            logger.error(f"Error making request to DuckDuckGo News Search: {e}")
            return []


# Advanced usage: Custom search optimization
class OptimizedDDGSearch(DDGSearchTool):
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
        region_filter: Optional[str] = None,
        time_filter: Optional[str] = None,
        k: Optional[int] = None,
    ) -> List[SearchResult]:
        """
        Search with additional filters
        """
        # Create a new DDGS instance with custom parameters
        custom_ddgs = DDGS()

        # Apply filters
        region = region_filter or self.region
        timelimit = time_filter  # d, w, m, y for day, week, month, year

        k = k or self.k
        max_results = self.max_results or k

        try:
            results = list(
                custom_ddgs.text(
                    query,
                    region=region,
                    safesearch=self.safesearch,
                    backend=self.backend,
                    timelimit=timelimit,
                    max_results=max_results,
                )
            )

            search_results = []
            for item in results[:k]:
                result = SearchResult(
                    title=item.get("title", ""),
                    url=item.get("href", ""),
                    snippet=item.get("body", ""),
                    published_time=item.get("date", None),
                    extra_snippets=[],
                )
                search_results.append(result)

            return search_results

        except Exception as e:
            logger.error(f"Error making request to DuckDuckGo Search: {e}")
            return []

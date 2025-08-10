import dspy
import click
from dspy.signatures import make_signature
from ddgs import DDGS
from typing import List, Dict, Optional, Any, Literal
from websearch.schema import SearchResult
import logging
from dspy.clients.cache import request_cache

logger = logging.getLogger("ddg_search")

logging.getLogger("primp").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)


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
            make_signature(
                "original_query -> optimized_search_query",
                "Optimizes search queries for DuckDuckGo. Do not use AND or OR in the optimized query.",
            )
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
def get_news(query: str, k: int, options: dict = {}) -> List[SearchResult]:
    # Use DuckDuckGo news search
    results = DDGS().news(query, max_results=k, **options)

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


@request_cache()
def get_text(query: str, k: int, options: dict = {}) -> List[SearchResult]:
    # Use DuckDuckGo search
    results = DDGS().text(query, max_results=k, **options)

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


def search_news(query: str) -> List[SearchResult]:
    return [str(item) for item in get_news(query, k=5)]


def search_web(query: str) -> List[SearchResult]:
    return [str(item) for item in get_text(query, k=5)]


class DDGSignature(dspy.Signature):
    """Find all relevant information to verify (or refute) the claim."""

    claim: str = dspy.InputField()
    results: str = dspy.OutputField(desc="The search results summary")


class DDGSearchResult(dspy.Signature):
    """Converts the observation to a list of SearchResult objects"""

    observation: str = dspy.InputField(desc="The observation")
    results: List[SearchResult] = dspy.OutputField(desc="The search results")


class DDGRelevanceChecker(dspy.Signature):
    """Checks if the observation is relevant to the claim"""

    claim: str = dspy.InputField()
    observation: str = dspy.InputField()
    relevant: bool = dspy.OutputField(
        desc="Whether the observation is relevant to the claim"
    )


class DDGCategory(dspy.Signature):
    """Categorizes the text into claim, question, or topic"""

    text: str = dspy.InputField()
    category: Literal["claim", "question", "topic"] = dspy.OutputField(
        desc="The category of the text"
    )


class DDGReACTSearcher(dspy.Module):
    def __init__(self, verbose: bool = False):
        self.react = dspy.ReAct(
            DDGSignature, tools=[search_web, search_news], max_iters=10
        )
        self.convert = dspy.Predict(DDGSearchResult)
        self.check = dspy.Predict(DDGRelevanceChecker)
        self.category = dspy.Predict(DDGCategory)
        self.verbose = verbose

    def forward(self, claim: str) -> list[SearchResult]:
        category = self.category(text=claim).category
        if self.verbose:
            print(click.style(f"Category: {category}", fg="yellow"))

        result = self.react(claim=claim)

        observations = []
        for k, v in result.trajectory.items():
            if self.verbose:
                print(click.style(k, fg="blue"))
                print(click.style(v, fg="green"))
                print()

            if k.startswith("observation"):
                results = self.convert(observation=v).results
                for item in results:
                    if self.check(claim=claim, observation=item.title).relevant:
                        observations.append(item)

        if self.verbose:
            print(click.style(result.reasoning, fg="yellow"))
            print(click.style(result.results, fg="green"))

        return dspy.Prediction(
            results=result.results,
            summary=result.reasoning,
            search_results=observations,
        )


def tool_search_web(query: str) -> str:
    searcher = DDGReACTSearcher(verbose=False)
    output = searcher(query)

    memory_context = "## Web Search Results\n"
    for item in output.search_results:
        memory_context += str(item)
    memory_context += "\n## Web Search Summary\n"
    memory_context += output.summary
    memory_context += output.results

    return memory_context

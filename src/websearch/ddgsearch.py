import dspy
import re
import click
from dspy.signatures import make_signature
from ddgs import DDGS, exceptions as ddgs_exceptions
from typing import List, Dict, Optional, Any, Literal
from websearch.schema import SearchResult
import logging
from dspy.clients.cache import request_cache
import time

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


@request_cache()
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


def search_news(query: str, k: int = 3) -> List[SearchResult]:
    return [str(item) for item in get_news(query, k=k)]


def search_web(query: str, k: int = 3) -> List[SearchResult]:
    return [str(item) for item in get_text(query, k=k)]


class DDGSignature(dspy.Signature):
    """Find all relevant information to verify (or refute) the claim."""

    claim: str = dspy.InputField()
    results: list[str] = dspy.OutputField(desc="The search results summary")


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
        self.check = dspy.Predict(DDGRelevanceChecker)
        self.category = dspy.Predict(DDGCategory)
        self.verbose = verbose

    def forward(self, claim: str) -> list[SearchResult]:
        start_time = time.time()
        category = self.category(text=claim).category
        if self.verbose:
            print(click.style(f"Category: {category}", fg="yellow"))

        result = self.react(claim=claim)

        iterations = 1
        observations = []
        for k, v in result.trajectory.items():
            if self.verbose:
                print(click.style(k, fg="blue"))
                print(click.style(v, fg="green"))
                print()

            if k.startswith("observation"):
                results = self.convert(observation=v)
                if not results:
                    continue
                for item in results:
                    if self.check(claim=claim, observation=item.title).relevant:
                        observations.append(item)
                iterations += 1

        if self.verbose:
            print(click.style(result.reasoning, fg="yellow"))
            print(click.style(result.results, fg="green"))

        execution_time = time.time() - start_time
        print(f"DDGReACTSearcher|{claim}|{category}|{iterations} Iterations|{len(observations)} Results|{execution_time:.2f}s")
        return dspy.Prediction(
            summary=result.results,
            reasoning=result.reasoning,
            search_results=observations,
        )

    def convert(self, observation: list[str] | str) -> List[SearchResult]:
        results = []
        if not isinstance(observation, list):
            return results

        for item in observation:
            # Extract title using regex pattern
            title_match = re.search(r"- Title: (.*)", item)
            title = title_match.group(1) if title_match else ""
            url_match = re.search(r"- URL: (.*)", item)
            url = url_match.group(1) if url_match else ""
            snippet_match = re.search(r"- Content: (.*)", item)
            snippet = snippet_match.group(1) if snippet_match else ""

            results.append(SearchResult(
                title=title, 
                url=url, 
                snippet=snippet))

        return results



def tool_search_web(query: str, verbose: bool = False) -> str:
    searcher = DDGReACTSearcher(verbose=verbose)
    output = searcher(query)

    # Format the search results and summary
    memory_context = f"## Web Search Results on {query}\n\n"
    for i, item in enumerate(output.search_results):
        memory_context += str(item).replace("=====", f"### Web Search Result {i+1} ###")
        memory_context += "\n"
    memory_context += f"\n## Web Search Summary on {query}\n\n"
    memory_context += '\n'.join([f"- {item}" for item in output.summary])
    memory_context += "\n"

    return memory_context

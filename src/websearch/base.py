import dspy
from websearch.schema import SearchResult
import time
import re
from typing import Literal


class Category(dspy.Signature):
    """Categorizes the text into claim, question, or topic"""

    text: str = dspy.InputField()
    category: Literal["claim", "question", "topic"] = dspy.OutputField(
        desc="The category of the text"
    )


class Summary(dspy.Signature):
    """Select query-related facts from the search results. Generates a factual summary."""

    query: str = dspy.InputField()
    results: str = dspy.InputField()
    summary: str = dspy.OutputField(
        desc="The summary of the snippets. Use the citation numbers in [^{number}] to reference the snippets."
    )


class BaseSearcher(dspy.Module):
    def __init__(self, engine: str = "tavily", k: int = 3, verbose: bool = False):
        self.engine = engine
        self.k = k
        self.verbose = verbose
        self._search_results = {}
        self._name = "BaseSearcher"

        self.category = dspy.Predict(Category)
        self.summary = dspy.Predict(Summary)

    def forward(self, query: str) -> str:
        start_time = time.time()
        category = self.category(text=query).category

        self._setup_tools(category, self.engine)

        search_summary, sources, proc_info = self._search(query)
        markdown = search_summary + f"\n## Sources\n\n" + sources + "\n"

        self.execution_time = time.time() - start_time
        print(
            f"{self._name}|{category}|{query}|{proc_info}|{self.engine}|{self.execution_time:.2f}s"
        )

        return dspy.Prediction(
            query=query,
            summary=search_summary,
            sources=self.search_results,
            markdown=markdown,
        )

    def _setup_tools(self, category: str, engine: str):
        raise NotImplementedError("Subclasses must implement this method")

    def _search(self, query: str) -> tuple[str, str, str]:
        raise NotImplementedError("Subclasses must implement this method")

    def _add_search_results(self, results: list[SearchResult]):
        for result in results:
            if result.url not in self._search_results:
                self._search_results[result.url] = result

    def _get_summary(self, query: str, results: list[SearchResult]) -> str:
        query_summary = ""
        for result in results:
            query_summary += f"- [^{result.sid}] Title: {result.title}\nSnippet: {result.snippet}\n"

        summary = self.summary(query=query, results=query_summary).summary
        
        # Apply regex to change [number] to [^number] for any digit
        summary = re.sub(r'\[(\d+)\]', r'[^\1]', summary)
        summary = re.sub(r'\[\^\{(\d+)\}\]', r'[^\1]', summary)
        
        return summary

    @property
    def search_results(self) -> list[SearchResult]:
        return list(self._search_results.values())

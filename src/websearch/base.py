import logging
import re
import time
from typing import ClassVar, Literal

import dspy

from websearch.schema import SearchResult

logger = logging.getLogger(__name__)

# Compiled regex patterns for citation normalization
_CITATION_PATTERN = re.compile(r"\[(\d+)\]")
_TEMPLATE_CITATION_PATTERN = re.compile(r"\[\^\{(\d+)\}\]")


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
    _name: ClassVar[str] = "BaseSearcher"

    def __init__(
        self, engine: str = "tavily", k: int = 3, verbose: bool = False
    ) -> None:
        super().__init__()
        self.engine = engine
        self.k = k
        self.verbose = verbose
        self._search_results: dict[str, SearchResult] = {}

        self._categorizer = dspy.Predict(Category)
        self._summarizer = dspy.Predict(Summary)

    def forward(self, query: str) -> dspy.Prediction:
        start_time = time.time()
        category = self._categorizer(text=query).category

        self._setup_tools(category, self.engine)

        search_summary, sources, proc_info = self._search(query)
        markdown = f"{search_summary}\n## Sources\n\n{sources}\n"

        self.execution_time = time.time() - start_time
        logger.info(
            "%s|%s|%s|%s|%s|%.2fs",
            self._name,
            category,
            query,
            proc_info,
            self.engine,
            self.execution_time,
        )

        return dspy.Prediction(
            query=query,
            summary=search_summary,
            sources=self.search_results,
            markdown=markdown,
        )

    def _setup_tools(self, category: str, engine: str) -> None:
        raise NotImplementedError("Subclasses must implement this method")

    def _search(self, query: str) -> tuple[str, str, str]:
        raise NotImplementedError("Subclasses must implement this method")

    def _add_search_results(self, results: list[SearchResult]) -> None:
        for result in results:
            if result.url not in self._search_results:
                self._search_results[result.url] = result

    def _get_summary(self, query: str, results: list[SearchResult]) -> str:
        if not results:
            return "No results found."

        formatted_results = "\n".join(
            f"- [^{r.sid}] Title: {r.title}\nSnippet: {r.snippet}" for r in results
        )

        try:
            summary = self._summarizer(query=query, results=formatted_results).summary
        except Exception as e:
            logger.error("Summary generation failed: %s", e)
            return "Summary generation failed."

        return self._normalize_citations(summary)

    def _normalize_citations(self, text: str) -> str:
        text = _CITATION_PATTERN.sub(r"[^\1]", text)
        text = _TEMPLATE_CITATION_PATTERN.sub(r"[^\1]", text)
        return text

    @property
    def search_results(self) -> list[SearchResult]:
        return list(self._search_results.values())

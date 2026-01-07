from __future__ import annotations

import asyncio
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar, Literal

import dspy

from websearch.base import BaseSearcher
from websearch.brave import AsyncBraveSearch
from websearch.ddg import AsyncDDGSearch
from websearch.schema import SearchResult
from websearch.tavily import AsyncTavilySearch

if TYPE_CHECKING:
    from collections.abc import Callable

logger = logging.getLogger(__name__)


class QueryOptimizer(dspy.Signature):
    """Optimizes search queries for search engine, create only 3-5 queries that are relevant to the original query."""

    original_query: str = dspy.InputField()
    optimized_search_query: list[str] = dspy.OutputField(
        desc="Generate multiple queries to search for the original query"
    )


class SelectSource(dspy.Signature):
    """Choose web or news source for the search query."""

    query: str = dspy.InputField()
    source: Literal["web", "news"] = dspy.OutputField(
        desc="If the query is about a specific event, recent changes, or recent news, choose news. Otherwise, choose web."
    )


class BatchQuerySummary(dspy.Signature):
    """Generate summaries for multiple search result sets in a single call."""

    queries_with_results: str = dspy.InputField(
        desc="JSON array of objects with 'query' and 'results' fields"
    )
    summaries: list[str] = dspy.OutputField(
        desc="Array of summaries with citations [^N], one per query in same order"
    )


class QuerySearcher(BaseSearcher):
    _name: ClassVar[str] = "QuerySearcher"
    _date_instruction_set: ClassVar[bool] = False

    def __init__(
        self,
        engine: str = "tavily",
        k: int = 3,
        verbose: bool = False,
        max_workers: int = 5,
        use_parallel: bool = True,
        batch_summarize: bool = True,
        use_async: bool = True,
    ) -> None:
        super().__init__(engine, k, verbose)
        self.max_workers = max_workers
        self.use_parallel = use_parallel
        self.batch_summarize = batch_summarize
        self.use_async = use_async

        self._query_optimizer = dspy.ChainOfThought(QueryOptimizer)
        self._select_source = dspy.ChainOfThought(SelectSource)
        self._batch_summarizer = dspy.Predict(BatchQuerySummary)
        self._init_select_source_instructions()

        self._async_brave: AsyncBraveSearch | None = None
        self._async_tavily: AsyncTavilySearch | None = None
        self._async_ddg: AsyncDDGSearch | None = None

    @classmethod
    def _init_select_source_instructions(cls) -> None:
        if not cls._date_instruction_set:
            SelectSource.instructions = (
                f"The current date is {datetime.now().strftime('%Y-%m-%d')}."
            )
            cls._date_instruction_set = True

    def _setup_tools(self, category: str, engine: str) -> None:
        search_web, search_news = self._load_search_functions(engine)
        self._search_web: Callable = search_web
        self._search_news: Callable = search_news
        self._use_llm_for_source = False

    def _search(self, query: str) -> tuple[str, str, str]:
        query_list = self._optimize_query(query)

        if self.use_async and self.use_parallel:
            all_results = self._search_async(query_list)
        elif self.use_parallel:
            all_results = self._search_parallel(query_list)
        else:
            all_results = self._search_sequential(query_list)

        self._collect_results(all_results)
        query_summaries = self._generate_summaries(all_results)

        proc_info = f"{len(query_list)} Sub-Queries|{len(self.search_results)} Results"
        sources = "\n".join(item.to_markdown() for item in self.search_results)
        search_summary = f"## Web Search Results on |{query}|\n\n"
        search_summary += "\n\n".join(query_summaries)
        search_summary += "\n"

        return search_summary, sources, proc_info

    def _optimize_query(self, query: str) -> list[str]:
        try:
            outcome = self._query_optimizer(original_query=query)
            query_list: list[str] = outcome.optimized_search_query  # type: ignore[attr-defined]
            if self.verbose:
                logger.debug("Optimized query: %s -> %s", query, query_list)
                logger.debug("Reasoning: %s", getattr(outcome, "reasoning", "N/A"))
            return query_list
        except Exception as e:
            logger.error("Query optimization failed: %s", e)
            return [query]

    def _search_parallel(
        self, query_list: list[str]
    ) -> list[tuple[str, str, list[SearchResult]]]:
        def search_one(q: str) -> tuple[str, str, list[SearchResult]]:
            source = self._determine_source(q)
            try:
                raw_results = self._execute_search(q, source)
                results = [SearchResult.from_json(r) for r in raw_results]
                return q, source, results
            except Exception as e:
                logger.error("Search failed for '%s': %s", q, e)
                return q, source, []

        results: list[tuple[str, str, list[SearchResult]]] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(search_one, q): q for q in query_list}
            for future in as_completed(futures):
                results.append(future.result())

        order = {q: i for i, q in enumerate(query_list)}
        results.sort(key=lambda x: order.get(x[0], 999))
        return results

    def _search_async(
        self, query_list: list[str]
    ) -> list[tuple[str, str, list[SearchResult]]]:
        async def run_searches() -> list[tuple[str, str, list[SearchResult]]]:
            client = self._get_async_client()
            tasks = [client.search(q, self.k) for q in query_list]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            output: list[tuple[str, str, list[SearchResult]]] = []
            for q, result in zip(query_list, results, strict=False):
                if isinstance(result, Exception):
                    logger.error("Async search failed for '%s': %s", q, result)
                    output.append((q, "web", []))
                else:
                    output.append((q, "web", result))
            return output

        try:
            loop = asyncio.get_running_loop()
            future = asyncio.ensure_future(run_searches())
            return loop.run_until_complete(future)
        except RuntimeError:
            return asyncio.run(run_searches())

    def _get_async_client(
        self,
    ) -> AsyncBraveSearch | AsyncTavilySearch | AsyncDDGSearch:
        if self.engine == "brave":
            if self._async_brave is None:
                self._async_brave = AsyncBraveSearch()
            return self._async_brave
        elif self.engine == "tavily":
            if self._async_tavily is None:
                self._async_tavily = AsyncTavilySearch()
            return self._async_tavily
        elif self.engine == "ddg":
            if self._async_ddg is None:
                self._async_ddg = AsyncDDGSearch()
            return self._async_ddg
        else:
            msg = f"Async not supported for engine: {self.engine}"
            raise ValueError(msg)

    def _search_sequential(
        self, query_list: list[str]
    ) -> list[tuple[str, str, list[SearchResult]]]:
        results: list[tuple[str, str, list[SearchResult]]] = []
        for q in query_list:
            source = self._determine_source(q)
            try:
                raw_results = self._execute_search(q, source)
                parsed = [SearchResult.from_json(r) for r in raw_results]
                results.append((q, source, parsed))
            except Exception as e:
                logger.error("Search failed for '%s': %s", q, e)
                results.append((q, source, []))
        return results

    def _collect_results(
        self, all_results: list[tuple[str, str, list[SearchResult]]]
    ) -> None:
        for _, _, results in all_results:
            self._add_search_results(results)

    def _generate_summaries(
        self, all_results: list[tuple[str, str, list[SearchResult]]]
    ) -> list[str]:
        if self.batch_summarize and len(all_results) > 1:
            return self._get_batch_summaries(all_results)
        return self._get_individual_summaries(all_results)

    def _get_batch_summaries(
        self, all_results: list[tuple[str, str, list[SearchResult]]]
    ) -> list[str]:
        formatted_input = []
        for q, _, results in all_results:
            result_text = "\n".join(
                f"[^{r.sid}] Title: {r.title}\nSnippet: {r.snippet}" for r in results
            )
            formatted_input.append({"query": q, "results": result_text})

        try:
            output = self._batch_summarizer(
                queries_with_results=json.dumps(formatted_input, ensure_ascii=False)
            )
            summaries: list[str] = output.summaries  # type: ignore[attr-defined]

            if len(summaries) != len(all_results):
                logger.warning(
                    "Batch summary count mismatch: %d vs %d",
                    len(summaries),
                    len(all_results),
                )
                return self._get_individual_summaries(all_results)

            query_summaries = []
            for (q, source, _), summary in zip(all_results, summaries, strict=False):
                summary = self._normalize_citations(summary)
                query_summaries.append(f"**{q} ({source}):** {summary}")
            return query_summaries

        except Exception as e:
            logger.error("Batch summarization failed: %s", e)
            return self._get_individual_summaries(all_results)

    def _get_individual_summaries(
        self, all_results: list[tuple[str, str, list[SearchResult]]]
    ) -> list[str]:
        return [
            f"**{q} ({source}):** {self._get_summary(q, results)}"
            for q, source, results in all_results
        ]

    def _determine_source(self, query: str) -> str:
        if not self._use_llm_for_source:
            return "web"

        try:
            result = self._select_source(query=query)
            if self.verbose:
                logger.debug("Source selection reasoning: %s", result.reasoning)  # type: ignore[attr-defined]
            return result.source  # type: ignore[attr-defined]
        except Exception as e:
            logger.error("Source selection failed: %s", e)
            return "web"

    def _execute_search(self, query: str, source: str) -> list:
        if source == "news":
            return self._search_news(query, self.k)
        return self._search_web(query, self.k)


REACT_GOALS: dict[str, str] = {
    "claim": "Find all relevant information to verify (or refute) the claim. Use the search tool with k=3 to 5.",
    "question": "Find all relevant information to answer the question. Use the search tool with k=3.",
    "topic": "Find comprehensive information about the topic with multiple perspectives. Use the search tool with k=3 to 5.",
}


class ReACTGoal(dspy.Signature):
    """Find all relevant information to verify (or refute) the claim."""

    claim: str = dspy.InputField()
    results: str = dspy.OutputField(
        desc="The search results summary in a single sentence"
    )


class ReACTSearcher(BaseSearcher):
    _name: ClassVar[str] = "ReACTSearcher"

    def __init__(
        self,
        engine: str = "tavily",
        k: int = 3,
        verbose: bool = False,
        max_workers: int = 5,
        use_parallel: bool = True,
        batch_summarize: bool = True,
    ) -> None:
        super().__init__(engine, k, verbose)
        self.max_workers = max_workers
        self.use_parallel = use_parallel
        self.batch_summarize = batch_summarize
        self._batch_summarizer = dspy.Predict(BatchQuerySummary)

    def _setup_tools(self, category: str, engine: str) -> None:
        search_web, search_news = self._load_search_functions(engine)

        ReACTGoal.instructions = REACT_GOALS.get(category, REACT_GOALS["topic"])
        if self.verbose:
            logger.debug("ReACT goal: %s", ReACTGoal.instructions)

        self._react = dspy.ReAct(
            ReACTGoal, tools=[search_web, search_news], max_iters=5
        )

    def _search(self, query: str) -> tuple[str, str, str]:
        try:
            result = self._react(claim=query)
        except Exception as e:
            logger.error("ReACT search failed: %s", e)
            return "Search failed.", "", "0 Iterations|0 Results"

        iterations = 1
        observations: list[SearchResult] = []
        query_data: list[tuple[str, str, list[SearchResult]]] = []

        source = "web"
        current_query = ""

        for key, value in result.trajectory.items():  # type: ignore[attr-defined]
            if self.verbose:
                logger.debug("%s: %s", key, value)

            if key.startswith("tool_name") and value.startswith("search_"):
                source = value.replace("search_", "")

            if key.startswith("tool_args") and value:
                current_query = value.get("query", "")

            if key.startswith("observation") and value != "Completed.":
                web_results = [SearchResult.from_json(item) for item in value]
                observations.extend(web_results)
                iterations += 1

                if current_query:
                    query_data.append((current_query, source, web_results))

        if self.verbose:
            logger.debug("Final reasoning: %s", result.reasoning)  # type: ignore[attr-defined]

        # Generate summaries in parallel or batch
        query_summaries = self._generate_summaries(query_data)

        proc_info = f"{iterations} Iterations|{len(observations)} Results"
        sources = "\n".join(item.to_markdown() for item in observations)
        search_summary = f"## Web Search Results on |{query}|\n"
        search_summary += f"\n{result.results}\n\n"  # type: ignore[attr-defined]
        search_summary += "\n\n".join(query_summaries)
        search_summary += "\n"

        return search_summary, sources, proc_info

    def _generate_summaries(
        self, query_data: list[tuple[str, str, list[SearchResult]]]
    ) -> list[str]:
        """Generate summaries using batch or parallel processing."""
        if not query_data:
            return []

        if self.batch_summarize and len(query_data) > 1:
            return self._get_batch_summaries(query_data)
        return self._get_individual_summaries(query_data)

    def _get_batch_summaries(
        self, query_data: list[tuple[str, str, list[SearchResult]]]
    ) -> list[str]:
        """Batch summarize all queries in a single LLM call."""
        formatted_input = []
        for q, _, results in query_data:
            result_text = "\n".join(
                f"[^{r.sid}] Title: {r.title}\nSnippet: {r.snippet}" for r in results
            )
            formatted_input.append({"query": q, "results": result_text})

        try:
            output = self._batch_summarizer(
                queries_with_results=json.dumps(formatted_input, ensure_ascii=False)
            )
            summaries: list[str] = output.summaries  # type: ignore[attr-defined]

            if len(summaries) != len(query_data):
                logger.warning(
                    "Batch summary count mismatch: %d vs %d",
                    len(summaries),
                    len(query_data),
                )
                return self._get_individual_summaries(query_data)

            query_summaries = []
            for (q, source, results), summary in zip(query_data, summaries, strict=False):
                summary = self._normalize_citations(summary)
                web_citations = " ".join(f"[^{item.sid}]" for item in results)
                query_summaries.append(
                    f"**{q} ({source}):** {summary} {web_citations}"
                )
            return query_summaries

        except Exception as e:
            logger.error("Batch summarization failed: %s", e)
            return self._get_individual_summaries(query_data)

    def _get_individual_summaries(
        self, query_data: list[tuple[str, str, list[SearchResult]]]
    ) -> list[str]:
        """Generate summaries individually, optionally in parallel."""
        if self.use_parallel and len(query_data) > 1:
            return self._get_parallel_summaries(query_data)
        return self._get_sequential_summaries(query_data)

    def _get_parallel_summaries(
        self, query_data: list[tuple[str, str, list[SearchResult]]]
    ) -> list[str]:
        """Generate summaries in parallel using ThreadPoolExecutor."""
        def summarize_one(
            idx: int, q: str, source: str, results: list[SearchResult]
        ) -> tuple[int, str]:
            web_summary = self._get_summary(q, results)
            web_citations = " ".join(f"[^{item.sid}]" for item in results)
            return idx, f"**{q} ({source}):** {web_summary} {web_citations}"

        summaries_dict: dict[int, str] = {}
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(summarize_one, idx, q, source, results): idx
                for idx, (q, source, results) in enumerate(query_data)
            }
            for future in as_completed(futures):
                idx, summary = future.result()
                summaries_dict[idx] = summary

        return [summaries_dict[i] for i in range(len(query_data))]

    def _get_sequential_summaries(
        self, query_data: list[tuple[str, str, list[SearchResult]]]
    ) -> list[str]:
        """Generate summaries sequentially."""
        query_summaries = []
        for q, source, results in query_data:
            web_summary = self._get_summary(q, results)
            web_citations = " ".join(f"[^{item.sid}]" for item in results)
            query_summaries.append(
                f"**{q} ({source}):** {web_summary} {web_citations}"
            )
        return query_summaries

from __future__ import annotations

import asyncio
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, ClassVar, Literal

import dspy

from websearch.base import BaseSearcher
from websearch.brave import AsyncBraveSearch
from websearch.ddg import AsyncDDGSearch
from websearch.schema import SearchResult
from websearch.tavily import AsyncTavilySearch

logger = logging.getLogger(__name__)

EngineType = Literal["brave", "tavily", "ddg"]


class QueryOptimizer(dspy.Signature):
    """Optimizes search queries for search engine, create only 3-5 queries."""

    original_query: str = dspy.InputField()
    optimized_search_query: list[str] = dspy.OutputField(
        desc="Generate 3-5 diverse queries to search for the original query"
    )


class BatchSummary(dspy.Signature):
    """Generate summaries for multiple search result sets in a single call."""

    queries_with_results: str = dspy.InputField(
        desc="JSON array of objects with 'query' and 'results' fields"
    )
    summaries: list[str] = dspy.OutputField(
        desc="Array of summaries with citations [^N], one per query in same order"
    )


class SingleSummary(dspy.Signature):
    """Select query-related facts from search results with citations."""

    query: str = dspy.InputField()
    results: str = dspy.InputField()
    summary: str = dspy.OutputField(
        desc="Summary with citation numbers in [^{number}] format"
    )


class OptimizedSearcher(BaseSearcher):
    _name: ClassVar[str] = "OptimizedSearcher"

    def __init__(
        self,
        engine: EngineType = "brave",
        k: int = 3,
        verbose: bool = False,
        max_workers: int = 5,
        skip_categorization: bool = True,
        batch_summarize: bool = True,
        use_async: bool = True,
    ) -> None:
        super().__init__(engine=engine, k=k, verbose=verbose)
        self.max_workers = max_workers
        self.skip_categorization = skip_categorization
        self.batch_summarize = batch_summarize
        self.use_async = use_async

        self._query_optimizer = dspy.ChainOfThought(QueryOptimizer)
        self._batch_summarizer = dspy.Predict(BatchSummary)
        self._single_summarizer = dspy.Predict(SingleSummary)

        self._async_brave: AsyncBraveSearch | None = None
        self._async_tavily: AsyncTavilySearch | None = None
        self._async_ddg: AsyncDDGSearch | None = None

        self._setup_sync_tools()

    def _setup_sync_tools(self) -> None:
        if self.engine == "tavily":
            from websearch.tavily import search_news, search_web
        elif self.engine == "ddg":
            from websearch.ddg import search_news, search_web
        elif self.engine == "brave":
            from websearch.brave import search_news, search_web
        else:
            msg = f"Invalid engine: {self.engine}"
            raise ValueError(msg)

        self._search_web_sync = search_web
        self._search_news_sync = search_news

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

    def forward(self, query: str) -> dspy.Prediction:
        start_time = time.time()
        self._search_results.clear()

        query_list = self._generate_optimized_queries(query)
        all_results = self._execute_parallel_searches(query_list)
        self._collect_results(all_results)
        query_summaries = self._generate_summaries(all_results)

        execution_time = time.time() - start_time
        return self._build_prediction(
            query, query_list, query_summaries, execution_time
        )

    def _generate_optimized_queries(self, query: str) -> list[str]:
        outcome = self._query_optimizer(original_query=query)
        query_list: list[str] = outcome.optimized_search_query  # type: ignore[attr-defined]

        if self.verbose:
            logger.info("Optimized: %s -> %s", query, query_list)
            logger.info("Reasoning: %s", outcome.reasoning)  # type: ignore[attr-defined]

        return query_list

    def _execute_parallel_searches(
        self,
        query_list: list[str],
    ) -> list[tuple[str, list[SearchResult]]]:
        if self.use_async:
            return self._search_async(query_list)
        return self._search_parallel_sync(query_list)

    def _collect_results(
        self,
        all_results: list[tuple[str, list[SearchResult]]],
    ) -> None:
        for _, results in all_results:
            self._add_search_results(results)

    def _generate_summaries(
        self,
        all_results: list[tuple[str, list[SearchResult]]],
    ) -> list[str]:
        if self.batch_summarize and len(all_results) > 1:
            return self._get_batch_summaries(all_results)
        return [
            f"**{q} (web):** {self._get_single_summary(q, r)}" for q, r in all_results
        ]

    def _build_prediction(
        self,
        query: str,
        query_list: list[str],
        query_summaries: list[str],
        execution_time: float,
    ) -> dspy.Prediction:
        proc_info = f"{len(query_list)} Sub-Queries|{len(self.search_results)} Results"
        sources = "\n".join(item.to_markdown() for item in self.search_results)
        search_summary = f"## Web Search Results on |{query}|\n\n"
        search_summary += "\n\n".join(query_summaries)
        search_summary += "\n"
        markdown = f"{search_summary}\n## Sources\n\n{sources}\n"

        if self.verbose:
            logger.info(
                "%s|%s|%s|%s|%.2fs",
                self._name,
                query,
                proc_info,
                self.engine,
                execution_time,
            )

        return dspy.Prediction(
            query=query,
            summary=search_summary,
            sources=self.search_results,
            markdown=markdown,
            execution_time=execution_time,
        )

    def _search_async(
        self,
        query_list: list[str],
    ) -> list[tuple[str, list[SearchResult]]]:
        async def run_searches() -> list[tuple[str, list[SearchResult]]]:
            client = self._get_async_client()
            tasks = [client.search(q, self.k) for q in query_list]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            output = []
            for q, result in zip(query_list, results, strict=False):
                if isinstance(result, Exception):
                    logger.error("Search failed for '%s': %s", q, result)
                    output.append((q, []))
                else:
                    output.append((q, result))
            return output

        try:
            loop = asyncio.get_running_loop()
            future = asyncio.ensure_future(run_searches())
            return loop.run_until_complete(future)
        except RuntimeError:
            return asyncio.run(run_searches())

    def _search_parallel_sync(
        self,
        query_list: list[str],
    ) -> list[tuple[str, list[SearchResult]]]:
        def search_one(q: str) -> tuple[str, list[SearchResult]]:
            try:
                raw_results = self._search_web_sync(q, self.k)
                results = [SearchResult.from_json(r) for r in raw_results]
                return q, results
            except Exception as e:
                logger.error("Search failed for '%s': %s", q, e)
                return q, []

        results: list[tuple[str, list[SearchResult]]] = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(search_one, q): q for q in query_list}
            for future in as_completed(futures):
                results.append(future.result())

        order = {q: i for i, q in enumerate(query_list)}
        results.sort(key=lambda x: order.get(x[0], 999))
        return results

    def _get_batch_summaries(
        self,
        all_results: list[tuple[str, list[SearchResult]]],
    ) -> list[str]:
        formatted_input = []
        for q, results in all_results:
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
                return self._fallback_to_individual_summaries(all_results)

            query_summaries = []
            for (q, _), summary in zip(all_results, summaries, strict=False):
                summary = self._normalize_citations(summary)
                query_summaries.append(f"**{q} (web):** {summary}")
            return query_summaries

        except Exception as e:
            logger.error("Batch summarization failed: %s", e)
            return self._fallback_to_individual_summaries(all_results)

    def _fallback_to_individual_summaries(
        self,
        all_results: list[tuple[str, list[SearchResult]]],
    ) -> list[str]:
        return [
            f"**{q} (web):** {self._get_single_summary(q, r)}" for q, r in all_results
        ]

    def _get_single_summary(self, query: str, results: list[SearchResult]) -> str:
        if not results:
            return "No results found."

        result_text = "\n".join(
            f"[^{r.sid}] Title: {r.title}\nSnippet: {r.snippet}" for r in results
        )

        try:
            output = self._single_summarizer(query=query, results=result_text)
            return self._normalize_citations(output.summary)  # type: ignore[attr-defined]
        except Exception as e:
            logger.error("Summarization failed: %s", e)
            return "Summary generation failed."

    async def cleanup(self) -> None:
        if self._async_brave:
            await self._async_brave.close()
        if self._async_tavily:
            await self._async_tavily.close()
        if self._async_ddg:
            await self._async_ddg.close()


def create_optimized_searcher(
    engine: EngineType = "brave",
    fast_mode: bool = True,
    **kwargs: Any,  # noqa: ANN401
) -> OptimizedSearcher:
    defaults = {
        "skip_categorization": fast_mode,
        "batch_summarize": fast_mode,
        "use_async": True,
        "max_workers": 5,
        "k": 3,
    }
    defaults.update(kwargs)
    return OptimizedSearcher(engine=engine, **defaults)


def quick_search(
    query: str, engine: EngineType = "brave", k: int = 3
) -> dspy.Prediction:
    searcher = create_optimized_searcher(engine=engine, k=k, fast_mode=True)
    result: dspy.Prediction = searcher(query)  # type: ignore[assignment]
    return result

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

import dspy
import httpx
from dotenv import load_dotenv

from websearch.schema import SearchResult

if TYPE_CHECKING:
    pass

load_dotenv()

logger = logging.getLogger("optimized_searcher")

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


@dataclass
class AsyncSearchConfig:
    timeout: float = 10.0
    max_connections: int = 10
    max_keepalive_connections: int = 5


class AsyncBraveSearch:
    BASE_URL = "https://api.search.brave.com/res/v1"

    def __init__(self, config: AsyncSearchConfig | None = None) -> None:
        self.config = config or AsyncSearchConfig()
        self.api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                limits=httpx.Limits(
                    max_connections=self.config.max_connections,
                    max_keepalive_connections=self.config.max_keepalive_connections,
                ),
                headers={
                    "Accept": "application/json",
                    "Accept-Encoding": "gzip",
                    "X-Subscription-Token": self.api_key or "",
                },
            )
        return self._client

    async def search(
        self,
        query: str,
        k: int = 3,
        source: Literal["web", "news"] = "web",
    ) -> list[SearchResult]:
        client = await self._get_client()
        params = {
            "q": query,
            "count": k,
            "country": "US",
            "search_lang": "en",
            "safesearch": "moderate",
            "text_decorations": False,
            "spellcheck": True,
        }

        try:
            response = await client.get(
                f"{self.BASE_URL}/{source}/search", params=params
            )
            response.raise_for_status()
            data = response.json()

            results = []
            if source in data and "results" in data[source]:
                for item in data[source]["results"]:
                    extra = item.get("extra_snippets", [])
                    snippet = item.get("description", "")
                    if extra:
                        snippet += "\n" + "\n".join(extra)
                    results.append(
                        SearchResult(
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            snippet=snippet,
                            published_time=item.get("published"),
                            source=source,
                        )
                    )
            return results
        except httpx.HTTPError as e:
            logger.error(f"Brave search failed: {e}")
            return []

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()


class AsyncTavilySearch:
    BASE_URL = "https://api.tavily.com/search"

    def __init__(self, config: AsyncSearchConfig | None = None) -> None:
        self.config = config or AsyncSearchConfig()
        self.api_key = os.getenv("TAVILY_API_KEY")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=self.config.timeout,
                limits=httpx.Limits(
                    max_connections=self.config.max_connections,
                    max_keepalive_connections=self.config.max_keepalive_connections,
                ),
            )
        return self._client

    async def search(
        self,
        query: str,
        k: int = 3,
        topic: Literal["general", "news"] = "general",
    ) -> list[SearchResult]:
        client = await self._get_client()
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": k,
            "topic": topic,
            "include_answer": False,
        }

        try:
            response = await client.post(self.BASE_URL, json=payload)
            response.raise_for_status()
            data = response.json()

            results = []
            for item in data.get("results", []):
                results.append(
                    SearchResult(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        snippet=item.get("content", ""),
                        published_time=item.get("published_date"),
                        source="news" if topic == "news" else "web",
                    )
                )
            return results
        except httpx.HTTPError as e:
            logger.error(f"Tavily search failed: {e}")
            return []

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()


class OptimizedSearcher(dspy.Module):
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
        super().__init__()
        self.engine = engine
        self.k = k
        self.verbose = verbose
        self.max_workers = max_workers
        self.skip_categorization = skip_categorization
        self.batch_summarize = batch_summarize
        self.use_async = use_async

        self._search_results: dict[str, SearchResult] = {}
        self._name = "OptimizedSearcher"

        self.query_optimizer = dspy.ChainOfThought(QueryOptimizer)
        self.batch_summarizer = dspy.Predict(BatchSummary)
        self.single_summarizer = dspy.Predict(SingleSummary)

        self._async_brave: AsyncBraveSearch | None = None
        self._async_tavily: AsyncTavilySearch | None = None

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

    def _get_async_client(self) -> AsyncBraveSearch | AsyncTavilySearch:
        if self.engine == "brave":
            if self._async_brave is None:
                self._async_brave = AsyncBraveSearch()
            return self._async_brave
        elif self.engine == "tavily":
            if self._async_tavily is None:
                self._async_tavily = AsyncTavilySearch()
            return self._async_tavily
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
        outcome = self.query_optimizer(original_query=query)
        query_list: list[str] = outcome.optimized_search_query  # type: ignore[attr-defined]

        if self.verbose:
            logger.info(f"Optimized: {query} -> {query_list}")
            logger.info(f"Reasoning: {outcome.reasoning}")  # type: ignore[attr-defined]

        return query_list

    def _execute_parallel_searches(
        self,
        query_list: list[str],
    ) -> list[tuple[str, list[SearchResult]]]:
        if self.use_async and self.engine in ("brave", "tavily"):
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
        sources = "\n".join([item.to_markdown() for item in self.search_results])
        search_summary = f"## Web Search Results on |{query}|\n\n"
        search_summary += "\n\n".join(query_summaries)
        search_summary += "\n"
        markdown = search_summary + "\n## Sources\n\n" + sources + "\n"

        if self.verbose:
            logger.info(
                f"{self._name}|{query}|{proc_info}|{self.engine}|{execution_time:.2f}s"
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
                    logger.error(f"Search failed for '{q}': {result}")
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
                logger.error(f"Search failed for '{q}': {e}")
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
                [f"[^{r.sid}] Title: {r.title}\nSnippet: {r.snippet}" for r in results]
            )
            formatted_input.append({"query": q, "results": result_text})

        try:
            output = self.batch_summarizer(
                queries_with_results=json.dumps(formatted_input, ensure_ascii=False)
            )
            summaries: list[str] = output.summaries  # type: ignore[attr-defined]

            if len(summaries) != len(all_results):
                logger.warning(
                    f"Batch summary count mismatch: {len(summaries)} vs {len(all_results)}"
                )
                return self._fallback_to_individual_summaries(all_results)

            query_summaries = []
            for (q, _), summary in zip(all_results, summaries, strict=False):
                summary = self._fix_citations(summary)
                query_summaries.append(f"**{q} (web):** {summary}")
            return query_summaries

        except Exception as e:
            logger.error(f"Batch summarization failed: {e}")
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
            [f"[^{r.sid}] Title: {r.title}\nSnippet: {r.snippet}" for r in results]
        )

        try:
            output = self.single_summarizer(query=query, results=result_text)
            return self._fix_citations(output.summary)  # type: ignore[attr-defined]
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            return "Summary generation failed."

    def _fix_citations(self, text: str) -> str:
        text = re.sub(r"\[(\d+)\]", r"[^\1]", text)
        text = re.sub(r"\[\^\{(\d+)\}\]", r"[^\1]", text)
        return text

    def _add_search_results(self, results: list[SearchResult]) -> None:
        for result in results:
            if result.url not in self._search_results:
                self._search_results[result.url] = result

    @property
    def search_results(self) -> list[SearchResult]:
        return list(self._search_results.values())

    async def cleanup(self) -> None:
        if self._async_brave:
            await self._async_brave.close()
        if self._async_tavily:
            await self._async_tavily.close()


def create_optimized_searcher(
    engine: EngineType = "brave",
    fast_mode: bool = True,
    **kwargs: Any,
) -> OptimizedSearcher:
    defaults = {
        "skip_categorization": fast_mode,
        "batch_summarize": fast_mode,
        "use_async": engine in ("brave", "tavily"),
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

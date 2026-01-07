import time
from unittest.mock import MagicMock, patch

import pytest

from websearch.optimized_searcher import (
    OptimizedSearcher,
    create_optimized_searcher,
)
from websearch.schema import SearchResult


@pytest.fixture
def mock_search_results() -> list[str]:
    results = []
    for i in range(3):
        sr = SearchResult(
            title=f"Title {i}",
            url=f"https://example.com/{i}",
            snippet=f"Snippet content {i}",
        )
        results.append(sr.to_json())
    return results


@pytest.fixture
def mock_dspy_lm() -> MagicMock:
    with patch("dspy.settings") as mock_settings:
        mock_lm = MagicMock()
        mock_settings.lm = mock_lm
        yield mock_lm


class TestOptimizedSearcher:
    def test_create_optimized_searcher_defaults(self) -> None:
        searcher = create_optimized_searcher(engine="ddg")
        assert searcher.engine == "ddg"
        assert searcher.skip_categorization is True
        assert searcher.batch_summarize is True
        assert searcher.max_workers == 5

    def test_create_optimized_searcher_slow_mode(self) -> None:
        searcher = create_optimized_searcher(engine="ddg", fast_mode=False)
        assert searcher.skip_categorization is False
        assert searcher.batch_summarize is False

    def test_search_results_deduplication(self) -> None:
        searcher = OptimizedSearcher(engine="ddg", use_async=False)

        results1 = [
            SearchResult(title="A", url="https://a.com", snippet="A"),
            SearchResult(title="B", url="https://b.com", snippet="B"),
        ]
        results2 = [
            SearchResult(title="A dup", url="https://a.com", snippet="A dup"),
            SearchResult(title="C", url="https://c.com", snippet="C"),
        ]

        searcher._add_search_results(results1)
        searcher._add_search_results(results2)

        assert len(searcher.search_results) == 3
        urls = {r.url for r in searcher.search_results}
        assert urls == {"https://a.com", "https://b.com", "https://c.com"}

    def test_normalize_citations(self) -> None:
        searcher = OptimizedSearcher(engine="ddg", use_async=False)

        assert searcher._normalize_citations("[1]") == "[^1]"
        assert searcher._normalize_citations("[^{2}]") == "[^2]"
        assert searcher._normalize_citations("Text [1] and [2]") == "Text [^1] and [^2]"

    @patch("websearch.optimized_searcher.OptimizedSearcher._search_parallel_sync")
    @patch("websearch.optimized_searcher.OptimizedSearcher._generate_optimized_queries")
    @patch("websearch.optimized_searcher.OptimizedSearcher._get_batch_summaries")
    def test_forward_uses_parallel_search(
        self,
        mock_batch_summaries: MagicMock,
        mock_gen_queries: MagicMock,
        mock_parallel_search: MagicMock,
    ) -> None:
        mock_gen_queries.return_value = ["query1", "query2", "query3"]
        mock_parallel_search.return_value = [
            ("query1", [SearchResult(title="R1", url="https://r1.com", snippet="S1")]),
            ("query2", [SearchResult(title="R2", url="https://r2.com", snippet="S2")]),
            ("query3", [SearchResult(title="R3", url="https://r3.com", snippet="S3")]),
        ]
        mock_batch_summaries.return_value = [
            "**query1 (web):** Summary 1",
            "**query2 (web):** Summary 2",
            "**query3 (web):** Summary 3",
        ]

        searcher = OptimizedSearcher(engine="ddg", use_async=False)
        result = searcher.forward("test query")

        mock_parallel_search.assert_called_once()
        mock_batch_summaries.assert_called_once()
        assert "test query" in result.query
        assert len(searcher.search_results) == 3


class TestPerformanceComparison:
    @pytest.mark.skip(reason="Requires API keys and network access")
    def test_parallel_faster_than_sequential(self) -> None:
        queries = ["python async", "web scraping", "data science", "machine learning"]

        from websearch.ddg import search_web

        start_sequential = time.time()
        for q in queries:
            search_web(q, k=3)
        sequential_time = time.time() - start_sequential

        from concurrent.futures import ThreadPoolExecutor

        start_parallel = time.time()
        with ThreadPoolExecutor(max_workers=4) as executor:
            list(executor.map(lambda q: search_web(q, k=3), queries))
        parallel_time = time.time() - start_parallel

        assert parallel_time < sequential_time
        print(f"Sequential: {sequential_time:.2f}s, Parallel: {parallel_time:.2f}s")
        print(f"Speedup: {sequential_time / parallel_time:.2f}x")

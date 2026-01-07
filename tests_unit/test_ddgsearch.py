#!/usr/bin/env python3
"""Test script for DuckDuckGo search functionality."""

from websearch.ddg import search_news, search_web
from websearch.schema import SearchResult
from websearch.optimized_searcher import create_optimized_searcher
import dspy
from utils.llm import llm_setup


def show_search_results(qtype: str, query: str, results: list[SearchResult]):
    print(f"{qtype} Query: {query}")
    print(f"Found {len(results)} results:")
    for result in results:
        print(result)


def test_basic_search():
    """Test basic search functionality using module-level functions."""
    print("Testing basic DDG search...")

    query = "Python programming"
    results = search_web(query, k=3)
    # Results are JSON strings, convert to SearchResult
    search_results = [SearchResult.from_json(r) for r in results]
    show_search_results("Basic", query, search_results)


def test_news_search():
    """Test news search functionality."""
    print("\n" + "=" * 50)
    print("Testing news search...")

    query = "Tariff of 2025"
    results = search_news(query, k=3)
    search_results = [SearchResult.from_json(r) for r in results]
    show_search_results("News", query, search_results)


def test_optimized_search():
    """Test optimized search functionality using OptimizedSearcher."""
    print("\n" + "=" * 50)
    print("Testing optimized search with DDG...")

    searcher = create_optimized_searcher(engine="ddg", k=3, use_async=False)
    query = "Trends of S&P 500 Index"
    result = searcher(query)

    print(f"Query: {query}")
    print(f"Found {len(result.sources)} results")
    print(f"Execution time: {result.execution_time:.2f}s")
    print(f"\nSummary:\n{result.summary[:500]}...")


if __name__ == "__main__":
    llm_setup("gemini/gemini-2.5-flash-lite")
    dspy.configure_cache(
        enable_disk_cache=True,
        enable_memory_cache=True,
    )
    test_basic_search()
    test_news_search()
    test_optimized_search()

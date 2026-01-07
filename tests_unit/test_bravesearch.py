#!/usr/bin/env python3
"""Test script for Brave search functionality."""

from websearch.brave import search_news, search_web, AsyncBraveSearch
from websearch.schema import SearchResult
from websearch.optimized_searcher import create_optimized_searcher
from dotenv import load_dotenv
from utils.llm import llm_setup, check_environment_cli

load_dotenv()
llm_setup("openai/gpt-4o-mini")
check_environment_cli("openai/gpt-4o-mini", "brave")


def show_search_results(qtype: str, query: str, results: list[SearchResult]):
    print(f"{qtype} Query: {query}")
    print(f"Found {len(results)} results:")

    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Title: {result.title}")
        print(f"URL: {result.url}")
        print(f"Snippet: {result.snippet[:200]}...")
        if result.published_time:
            print(f"Published: {result.published_time}")


def test_basic_search():
    """Test basic search functionality using module-level functions."""
    print("Testing basic Brave search...")

    query = "Python programming"
    results = search_web(query, k=3)
    # Results are JSON strings, convert to SearchResult
    search_results = [SearchResult.from_json(r) for r in results]
    show_search_results("Basic", query, search_results)


def test_news_search():
    """Test news search functionality."""
    print("\n" + "=" * 50)
    print("Testing news search...")

    query = "artificial intelligence"
    results = search_news(query, k=3)
    search_results = [SearchResult.from_json(r) for r in results]
    show_search_results("News", query, search_results)


def test_optimized_search():
    """Test optimized search functionality using OptimizedSearcher."""
    print("\n" + "=" * 50)
    print("Testing optimized search...")

    searcher = create_optimized_searcher(engine="brave", k=3)
    query = "artificial intelligence trends 2024"
    result = searcher(query)

    print(f"Query: {query}")
    print(f"Found {len(result.sources)} results")
    print(f"Execution time: {result.execution_time:.2f}s")
    print(f"\nSummary:\n{result.summary[:500]}...")


async def test_async_search():
    """Test async search functionality."""
    print("\n" + "=" * 50)
    print("Testing async search...")

    client = AsyncBraveSearch()
    try:
        query = "machine learning"
        results = await client.search(query, k=3)
        show_search_results("Async", query, results)
    finally:
        await client.close()


if __name__ == "__main__":
    test_basic_search()
    test_news_search()
    test_optimized_search()

    # Run async test
    import asyncio

    asyncio.run(test_async_search())

#!/usr/bin/env python3
"""Simple test script for BraveSearchTool (basic functionality only)."""

from websearch.bravesearch import BraveSearchTool, OptimizedBraveSearch
from websearch.schema import SearchResult
from typing import List
from dotenv import load_dotenv
from utils.llm import llm_setup, check_environment_cli

load_dotenv()
llm_setup("openai/gpt-4o-mini")
check_environment_cli("openai/gpt-4o-mini", "brave")


def show_search_results(qtype: str, query: str, results: List[SearchResult]):
    print(f"{qtype} Query: {query}")
    print(f"Found {len(results)} results:")

    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Title: {result.title}")
        print(f"URL: {result.url}")
        print(f"Snippet: {result.snippet}")
        print(f"Extra Snippets: {result.extra_snippets}")
        if result.published_time:
            print(f"Published: {result.published_time}")


def test_basic_search():
    """Test basic search functionality"""
    print("Testing basic BraveSearchTool...")

    # Initialize the search tool
    search_tool = BraveSearchTool(k=3)

    # Perform a simple search
    query = "Python programming"
    results = search_tool.search(query)
    show_search_results("Basic", query, results)


def test_news_search():
    """Test news search functionality"""
    print("\n" + "=" * 50)
    print("Testing news search...")

    # Initialize the search tool
    search_tool = BraveSearchTool(k=2)

    # Perform a news search
    query = "artificial intelligence"
    results = search_tool.search_news(query)

    show_search_results("News", query, results)


def test_optimized_search():
    """Test optimized search functionality"""
    print("\n" + "=" * 50)
    print("Testing optimized search...")


    # Initialize the search tool
    search_tool = OptimizedBraveSearch(k=2)

    # Perform an optimized search
    query = "artificial intelligence"
    results = search_tool.optimized_search(query)

    show_search_results("Optimized", query, results)


def test_filtered_search():
    """Test search with filters"""
    print("\n" + "=" * 50)
    print("Testing filtered search...")

    # Initialize the optimized search tool (which has search_with_filters)
    search_tool = OptimizedBraveSearch(k=2)

    # Perform a filtered search
    query = "machine learning"
    results = search_tool.search_with_filters(
        query=query,
        domain_filter="wikipedia.org",
        date_filter="2024-01-01",
    )

    show_search_results("Filtered", query, results)


if __name__ == "__main__":
    test_basic_search()
    test_news_search()
    test_optimized_search()
    test_filtered_search()

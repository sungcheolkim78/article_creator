#!/usr/bin/env python3
"""
Simple test script for DDGSearchTool (basic functionality only)
"""

from websearch.tavily import search_news, search_web
from websearch.schema import SearchResult
from typing import List
import dspy
from utils.llm import llm_setup


def show_search_results(qtype: str, query: str, results: List[SearchResult]):
    print(f"{qtype} Query: {query}")
    print(f"Found {len(results)} results:")
    for result in results:
        print(result)


def test_basic_search():
    """Test basic search functionality"""
    print("Testing basic TavilySearch...")

    # Perform a simple search
    query = "Python programming"
    results = search_web(query)
    show_search_results("Basic", query, results)


def test_news_search():
    """Test news search functionality"""
    print("\n" + "=" * 50)
    print("Testing news search...")

    # Perform a news search
    query = "Tariff of 2025"
    results = search_news(query)
    show_search_results("News", query, results)


if __name__ == "__main__":
    # llm_setup("openrouter/x-ai/grok-3-mini")
    # llm_setup("openrouter/google/gemini-2.5-flash-lite")
    # llm_setup("openai/gpt-4o-mini")
    llm_setup("gemini/gemini-2.5-flash-lite")
    dspy.configure_cache(
        enable_disk_cache=True,
        enable_memory_cache=True,
    )
    test_basic_search()
    test_news_search()
    # test_optimized_search()
    # test_filtered_search()
    # test_ddg_react_searcher()

    # txt = tool_search_web("Lovable AI", verbose=False)
    # print(txt)

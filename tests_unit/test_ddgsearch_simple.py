#!/usr/bin/env python3
"""
Simple test script for DDGSearchTool (basic functionality only)
"""

from ddgsearch import DDGSearchTool, OptimizedDDGSearch


def test_basic_search():
    """Test basic search functionality"""
    print("Testing basic DDGSearchTool...")

    # Initialize the search tool
    search_tool = DDGSearchTool(k=3)

    # Perform a simple search
    query = "Python programming"
    results = search_tool.search(query)

    print(f"Query: {query}")
    print(f"Found {len(results)} results:")

    for i, result in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Title: {result.title}")
        print(f"URL: {result.url}")
        print(f"Snippet: {result.snippet[:200]}...")
        if result.published_time:
            print(f"Published: {result.published_time}")


def test_news_search():
    """Test news search functionality"""
    print("\n" + "=" * 50)
    print("Testing news search...")

    # Initialize the search tool
    search_tool = DDGSearchTool(k=2)

    # Perform a news search
    query = "artificial intelligence"
    results = search_tool.search_news(query)

    print(f"News Query: {query}")
    print(f"Found {len(results)} news results:")

    for i, result in enumerate(results, 1):
        print(f"\n--- News Result {i} ---")
        print(f"Title: {result.title}")
        print(f"URL: {result.url}")
        print(f"Snippet: {result.snippet[:200]}...")
        if result.published_time:
            print(f"Published: {result.published_time}")


def test_filtered_search():
    """Test search with filters"""
    print("\n" + "=" * 50)
    print("Testing filtered search...")

    # Initialize the optimized search tool (which has search_with_filters)
    search_tool = OptimizedDDGSearch(k=2)

    # Perform a filtered search
    query = "machine learning"
    results = search_tool.search_with_filters(
        query=query,
        region_filter="us-en",
        time_filter="m",  # Last month
    )

    print(f"Filtered Query: {query}")
    print(f"Found {len(results)} results:")

    for i, result in enumerate(results, 1):
        print(f"\n--- Filtered Result {i} ---")
        print(f"Title: {result.title}")
        print(f"URL: {result.url}")
        print(f"Snippet: {result.snippet[:200]}...")
        if result.published_time:
            print(f"Published: {result.published_time}")


if __name__ == "__main__":
    try:
        test_basic_search()
        test_news_search()
        test_filtered_search()
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback

        traceback.print_exc()

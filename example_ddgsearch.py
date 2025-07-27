#!/usr/bin/env python3
"""
Example usage of DDGSearchTool and OptimizedDDGSearch
"""

from src.ddgsearch import DDGSearchTool, OptimizedDDGSearch


def main():
    """Demonstrate the usage of DDGSearchTool classes"""
    
    print("=== DDGSearchTool Example ===\n")
    
    # Basic search
    print("1. Basic Search:")
    search_tool = DDGSearchTool(k=2)
    results = search_tool.search("Python programming")
    
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result.title}")
        print(f"     {result.snippet[:100]}...")
        print()
    
    # News search
    print("2. News Search:")
    news_results = search_tool.search_news("artificial intelligence")
    
    for i, result in enumerate(news_results, 1):
        print(f"  {i}. {result.title}")
        print(f"     {result.snippet[:100]}...")
        print()
    
    print("=== OptimizedDDGSearch Example ===\n")
    
    # Filtered search (without LM optimization to avoid errors)
    print("3. Filtered Search:")
    optimized_tool = OptimizedDDGSearch(k=2)
    filtered_results = optimized_tool.search_with_filters(
        query="machine learning",
        region_filter="us-en",
        time_filter="m"  # Last month
    )
    
    for i, result in enumerate(filtered_results, 1):
        print(f"  {i}. {result.title}")
        print(f"     {result.snippet[:100]}...")
        print()
    
    print("=== Usage Summary ===")
    print("• DDGSearchTool: Basic search functionality")
    print("• OptimizedDDGSearch: Advanced features with query optimization")
    print("• Both support: text search, news search, and filtered search")
    print("• Compatible with DSPy framework")


if __name__ == "__main__":
    main() 
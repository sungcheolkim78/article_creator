#!/usr/bin/env python3
"""
Test script to verify the memory fixes work correctly.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from react_module import ReACTAgent
from bravesearch import OptimizedBraveSearch
import dspy


def setup_dspy():
    """Setup DSPy with OpenAI model."""
    try:
        # Try to use OpenAI
        lm = dspy.OpenAI(model="gpt-4o-mini", max_tokens=1000)
        dspy.settings.configure(lm=lm)
        print("✅ Using OpenAI GPT-4o-mini")
        return True
    except Exception as e:
        print(f"⚠️  OpenAI setup failed: {e}")
        print("Please set OPENAI_API_KEY environment variable")
        return False


def test_search_with_no_results():
    """Test search functionality with a query that might have no results."""
    print("\n" + "=" * 60)
    print("🧪 TEST: Search with No Results")
    print("=" * 60)

    # Initialize search tool and agent
    search_tool = OptimizedBraveSearch()
    agent = ReACTAgent(brave_search=search_tool, memory_size=100)

    # Test with a very specific query that might not have results
    test_query = "very specific technical term that probably doesn't exist 2024"

    print(f"\n🔍 Testing search with query: '{test_query}'")

    # Perform search directly
    search_result = agent._perform_search(test_query)

    print(f"\n📊 Search Result:")
    print(f"   - Success: {search_result.get('success', False)}")
    print(f"   - Num Results: {search_result.get('num_results', 0)}")

    if search_result.get("broader_query"):
        print(f"   - Broader Query: {search_result['broader_query']}")

    if search_result.get("note"):
        print(f"   - Note: {search_result['note']}")

    if search_result.get("error"):
        print(f"   - Error: {search_result['error']}")

    return search_result


def test_memory_storage():
    """Test that memory storage works correctly with SearchResult objects."""
    print("\n" + "=" * 60)
    print("🧪 TEST: Memory Storage")
    print("=" * 60)

    # Initialize search tool and agent
    search_tool = OptimizedBraveSearch()
    agent = ReACTAgent(brave_search=search_tool, memory_size=100)

    # Test with a simple query
    test_query = "AI agents"

    print(f"\n🔍 Testing memory storage with query: '{test_query}'")

    # Perform search
    search_result = agent._perform_search(test_query)

    # Store in memory
    agent._store_action_in_memory("search", test_query, search_result)

    # Check memory summary
    memory_summary = agent.memory.get_memory_summary()

    print(f"\n📊 Memory Summary:")
    print(f"   - Search Results: {memory_summary['total_search_results']}")
    print(f"   - Sources: {memory_summary['total_sources']}")
    print(f"   - Memory Size: {memory_summary['memory_size']}")

    # Test memory retrieval
    relevant_results = agent.memory.get_relevant_search_results(
        test_query, max_results=1
    )

    if relevant_results:
        print(f"\n✅ Memory retrieval successful:")
        print(f"   - Retrieved {len(relevant_results)} search results")
        print(f"   - Query: {relevant_results[0]['query']}")
        print(f"   - Results count: {len(relevant_results[0]['results'])}")
    else:
        print(f"\n❌ Memory retrieval failed")

    return memory_summary


def test_react_with_memory():
    """Test ReACT agent with memory functionality."""
    print("\n" + "=" * 60)
    print("🧪 TEST: ReACT with Memory")
    print("=" * 60)

    # Initialize search tool and agent
    search_tool = OptimizedBraveSearch()
    agent = ReACTAgent(brave_search=search_tool, memory_size=100)

    # Test with a simple goal
    test_goal = "Research AI agents"

    print(f"\n🎯 Testing ReACT with goal: '{test_goal}'")

    try:
        # Run ReACT for a few iterations
        result = agent.forward(test_goal, max_iterations=2)

        print(f"\n📊 ReACT Result:")
        print(f"   - Completed: {result.get('completed', False)}")
        print(f"   - Actions Taken: {len(result.get('actions_taken', []))}")
        print(
            f"   - Memory Size: {result.get('memory_summary', {}).get('memory_size', 0)}"
        )

        # Show actions taken
        for action in result.get("actions_taken", []):
            print(
                f"   - Action {action['iteration']}: {action['action']} - Success: {action['result'].get('success', False)}"
            )

        return result

    except Exception as e:
        print(f"\n❌ ReACT test failed: {e}")
        import traceback

        traceback.print_exc()
        return None


def main():
    """Main test function."""
    print("🧪 Testing Memory Fixes")
    print(
        "This script tests the fixes for SearchResult object handling and no-results scenarios."
    )

    # Setup DSPy
    if not setup_dspy():
        print("❌ DSPy setup failed. Exiting.")
        return

    try:
        # Run tests
        test_search_with_no_results()
        test_memory_storage()
        test_react_with_memory()

        print("\n" + "=" * 60)
        print("✅ All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

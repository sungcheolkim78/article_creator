#!/usr/bin/env python3
"""
Test script to verify the memory fixes work correctly.
"""

from core.react_base import ReACTAgent
from core.react_memory import ReactMemory
from websearch.optimized_searcher import create_optimized_searcher
from utils.llm import llm_setup
import dspy


def setup_dspy():
    """Setup DSPy with OpenAI model."""
    try:
        llm_setup("openai/gpt-4o-mini")
        print("Using OpenAI GPT-4o-mini")
        return True
    except Exception as e:
        print(f"OpenAI setup failed: {e}")
        print("Please set OPENAI_API_KEY environment variable")
        return False


def test_memory_basic():
    """Test basic memory functionality."""
    print("\n" + "=" * 60)
    print("TEST: Basic Memory Functionality")
    print("=" * 60)

    memory = ReactMemory(max_memory_size=100)

    # Test adding search results
    memory.add_search_result(
        query="test query",
        results=[
            {"title": "Test", "url": "http://test.com", "snippet": "Test snippet"}
        ],
        metadata={"num_results": 1},
    )

    # Test retrieval
    relevant = memory.get_relevant_search_results("test", max_results=1)
    print(f"Added and retrieved search result: {len(relevant)} results")

    # Test memory summary
    summary = memory.get_memory_summary()
    print(f"Memory Summary: {summary}")

    return summary


def test_search_with_optimized_searcher():
    """Test search functionality with OptimizedSearcher."""
    print("\n" + "=" * 60)
    print("TEST: Search with OptimizedSearcher")
    print("=" * 60)

    searcher = create_optimized_searcher(engine="ddg", k=3, use_async=False)
    query = "AI agents"

    print(f"Testing search with query: '{query}'")

    result = searcher(query)

    print(f"Search Result:")
    print(f"   - Num Results: {len(result.sources)}")
    print(f"   - Execution Time: {result.execution_time:.2f}s")
    print(f"   - Summary preview: {result.summary[:200]}...")

    return result


def test_react_agent_with_memory():
    """Test ReACT agent with memory functionality."""
    print("\n" + "=" * 60)
    print("TEST: ReACT Agent with Memory")
    print("=" * 60)

    # Initialize search tool and agent
    search_tool = create_optimized_searcher(engine="ddg", k=3, use_async=False)
    agent = ReACTAgent(search_tool, memory_size=100)

    # Test with a simple goal
    test_goal = "Research AI agents"

    print(f"Testing ReACT with goal: '{test_goal}'")

    try:
        # Run ReACT for a few iterations
        result = agent.forward(test_goal, max_iterations=2)

        print(f"\nReACT Result:")
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
        print(f"\nReACT test failed: {e}")
        import traceback

        traceback.print_exc()
        return None


def main():
    """Main test function."""
    print("Testing Memory System")
    print("This script tests the memory system and ReACT agent integration.")

    # Test basic memory without LLM
    test_memory_basic()

    # Setup DSPy for LLM-dependent tests
    if not setup_dspy():
        print("DSPy setup failed. Skipping LLM-dependent tests.")
        return

    try:
        # Run LLM-dependent tests
        test_search_with_optimized_searcher()
        test_react_agent_with_memory()

        print("\n" + "=" * 60)
        print("All tests completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

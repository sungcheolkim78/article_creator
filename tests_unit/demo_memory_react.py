#!/usr/bin/env python3
"""
Demo script for the memory-enhanced ReACT agent.
This script demonstrates how the ReACT agent can maintain context and search sources across iterations.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from react_module import ReACTAgent, ArticleReACTAgent
from bravesearch import OptimizedBraveSearch
import dspy


def setup_dspy():
    """Setup DSPy with OpenAI model."""
    try:
        # Try to use OpenAI
        lm = dspy.OpenAI(model="gpt-4o-mini", max_tokens=1000)
        dspy.settings.configure(lm=lm)
        print("✅ Using OpenAI GPT-4o-mini")
    except Exception as e:
        print(f"⚠️  OpenAI setup failed: {e}")
        print("Please set OPENAI_API_KEY environment variable")
        return False
    return True


def demo_basic_memory_react():
    """Demo basic ReACT agent with memory capabilities."""
    print("\n" + "=" * 60)
    print("🧠 DEMO: Basic ReACT Agent with Memory")
    print("=" * 60)

    # Initialize search tool and agent
    search_tool = OptimizedBraveSearch()
    agent = ReACTAgent(brave_search=search_tool, memory_size=500)

    # First goal - research AI agents
    print("\n🎯 Goal 1: Research AI agents")
    result1 = agent.forward(
        goal="Research current trends in AI agents and their applications",
        max_iterations=3,
    )

    print(f"\n📊 Memory Summary after Goal 1:")
    print(f"   - Search Results: {result1['memory_summary']['total_search_results']}")
    print(
        f"   - Research Findings: {result1['memory_summary']['total_research_findings']}"
    )
    print(f"   - Sources: {result1['memory_summary']['total_sources']}")

    # Second goal - related research using memory
    print("\n🎯 Goal 2: Research AI agent frameworks (should use memory)")
    result2 = agent.forward(
        goal="Research popular AI agent frameworks and tools", max_iterations=3
    )

    print(f"\n📊 Memory Summary after Goal 2:")
    print(f"   - Search Results: {result2['memory_summary']['total_search_results']}")
    print(
        f"   - Research Findings: {result2['memory_summary']['total_research_findings']}"
    )
    print(f"   - Sources: {result2['memory_summary']['total_sources']}")

    # Third goal - fact checking using memory
    print("\n🎯 Goal 3: Fact check AI agent claims (should use memory)")
    result3 = agent.forward(
        goal="Fact check claims about AI agent capabilities and limitations",
        max_iterations=2,
    )

    print(f"\n📊 Final Memory Summary:")
    print(f"   - Search Results: {result3['memory_summary']['total_search_results']}")
    print(
        f"   - Research Findings: {result3['memory_summary']['total_research_findings']}"
    )
    print(f"   - Fact Checks: {result3['memory_summary']['total_fact_checks']}")
    print(f"   - Sources: {result3['memory_summary']['total_sources']}")
    print(f"   - Insights: {result3['memory_summary']['total_insights']}")

    return agent


def demo_article_agent_with_memory():
    """Demo ArticleReACTAgent with memory for article generation."""
    print("\n" + "=" * 60)
    print("📝 DEMO: Article ReACT Agent with Memory")
    print("=" * 60)

    # Initialize search tool and article agent
    search_tool = OptimizedBraveSearch()
    article_agent = ArticleReACTAgent(brave_search=search_tool, memory_size=1000)

    # Generate article with research
    print("\n🎯 Generating article about AI agents with memory-enhanced research")
    result = article_agent.generate_article_with_research(
        topic="The Future of AI Agents in Software Development",
        initial_outline={
            "title": "The Future of AI Agents in Software Development",
            "sections": [
                "Introduction to AI Agents",
                "Current State of AI Agents in Development",
                "Future Trends and Predictions",
                "Challenges and Limitations",
                "Conclusion",
            ],
        },
    )

    print(f"\n📊 Article Generation Results:")
    print(f"   - Topic: {result['topic']}")
    print(f"   - Research Actions: {len(result['research_phase']['actions_taken'])}")
    print(f"   - Synthesis Actions: {len(result['synthesis_phase']['actions_taken'])}")
    print(f"   - Total Actions: {result['total_actions']}")

    print(f"\n📊 Memory Summary:")
    print(f"   - Search Results: {result['memory_summary']['total_search_results']}")
    print(
        f"   - Research Findings: {result['memory_summary']['total_research_findings']}"
    )
    print(f"   - Sources: {result['memory_summary']['total_sources']}")
    print(f"   - Insights: {result['memory_summary']['total_insights']}")

    # Show some memory insights
    print(f"\n💡 Recent Insights from Memory:")
    insights = article_agent.memory.get_recent_insights(max_insights=3)
    for i, insight in enumerate(insights, 1):
        print(f"   {i}. {insight[:100]}...")

    return article_agent


def demo_memory_persistence():
    """Demo how memory persists across different sessions."""
    print("\n" + "=" * 60)
    print("🔄 DEMO: Memory Persistence Across Sessions")
    print("=" * 60)

    search_tool = OptimizedBraveSearch()

    # First session
    print("\n📅 Session 1: Initial research")
    agent1 = ReACTAgent(brave_search=search_tool, memory_size=500)
    result1 = agent1.forward(
        goal="Research Python frameworks for AI agents", max_iterations=2
    )

    print(f"   - Memory items: {result1['memory_summary']['memory_size']}")

    # Second session with same agent (simulating persistence)
    print("\n📅 Session 2: Related research (should benefit from memory)")
    result2 = agent1.forward(
        goal="Research JavaScript frameworks for AI agents", max_iterations=2
    )

    print(f"   - Memory items: {result2['memory_summary']['memory_size']}")

    # Third session with new agent (simulating fresh start)
    print("\n📅 Session 3: New agent (no memory)")
    agent2 = ReACTAgent(brave_search=search_tool, memory_size=500)
    result3 = agent2.forward(
        goal="Research Python frameworks for AI agents", max_iterations=2
    )

    print(f"   - Memory items: {result3['memory_summary']['memory_size']}")

    print(
        "\n💭 Note: In a real application, memory would be persisted to disk/database"
    )


def main():
    """Main demo function."""
    print("🧠 ReACT Agent with Memory Demo")
    print(
        "This demo shows how the ReACT agent can maintain context and search sources across iterations."
    )

    # Setup DSPy
    if not setup_dspy():
        print("❌ DSPy setup failed. Exiting.")
        return

    try:
        # Run demos
        demo_basic_memory_react()
        demo_article_agent_with_memory()
        demo_memory_persistence()

        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("=" * 60)
        print("\nKey Features Demonstrated:")
        print("• Memory storage of search results, research findings, and sources")
        print("• Context-aware retrieval of relevant information")
        print("• Memory persistence across multiple goals")
        print("• Enhanced reasoning with memory context")
        print("• Automatic memory management and cleanup")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()

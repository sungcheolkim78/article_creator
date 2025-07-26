#!/usr/bin/env python3
"""
Demonstration script for enhanced article generator with web search and ReACT module.

This script shows different ways to use the enhanced article generation features:
1. Enhanced mode with ReACT agent
2. Web search mode 
3. ReACT-only research mode
4. Comparison with original article generator
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from utils import llm_setup
from bravesearch import OptimizedBraveSearch
from enhanced_article_creator import EnhancedDraftArticle, WebSearchArticleCreator
from react_module import ArticleReACTAgent
from article_creator import DraftArticle

load_dotenv()


def demo_enhanced_article_generation():
    """Demonstrate enhanced article generation with all features."""
    print("🚀 Enhanced Article Generator Demo")
    print("=" * 50)
    
    # Setup
    llm_setup("openai/gpt-4o-mini")
    
    # Check for API keys
    brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        print("❌ OPENAI_API_KEY not found. Please set this environment variable.")
        return
    
    if not brave_api_key:
        print("⚠️  BRAVE_SEARCH_API_KEY not found. Web search features will be limited.")
        print("   You can get a free API key at: https://api.search.brave.com/")
        return
    
    print("✅ API keys found. Initializing search tools...")
    
    # Initialize search tool
    search_tool = OptimizedBraveSearch(api_key=brave_api_key, k=5, source="web")
    
    # Demo topic
    topic = "Quantum computing breakthroughs in 2024"
    print(f"\n📝 Demo topic: {topic}")
    
    # 1. Enhanced Article Generation with ReACT
    print("\n" + "=" * 50)
    print("1️⃣  ENHANCED MODE WITH REACT AGENT")
    print("=" * 50)
    
    enhanced_generator = EnhancedDraftArticle(search_tool)
    print("Generating article with ReACT agent and comprehensive research...")
    
    try:
        enhanced_result = enhanced_generator.forward(
            topic=topic, 
            language="English", 
            use_react=True
        )
        
        print(f"✅ Enhanced article generated!")
        print(f"   Title: {enhanced_result.title}")
        print(f"   Sections: {len(enhanced_result.sections_en)}")
        print(f"   Research summary length: {len(enhanced_result.research_summary)} chars")
        
        # Save enhanced result
        output_dir = Path("data/demo_articles")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "enhanced_quantum_article.md", "w") as f:
            f.write(f"# {enhanced_result.title}\n\n")
            for section in enhanced_result.sections_en:
                f.write(section + "\n\n")
            
            if enhanced_result.key_sources:
                f.write("## Sources\n\n")
                for source in enhanced_result.key_sources:
                    f.write(f"- {source}\n")
        
        print(f"   Saved to: {output_dir / 'enhanced_quantum_article.md'}")
        
    except Exception as e:
        print(f"❌ Error in enhanced mode: {e}")
    
    # 2. Web Search Only Mode
    print("\n" + "=" * 50)
    print("2️⃣  WEB SEARCH MODE")
    print("=" * 50)
    
    web_generator = WebSearchArticleCreator(search_tool)
    print("Generating article with focused web search integration...")
    
    try:
        web_result = web_generator.forward(topic=topic, language="English")
        
        print(f"✅ Web search article generated!")
        print(f"   Title: {web_result.title}")
        print(f"   Sections: {len(web_result.sections_en)}")
        print(f"   Research sources: {len(web_result.research_sources)}")
        
        # Save web search result
        with open(output_dir / "websearch_quantum_article.md", "w") as f:
            f.write(f"# {web_result.title}\n\n")
            for section in web_result.sections_en:
                f.write(section + "\n\n")
            
            f.write("## Research Sources\n\n")
            for i, source in enumerate(web_result.research_sources, 1):
                f.write(f"{i}. [{source.title}]({source.url})\n")
                f.write(f"   {source.snippet}\n\n")
        
        print(f"   Saved to: {output_dir / 'websearch_quantum_article.md'}")
        
    except Exception as e:
        print(f"❌ Error in web search mode: {e}")
    
    # 3. ReACT Research Only
    print("\n" + "=" * 50)
    print("3️⃣  REACT RESEARCH MODE")
    print("=" * 50)
    
    react_agent = ArticleReACTAgent(search_tool)
    print("Running ReACT research analysis...")
    
    try:
        react_results = react_agent.generate_article_with_research(topic)
        
        print(f"✅ ReACT research completed!")
        print(f"   Total actions taken: {react_results['total_actions']}")
        print(f"   Research phase actions: {len(react_results['research_phase']['actions_taken'])}")
        print(f"   Synthesis phase actions: {len(react_results['synthesis_phase']['actions_taken'])}")
        
        # Save ReACT analysis
        with open(output_dir / "react_research_analysis.md", "w") as f:
            f.write(f"# ReACT Research Analysis: {topic}\n\n")
            f.write(f"## Enhanced Reasoning\n\n")
            f.write(f"**Strategy:** {react_results['enhanced_reasoning'].research_strategy}\n\n")
            f.write(f"**Action Plan:** {react_results['enhanced_reasoning'].action_plan}\n\n")
            
            f.write(f"## Research Phase Actions\n\n")
            for action in react_results['research_phase']['actions_taken']:
                f.write(f"### Action {action['iteration']}: {action['action']}\n\n")
                f.write(f"**Thought:** {action['thought']}\n\n")
                f.write(f"**Input:** {action['action_input']}\n\n")
                f.write(f"**Success:** {action['result'].get('success', 'Unknown')}\n\n")
        
        print(f"   Saved to: {output_dir / 'react_research_analysis.md'}")
        
    except Exception as e:
        print(f"❌ Error in ReACT mode: {e}")
    
    # 4. Comparison with Original
    print("\n" + "=" * 50)
    print("4️⃣  COMPARISON WITH ORIGINAL")
    print("=" * 50)
    
    print("Generating article with original method for comparison...")
    
    try:
        original_generator = DraftArticle()
        original_result = original_generator.forward(topic=topic, language="English")
        
        print(f"✅ Original article generated!")
        print(f"   Title: {original_result.title}")
        print(f"   Sections: {len(original_result.sections_en)}")
        
        # Save original result
        with open(output_dir / "original_quantum_article.md", "w") as f:
            f.write(f"# {original_result.title}\n\n")
            for section in original_result.sections_en:
                f.write(section + "\n\n")
        
        print(f"   Saved to: {output_dir / 'original_quantum_article.md'}")
        
    except Exception as e:
        print(f"❌ Error in original mode: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DEMO SUMMARY")
    print("=" * 50)
    print("Generated articles for comparison:")
    print("1. Enhanced with ReACT: comprehensive research + reasoning")
    print("2. Web Search: focused search integration")
    print("3. ReACT Research: research analysis only")
    print("4. Original: baseline comparison")
    print(f"\nAll files saved to: {output_dir}")
    print("\nKey improvements in enhanced version:")
    print("✨ Real-time web search integration")
    print("🧠 ReACT reasoning for intelligent research")
    print("🔍 Fact-checking capabilities")
    print("📚 Source citation and verification")
    print("🌐 Current information from multiple sources")


def demo_react_agent_standalone():
    """Demonstrate standalone ReACT agent capabilities."""
    print("\n🧠 ReACT Agent Standalone Demo")
    print("=" * 50)
    
    # Setup
    llm_setup("openai/gpt-4o-mini")
    brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    
    if not brave_api_key:
        print("❌ BRAVE_SEARCH_API_KEY required for this demo.")
        return
    
    search_tool = OptimizedBraveSearch(api_key=brave_api_key, k=5, source="web")
    react_agent = ArticleReACTAgent(search_tool)
    
    # Demo various ReACT goals
    goals = [
        "Research the latest AI safety developments and key concerns in 2024",
        "Find current information about renewable energy adoption worldwide",
        "Investigate recent breakthroughs in medical AI applications"
    ]
    
    for i, goal in enumerate(goals, 1):
        print(f"\n{i}. Goal: {goal}")
        print("-" * 60)
        
        try:
            result = react_agent.forward(goal, max_iterations=5)
            print(f"✅ Completed in {result['final_iteration']} iterations")
            print(f"   Actions taken: {len(result['actions_taken'])}")
            print(f"   Information gathered: {len(result['gathered_information'])}")
            
            # Show the reasoning process
            for action in result['actions_taken'][-2:]:  # Show last 2 actions
                print(f"   Last action: {action['action']} - {action['thought'][:100]}...")
                
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    # Run the demos
    demo_enhanced_article_generation()
    
    # Optionally run standalone ReACT demo
    response = input("\n🤔 Would you like to run the standalone ReACT agent demo? (y/N): ")
    if response.lower() == 'y':
        demo_react_agent_standalone()
    
    print("\n🎉 Demo completed! Check the generated articles in data/demo_articles/")
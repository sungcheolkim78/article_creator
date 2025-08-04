#!/usr/bin/env python3
"""
Command-line interface for the enhanced article creator

This CLI provides the same functionality as the Streamlit app but through command-line arguments.
It can generate articles using the enhanced article creator and displays the output in different
translation versions (English, Korean, and Research summary).
"""

import argparse
import os
import sys
from pathlib import Path
import time
from datetime import datetime
import json
from typing import Dict, Any, Optional

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent))

from enhanced_article_creator import EnhancedDraftArticle, WebSearchArticleCreator
from bravesearch import OptimizedBraveSearch
from ddgsearch import OptimizedDDGSearch
from utils import llm_setup

def setup_search_tool(search_tool_name: str) -> Optional[Any]:
    """Setup and return the search tool based on user selection."""
    try:
        if search_tool_name == "brave":
            brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
            if not brave_api_key:
                print("❌ BRAVE_SEARCH_API_KEY not found in environment variables.")
                print("Please set BRAVE_SEARCH_API_KEY for Brave Search functionality.")
                return None
            return OptimizedBraveSearch(api_key=brave_api_key, k=5, source="web")
        elif search_tool_name == "ddg":
            return OptimizedDDGSearch(k=5)
        else:
            print(f"❌ Invalid search tool: {search_tool_name}")
            return None
    except Exception as e:
        print(f"❌ Error setting up search tool: {str(e)}")
        return None

def generate_article(topic: str, language: str, mode: str, use_react: bool, 
                    llm_model: str, search_tool_name: str) -> Optional[Dict[str, Any]]:
    """Generate article using the enhanced article creator."""
    
    print("🔄 Setting up LLM and search tools...")
    try:
        # Setup LLM
        llm_setup(llm_model)
        
        # Setup search tool
        search_tool = setup_search_tool(search_tool_name)
        if not search_tool:
            return None
            
    except Exception as e:
        print(f"❌ Error during setup: {str(e)}")
        return None
    
    # Choose article generator based on mode
    if mode == "enhanced":
        print("🔄 Initializing Enhanced Article Creator...")
        article_generator = EnhancedDraftArticle(search_tool)
        
        print("🔄 Generating enhanced article with research and ReACT integration...")
        try:
            prediction = article_generator.forward(
                topic=topic, language=language, use_react=use_react
            )
            return prediction
        except Exception as e:
            print(f"❌ Error generating enhanced article: {str(e)}")
            return None
            
    elif mode == "websearch":
        print("🔄 Initializing Web Search Article Creator...")
        article_generator = WebSearchArticleCreator(search_tool)
        
        print("🔄 Generating article with web search integration...")
        try:
            prediction = article_generator.forward(topic=topic, language=language)
            return prediction
        except Exception as e:
            print(f"❌ Error generating web search article: {str(e)}")
            return None
    else:
        print(f"❌ Invalid mode: {mode}")
        return None

def display_article_metrics(article_data: Dict[str, Any]):
    """Display metrics about the generated article."""
    print("\n📊 Article Metrics:")
    print(f"  Title Length: {len(article_data.get('title', ''))}")
    
    sections_en = article_data.get('sections_en', [])
    total_en_words = sum(len(section.split()) for section in sections_en)
    print(f"  English Words: {total_en_words}")
    
    sections_other = article_data.get('sections_other', [])
    total_other_words = sum(len(section.split()) for section in sections_other)
    print(f"  Other Language Words: {total_other_words}")
    
    print(f"  Sections: {len(sections_en)}")

def display_article_content(article_data: Dict[str, Any], language: str):
    """Display the article content in a formatted way."""
    
    print(f"\n📝 Article: {article_data.get('title', 'Untitled Article')}")
    
    # Display metrics
    display_article_metrics(article_data)
    
    # Display content based on language
    if language.lower() == "english":
        sections = article_data.get('sections_en', [])
        print(f"\n📖 Article Content (English):")
    else:
        sections = article_data.get('sections_other', [])
        print(f"\n📖 Article Content ({language}):")
    
    # Display each section
    for i, section in enumerate(sections, 1):
        print(f"\n--- Section {i} ---")
        print(section)
    
    # Display sources if available
    if hasattr(article_data, 'key_sources') and article_data.key_sources:
        print(f"\n📚 Sources:")
        for source in article_data.key_sources:
            print(f"  - {source}")
    
    # Display research summary if available
    if hasattr(article_data, 'research_summary') and article_data.research_summary:
        print(f"\n🔬 Research Summary:")
        print(article_data.research_summary)

def save_article_to_file(article_data: Dict[str, Any], topic: str, language: str, 
                        output_dir: str, generation_params: Dict[str, Any]) -> Optional[Dict[str, str]]:
    """Save the generated article to files."""
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        topic_slug = topic.lower().replace(" ", "-").replace(",", "")
        lang_slug = language[:3].lower()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        saved_files = {}
        
        # Save translated version
        translated_file = output_path / f"{topic_slug}-{lang_slug}-{timestamp}.md"
        with open(translated_file, "w", encoding="utf-8") as f:
            f.write(f"# {article_data.get('title', 'Untitled Article')}\n\n")
            for section in article_data.get('sections_other', []):
                f.write(section)
                f.write("\n\n")
            
            # Add sources
            if hasattr(article_data, 'key_sources') and article_data.key_sources:
                f.write("## Sources\n\n")
                for source in article_data.key_sources:
                    f.write(f"- {source}\n")
        
        saved_files['translated_file'] = str(translated_file)
        print(f"✅ Saved translated version: {translated_file}")
        
        # Save English version
        english_file = output_path / f"{topic_slug}-en-{timestamp}.md"
        with open(english_file, "w", encoding="utf-8") as f:
            f.write(f"# {article_data.get('title', 'Untitled Article')}\n\n")
            for section in article_data.get('sections_en', []):
                f.write(section)
                f.write("\n\n")
            
            # Add sources
            if hasattr(article_data, 'key_sources') and article_data.key_sources:
                f.write("## Sources\n\n")
                for source in article_data.key_sources:
                    f.write(f"- {source}\n")
        
        saved_files['english_file'] = str(english_file)
        print(f"✅ Saved English version: {english_file}")
        
        # Save research summary if available
        if hasattr(article_data, 'research_summary') and article_data.research_summary:
            research_file = output_path / f"{topic_slug}-research-{timestamp}.md"
            with open(research_file, "w", encoding="utf-8") as f:
                f.write(f"# Research Summary: {article_data.get('title', 'Untitled Article')}\n\n")
                f.write(article_data.research_summary)
                f.write("\n\n")
                f.write("## Generation Parameters\n\n")
                f.write(f"- Topic: {generation_params['topic']}\n")
                f.write(f"- Language: {generation_params['language']}\n")
                f.write(f"- Mode: {generation_params['mode']}\n")
                f.write(f"- LLM Model: {generation_params['llm_model']}\n")
                f.write(f"- Search Tool: {generation_params['search_tool_name']}\n")
                f.write(f"- ReACT Agent: {'Enabled' if generation_params['use_react'] else 'Disabled'}\n")
                f.write(f"- Generated At: {generation_params['generation_time']}\n")
            
            saved_files['research_file'] = str(research_file)
            print(f"✅ Saved research summary: {research_file}")
        
        return saved_files
        
    except Exception as e:
        print(f"❌ Error saving article to file: {str(e)}")
        return None

def check_environment(llm_model: str, search_tool_name: str):
    """Check if required environment variables are set."""
    print("🔑 Environment Check:")
    
    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    brave_key = os.getenv("BRAVE_SEARCH_API_KEY")
    
    if "openai" in llm_model:
        if openai_key:
            print("✅ OpenAI API Key found")
        else:
            print("❌ OpenAI API Key missing")
            return False
    elif "anthropic" in llm_model:
        if anthropic_key:
            print("✅ Anthropic API Key found")
        else:
            print("❌ Anthropic API Key missing")
            return False
    elif "gemini" in llm_model:
        if gemini_key:
            print("✅ Gemini API Key found")
        else:
            print("❌ Gemini API Key missing")
            return False
    
    if search_tool_name == "brave":
        if brave_key:
            print("✅ Brave Search API Key found")
        else:
            print("⚠️ Brave Search API Key missing")
            return False
    
    return True

def main():
    """Main CLI application."""
    
    parser = argparse.ArgumentParser(
        description="Enhanced Article Creator CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate an article with default settings
  python src/cli.py --topic "The impact of AI on jobs in 2024"
  
  # Generate an article with custom settings
  python src/cli.py --topic "Machine learning in healthcare" \\
                    --language "Korean" \\
                    --mode "enhanced" \\
                    --llm-model "openai/gpt-4o" \\
                    --search-tool "ddg" \\
                    --output-dir "data/articles" \\
                    --no-react \\
                    --display-only
  
  # Generate and save article
  python src/cli.py --topic "Climate change solutions" \\
                    --language "Spanish" \\
                    --mode "websearch" \\
                    --output-dir "my_articles"
        """
    )
    
    # Required arguments
    parser.add_argument(
        "--topic",
        required=True,
        help="Topic for the article to generate"
    )
    
    # Optional arguments
    parser.add_argument(
        "--language",
        default="Korean",
        choices=["Korean", "English", "Japanese", "Chinese", "Spanish", "French", "German"],
        help="Target language for the translated version (default: Korean)"
    )
    
    parser.add_argument(
        "--mode",
        default="enhanced",
        choices=["enhanced", "websearch"],
        help="Generation mode: enhanced (full research with ReACT) or websearch (focused web search) (default: enhanced)"
    )
    
    parser.add_argument(
        "--llm-model",
        default="openai/gpt-4o-mini",
        choices=[
            "openai/gpt-4o-mini",
            "openai/gpt-4o",
            "anthropic/claude-sonnet-4-20250514",
            "anthropic/claude-3-7-sonnet-20250219",
            "anthropic/claude-3-5-haiku-20241022",
            "gemini/gemini-2.5-flash-lite",
            "gemini/gemini-2.5-flash",
            "gemini/gemini-2.5-pro"
        ],
        help="LLM model for article generation (default: openai/gpt-4o-mini)"
    )
    
    parser.add_argument(
        "--search-tool",
        default="ddg",
        choices=["ddg", "brave"],
        help="Search tool: ddg (DuckDuckGo, free) or brave (Brave Search, requires API key) (default: ddg)"
    )
    
    parser.add_argument(
        "--output-dir",
        default="data/articles",
        help="Directory to save generated articles (default: data/articles)"
    )
    
    parser.add_argument(
        "--no-react",
        action="store_true",
        help="Disable ReACT agent (only applies to enhanced mode)"
    )
    
    parser.add_argument(
        "--display-only",
        action="store_true",
        help="Display article content only, don't save to files"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Print header
    print("📝 Enhanced Article Creator CLI")
    print("=" * 50)
    
    # Check environment
    if not check_environment(args.llm_model, args.search_tool):
        print("\n❌ Environment check failed. Please set the required API keys.")
        sys.exit(1)
    
    # Store generation parameters
    generation_params = {
        'topic': args.topic,
        'language': args.language,
        'mode': args.mode,
        'use_react': not args.no_react if args.mode == "enhanced" else False,
        'llm_model': args.llm_model,
        'search_tool_name': args.search_tool,
        'output_dir': args.output_dir,
        'generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Display configuration
    print(f"\n⚙️ Configuration:")
    print(f"  Topic: {args.topic}")
    print(f"  Language: {args.language}")
    print(f"  Mode: {args.mode}")
    print(f"  LLM Model: {args.llm_model}")
    print(f"  Search Tool: {args.search_tool}")
    print(f"  ReACT Agent: {'Enabled' if generation_params['use_react'] else 'Disabled'}")
    print(f"  Output Directory: {args.output_dir}")
    print(f"  Display Only: {args.display_only}")
    
    # Generate article
    print(f"\n🚀 Generating article... This may take a few minutes.")
    start_time = time.time()
    
    article_data = generate_article(
        topic=args.topic,
        language=args.language,
        mode=args.mode,
        use_react=generation_params['use_react'],
        llm_model=args.llm_model,
        search_tool_name=args.search_tool
    )
    
    if article_data:
        end_time = time.time()
        generation_time = end_time - start_time
        
        print(f"\n✅ Article generated successfully in {generation_time:.2f} seconds!")
        
        # Display article content
        display_article_content(article_data, args.language)
        
        # Save to files if not display-only
        if not args.display_only:
            print(f"\n💾 Saving article to files...")
            saved_files = save_article_to_file(
                article_data,
                args.topic,
                args.language,
                args.output_dir,
                generation_params
            )
            
            if saved_files:
                print(f"\n✅ Article saved successfully!")
                print(f"📁 Files saved:")
                for file_type, file_path in saved_files.items():
                    if file_path:
                        print(f"  - {file_path}")
        
        # Display generation info
        if args.verbose:
            print(f"\n📊 Generation Information:")
            for key, value in generation_params.items():
                print(f"  {key}: {value}")
            print(f"  Generation Time: {generation_time:.2f} seconds")
        
        print(f"\n🎉 Article generation completed successfully!")
        
    else:
        print(f"\n❌ Failed to generate article. Please check your configuration and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
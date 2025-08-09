#!/usr/bin/env python3
"""
Command-line interface for the enhanced article creator

This CLI provides the same functionality as the Streamlit app but through command-line arguments.
It can generate articles using the enhanced article creator and displays the output in different
translation versions (English, Korean, and Research summary).
"""

import os
import sys
from pathlib import Path
import time
from datetime import datetime
import json
from typing import Dict, Any, Optional

import click

# Add the src directory to the path
sys.path.append(str(Path(__file__).parent))

from utils.llm import check_environment_cli, get_available_llm_models
from utils.text import generate_article, display_article_content, save_article_to_file
from utils.utils import (
    get_available_languages,
    get_available_search_tools,
    get_available_modes,
)


@click.command()
@click.option("--topic", required=True, help="Topic for the article to generate")
@click.option(
    "--language",
    default="Korean",
    type=click.Choice(get_available_languages()),
    help="Target language for the translated version (default: Korean)",
)
@click.option(
    "--mode",
    default="enhanced",
    type=click.Choice(get_available_modes()),
    help="Generation mode: enhanced (full research with ReACT) or websearch (focused web search) (default: enhanced)",
)
@click.option(
    "--llm-model",
    default="openai/gpt-4o-mini",
    type=click.Choice(get_available_llm_models()),
    help="LLM model for article generation (default: openai/gpt-4o-mini)",
)
@click.option(
    "--search-tool",
    default="ddg",
    type=click.Choice(get_available_search_tools()),
    help="Search tool: ddg (DuckDuckGo, free) or brave (Brave Search, requires API key) (default: ddg)",
)
@click.option(
    "--output-dir",
    default="data/articles",
    help="Directory to save generated articles (default: data/articles)",
)
@click.option(
    "--no-react",
    is_flag=True,
    help="Disable ReACT agent (only applies to enhanced mode)",
)
@click.option(
    "--display-only",
    is_flag=True,
    help="Display article content only, don't save to files",
)
@click.option("--verbose", is_flag=True, help="Enable verbose output")
def main(
    topic,
    language,
    mode,
    llm_model,
    search_tool,
    output_dir,
    no_react,
    display_only,
    verbose,
):
    """Enhanced Article Creator CLI
    
    Generate articles using the enhanced article creator with various options.
    
    Examples:
    
    \b
    # Generate an article with default settings
    python src/cli.py --topic "The impact of AI on jobs in 2024"
    
    \b
    # Generate an article with custom settings
    python src/cli.py --topic "Machine learning in healthcare" \\
                      --language "Korean" \\
                      --mode "enhanced" \\
                      --llm-model "openai/gpt-4o" \\
                      --search-tool "ddg" \\
                      --output-dir "data/articles" \\
                      --no-react \\
                      --display-only
    
    \b
    # Generate and save article
    python src/cli.py --topic "Climate change solutions" \\
                      --language "Spanish" \\
                      --mode "websearch" \\
                      --output-dir "my_articles"
    """

    # Print header
    print("📝 Enhanced Article Creator CLI")
    print("=" * 50)

    # Check environment
    if not check_environment_cli(llm_model, search_tool):
        print("\n❌ Environment check failed. Please set the required API keys.")
        sys.exit(1)

    # Store generation parameters
    generation_params = {
        "topic": topic,
        "language": language,
        "mode": mode,
        "use_react": not no_react if mode == "enhanced" else False,
        "llm_model": llm_model,
        "search_tool_name": search_tool,
        "output_dir": output_dir,
        "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # Display configuration
    print(f"\n⚙️ Configuration:")
    print(f"  Topic: {topic}")
    print(f"  Language: {language}")
    print(f"  Mode: {mode}")
    print(f"  LLM Model: {llm_model}")
    print(f"  Search Tool: {search_tool}")
    print(
        f"  ReACT Agent: {'Enabled' if generation_params['use_react'] else 'Disabled'}"
    )
    print(f"  Output Directory: {output_dir}")
    print(f"  Display Only: {display_only}")

    # Generate article
    print(f"\n🚀 Generating article... This may take a few minutes.")
    start_time = time.time()

    article_data = generate_article(
        topic=topic,
        language=language,
        mode=mode,
        use_react=generation_params["use_react"],
        llm_model=llm_model,
        search_tool_name=search_tool,
    )

    if article_data:
        end_time = time.time()
        generation_time = end_time - start_time

        print(f"\n✅ Article generated successfully in {generation_time:.2f} seconds!")

        # Display article content
        display_article_content(article_data, language)

        # Save to files if not display-only
        if not display_only:
            print(f"\n💾 Saving article to files...")
            saved_files = save_article_to_file(
                article_data, topic, language, output_dir, generation_params
            )

            if saved_files:
                print(f"\n✅ Article saved successfully!")
                print(f"📁 Files saved:")
                for file_type, file_path in saved_files.items():
                    if file_path:
                        print(f"  - {file_path}")

        # Display generation info
        if verbose:
            print(f"\n📊 Generation Information:")
            for key, value in generation_params.items():
                print(f"  {key}: {value}")
            print(f"  Generation Time: {generation_time:.2f} seconds")

        print(f"\n🎉 Article generation completed successfully!")

    else:
        print(
            f"\n❌ Failed to generate article. Please check your configuration and try again."
        )
        sys.exit(1)


if __name__ == "__main__":
    main()

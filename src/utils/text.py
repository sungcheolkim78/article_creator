from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import logging
import dspy
import unicodedata

from utils.llm import llm_setup
from core.enhanced_article_creator import EnhancedArticleCreator
from core.websearch_article_creator import WebSearchArticleCreator
from core.react_article import ArticleReACTAgent


logger = logging.getLogger("text")


def create_options_table(params: Dict[str, Any]) -> str:
    """Create a markdown table with the click options used to generate the article."""

    topic = params.get("topic", "Untitled Article")
    language = params["language"]
    output_dir = params["output_dir"]
    mode = params.get("mode", "query")
    engine = params.get("engine", "tavily")
    model = params.get("model", "gemini/gemini-2.5-flash")
    generation_time = params["generation_time"]

    table = f"""
## Generation Parameters

This article was generated using the following parameters:

| Parameter | Value |
|-----------|-------|
| **Topic** | {topic} |
| **Language** | {language} |
| **Output Directory** | {output_dir} |
| **LLM Model** | {model} |
| **Search Mode** | {mode} |
| **Search Engine** | {engine} |
| **Generated At** | {generation_time} |

### Command Used

```bash
python src/cli2.py \\
    --topic "{topic}" \\
    --language "{language}" \\
    --output_dir "{output_dir}" \\
    --model "{model}" \\
    --mode {mode} \\
    --engine "{engine}"
```
"""
    return table


def calculate_article_metrics(article_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate metrics about the generated article."""
    title_length = len(article_data.get("title", ""))

    sections_en = article_data.get("sections_en", [])
    total_en_words = sum(len(section.split()) for section in sections_en)

    sections_other = article_data.get("sections_other", [])
    total_other_words = sum(len(section.split()) for section in sections_other)

    return {
        "title_length": title_length,
        "total_en_words": total_en_words,
        "total_other_words": total_other_words,
        "sections_count": len(sections_en),
    }


def save_article_to_file(
    article_data: dspy.Prediction,
    generation_params: Dict[str, Any],
) -> Optional[Dict[str, str]]:
    """Save the generated article to files."""

    output_dir = generation_params["output_dir"]
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    topic = generation_params["topic"]
    language = generation_params["language"]
    topic_slug = topic.lower().replace(" ", "-").replace(",", "")
    lang_slug = language[:3].lower()
    timestamp = generation_params["generation_time"]

    options_table = create_options_table(generation_params)

    saved_files = {}

    def write(f, article_data, options_table, translated=False):
        f.write(f"# {article_data.title}\n\n")
        sections = article_data.sections_translated if translated else article_data.sections_en
        for i, section in enumerate(sections):
            f.write(f"{i+1}. {section}\n\n")
        sources = article_data.key_sources.replace("\n\n", "\n")
        sources = unicodedata.normalize("NFKC", sources)
        f.write(options_table)
        f.write(f"## Sources\n\n{sources}")

    # Save translated version
    translated_file = output_path / f"{topic_slug}-{lang_slug}-{timestamp}.md"
    with open(translated_file, "w", encoding="utf-8") as f:
        write(f, article_data, options_table, translated=True)

    # Save English version
    english_file = output_path / f"{topic_slug}-en-{timestamp}.md"
    with open(english_file, "w") as f:
        write(f, article_data, options_table)

    return saved_files


def generate_article(
    topic: str,
    language: str,
    mode: str,
    use_react: bool,
    llm_model: str,
    search_tool_name: str,
) -> Optional[Dict[str, Any]]:
    """Generate article using the enhanced article creator."""

    # Setup LLM
    llm_setup(llm_model)

    # Setup search tool
    search_tool = setup_search_tool(search_tool_name)
    if not search_tool:
        return None

    # Choose article generator based on mode
    if mode == "enhanced":
        article_generator = EnhancedArticleCreator(search_tool)

        prediction = article_generator.forward(
            topic=topic, language=language, use_react=use_react
        )
        return prediction

    elif mode == "websearch":
        article_generator = WebSearchArticleCreator(search_tool)

        try:
            prediction = article_generator.forward(topic=topic, language=language)
            return prediction
        except Exception as e:
            return None
    else:
        return None


def generate_article_old(
    topic, language, output_dir, mode, use_react, llm_model, search_tool_name
):
    """Enhanced article creator with web search and ReACT integration."""

    # Setup
    llm_setup(llm_model)

    # Initialize Brave Search
    brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not brave_api_key:
        logger.warning(
            "Warning: BRAVE_SEARCH_API_KEY not found. Using limited functionality."
        )
        logger.warning(
            "Please set BRAVE_SEARCH_API_KEY environment variable for full web search capabilities."
        )
        return

    if search_tool_name == "brave":
        search_tool = OptimizedBraveSearch(api_key=brave_api_key, k=5, source="web")
    elif search_tool_name == "ddg":
        search_tool = OptimizedDDGSearch(k=5)
    else:
        raise ValueError(f"Invalid search tool: {search_tool_name}")

    # Choose article generator based on mode
    if mode == "enhanced":
        article_generator = EnhancedArticleCreator(search_tool)
        prediction = article_generator.forward(
            topic=topic, language=language, use_react=use_react
        )
    elif mode == "websearch":
        article_generator = WebSearchArticleCreator(search_tool)
        prediction = article_generator.forward(topic=topic, language=language)
    elif mode == "react":
        react_agent = ArticleReACTAgent(search_tool)
        react_results = react_agent.generate_article_with_research(topic)
        logger.info(
            "ReACT research completed. Use 'enhanced' mode to generate full article."
        )
        logger.info(f"Research summary: {react_results}")
        return

    # Save articles
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    topic_slug = topic.lower().replace(" ", "-").replace(",", "")
    lang_slug = language[:3].lower()

    # Create click options table
    options_table = create_click_options_table(
        topic=topic,
        language=language,
        output_dir=str(output_dir),
        mode=mode,
        use_react=use_react,
        llm_model=llm_model,
        search_tool_name=search_tool_name,
    )

    # Save translated version
    with open(output_dir / f"{topic_slug}-{lang_slug}.md", "w", encoding="utf-8") as f:
        f.write(f"# {prediction.title}\n\n")
        for section in prediction.sections_other:
            f.write(section)
            f.write("\n\n")

        # Add sources if available
        if hasattr(prediction, "key_sources") and prediction.key_sources:
            f.write("## Sources\n\n")
            for source in prediction.key_sources:
                f.write(f"- {source}\n")

        # Add click options table
        f.write(options_table)

    # Save English version
    with open(output_dir / f"{topic_slug}-en.md", "w", encoding="utf-8") as f:
        f.write(f"# {prediction.title}\n\n")
        for section in prediction.sections_en:
            f.write(section)
            f.write("\n\n")

        # Add sources if available
        if hasattr(prediction, "key_sources") and prediction.key_sources:
            f.write("## Sources\n\n")
            for source in prediction.key_sources:
                f.write(f"- {source}\n")

        # Add click options table
        f.write(options_table)

    # Save research summary if available
    if hasattr(prediction, "research_summary") and prediction.research_summary:
        with open(output_dir / f"{topic_slug}-research.md", "w", encoding="utf-8") as f:
            f.write(f"# Research Summary: {prediction.title}\n\n")
            f.write(prediction.research_summary)
            f.write("\n\n")
            f.write(options_table)

    logger.info(f"Enhanced article saved to {output_dir}")
    logger.info(f"Files created:")
    logger.info(f"  - {topic_slug}-{lang_slug}.md (translated)")
    logger.info(f"  - {topic_slug}-en.md (English)")
    if hasattr(prediction, "research_summary"):
        logger.info(f"  - {topic_slug}-research.md (research summary)")


def display_article_metrics(article_data: Dict[str, Any]):
    """Display metrics about the generated article."""
    metrics = calculate_article_metrics(article_data)

    print("\n📊 Article Metrics:")
    print(f"  Title Length: {metrics['title_length']}")
    print(f"  English Words: {metrics['total_en_words']}")
    print(f"  Other Language Words: {metrics['total_other_words']}")
    print(f"  Sections: {metrics['sections_count']}")


def display_article_content(article_data: Dict[str, Any], language: str):
    """Display the article content in a formatted way."""

    print(f"\n📝 Article: {article_data.get('title', 'Untitled Article')}")

    # Display metrics
    display_article_metrics(article_data)

    # Display content based on language
    if language.lower() == "english":
        sections = article_data.get("sections_en", [])
        print(f"\n📖 Article Content (English):")
    else:
        sections = article_data.get("sections_other", [])
        print(f"\n📖 Article Content ({language}):")

    # Display each section
    for i, section in enumerate(sections, 1):
        print(f"\n--- Section {i} ---")
        print(section)

    # Display sources if available
    if hasattr(article_data, "key_sources") and article_data.key_sources:
        print(f"\n📚 Sources:")
        for source in article_data.key_sources:
            print(f"  - {source}")

    # Display research summary if available
    if hasattr(article_data, "research_summary") and article_data.research_summary:
        print(f"\n🔬 Research Summary:")
        print(article_data.research_summary)

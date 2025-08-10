import dspy
from datetime import datetime

from agents.writer import ArticleWriter
from utils.llm import llm_setup
from utils.text import display_article_content, save_article_to_file


def test_writer():
    llm_setup("openai/gpt-4o-mini")

    writer = ArticleWriter(verbose=True)

    topic = "The benefits of using React in web development"
    language = "Korean"
    output = writer(topic=topic, language=language)

    print(output.title)
    print(output.sections_en)
    print(output.sections_translated)
    print(output.research_summary)
    print(output.key_sources)

    display_article_content(output, language)

    # Save to files if not display-only
    output_dir = "data/articles"
    generation_params = {
        "topic": topic,
        "language": language,
        "mode": "enhanced",
        "use_react": True,
        "llm_model": "openai/gpt-4o-mini",
        "search_tool_name": "ddg",
        "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    saved_files = save_article_to_file(
        output, topic, language, output_dir, generation_params
    )

if __name__ == "__main__":
    dspy.configure_cache(
        enable_disk_cache=True,
        enable_memory_cache=True,
    )
    test_writer()
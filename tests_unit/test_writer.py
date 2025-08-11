import dspy
from datetime import datetime

from agents.writer import ArticleWriter
from utils.llm import llm_setup
from utils.text import display_article_content, save_article_to_file


def test_writer():
    llm_setup("openrouter/openai/gpt-oss-20b")

    writer = ArticleWriter(verbose=True)

    topic = "TypeScript"
    language = "Korean"
    output = writer(topic=topic, language=language)

    output_dir = "data/articles"
    generation_params = {
        "topic": topic,
        "language": language,
        "mode": "enhanced",
        "use_react": True,
        "llm_model": "openrouter/openai/gpt-oss-20b",
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
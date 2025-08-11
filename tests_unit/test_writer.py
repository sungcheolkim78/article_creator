import dspy
from datetime import datetime

from agents.writer import ArticleWriter
from utils.llm import llm_setup
from utils.text import save_article_to_file


def test_writer():
    llm_setup("openai/gpt-4o-mini")

    writer = ArticleWriter(verbose=True)

    topic = "Lovable AI"
    language = "Korean"
    output = writer(topic=topic, language=language)

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
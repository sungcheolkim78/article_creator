import dspy
from datetime import datetime

from agents.writer import ArticleWriter
from utils.llm import llm_setup
from utils.text import save_article_to_file


def test_writer():
    model_name = "gemini/gemini-2.5-flash"
    llm_setup(model_name)

    writer = ArticleWriter(verbose=False)

    topic = "Efficient Transformer Architectures"
    language = "Korean"
    output = writer(topic=topic, language=language)

    output_dir = "data/articles"
    generation_params = {
        "topic": topic,
        "language": language,
        "mode": "enhanced",
        "use_react": True,
        "llm_model": model_name,
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
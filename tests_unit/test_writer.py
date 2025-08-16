import click
from datetime import datetime

from agents.writer import ArticleWriter
from agents.tools import MemoryTools
from utils.llm import llm_setup
from utils.text import save_article_to_file


@click.command()
@click.option("--topic", type=str, default="Lovable AI")
@click.option("--language", type=str, default="Korean")
@click.option("--mode", type=str, default="query")
@click.option("--engine", type=str, default="tavily")
def test_writer(topic, language, mode, engine):
    model = "anthropic/claude-3-5-haiku-latest"
    model = "openai/gpt-4o-mini"
    model = "gemini/gemini-2.5-flash"
    
    output_dir = "data/articles"
    generation_params = {
        "topic": topic,
        "language": language,
        "mode": mode,
        "engine": engine,
        "llm_model": model,
        "generation_time": datetime.now().strftime("%Y%m%d_%H%M%S"),
    }

    llm_setup(model, cache=True, extra_options={"max_tokens": 6048})
    memory_tools = MemoryTools(mode=mode, engine=engine, verbose=False)
    writer = ArticleWriter(memory_tools, verbose=False)
    output = writer(topic=topic, language=language)

    saved_files = save_article_to_file(output, output_dir, generation_params)


if __name__ == "__main__":
    test_writer()

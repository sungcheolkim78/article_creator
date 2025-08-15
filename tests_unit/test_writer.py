import click
from datetime import datetime

from agents.writer import ArticleWriter
from utils.llm import llm_setup
from utils.text import save_article_to_file


@click.command()
@click.option("--topic", type=str, default="Retrieval Augmented Generation")
@click.option("--language", type=str, default="Korean")
@click.option("--mode", type=str, default="react")
@click.option("--engine", type=str, default="tavily")
def test_writer(topic, language, mode, engine):
    model_name = "gemini/gemini-2.5-flash"
    output_dir = "data/articles"
    generation_params = {
        "topic": topic,
        "language": language,
        "mode": mode,
        "engine": engine,
        "llm_model": model_name,
        "generation_time": datetime.now().strftime("%Y%m%d_%H%M%S"),
    }

    llm_setup(model_name, cache=True, extra_options={"max_tokens": 6048})
    writer = ArticleWriter(mode=mode, engine=engine, verbose=False)
    output = writer(topic=topic, language=language)

    saved_files = save_article_to_file(output, output_dir, generation_params)


if __name__ == "__main__":
    test_writer()

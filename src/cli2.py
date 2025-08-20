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
@click.option("--model", type=str, default="gemini/gemini-2.5-flash")
@click.option("--output-dir", type=str, default="data/articles")
def test_writer(topic, language, mode, engine, model, output_dir):
    model_list = [
        "anthropic/claude-3-5-haiku-latest",
        "openai/gpt-4o-mini",
        "openai/gpt-5-mini",
        "openai/gpt-oss-20b",
        "gemini/gemini-2.5-flash-lite",
        "gemini/gemini-2.5-flash",
        "openrouter/z-ai/glm-4.5",
        "ollama_chat/qwen3:8b",
    ]
    if model not in model_list:
        raise ValueError(f"Invalid model: {model}")

    generation_params = {
        "topic": topic,
        "language": language,
        "mode": mode,
        "engine": engine,
        "llm_model": model,
        "output_dir": output_dir,
        "generation_time": datetime.now().strftime("%Y%m%d_%H%M%S"),
    }

    llm_setup(model, cache=True, extra_options={"max_tokens": 6048})
    memory_tools = MemoryTools(mode=mode, engine=engine, verbose=False)
    writer = ArticleWriter(memory_tools, verbose=False)
    output = writer(topic=topic, language=language)

    saved_files = save_article_to_file(output, generation_params)
    writer.save_research(output_dir, generation_params["generation_time"])


if __name__ == "__main__":
    test_writer()

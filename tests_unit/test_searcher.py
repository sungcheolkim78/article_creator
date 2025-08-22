from agents.searcher import ReACTSearcher, QuerySearcher
from utils.llm import llm_setup
import click


@click.command()
@click.option("--topic", type=str, default="Overview on Rust programming language")
@click.option("--model", type=str, default="openai/gpt-4o-mini")
@click.option("--mode", type=str, default="react")
@click.option("--engine", type=str, default="tavily")
@click.option("--verbose", type=bool, default=True)
def test_basic_search(topic, model, mode, engine, verbose):
    llm_options = llm_setup(model, cache=True)

    if mode == "react":
        searcher = ReACTSearcher(engine=engine, verbose=verbose)
    elif mode == "query":
        searcher = QuerySearcher(engine=engine, verbose=verbose)
    else:
        raise ValueError(f"Invalid mode: {mode}")

    result = searcher(topic)

    print(result.markdown)


if __name__ == "__main__":
    test_basic_search()

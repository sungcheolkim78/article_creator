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
    lm = llm_setup(model, cache=True)

    if mode == "react":
        searcher = ReACTSearcher(engine=engine, verbose=verbose)
    elif mode == "query":
        searcher = QuerySearcher(engine=engine, verbose=verbose)
    else:
        raise ValueError(f"Invalid mode: {mode}")

    result = searcher(topic)

    print(result.markdown)

    print('-' * 100)
    total_tokens = sum([history['usage'].get('total_tokens', 0) for history in lm.history])
    total_cost = sum([history['cost'] for history in lm.history])
    print(f"Total history: {len(lm.history)}")
    print(f"Total tokens: {total_tokens}")
    print(f"Total cost: ${total_cost:.8f}")


if __name__ == "__main__":
    test_basic_search()

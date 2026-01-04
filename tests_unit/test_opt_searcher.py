import click
from websearch import OptimizedSearcher, create_optimized_searcher, quick_search
from utils.llm import llm_setup, get_llm_cost


@click.command()
@click.option("--topic", type=str, default="AI trends 2025")
@click.option("--model", type=str, default="gemini/gemini-2.5-flash")
@click.option("--engine", type=str, default="tavily")
@click.option("--verbose", type=bool, default=True)
def test_searcher(topic, model, engine, verbose):
    lm = llm_setup(model, cache=True)
    result = quick_search(topic, engine=engine)

    print(result.summary)
    print(f"Execution time: {result.execution_time} seconds")

    print("-" * 80)
    get_llm_cost(lm, verbose=True)


if __name__ == "__main__":
    test_searcher()

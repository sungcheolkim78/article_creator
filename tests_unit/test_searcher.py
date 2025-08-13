from websearch.searcher import ReACTSearcher, tool_search_web, QuerySearcher
from utils.llm import llm_setup
import click


@click.command()
@click.option("--topic", type=str, default="Overview on Rust programming language")
@click.option("--mode", type=str, default="react")
def test_basic_search(topic, mode):
    llm_options = llm_setup("gemini/gemini-2.5-flash-lite", cache=True, extra_options={"max_tokens": 4096})

    if mode == "react":
        searcher = ReACTSearcher(engine="tavily", verbose=True)
    elif mode == "query":
        searcher = QuerySearcher(engine="tavily", verbose=True)
    else:
        raise ValueError(f"Invalid mode: {mode}")

    result = searcher(topic)

    print(result.markdown)


if __name__ == "__main__":
    test_basic_search()
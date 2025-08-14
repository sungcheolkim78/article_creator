import dspy
from agents.planner import ArticlePlanner
from utils.llm import llm_setup
import click


@click.command()
@click.option("--topic", type=str, default="Lovable AI")
@click.option("--mode", type=str, default="query")
@click.option("--engine", type=str, default="tavily")
def test_planner(topic, mode, engine):
    """Test the planner tool"""

    llm_setup("gemini/gemini-2.5-flash-lite", cache=True, extra_options={"max_tokens": 4096})

    planner = ArticlePlanner(mode=mode, engine=engine, verbose=True)
    result = planner.forward(topic)

    print("-" * 100)
    print(result.research_strategy)
    print("-" * 100)
    print(result.action_plan)
    print("-" * 100)
    print(result.outline)
    print("-" * 100)
    print(result.memory_context)
    print("-" * 100)


if __name__ == "__main__":
    test_planner()

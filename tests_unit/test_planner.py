import dspy
from agents.planner import ArticlePlanner
from agents.tools import MemoryTools
from utils.llm import llm_setup, get_llm_cost
import click


@click.command()
@click.option("--topic", type=str, default="Lovable AI")
@click.option("--mode", type=str, default="query")
@click.option("--engine", type=str, default="tavily")
@click.option("--model", type=str, default="gemini/gemini-2.5-flash-lite")
@click.option("--verbose", type=bool, default=True)
def test_planner(topic, mode, engine, model, verbose):
    """Test the planner tool"""

    lm = llm_setup(model, cache=True)
    memory_tools = MemoryTools(mode=mode, engine=engine, verbose=verbose)

    planner = ArticlePlanner(memory_tools, verbose=verbose)
    result = planner.forward(topic)

    print("-" * 100)
    print(result.research_strategy)
    print("-" * 100)
    print(result.action_plan)
    print("-" * 100)
    print(result.outline_str)
    print("-" * 100)
    get_llm_cost(lm, verbose=True)


if __name__ == "__main__":
    test_planner()

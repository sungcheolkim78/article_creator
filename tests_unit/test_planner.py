import dspy
from agents.planner import ArticlePlanner
from agents.tools import MemoryTools
from utils.llm import llm_setup
import click


@click.command()
@click.option("--topic", type=str, default="Lovable AI")
@click.option("--mode", type=str, default="query")
@click.option("--engine", type=str, default="tavily")
def test_planner(topic, mode, engine):
    """Test the planner tool"""

    llm_setup("gemini/gemini-2.5-flash-lite", cache=True, extra_options={"max_tokens": 6048})
    memory_tools = MemoryTools(mode=mode, engine=engine, verbose=False)

    planner = ArticlePlanner(memory_tools, verbose=True)
    result = planner.forward(topic)

    print("-" * 100)
    print(result.research_strategy)
    print("-" * 100)
    print(result.action_plan)
    print("-" * 100)
    print(result.outline_str)


if __name__ == "__main__":
    test_planner()

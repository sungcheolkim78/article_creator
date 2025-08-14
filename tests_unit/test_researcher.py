from agents.researcher import ArticleReACTResearcher
from agents.planner import ArticlePlanner
from utils.llm import llm_setup
import click


@click.command()
@click.option("--topic", type=str, default="Lovable AI")
@click.option("--mode", type=str, default="query")
@click.option("--engine", type=str, default="tavily")
def test_researcher(topic, mode, engine):
    """Test the researcher tool"""

    llm_setup("gemini/gemini-2.5-flash-lite", cache=True, extra_options={"max_tokens": 4096})

    planner = ArticlePlanner(mode=mode, engine=engine, verbose=False)
    result = planner.forward(topic)

    researcher = ArticleReACTResearcher(
        result.research_strategy,
        result.action_plan,
        verbose=True,
    )
    output_researcher = researcher(
        topic=topic,
        outline=result.outline,
        memory_content=result.memory_context,
    )

    print(output_researcher.final_title)
    print("-" * 100)
    print(output_researcher.final_outline)
    print("-" * 100)
    print(output_researcher.final_content)


if __name__ == "__main__":
    test_researcher()

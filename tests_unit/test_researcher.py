from agents.researcher import ArticleReACTResearcher
from agents.planner import ArticlePlanner
from agents.tools import MemoryTools
from utils.llm import llm_setup
import click


@click.command()
@click.option("--topic", type=str, default="Lovable AI")
@click.option("--mode", type=str, default="query")
@click.option("--engine", type=str, default="tavily")
def test_researcher(topic, mode, engine):
    """Test the researcher tool"""

    llm_setup("gemini/gemini-2.5-flash-lite", cache=True, extra_options={"max_tokens": 6048})

    memory_tools = MemoryTools(mode=mode, engine=engine, verbose=False)

    planner = ArticlePlanner(memory_tools, verbose=False)
    outcome = planner.forward(topic)

    researcher = ArticleReACTResearcher(memory_tools, verbose=True)
    outcome = researcher(
        topic=topic,
        outline_str=memory_tools.outline_str,
        memory_content=memory_tools.get_findings(),
    )
    researcher.save(f"data/research/researcher_{topic.replace(' ', '_')}.md")

    print(outcome.final_title)
    print("-" * 100)
    print(outcome.final_sections)
    print("-" * 100)
    print(outcome.final_section_subheadings)
    print("-" * 100)


if __name__ == "__main__":
    test_researcher()

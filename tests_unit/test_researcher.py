import dspy
from agents.researcher import ArticleReACTResearcher
from agents.planner import planner_tool
from utils.llm import llm_setup


def test_researcher():
    """Test the researcher tool"""
    llm_setup("openai/gpt-4o-mini")

    topic = "Lovable AI"
    output_planner = planner_tool(topic, verbose=True)

    researcher = ArticleReACTResearcher(
        output_planner.research_strategy,
        output_planner.action_plan,
        verbose=True,
    )
    output_researcher = researcher(
        topic=topic,
        outline=output_planner.outline,
        memory_content=output_planner.memory_context)

    print(output_researcher.final_title)
    print("-" * 100)
    print(output_researcher.final_outline)
    print("-" * 100)
    print(output_researcher.final_content)


if __name__ == "__main__":
    dspy.configure_cache(
        enable_disk_cache=True,
        enable_memory_cache=True,
    )
    test_researcher()
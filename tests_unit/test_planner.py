import dspy
from agents.planner import planner_tool
from utils.llm import llm_setup


def test_planner():
    """Test the planner tool"""

    topic = "Lovable AI"
    current_outline = None
    research_gaps = ""
    available_tools = ""
    memory_context = ""
    result = planner_tool(
        topic, current_outline, research_gaps, available_tools, memory_context, verbose=True
    )

    print("-" * 100)
    print(result.research_strategy)
    print("-" * 100)
    print(result.action_plan)


if __name__ == "__main__":
    llm_setup("openai/gpt-4o-mini")
    dspy.configure_cache(
        enable_disk_cache=True,
        enable_memory_cache=True,
    )
    test_planner()

import dspy
import click
from agents.tools import MemoryTools



class ArticlePlanner(dspy.Module):
    def __init__(self, memory_tools: MemoryTools, verbose: bool = False):
        self.verbose = verbose
        self.memory_tools = memory_tools

    def forward(self, topic: str) -> dspy.Prediction:
        """Generate an article plan using ReACT approach."""

        if self.verbose:
            print(click.style(f"Step 1: Search Topic - {topic}", fg="blue"))
        initial_search = self.memory_tools.search_web(topic)

        # Generate the outline if not provided
        outline_str = self.memory_tools.outline(topic, "no initial outline")

        if self.verbose:
            print(click.style(f"Step 2: Generate Outline - {outline_str}", fg="blue"))

        # Research gaps
        research_gap = self.memory_tools.research_gap(outline_str)
        if self.verbose:
            print(click.style(f"Step 3: Research Gap - {research_gap}", fg="blue"))

        # Generate the research strategy and action plan
        output = self.memory_tools.plan(topic=topic, research_gap=research_gap)
        if self.verbose:
            print(
                click.style("Step 4: Generate Research Strategy and Action Plan", fg="blue")
            )
        return dspy.Prediction(
            research_strategy=output.research_strategy,
            action_plan=output.action_plan,
            outline_str=outline_str,
        )

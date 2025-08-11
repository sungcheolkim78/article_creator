import dspy
from typing import Dict, Optional, Any
import json
import click
from websearch.ddgsearch import DDGReACTSearcher, tool_search_web


class ArticlePlanner(dspy.Signature):
    """Given a topic, current outline, research gaps, available tools, and memory
    context, generate a research strategy and action plan to create an comprehensive
    article about the topic."""

    topic: str = dspy.InputField()
    current_outline: str = dspy.InputField(desc="Current article outline or structure")
    research_gaps: str = dspy.InputField(
        desc="Identified gaps in current research or information"
    )
    available_tools: str = dspy.InputField(
        desc="description of the research and analysis tools"
    )
    memory_context: str = dspy.InputField(
        desc="Relevant information from memory for this topic"
    )

    research_strategy: str = dspy.OutputField(
        desc="Strategy for gathering the needed information"
    )
    action_plan: str = dspy.OutputField(
        desc="Specific actions to take with their parameters"
    )


class ArticleOutline(dspy.Signature):
    """Given a topic, generate a comprehensive outline for an article."""

    topic: str = dspy.InputField()
    content: str = dspy.InputField(desc="The content of the article")

    title: str = dspy.OutputField()
    sections: list[str] = dspy.OutputField()
    section_subheadings: dict[str, list[str]] = dspy.OutputField(
        desc="mapping from section headings to subheadings"
    )


class ResearchGap(dspy.Signature):
    """Given a outline and content, generate a information gap for the comprehensive article."""

    topic: str = dspy.InputField()
    outline: str = dspy.InputField()
    content: str = dspy.InputField()
    info_gap: str = dspy.OutputField(desc="The information gap for the comprehensive article")


def planner_tool(
    topic: str,
    current_outline: Optional[Dict] = None,
    research_gaps: str = "",
    available_tools: str = "",
    memory_context: str = "",
    verbose: bool = False,
) -> dspy.Prediction:
    """Generate an article plan using ReACT approach."""

    if verbose:
        print(click.style(f"Step 1: Search Topic - {topic}", fg="blue"))
    memory_context += tool_search_web(topic, verbose=verbose)

    # Generate the outline if not provided
    if current_outline is None:
        outline = dspy.ChainOfThought(ArticleOutline)(
            topic=topic, content=memory_context
        )
        outline_str = json.dumps(outline.section_subheadings)
    else:
        outline = current_outline
        outline_str = json.dumps(outline)

    if verbose:
        print(click.style(f"Step 2: Generate Outline - {outline_str}", fg="blue"))

    # Research gaps
    if research_gaps == "":
        research_gap = dspy.ChainOfThought(ResearchGap)(
            topic=topic, outline=outline_str, content=memory_context
        ).info_gap
    else:
        research_gap = research_gaps
    if verbose:
        print(click.style(f"Step 3: Research Gap - {research_gap}", fg="blue"))

    # Available tools
    if available_tools == "":
        available_tools = "The available tools are: tool_search_web"

    # Generate the research strategy and action plan
    planner = dspy.ChainOfThought(ArticlePlanner)
    output = planner(
        topic=topic,
        current_outline=outline_str,
        research_gaps=research_gap,
        available_tools=available_tools,
        memory_context=memory_context,
    )
    if verbose:
        print(click.style("Step 4: Generate Research Strategy and Action Plan", fg="blue"))
    return dspy.Prediction(
        research_strategy=output.research_strategy,
        action_plan=output.action_plan,
        title=outline.title,
        outline=outline.section_subheadings,
        memory_context=memory_context,
    )

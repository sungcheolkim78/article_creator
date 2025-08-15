import dspy
from typing import Dict, Optional
import json
import click
from agents.searcher import tool_search_web


class ArticlePlan(dspy.Signature):
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


class ResearchGap(dspy.Signature):
    """Given a outline and content, generate a information gap for the comprehensive article."""

    topic: str = dspy.InputField()
    outline: str = dspy.InputField()
    content: str = dspy.InputField()
    info_gap: str = dspy.OutputField(
        desc="The information gap for the comprehensive article"
    )


class ArticlePlanner(dspy.Module):
    def __init__(self, mode: str = "react", engine: str = "tavily", verbose: bool = False):
        self.verbose = verbose
        self.mode = mode
        self.engine = engine

        self.planner = dspy.ChainOfThought(ArticlePlan)
        self.research_gap = dspy.ChainOfThought(ResearchGap)

    def forward(self, topic: str) -> dspy.Prediction:
        """Generate an article plan using ReACT approach."""

        if self.verbose:
            print(click.style(f"Step 1: Search Topic - {topic}", fg="blue"))
        initial_search = tool_search_web(topic, mode=self.mode, engine=self.engine, verbose=self.verbose)
        memory_context = json.loads(initial_search)["summary"]

        # Generate the outline if not provided
        outline_str = tool_outline(topic, "no initial outline", memory_context)

        if self.verbose:
            print(click.style(f"Step 2: Generate Outline - {outline_str}", fg="blue"))

        # Research gaps
        research_gap = self.research_gap(
            topic=topic, outline=outline_str, content=memory_context
        ).info_gap
        if self.verbose:
            print(click.style(f"Step 3: Research Gap - {research_gap}", fg="blue"))

        # Available tools
        available_tools = "The available tools are:"
        available_tools += "\ntool_search_web: " + tool_search_web.__doc__
        available_tools += "\ntool_outline: " + tool_outline.__doc__
        available_tools += "\ntool_analyze: " + tool_analyze.__doc__
        available_tools += "\ntool_synthesize: " + tool_synthesize.__doc__

        # Generate the research strategy and action plan
        output = self.planner(
            topic=topic,
            current_outline=outline_str,
            research_gaps=research_gap,
            available_tools=available_tools,
            memory_context=memory_context,
        )
        if self.verbose:
            print(
                click.style("Step 4: Generate Research Strategy and Action Plan", fg="blue")
            )
        return dspy.Prediction(
            research_strategy=output.research_strategy,
            action_plan=output.action_plan,
            outline_str=outline_str,
            memory_context=memory_context,
        )


class AnalyzedInfo(dspy.Signature):
    """Given a question and related content, generate a comprehensive analysis of the content."""

    question: str = dspy.InputField()
    related_content: str = dspy.InputField()
    analysis_content: str = dspy.OutputField(desc="markdown content")


def tool_analyze(question: str, related_content: str) -> str:
    """Given a question and related content, generate a comprehensive analysis of the content."""
    analyzer = dspy.ChainOfThought(AnalyzedInfo)
    return analyzer(question=question, related_content=related_content).analysis_content


class SynthesizedInfo(dspy.Signature):
    """Integrate the findings into the existing article outline, expanding on the sections that were previously lacking detail. Ensure smooth transitions and a coherent narrative."""

    analysis_content: str = dspy.InputField()
    outline: str = dspy.InputField()
    research_gaps: str = dspy.InputField()

    new_outline: str = dspy.OutputField()
    synthesized_content: str = dspy.OutputField(desc="Additional content to fill the research gap in markdown format.")


def tool_synthesize(analysis_content: str, outline: str, research_gaps: str) -> str:
    """Integrate the findings into the existing article outline, expanding on the sections that were previously lacking detail. Ensure smooth transitions and a coherent narrative."""
    synthesizer = dspy.ChainOfThought(SynthesizedInfo)
    return synthesizer(analysis_content=analysis_content, outline=outline, research_gaps=research_gaps).synthesized_content


class ArticleOutline(dspy.Signature):
    """Given a topic, previous outline, and research findings, generate a comprehensive outline for an article."""

    topic: str = dspy.InputField()
    prev_outline: str = dspy.InputField(desc="The previous outline of the article")
    content: str = dspy.InputField(desc="The research findings of the article")

    title: str = dspy.OutputField()
    sections: list[str] = dspy.OutputField()
    section_subheadings: dict[str, list[str]] = dspy.OutputField(
        desc="mapping from section headings to subheadings"
    )


def tool_outline(topic: str, outline: str, memory_content: str) -> dspy.Prediction:
    """Given a topic, previous outline, and research findings, generate a comprehensive outline for an article."""

    outliner = dspy.ChainOfThought(ArticleOutline)
    outcome = outliner(
        topic=topic, prev_outline=outline, content=memory_content
    )
    return json.dumps({
        "title": outcome.title,
        "outline": outcome.section_subheadings,
    })

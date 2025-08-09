import dspy
from typing import Dict, Any, Optional
import json
import logging
import click

from core.react_base import ReACTAgent

logger = logging.getLogger("react_article")


class ArticleReACTPlanner(dspy.Signature):
    """Enhanced ReACT signature with domain-specific reasoning for article generation."""

    topic: str = dspy.InputField(desc="Article topic or subject")
    current_outline: str = dspy.InputField(desc="Current article outline or structure")
    research_gaps: str = dspy.InputField(
        desc="Identified gaps in current research or information"
    )
    available_tools: str = dspy.InputField(desc="Available research and analysis tools")
    memory_context: str = dspy.InputField(
        desc="Relevant information from memory for this topic"
    )

    research_strategy: str = dspy.OutputField(
        desc="Strategy for gathering the needed information"
    )
    action_plan: str = dspy.OutputField(
        desc="Specific actions to take with their parameters"
    )


class ArticleReACTAgent(ReACTAgent):
    """
    Specialized ReACT agent for article generation with enhanced reasoning capabilities.
    """

    def __init__(self, search_tool, memory_size: int = 2000):
        super().__init__(search_tool, memory_size=memory_size)
        self.article_react_planner = dspy.ChainOfThought(ArticleReACTPlanner)

        self.research_max_iterations = 8
        self.synthesis_max_iterations = 3

    def generate_article_with_research(
        self, topic: str, initial_outline: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Generate an article with comprehensive research using ReACT approach."""
        logger.info(f"Starting ReACT-enhanced article generation for: {topic}")

        # Phase 1: Enhanced reasoning about research needs
        outline_str = (
            json.dumps(initial_outline)
            if initial_outline
            else "No initial outline provided"
        )

        # Get memory context for the topic
        memory_context = self._get_memory_context(topic, "")

        react_plan = self.article_react_planner(
            topic=topic,
            current_outline=outline_str,
            research_gaps="Initial research needed for comprehensive article",
            available_tools=self.tools_description,
            memory_context=memory_context,
        )

        print(click.style(f"\nArticle ReACT Plan:", fg='blue', bold=True))
        print(click.style(f"[Strategy]: {react_plan.research_strategy}", fg='blue'))
        print(click.style(f"[Action Plan]: {react_plan.action_plan}", fg='blue'))

        # Phase 2: Execute research plan using ReACT
        research_goal = f"""
Research and gather comprehensive, current information about '{topic}' to create a well-informed article.

Research Strategy: {react_plan.research_strategy}
Action Plan: {react_plan.action_plan}

Goal: Gather enough information to write authoritative sections on the topic with current facts and multiple perspectives.
"""

        research_results = self.forward(
            research_goal, max_iterations=self.research_max_iterations
        )

        # Phase 3: Synthesize research into article structure
        synthesis_goal = f"""
Synthesize all gathered research into a comprehensive article outline and key content points for '{topic}'.
Use the research findings to create detailed, factual content.
"""

        synthesis_results = self.forward(
            synthesis_goal, max_iterations=self.synthesis_max_iterations
        )

        total_actions = len(research_results["actions_taken"]) + len(synthesis_results["actions_taken"])

        return {
            "topic": topic,
            "react_plan": react_plan,
            "research_phase": research_results,
            "synthesis_phase": synthesis_results,
            "total_actions": total_actions,
            "memory_summary": self.memory.get_memory_summary(),
        }

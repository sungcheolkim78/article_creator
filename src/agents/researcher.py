import logging
import os
from typing import TYPE_CHECKING

import click
import dspy

from agents.tools import MemoryTools

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)

# Constants
# ReACT trajectory typically contains 4 entries per iteration: thought, action, action_input, observation
TRAJECTORY_ENTRIES_PER_ITERATION = 4


class ReACTGoal(dspy.Signature):
    """The goal is to research the topic and create a comprehensive outline and collect organized information."""

    topic: str = dspy.InputField()
    outline: str = dspy.InputField()
    memory_content: str = dspy.InputField()

    final_title: str = dspy.OutputField()
    final_sections: list[str] = dspy.OutputField()
    final_section_subheadings: dict[str, list[str]] = dspy.OutputField()


class ArticleReACTResearcher(dspy.Module):
    """ReACT-based researcher for article generation.

    Uses ReACT reasoning to research topics and create comprehensive
    article outlines with organized information. The researcher uses
    memory tools to search, analyze, and outline articles.
    """

    def __init__(self, memory_tools: MemoryTools, verbose: bool = False):
        """Initialize the ArticleReACTResearcher.

        Args:
            memory_tools: MemoryTools instance providing search, analyze, and outline capabilities
            verbose: If True, print detailed trajectory information during execution
        """
        self.memory_tools = memory_tools
        self.verbose = verbose

        # Store base instructions to avoid mutating class-level state
        base_instructions = getattr(ReACTGoal, "instructions", "") or ""
        
        # Get research strategy and action plan if available (set by planner)
        research_strategy = getattr(self.memory_tools, "research_strategy", "")
        action_plan = getattr(self.memory_tools, "action_plan", "")
        
        # Build instructions with strategy and plan if available
        additional_instructions = ""
        if research_strategy:
            additional_instructions += "\n" + research_strategy
        if action_plan:
            additional_instructions += "\n" + action_plan
        
        self._instructions = base_instructions + additional_instructions

        # Set instructions on the signature before creating ReAct instance
        # Note: This mutates the class-level attribute, but we restore it in forward()
        # If multiple instances run concurrently, there may be race conditions.
        # For thread-safe usage, consider creating separate signature classes per instance.
        ReACTGoal.instructions = self._instructions

        self.react = dspy.ReAct(
            ReACTGoal,
            tools=self.memory_tools.tool_list(),
            max_iters=10,
        )

    def forward(
        self, topic: str, outline_str: str, memory_content: str
    ) -> dspy.Prediction:
        """Execute ReACT research process.

        Args:
            topic: The topic to research
            outline_str: Current outline as JSON string
            memory_content: Memory content from previous research

        Returns:
            dspy.Prediction containing final_title, final_sections, and final_section_subheadings

        Raises:
            AttributeError: If ReACT output is missing required fields
            Exception: If ReACT execution fails
        """
        try:
            # Restore instance-specific instructions before execution
            ReACTGoal.instructions = self._instructions

            output = self.react(
                topic=topic, outline=outline_str, memory_content=memory_content
            )
        except Exception as e:
            logger.error("ReACT research failed: %s", e)
            raise

        # Validate output has required attributes
        if not hasattr(output, "trajectory"):
            raise AttributeError("ReACT output missing 'trajectory' attribute")
        if not hasattr(output, "final_title"):
            raise AttributeError("ReACT output missing 'final_title' attribute")

        # Log trajectory if verbose
        for k, v in output.trajectory.items():
            if self.verbose:
                print(click.style(k, fg="blue"))
                print(click.style(v, fg="green"))
                print()

        # Calculate iterations based on trajectory structure
        # Each iteration typically produces 4 entries in trajectory
        iterations = len(output.trajectory) // TRAJECTORY_ENTRIES_PER_ITERATION

        if self.verbose:
            reasoning = getattr(output, "reasoning", "N/A")
            print(click.style(reasoning, fg="yellow"))

        final_title = getattr(output, "final_title", "")
        final_sections = getattr(output, "final_sections", [])
        final_section_subheadings = getattr(
            output, "final_section_subheadings", {}
        )

        logger.info(
            "ArticleReACTResearcher|%d Iterations|%s", iterations, final_title
        )
        print(f"ArticleReACTResearcher|{iterations} Iterations|{final_title}")

        return dspy.Prediction(
            final_title=final_title,
            final_sections=final_sections,
            final_section_subheadings=final_section_subheadings,
        )

    def save(self, filepath: str) -> None:
        """Save research findings and sources to a file.

        Args:
            filepath: Path to the output file

        Raises:
            OSError: If file cannot be created or written
            ValueError: If filepath is invalid
        """
        if not filepath:
            raise ValueError("filepath cannot be empty")

        try:
            # Create parent directories if they don't exist
            filepath_obj = os.path.abspath(filepath)
            parent_dir = os.path.dirname(filepath_obj)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)

            content = (
                self.memory_tools.get_findings()
                + "\n## Sources\n\n"
                + self.memory_tools.get_sources()
            )

            with open(filepath_obj, "w", encoding="utf-8") as f:
                f.write(content)

            logger.info("Saved research results to %s", filepath)
        except OSError as e:
            logger.error("Failed to save research results to %s: %s", filepath, e)
            raise
        except Exception as e:
            logger.error("Unexpected error saving research results: %s", e)
            raise

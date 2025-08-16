import dspy
import click
from pathlib import Path
from datetime import datetime

from agents.tools import MemoryTools


class ReACTGoal(dspy.Signature):
    "The goal is to research the topic and create a comprehensive outline and collect orgarnized information."
    topic: str = dspy.InputField()
    outline: str = dspy.InputField()
    memory_content: str = dspy.InputField()

    final_title: str = dspy.OutputField()
    final_sections: list[str] = dspy.OutputField()
    final_section_subheadings: dict[str, list[str]] = dspy.OutputField()


class ArticleReACTResearcher(dspy.Module):
    def __init__(self, memory_tools: MemoryTools, verbose: bool = False):
        self.memory_tools = memory_tools

        ReACTGoal.instructions += "\n" + self.memory_tools.research_strategy + "\n" + self.memory_tools.action_plan
        self.react = dspy.ReAct(
            ReACTGoal, 
            tools=self.memory_tools.tool_list(),
            max_iters=10)
        self.verbose = verbose

    def forward(
        self, topic: str, outline_str: str, memory_content: str
    ) -> dspy.Prediction:
        output = self.react(topic=topic, outline=outline_str, memory_content=memory_content)

        for k, v in output.trajectory.items():
            if self.verbose:
                print(click.style(k, fg="blue"))
                print(click.style(v, fg="green"))
                print()
        iterations = len(output.trajectory) // 4

        if self.verbose:
            print(click.style(output.reasoning, fg="yellow"))

        print(f"ArticleReACTResearcher|{iterations} Iterations|{output.final_title}")
        return dspy.Prediction(
            final_title=output.final_title,
            final_sections=output.final_sections,
            final_section_subheadings=output.final_section_subheadings,
        )

    def save(self, filepath: str):
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = Path(filepath)
        filepath = filepath.with_stem(filepath.stem + f"_{now}")
        with open(filepath, "w") as f:
            f.write(self.memory_tools.get_findings() + "\n## Sources\n\n" + self.memory_tools.get_sources())

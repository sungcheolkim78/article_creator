import dspy
import json
import click
from agents.searcher import tool_search_web
from agents.planner import tool_analyze, tool_synthesize, tool_outline


class ReACTGoal(dspy.Signature):
    "The goal is to research the topic and create a comprehensive outline and content about the topic."
    topic: str = dspy.InputField()
    outline: dict[str, list[str]] = dspy.InputField()
    memory_content: str = dspy.InputField()

    final_title: str = dspy.OutputField()
    final_outline: dict[str, list[str]] = dspy.OutputField()
    final_content: str = dspy.OutputField()


class ArticleReACTResearcher(dspy.Module):
    def __init__(self, strategy: str, action_plan: str, verbose: bool = False):
        ReACTGoal.instructions += "\n" + strategy + "\n" + action_plan
        self.react = dspy.ReAct(
            ReACTGoal, 
            tools=[tool_search_web, tool_analyze, tool_synthesize, tool_outline], 
            max_iters=10)
        self.verbose = verbose

    def forward(
        self, topic: str, outline_str: str, memory_content: str
    ) -> dspy.Prediction:
        tmp = json.loads(outline_str)
        output = self.react(topic=topic, outline=tmp['outline'], memory_content=memory_content)

        iterations = 1
        source_content = ""
        tool_name = ""
        for k, v in output.trajectory.items():
            if self.verbose:
                print(click.style(k, fg="blue"))
                print(click.style(v, fg="green"))
                print()
            if k.startswith("tool_name"):
                tool_name = v

            if tool_name == "tool_search_web" and k.startswith("observation"):
                temp = json.loads(v)
                memory_content += f"\n{temp['summary']}"
                source_content += f"\n{temp['sources']}"
                iterations += 1

            if tool_name == "tool_analyze" and k.startswith("observation"):
                memory_content += f"\n## Analyzed Contents\n\n{v}\n"
                iterations += 1

            if tool_name == "tool_synthesize" and k.startswith("observation"):
                memory_content += f"\n## Synthesizd Contents\n\n{v}\n"
                iterations += 1

        if self.verbose:
            print(click.style(output.reasoning, fg="yellow"))

        print(f"ArticleReACTResearcher|{iterations} Iterations|{output.final_title}")
        return dspy.Prediction(
            final_title=output.final_title,
            final_outline=output.final_outline,
            final_content=memory_content,
        )

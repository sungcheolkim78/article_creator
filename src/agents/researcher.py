import dspy
import click
from websearch.ddgsearch import tool_search_web
from dspy.signatures import make_signature


class ArticleReACTResearcher(dspy.Module):
    def __init__(self, strategy: str, action_plan: str, verbose: bool = False):
        Goal = make_signature(
            "topic, outline, memory_content -> final_outline, final_content",
            "The goal is to research the topic and create a comprehensive article about the topic.\n" + strategy + "\n" + action_plan
        )
        self.react = dspy.ReAct(
            Goal, tools=[tool_search_web], max_iters=5
        )
        self.verbose = verbose

    def forward(self, topic: str, outline: str, memory_content: str) -> dspy.Prediction:
        output = self.react(topic=topic, outline=outline, memory_content=memory_content)

        for k, v in output.trajectory.items():
            if self.verbose:
                print(click.style(k, fg="blue"))
                print(click.style(v, fg="green"))
                print()
            if k.startswith("observation"):
                memory_content += v

        if self.verbose:
            print(click.style(output.reasoning, fg="yellow"))

        return dspy.Prediction(
            final_outline=output.final_outline,
            final_content=output.final_content,
            final_sources=memory_content,
        )
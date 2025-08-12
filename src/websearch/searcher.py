from typing import List
from websearch.schema import SearchResult
import dspy
import time
import re
import click
from typing import Literal

GOALS = {
    "claim": "Find all relevant information to verify (or refute) the claim.",
    "question": "Find all relevant information to answer the question.",
    "topic": "Find various information on topic in multiple perspective.",
}


class ReACTGoal(dspy.Signature):
    """Find all relevant information to verify (or refute) the claim."""

    claim: str = dspy.InputField()
    results: str = dspy.OutputField(desc="The search results summary in a single sentence")


class RelevanceChecker(dspy.Signature):
    """Checks if the observation is relevant to the claim"""

    claim: str = dspy.InputField()
    observation: str = dspy.InputField()
    relevant: bool = dspy.OutputField(
        desc="Whether the observation is relevant to the claim"
    )


class Category(dspy.Signature):
    """Categorizes the text into claim, question, or topic"""

    text: str = dspy.InputField()
    category: Literal["claim", "question", "topic"] = dspy.OutputField(
        desc="The category of the text"
    )


class ReACTSearcher(dspy.Module):
    def __init__(self, engine: str = "tavily", verbose: bool = False):
        if engine == "tavily":
            from websearch.tavilysearch import search_news, search_web
        elif engine == "ddg":
            from websearch.ddgsearch import search_news, search_web
        else:
            raise ValueError(f"Invalid engine: {engine}")

        self.search_web = search_web
        self.search_news = search_news
        self.check = dspy.Predict(RelevanceChecker)
        self.category = dspy.Predict(Category)
        self.summary = dspy.Predict("query, results -> summary")
        self.verbose = verbose

    def forward(self, claim: str) -> list[SearchResult]:
        start_time = time.time()
        category = self.category(text=claim).category
        if self.verbose:
            print(click.style(f"Category: {category}", fg="yellow"))

        ReACTGoal.instructions = GOALS[category]
        if self.verbose:
            print(ReACTGoal.instructions)
        self.react = dspy.ReAct(
            ReACTGoal, tools=[self.search_web, self.search_news], max_iters=5
        )
        result = self.react(claim=claim)

        iterations = 1
        observations = []
        query_summarys = []
        for k, v in result.trajectory.items():
            if self.verbose:
                print(click.style(k, fg="blue"))
                print(click.style(v, fg="green"))
                print()

            if k.startswith("tool_args") and v:
                query = v.get("query", "")

            if k.startswith("observation") and v != "Completed.":
                results = [SearchResult.from_json(item) for item in v]
                query_summary = ""
                for item in results:
                    if self.check(claim=claim, observation=item.title).relevant:
                        observations.append(item)
                        query_summary += f"\n- {item.title}|{item.snippet}\n"

                iterations += 1
                if query != "":
                    query_summary = self.summary(query=query, results=query_summary).summary
                    query_summarys.append(f"**{query}:** {query_summary}")

        if self.verbose:
            print(click.style(result.reasoning, fg="yellow"))
            print(click.style(result.results, fg="green"))
            print(click.style(query_summarys, fg="blue"))

        execution_time = time.time() - start_time
        print(f"ReACTSearcher|{claim}|{category}|{iterations} Iterations|{len(observations)} Results|{execution_time:.2f}s")

        markdown = f"## Web Search Results on [{claim}]\n" 
        markdown += f"\n{result.results}\n\n"
        markdown += "\n\n".join([item for item in query_summarys])
        markdown += "\n\n"
        markdown += f"## Sources\n\n"
        markdown += "\n".join([item.to_markdown() for item in observations])
        markdown += "\n"

        return dspy.Prediction(
            query=claim,
            summary=result.results,
            markdown=markdown,
            sources=observations,
        )


def tool_search_web(query: str, engine: str = "tavily", verbose: bool = False) -> str:
    searcher = ReACTSearcher(engine=engine, verbose=verbose)
    output = searcher(query)

    # Format the search results and summary
    memory_context = f"## Web Search Results on {query}\n\n"
    for i, item in enumerate(output.search_results):
        memory_context += str(item).replace("=====", f"### Web Search Result {i+1} ###")
        memory_context += "\n"
    memory_context += f"\n## Web Search Summary on {query}\n\n"
    memory_context += '\n'.join([f"- {item}" for item in output.summary])
    memory_context += "\n"

    return memory_context
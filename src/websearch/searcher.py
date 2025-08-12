from typing import List
from websearch.schema import SearchResult
from dspy.signatures import make_signature
import dspy
import time
import re
import click
from typing import Literal


class QueryOptimizer(dspy.Signature):
    """Optimizes search queries for search engine"""

    original_query: str = dspy.InputField()
    optimized_search_query: list[str] = dspy.OutputField(desc="generate multiple queries to search for the original query")


class QuerySearcher(dspy.Module):
    def __init__(self, engine: str = "tavily", k: int = 3, verbose: bool = False):
        self.engine = engine
        self.k = k
        self.verbose = verbose
        self.query_optimizer = dspy.ChainOfThought(QueryOptimizer)
        self._search_results = {}

    def _setup_tools(self, engine: str):
        if engine == "tavily":
            from websearch.tavily import search_news, search_web
        elif engine == "ddg":
            from websearch.ddg import search_news, search_web
        else:
            raise ValueError(f"Invalid engine: {engine}")

        self.search_web = search_web
        self.search_news = search_news

    def forward(self, query: str) -> str:
        start_time = time.time()
        self._setup_tools(self.engine)
        query_list = self.query_optimizer(original_query=query).optimized_search_query

        if self.verbose:
            print(click.style(f"Optimized query: {query} -> {query_list}", fg="yellow"))

        for item in query_list:
            web_results = self.search_web(item, self.k)
            self._add_search_results([SearchResult.from_json(result) for result in web_results])

        markdown = f"## Web Search Results on [{','.join(query_list)}]\n" 
        markdown += "\n".join([item.to_markdown() for item in self.search_results])
        markdown += "\n"

        execution_time = time.time() - start_time
        print(f"QuerySearcher|{query}|{len(query_list)} Sub-Queries|{len(self.search_results)} Results|{execution_time:.2f}s")

        return dspy.Prediction(
            query=query,
            optimized_query=','.join(query_list),
            markdown=markdown,
        )

    def _add_search_results(self, results: list[SearchResult]):
        for result in results:
            if result.url not in self._search_results:
                self._search_results[result.url] = result
    
    @property
    def search_results(self) -> list[SearchResult]:
        return list(self._search_results.values())


GOALS = {
    "claim": "Find all relevant information to verify (or refute) the claim. Use the search tool with k=3 to 5.",
    "question": "Find all relevant information to answer the question. Use the search tool with k=3.",
    "topic": "Find various information on topic with multiple perspective. Use the search tool with starting k=5 and decreasing k"
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
    def __init__(self, engine: str = "tavily", k: int = 3, verbose: bool = False):
        self.check = dspy.Predict(RelevanceChecker)
        self.category = dspy.Predict(Category)
        self.summary = dspy.Predict("query, results -> summary")
        self.engine = engine
        self.verbose = verbose

    def _setup_react(self, category: str, engine: str):
        ReACTGoal.instructions = GOALS[category]
        if self.verbose:
            print(ReACTGoal.instructions)

        if engine == "tavily":
            from websearch.tavily import search_news, search_web
        elif engine == "ddg":
            from websearch.ddg import search_news, search_web
        else:
            raise ValueError(f"Invalid engine: {engine}")

        return dspy.ReAct(ReACTGoal, tools=[search_web, search_news], max_iters=5)

    def forward(self, claim: str) -> list[SearchResult]:
        start_time = time.time()
        category = self.category(text=claim).category
        react = self._setup_react(category, self.engine)

        if self.verbose:
            print(click.style(f"Category: {category}", fg="yellow"))

        result = react(claim=claim)

        iterations = 1
        observations = []
        query_summarys = []
        for k, v in result.trajectory.items():
            if self.verbose:
                print(click.style(k, fg="blue"))
                print(click.style(v, fg="green"))
                print()

            if k.startswith("tool_name") and v.startswith("search_"):
                source = v.replace("search_", "")

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
                    query_summarys.append(f"**{query} ({source}):** {query_summary}")

        if self.verbose:
            print(click.style(result.reasoning, fg="yellow"))
            print(click.style(result.results, fg="green"))
            print(click.style(query_summarys, fg="blue"))

        execution_time = time.time() - start_time
        print(f"ReACTSearcher|{claim}|{category}|{iterations} Iterations|{len(observations)} Results|{execution_time:.2f}s")

        search_summary = f"## Web Search Results on [{claim}]\n" 
        search_summary += f"\n{result.results}\n\n"
        search_summary += "\n\n".join([item for item in query_summarys])
        search_summary += "\n"

        sources = "\n".join([item.to_markdown() for item in observations])

        markdown = search_summary + f"\n## Sources\n\n" + sources + "\n"

        return dspy.Prediction(
            query=claim,
            summary=search_summary,
            sources=observations,
            markdown=markdown,
        )


def tool_search_web(query: str, engine: str = "tavily", verbose: bool = False) -> str:
    """Generate a search summary for the given query using the ReACTSearcher"""

    searcher = ReACTSearcher(engine=engine, verbose=verbose)
    output = searcher(query)

    return json.dumps({
        "query": query,
        "summary": output.summary,
        "sources": "\n".join([item.to_json() for item in output.sources]),
    })
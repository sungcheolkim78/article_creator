import dspy
import click
from datetime import datetime
from typing import Literal

from websearch.base import BaseSearcher
from websearch.schema import SearchResult


class QueryOptimizer(dspy.Signature):
    """Optimizes search queries for search engine, create only 3-5 queries that are relevant to the original query."""

    original_query: str = dspy.InputField()
    optimized_search_query: list[str] = dspy.OutputField(
        desc="Generate multiple queries to search for the original query"
    )


class SelectSource(dspy.Signature):
    """Choose web or news source for the search query."""

    query: str = dspy.InputField()
    source: Literal["web", "news"] = dspy.OutputField(
        desc="If the query is about a specific event, recent changes, or recent news, choose news. Otherwise, choose web."
    )


class QuerySearcher(BaseSearcher):
    def __init__(self, engine: str = "tavily", k: int = 3, verbose: bool = False):
        super().__init__(engine, k, verbose)
        self.query_optimizer = dspy.ChainOfThought(QueryOptimizer)
        SelectSource.instructions += f"The current date is {datetime.now().strftime('%Y-%m-%d')}."
        self.select_source = dspy.ChainOfThought(SelectSource)
        self._name = "QuerySearcher"

    def _setup_tools(self, category: str, engine: str):
        if engine == "tavily":
            from websearch.tavily import search_news, search_web
        elif engine == "ddg":
            from websearch.ddg import search_news, search_web
        elif engine == "brave":
            from websearch.brave import search_news, search_web
        else:
            raise ValueError(f"Invalid engine: {engine}")

        self.search_web = search_web
        self.search_news = search_news
        self.use_llm_for_web_news = False

    def _search(self, query: str) -> tuple[str, str, str]:
        outcome = self.query_optimizer(original_query=query)
        query_list = outcome.optimized_search_query
        if self.verbose:
            print(click.style(f"Optimized query: {query} -> {query_list}", fg="yellow"))
            print(click.style(f"Reasoning: {outcome.reasoning}", fg="yellow"))

        query_summaries = []
        for item in query_list:
            if self.use_llm_for_web_news:
                temp = self.select_source(query=item)
                if self.verbose:
                    print(click.style(f"Reasoning: {temp.reasoning}", fg="yellow"))
                source = temp.source
            else:
                source = "web"  # default to web if not using llm for web/news selection
            if source == "web":
                web_results = self.search_web(item, self.k)
            elif source == "news":
                web_results = self.search_news(item, self.k)
            
            web_results = [SearchResult.from_json(result) for result in web_results]
            web_summary = self._get_summary(item, web_results)
            query_summaries.append(f"**{item} ({source}):** {web_summary}")
            self._add_search_results(web_results)

        proc_info = f"{len(query_list)} Sub-Queries|{len(self.search_results)} Results"
        sources = "\n".join([item.to_markdown() for item in self.search_results])
        search_summary = f"## Web Search Results on |{query}|\n\n"
        search_summary += "\n\n".join([item for item in query_summaries])
        search_summary += "\n"

        return search_summary, sources, proc_info


GOALS = {
    "claim": "Find all relevant information to verify (or refute) the claim. Use the search tool with k=3 to 5.",
    "question": "Find all relevant information to answer the question. Use the search tool with k=3.",
    "topic": "Find comprehensive information about the topic with multiple perspectives. Use the search tool with k=3 to 5.",
}


class ReACTGoal(dspy.Signature):
    """Find all relevant information to verify (or refute) the claim."""

    claim: str = dspy.InputField()
    results: str = dspy.OutputField(
        desc="The search results summary in a single sentence"
    )


class RelevanceChecker(dspy.Signature):
    """Checks if the observation is relevant to the claim"""

    claim: str = dspy.InputField()
    observation: str = dspy.InputField()
    relevant: bool = dspy.OutputField(
        desc="Whether the observation is relevant to the claim"
    )


class ReACTSearcher(BaseSearcher):
    def __init__(self, engine: str = "tavily", k: int = 3, verbose: bool = False):
        super().__init__(engine, k, verbose)
        self.check = dspy.Predict(RelevanceChecker)
        self._name = "ReACTSearcher"

    def _setup_tools(self, category: str, engine: str):
        if engine == "tavily":
            from websearch.tavily import search_news, search_web
        elif engine == "ddg":
            from websearch.ddg import search_news, search_web
        elif engine == "brave":
            from websearch.brave import search_news, search_web
        else:
            raise ValueError(f"Invalid engine: {engine}")

        ReACTGoal.instructions = GOALS[category]
        if self.verbose:
            print(ReACTGoal.instructions)

        self.search_web = search_web
        self.search_news = search_news
        self.react = dspy.ReAct(ReACTGoal, tools=[search_web, search_news], max_iters=5)

    def _search(self, claim: str) -> tuple[str, str, str]:
        result = self.react(claim=claim)

        iterations = 1
        observations = []
        query_summaries = []
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
                web_results = [SearchResult.from_json(item) for item in v]
                # web_results = [item for item in web_results if self.check(claim=query, observation=item.title).relevant]
                observations.extend(web_results)

                iterations += 1
                if query != "":
                    web_citations = " ".join([f"[^{item.sid}]" for item in web_results])
                    web_summary = self._get_summary(query, web_results)
                    query_summaries.append(
                        f"**{query} ({source}):** {web_summary} {web_citations}"
                    )

        if self.verbose:
            print(click.style(result.reasoning, fg="yellow"))

        proc_info = f"{iterations} Iterations|{len(observations)} Results"
        sources = "\n".join([item.to_markdown() for item in observations])
        search_summary = f"## Web Search Results on |{claim}|\n"
        search_summary += f"\n{result.results}\n\n"
        search_summary += "\n\n".join([item for item in query_summaries])
        search_summary += "\n"

        return search_summary, sources, proc_info

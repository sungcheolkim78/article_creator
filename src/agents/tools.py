import json
import time
from typing import Callable
from functools import wraps

from agents.searcher import ReACTSearcher, QuerySearcher
from dspy.clients.cache import request_cache
import dspy


def execution_time(func):
    """Decorator to calculate and store execution time of functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time_seconds = end_time - start_time
        
        # Store execution time in the instance if it's a method
        if args and hasattr(args[0], 'execution_times'):
            if not hasattr(args[0], 'execution_times'):
                args[0].execution_times = {}
            if func.__name__ not in args[0].execution_times:
                args[0].execution_times[func.__name__] = 0
            args[0].execution_times[func.__name__] += execution_time_seconds
        
        # Print execution time for debugging
        print(f"⏱️  {func.__name__} executed in {execution_time_seconds:.2f} seconds")
        
        return result
    return wrapper


class MemoryTools:
    """Article Generation Tools with Memory."""
    def __init__(self, mode: str = "query", engine: str = "tavily", verbose: bool = False):
        self.memory_content = ""
        self.search_summary = ""
        self.source_content = ""

        self.search_results = []
        self.analysis_results = []
        self.gap_results = []
        self.sources = []
        self.search_time = 0
        self.execution_times = {}  # Store execution times for all decorated functions

        self.mode = mode
        self.engine = engine
        self.verbose = verbose

        self.analyzer = dspy.ChainOfThought(AnalyzedInfo)
        self.outliner = dspy.ChainOfThought(ArticleOutline)
        self.gap_researcher = dspy.ChainOfThought(ResearchGap)
        self.planner = dspy.ChainOfThought(ArticlePlan)

    @request_cache()
    @execution_time
    def search_web(self, query: str) -> str:
        """Search the web for the given query, and return the search summary."""
        print("... Use search_web tool ...")

        if self.mode == "react":
            searcher = ReACTSearcher(engine=self.engine, verbose=self.verbose)
        elif self.mode == "query":
            searcher = QuerySearcher(engine=self.engine, verbose=self.verbose)
        else:
            raise ValueError(f"Invalid mode: {self.mode}")

        output = searcher(query)

        self.search_results.append(output.summary)
        self.sources.extend(output.sources)
        self.search_time += searcher.execution_time

        return json.dumps(
            {
                "query": query,
                "summary": output.summary,
            }
        )

    @execution_time
    def analyze(self, question: str) -> str:
        """Generate a comprehensive analysis of the question with internal web search results."""
        print("... Use analyze tool ...")

        output = self.analyzer(question=question, web_search_results=self.search_results).analysis_content
        output_str = f"## Analysis of |{question}|\n\n{output}"
        self.analysis_results.append(output_str)
        return output_str

    @execution_time
    def outline(self, topic: str, current_outline: str) -> str:
        """Given a topic, previous outline, and research findings, generate a comprehensive outline for an article."""
        print("... Use outline tool ...")

        outcome = self.outliner(
            topic=topic, current_outline=current_outline, content=self.get_findings()
        )

        self.topic = topic
        self.title = outcome.title
        self.sections = outcome.sections
        self.section_subheadings = outcome.section_subheadings

        return self.outline_str

    @execution_time
    def research_gap(self, outline_str: str) -> str:
        """Generate a research gap for the given outline and research findings."""
        print("... Use research_gap tool ...")

        output =  self.gap_researcher(findings=self.get_findings(), outline=outline_str).infomation_gap
        self.gap_results.append(output)
        return output

    @execution_time
    def plan(self, topic: str, research_gap: str) -> str:
        """Generate a research plan for the given topic and research gap."""
        print("... Use plan tool ...")

        output = self.planner(
            topic=topic, 
            current_outline=self.outline_str, 
            research_gaps=research_gap, 
            available_tools=self.available_tools, 
            memory_context=self.get_findings()
        )
        self.research_strategy = output.research_strategy
        self.action_plan = output.action_plan
        return output

    def get_findings(self, full_report: bool = False) -> str:
        """Get the findings of the analysis results."""
        content = "\n\n".join(self.search_results)
        content += "\n\n" + "\n\n".join(self.analysis_results)
        if full_report:
            content += "\n\n" + "\n\n".join(self.gap_results)
        return content

    def get_sources(self) -> str:
        """Get the sources of the search results."""
        content = '\n'.join([item.to_markdown() for item in self.sources])
        return content

    @property
    def outline_str(self) -> str:
        outline_str = json.dumps({
            "title": self.title,
            "sections": self.sections,
            "section_subheadings": self.section_subheadings,
        })
        return outline_str

    @property
    def available_tools(self) -> str:
        available_tools = "The available tools are:"
        available_tools += "\ntool_search_web: " + self.search_web.__doc__
        available_tools += "\ntool_outline: " + self.outline.__doc__
        available_tools += "\ntool_analyze: " + self.analyze.__doc__
        return available_tools

    def tool_list(self) -> list[Callable]:
        return [self.search_web, self.outline, self.analyze]

    def report(self) -> str:
        report = "## Execution Times\n"
        for func_name, time in self.execution_times.items():
            report += f"- {func_name}: {time:.2f} seconds\n"
        report += f"- Total search time: {self.search_time:.2f} seconds\n"
        report += "\n## Finding Statistics\n"
        report += f"- Total findings: {len(self.search_results)}\n"
        report += f"- Total analysis: {len(self.analysis_results)}\n"
        report += f"- Total gap: {len(self.gap_results)}\n"
        report += f"- Total sources: {len(self.sources)}\n"
        return report


class AnalyzedInfo(dspy.Signature):
    """Given a question and web search results, generate a analysis of the question. It can include the main findings, the potential gaps, and the potential solutions."""

    question: str = dspy.InputField()
    web_search_results: str = dspy.InputField()
    analysis_content: str = dspy.OutputField(desc="one or two paragraphs of analysis including citations. citations should be in markdown format such as [^1], [^2], etc.")


class ArticleOutline(dspy.Signature):
    """Given a topic, current outline, and research findings, generate a new comprehensive outline for an article."""

    topic: str = dspy.InputField()
    current_outline: str = dspy.InputField(desc="The current outline of the article")
    content: str = dspy.InputField(desc="The research findings of the article")

    title: str = dspy.OutputField()
    sections: list[str] = dspy.OutputField(desc="list of sections, maximum 7 sections")
    section_subheadings: dict[str, list[str]] = dspy.OutputField(
        desc="mapping from section headings to subheadings, maximum 3 subheadings per section"
    )


class ResearchGap(dspy.Signature):
    """Given a outline and research findings, generate a information gap for the comprehensive article."""

    outline: str = dspy.InputField(desc="The outline of the article")
    findings: str = dspy.InputField(desc="The research findings of the article")
    infomation_gap: str = dspy.OutputField(
        desc="The information gap for the comprehensive article"
    )


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


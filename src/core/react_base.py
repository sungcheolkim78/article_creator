import dspy
import json
import logging
import click
from datetime import datetime
from typing import List, Dict, Any, Optional, Literal

from core.react_memory import ReactMemory
from core.research_tool import ResearchTool
from utils.utils import broaden_search_query

logger = logging.getLogger("react_base")


class ReACTStep(dspy.Signature):
    """ReACT step signature for reasoning and acting on article generation tasks."""

    goal: str = dspy.InputField(desc="The goal or question to accomplish")
    available_tools: str = dspy.InputField(
        desc="List of available tools and their capabilities"
    )
    previous_actions: str = dspy.InputField(
        desc="Previous actions taken and their results"
    )
    memory_context: str = dspy.InputField(desc="Relevant information from memory")

    action: Literal["search", "research", "fact_check", "analyze", "finish"] = dspy.OutputField()
    action_input: dict = dspy.OutputField(desc="Input parameters for the action.")


class ReACTAgent(dspy.Module):
    """
    ReACT (Reasoning and Acting) agent for enhanced article generation.

    This agent can reason about what information is needed and take actions
    to gather that information using web search and research tools.
    """

    def __init__(self, search_tool, memory_size: int = 1000):
        super().__init__()
        self.search_tool = search_tool
        self.research_tool = ResearchTool(search_tool)
        self.react_step = dspy.ChainOfThought(ReACTStep)
        self.memory = ReactMemory(max_memory_size=memory_size)

        # Available tools description
        self.tools_description = """
        Available tools:
        1. search: Perform web search for current information, need to provide a query
        2. research: Deep research on a specific question with synthesis, need to provide a list of questions
        3. analyze: Analyze and synthesize information, need to provide a content
        4. fact_check: Verify claims or facts, need to provide a claim
        5. finish: Complete the task with final output
        """

        self.research_num_sources = 5
        self.max_iterations = 10

    def forward(
        self, goal: str, max_iterations: Optional[int] = None
    ) -> Dict[str, Any]:
        """Execute ReACT loop to accomplish the given goal."""
        max_iter = max_iterations or self.max_iterations
        actions_taken = []
        gathered_info = []

        for iteration in range(max_iter):
            # Format previous actions for context
            previous_actions_str = self._format_previous_actions(actions_taken)

            # Get relevant memory context
            memory_context = self._get_memory_context(goal, actions_taken)
            print()
            print(click.style(f'⚙️ Iteration {iteration + 1}', fg='green', bold=True))
            print(click.style(f"Memory Context: {memory_context}", fg='red'))

            # Get next action from ReACT reasoning
            react_output = self.react_step(
                goal=goal,
                available_tools=self.tools_description,
                previous_actions=previous_actions_str,
                memory_context=memory_context,
            )

            print(click.style(f'💡 Thought: {react_output.reasoning}', fg='green'))
            print(click.style(f'🔍 Action: {react_output.action}', fg='green'))
            print(click.style(f'🔍 Action Input: {react_output.action_input}', fg='green'))

            # Execute the action
            action_result = self._execute_action(
                react_output.action, react_output.action_input
            )

            # Store results in memory
            self._store_action_in_memory(
                react_output.action, react_output.action_input, action_result
            )

            # Record the action
            action_record = {
                "iteration": iteration + 1,
                "thought": react_output.reasoning,
                "action": react_output.action,
                "action_input": str(react_output.action_input),
                "result": action_result,
            }
            actions_taken.append(action_record)

            # Check if we should finish
            if react_output.action.lower() == "finish":
                break

            # Add successful results to gathered info
            if action_result and action_result.get("success", True):
                gathered_info.append(action_result)

        return {
            "goal": goal,
            "actions_taken": actions_taken,
            "gathered_information": gathered_info,
            "final_iteration": iteration + 1,
            "completed": react_output.action.lower() == "finish",
            "memory_summary": self.memory.get_memory_summary(),
        }

    def _get_memory_context(self, goal: str, actions_taken: List[Dict[str, Any]]) -> str:
        """Get relevant context from memory for the current goal and actions."""
        context_parts = []

        # Get relevant search results
        relevant_searches = self.memory.get_relevant_search_results(goal, max_results=3)
        if relevant_searches:
            context_parts.append("Relevant previous searches:")
            for search in relevant_searches:
                context_parts.append(f"- Query: {search['query']}")
                if search.get("metadata", {}).get("broader_query"):
                    context_parts.append(
                        f"  Broader query used: {search['metadata']['broader_query']}"
                    )
                context_parts.append(f"  Results: {len(search['results'])} items found")
                if search.get("metadata", {}).get("note"):
                    context_parts.append(f"  Note: {search['metadata']['note']}")

        # Get relevant research findings
        if actions_taken:
            print(actions_taken[-1])
        if actions_taken and "answers" in actions_taken[-1]["result"]:
            questions = actions_taken[-1]["result"].get("questions", "")
            relevant_findings = []
            for question in questions:
                findings = self.memory.get_research_findings(question)
                if findings:
                    relevant_findings.extend(findings)
        else:
            relevant_findings = self.memory.get_research_findings(goal)
        if relevant_findings:
            context_parts.append("Relevant research findings:")
            for finding in relevant_findings[:2]:  # Limit to 2 findings
                finding_str = finding['finding'].get('answer', 'Finding available')[:200].replace('\n\n', '\n')
                context_parts.append(f"- {finding_str}...")

        # Get relevant context
        relevant_context = self.memory.get_relevant_context(goal, max_context=2)
        if relevant_context:
            context_parts.append("Relevant context:")
            for context in relevant_context:
                context_parts.append(f"- {context[:150]}...")

        # Get recent insights
        recent_insights = self.memory.get_recent_insights(max_insights=2)
        if recent_insights:
            context_parts.append("Recent insights:")
            for insight in recent_insights:
                context_parts.append(f"- {insight[:100]}...")

        if not context_parts:
            return "No relevant memory context available."

        return "\n".join(context_parts)

    def _store_action_in_memory(
        self, action: str, action_input: str, result: Dict[str, Any]
    ):
        """Store action results in memory for future reference."""
        if not result or not result.get("success", False):
            return

        action = action.lower().strip()

        if action == "search":
            # Store search results
            search_results = result.get("results", [])
            num_results = len(search_results)

            # Convert SearchResult objects to dictionaries for storage
            results_dict = []
            for search_result in search_results:
                if hasattr(search_result, "url"):  # Check if it's a SearchResult object
                    results_dict.append(
                        {
                            "title": getattr(search_result, "title", ""),
                            "url": getattr(search_result, "url", ""),
                            "snippet": getattr(search_result, "snippet", ""),
                            "published_time": getattr(
                                search_result, "published_time", None
                            ),
                            "extra_snippets": getattr(
                                search_result, "extra_snippets", []
                            ),
                        }
                    )
                elif isinstance(search_result, dict):  # Already a dictionary
                    results_dict.append(search_result)

            # Store the search result with additional metadata
            metadata = {
                "num_results": num_results, 
                "action": action,
                "query": action_input.get("query", ""),
                "broader_query": result.get("broader_query", ""),
                "note": result.get("note", "")
            }

            self.memory.add_search_result(
                query=action_input.get("query", ""), results=results_dict, metadata=metadata
            )

            # Extract and store sources
            for search_result in search_results:
                if (
                    hasattr(search_result, "url") and search_result.url
                ):  # SearchResult object
                    self.memory.add_source(
                        url=search_result.url,
                        source_info={
                            "title": search_result.title,
                            "snippet": search_result.snippet,
                            "query": action_input,
                        },
                    )
                elif isinstance(search_result, dict) and search_result.get(
                    "url"
                ):  # Dictionary
                    self.memory.add_source(
                        url=search_result["url"],
                        source_info={
                            "title": search_result.get("title", ""),
                            "snippet": search_result.get("snippet", ""),
                            "query": action_input,
                        },
                    )

        elif action == "fact_check":
            # Store fact check results
            self.memory.add_fact_check(
                claim=action_input,
                verification={
                    "status": result.get("verification_status", ""),
                    "explanation": result.get("explanation", ""),
                    "sources": result.get("sources", []),
                },
            )



    def _execute_action(self, action: str, action_input: str) -> Dict[str, Any]:
        """Execute the specified action with given input."""

        action = action.lower().strip()

        if action == "search":
            return self._perform_search(action_input.get("query", ""))
        elif action == "research":
            return self._perform_research(action_input)
        elif action == "fact_check":
            return self._perform_fact_check(action_input.get("claim", ""))
        elif action == "analyze":
            return self._perform_analysis(action_input.get("content", ""))
        elif action == "finish":
            return {"action": "finish", "result": action_input, "success": True}
        else:
            return {
                "action": action,
                "error": f"Unknown action: {action}",
                "success": False,
            }

    def _perform_search(self, query: str) -> Dict[str, Any]:
        """Perform web search."""
        try:
            # Parse query if it's JSON-like
            if query.startswith("{"):
                query_data = json.loads(query)
                search_query = query_data.get("query", query)
                num_results = query_data.get("num_results", 5)
            else:
                search_query = query
                num_results = 5

            results = self.search_tool.optimized_search(search_query, k=num_results)
            # Check if we got any results
            if results:
                return {
                    "action": "search",
                    "query": search_query,
                    "results": results,
                    "num_results": len(results),
                    "success": True,
                }

            # Try with a broader search
            broader_query = broaden_search_query(search_query)
            logger.warning(
                f"⚠️  No results found for '{search_query}'. Trying broader search: '{broader_query}'"
            )

            broader_results = self.search_tool.optimized_search(
                broader_query, k=num_results
            )

            if broader_results:
                return {
                    "action": "search",
                    "query": search_query,
                    "broader_query": broader_query,
                    "results": broader_results,
                    "num_results": len(broader_results),
                    "success": True,
                    "note": f"No results for original query. Used broader search: '{broader_query}'",
                }

            return {
                "action": "search",
                "query": search_query,
                "broader_query": broader_query,
                "results": [],
                "num_results": 0,
                "success": False,
                "note": f"No results found for '{search_query}' or broader query '{broader_query}'. Consider using a more general topic or different keywords.",
            }

        except Exception as e:
            return {"action": "search", "error": str(e), "success": False}

    def _perform_research(self, action_input: dict) -> Dict[str, Any]:
        """Perform deep research on a question."""
        questions = action_input.get("questions", [action_input.get("question", "")])
        answers = []

        for question in questions:
            result = self.research_tool.research_question(
                question, num_sources=self.research_num_sources
            )
            answers.append(result.get("answer", ""))

            # Store research findings
            self.memory.add_research_finding(
                topic=question,
                finding={
                    "answer": result.get("answer", ""),
                    "search_query": result.get("search_query", ""),
                    "content": result.get("content", ""),
                },
            )

            # Store sources from research
            for source in result.get("sources", []):
                self.memory.add_source(
                    url=source.url,
                    source_info={
                        "title": source.title,
                        "content": source.snippet,
                        "research_topic": question,
                    },
                )

        return {
            "action": "research",
            "questions": questions,
            "answers": answers,
            "success": True,
        }

    def _perform_fact_check(self, claim: str) -> Dict[str, Any]:
        """Fact-check a claim."""
        try:
            result = self.research_tool.verify_fact(claim, num_sources=3)

            return {
                "action": "fact_check",
                "claim": claim,
                "verification_status": result["verification_status"],
                "explanation": result["explanation"],
                "sources": result["sources"],
                "success": True,
            }
        except Exception as e:
            return {"action": "fact_check", "error": str(e), "success": False}

    def _perform_analysis(self, content: str) -> Dict[str, Any]:
        """Analyze and synthesize information."""
        try:
            # Use DSPy to analyze the content
            analyzer = dspy.ChainOfThought(
                "content -> analysis, key_insights, recommendations"
            )
            result = analyzer(content=content)

            # Store analysis insights
            self.memory.add_insight(
                insight=result.get("key_insights", ""), category="analysis"
            )

            # Store analysis context
            self.memory.add_context(
                context=f"Analysis of: {content[:200]}...", relevance_score=0.8
            )

            return {
                "action": "analyze",
                "content": content,
                "analysis": result.analysis,
                "key_insights": result.key_insights,
                "recommendations": result.recommendations,
                "success": True,
            }
        except Exception as e:
            return {"action": "analyze", "error": str(e), "success": False}

    def _format_previous_actions(self, actions: List[Dict[str, Any]]) -> str:
        """Format previous actions for context."""
        if not actions:
            return "No previous actions taken."

        formatted = []
        # Only show last 3 actions to avoid context overflow
        for action in actions[-3:]:  
            formatted.append(
                f"Action {action['iteration']}: {action['action']} - "
                f"Input: {action['action_input'][:200]}... - "
                f"Success: {action['result'].get('success', 'Unknown')}"
            )

        return "\n".join(formatted)

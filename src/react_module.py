import dspy
from typing import List, Dict, Any, Optional
from bravesearch import OptimizedBraveSearch
from research_assistant import ResearchAssistant
import json
from datetime import datetime
import hashlib
import logging
import click

logger = logging.getLogger("react_module")


class Memory:
    """
    Memory system for ReACT agent to maintain context and search sources across iterations.
    """

    def __init__(self, max_memory_size: int = 1000):
        self.max_memory_size = max_memory_size
        self.memory_store = {
            "search_results": {},  # Store search results by query hash
            "research_findings": {},  # Store research findings by topic
            "fact_checks": {},  # Store fact verification results
            "context": [],  # Store contextual information
            "sources": {},  # Store source URLs and metadata
            "insights": [],  # Store key insights and learnings
            "action_history": [],  # Store action patterns and outcomes
        }
        self.access_count = {}  # Track access frequency for memory management

    def add_search_result(self, query: str, results: List[Dict], metadata: Dict = None):
        """Add search results to memory with query as key."""
        query_hash = self._hash_query(query)
        self.memory_store["search_results"][query_hash] = {
            "query": query,
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
            "access_count": 0,
        }
        self._manage_memory_size()

    def add_research_finding(self, topic: str, finding: Dict):
        """Add research finding to memory."""
        topic_hash = self._hash_query(topic)
        if topic_hash not in self.memory_store["research_findings"]:
            self.memory_store["research_findings"][topic_hash] = []

        self.memory_store["research_findings"][topic_hash].append(
            {
                "finding": finding,
                "timestamp": datetime.now().isoformat(),
                "access_count": 0,
            }
        )
        self._manage_memory_size()

    def add_fact_check(self, claim: str, verification: Dict):
        """Add fact check result to memory."""
        claim_hash = self._hash_query(claim)
        self.memory_store["fact_checks"][claim_hash] = {
            "claim": claim,
            "verification": verification,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0,
        }
        self._manage_memory_size()

    def add_context(self, context: str, relevance_score: float = 1.0):
        """Add contextual information to memory."""
        self.memory_store["context"].append(
            {
                "context": context,
                "relevance_score": relevance_score,
                "timestamp": datetime.now().isoformat(),
                "access_count": 0,
            }
        )
        self._manage_memory_size()

    def add_source(self, url: str, source_info: Dict):
        """Add source information to memory."""
        url_hash = self._hash_query(url)
        self.memory_store["sources"][url_hash] = {
            "url": url,
            "info": source_info,
            "timestamp": datetime.now().isoformat(),
            "access_count": 0,
        }
        self._manage_memory_size()

    def add_insight(self, insight: str, category: str = "general"):
        """Add key insight to memory."""
        self.memory_store["insights"].append(
            {
                "insight": insight,
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "access_count": 0,
            }
        )
        self._manage_memory_size()

    def get_relevant_search_results(
        self, query: str, max_results: int = 5
    ) -> List[Dict]:
        """Retrieve relevant search results based on query similarity."""
        query_hash = self._hash_query(query)

        # Direct match
        if query_hash in self.memory_store["search_results"]:
            result = self.memory_store["search_results"][query_hash]
            result["access_count"] += 1
            return [result]

        # Similarity search (simple keyword matching for now)
        relevant_results = []
        query_lower = query.lower()

        for stored_query_hash, stored_result in self.memory_store[
            "search_results"
        ].items():
            stored_query = stored_result["query"].lower()
            # Simple keyword overlap check
            query_words = set(query_lower.split())
            stored_words = set(stored_query.split())
            overlap = len(query_words.intersection(stored_words))

            if overlap > 0:
                stored_result["access_count"] += 1
                relevant_results.append(stored_result)

        # Sort by relevance (overlap) and recency
        relevant_results.sort(
            key=lambda x: (
                len(
                    set(query_lower.split()).intersection(
                        set(x["query"].lower().split())
                    )
                ),
                x["timestamp"],
            ),
            reverse=True,
        )

        return relevant_results[:max_results]

    def get_research_findings(self, topic: str) -> List[Dict]:
        """Retrieve research findings for a topic."""
        topic_hash = self._hash_query(topic)
        if topic_hash in self.memory_store["research_findings"]:
            findings = self.memory_store["research_findings"][topic_hash]
            for finding in findings:
                finding["access_count"] += 1
            return findings
        return []

    def get_fact_check(self, claim: str) -> Optional[Dict]:
        """Retrieve fact check result for a claim."""
        claim_hash = self._hash_query(claim)
        if claim_hash in self.memory_store["fact_checks"]:
            result = self.memory_store["fact_checks"][claim_hash]
            result["access_count"] += 1
            return result
        return None

    def get_relevant_context(self, query: str, max_context: int = 3) -> List[str]:
        """Retrieve relevant contextual information."""
        query_lower = query.lower()
        relevant_contexts = []

        for context_item in self.memory_store["context"]:
            context_lower = context_item["context"].lower()
            # Simple keyword matching
            query_words = set(query_lower.split())
            context_words = set(context_lower.split())
            overlap = len(query_words.intersection(context_words))

            if overlap > 0:
                context_item["access_count"] += 1
                relevant_contexts.append(context_item)

        # Sort by relevance and recency
        relevant_contexts.sort(
            key=lambda x: (x["relevance_score"], x["timestamp"]), reverse=True
        )

        return [item["context"] for item in relevant_contexts[:max_context]]

    def get_recent_insights(
        self, category: str = None, max_insights: int = 5
    ) -> List[str]:
        """Retrieve recent insights, optionally filtered by category."""
        insights = self.memory_store["insights"]
        if category:
            insights = [
                insight for insight in insights if insight["category"] == category
            ]

        # Sort by recency
        insights.sort(key=lambda x: x["timestamp"], reverse=True)

        for insight in insights[:max_insights]:
            insight["access_count"] += 1

        return [insight["insight"] for insight in insights[:max_insights]]

    def get_memory_summary(self) -> Dict[str, Any]:
        """Get a summary of memory contents."""
        return {
            "total_search_results": len(self.memory_store["search_results"]),
            "total_research_findings": sum(
                len(findings)
                for findings in self.memory_store["research_findings"].values()
            ),
            "total_fact_checks": len(self.memory_store["fact_checks"]),
            "total_context_items": len(self.memory_store["context"]),
            "total_sources": len(self.memory_store["sources"]),
            "total_insights": len(self.memory_store["insights"]),
            "memory_size": self._get_memory_size(),
        }

    def _hash_query(self, query: str) -> str:
        """Create a hash for a query string."""
        return hashlib.md5(query.encode()).hexdigest()

    def _get_memory_size(self) -> int:
        """Calculate current memory size."""
        total_size = 0
        for category, items in self.memory_store.items():
            if isinstance(items, dict):
                total_size += len(items)
            elif isinstance(items, list):
                total_size += len(items)
        return total_size

    def _manage_memory_size(self):
        """Manage memory size by removing least accessed items if needed."""
        current_size = self._get_memory_size()

        if current_size <= self.max_memory_size:
            return

        # Remove least accessed items from each category
        for category, items in self.memory_store.items():
            if isinstance(items, dict):
                # Sort by access count and remove least accessed
                sorted_items = sorted(
                    items.items(), key=lambda x: x[1].get("access_count", 0)
                )
                items_to_remove = current_size - self.max_memory_size
                for i in range(min(items_to_remove, len(sorted_items))):
                    del items[sorted_items[i][0]]
            elif isinstance(items, list):
                # Sort by access count and remove least accessed
                items.sort(key=lambda x: x.get("access_count", 0))
                items_to_remove = current_size - self.max_memory_size
                if items_to_remove > 0:
                    self.memory_store[category] = items[items_to_remove:]


class ReACTSignature(dspy.Signature):
    """ReACT signature for reasoning and acting on article generation tasks."""

    goal: str = dspy.InputField(desc="The goal or question to accomplish")
    available_tools: str = dspy.InputField(
        desc="List of available tools and their capabilities"
    )
    previous_actions: str = dspy.InputField(
        desc="Previous actions taken and their results"
    )
    memory_context: str = dspy.InputField(desc="Relevant information from memory")

    thought: str = dspy.OutputField(desc="Reasoning about what to do next")
    action: str = dspy.OutputField(
        desc="The action to take (search, analyze, synthesize, or finish)"
    )
    action_input: str = dspy.OutputField(desc="Input parameters for the action")


class ReACTAgent(dspy.Module):
    """
    ReACT (Reasoning and Acting) agent for enhanced article generation.

    This agent can reason about what information is needed and take actions
    to gather that information using web search and research tools.
    """

    def __init__(self, brave_search: OptimizedBraveSearch, memory_size: int = 1000):
        super().__init__()
        self.search_tool = brave_search
        self.research_assistant = ResearchAssistant(brave_search)
        self.react_step = dspy.ChainOfThought(ReACTSignature)
        self.memory = Memory(max_memory_size=memory_size)

        # Available tools description
        self.tools_description = """
        Available tools:
        1. search: Perform web search for current information
        2. research: Deep research on a specific question with synthesis
        3. fact_check: Verify claims or facts
        4. analyze: Analyze and synthesize information
        5. finish: Complete the task with final output
        """

        self.max_iterations = 10

    def forward(
        self, goal: str, max_iterations: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute ReACT loop to accomplish the given goal.
        """
        max_iter = max_iterations or self.max_iterations
        actions_taken = []
        gathered_info = []

        for iteration in range(max_iter):
            # Format previous actions for context
            previous_actions_str = self._format_previous_actions(actions_taken)

            # Get relevant memory context
            memory_context = self._get_memory_context(goal, previous_actions_str)

            # Get next action from ReACT reasoning
            react_output = self.react_step(
                goal=goal,
                available_tools=self.tools_description,
                previous_actions=previous_actions_str,
                memory_context=memory_context,
            )

            print(f"\n{click.style('⚙️ Iteration ' + str(iteration + 1), fg='green', bold=True)}")
            print(f"{click.style('💡 Thought: ' + react_output.thought, fg='green')}")
            print(f"{click.style('🔍 Action: ' + react_output.action, fg='green')}")
            print(f"{click.style('🔍 Action Input: ' + react_output.action_input, fg='green')}")

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
                "thought": react_output.thought,
                "action": react_output.action,
                "action_input": react_output.action_input,
                "result": action_result,
            }
            actions_taken.append(action_record)

            # Provide feedback for failed searches
            if (
                react_output.action.lower() == "search"
                and action_result
                and not action_result.get("success", True)
            ):
                logger.warning(
                    f"❌ Search failed: {action_result.get('error', 'Unknown error')}"
                )
                if action_result.get("broader_query"):
                    logger.warning(
                        f"💡 Suggestion: Try a broader topic or different keywords"
                    )

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

    def _get_memory_context(self, goal: str, previous_actions: str) -> str:
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
        relevant_findings = self.memory.get_research_findings(goal)
        if relevant_findings:
            context_parts.append("Relevant research findings:")
            for finding in relevant_findings[:2]:  # Limit to 2 findings
                context_parts.append(
                    f"- {finding['finding'].get('answer', 'Finding available')[:100]}..."
                )

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
            metadata = {"num_results": num_results, "action": "search"}

            # Add broader search information if available
            if result.get("broader_query"):
                metadata["broader_query"] = result["broader_query"]
                metadata["original_query"] = action_input

            if result.get("note"):
                metadata["note"] = result["note"]

            self.memory.add_search_result(
                query=action_input, results=results_dict, metadata=metadata
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

        elif action == "research":
            # Store research findings
            self.memory.add_research_finding(
                topic=action_input,
                finding={
                    "answer": result.get("answer", ""),
                    "sources": result.get("sources", []),
                    "search_query": result.get("search_query", ""),
                },
            )

            # Store sources from research
            for source in result.get("sources", []):
                if isinstance(source, dict) and source.get("url"):
                    self.memory.add_source(
                        url=source["url"],
                        source_info={
                            "title": source.get("title", ""),
                            "content": source.get("content", "")[:200],
                            "research_topic": action_input,
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

        elif action == "analyze":
            # Store analysis insights
            self.memory.add_insight(
                insight=result.get("key_insights", ""), category="analysis"
            )

            # Store analysis context
            self.memory.add_context(
                context=f"Analysis of: {action_input[:100]}...", relevance_score=0.8
            )

    def _execute_action(self, action: str, action_input: str) -> Dict[str, Any]:
        """Execute the specified action with given input."""

        action = action.lower().strip()

        try:
            if action == "search":
                return self._perform_search(action_input)
            elif action == "research":
                return self._perform_research(action_input)
            elif action == "fact_check":
                return self._perform_fact_check(action_input)
            elif action == "analyze":
                return self._perform_analysis(action_input)
            elif action == "finish":
                return {"action": "finish", "result": action_input, "success": True}
            else:
                return {
                    "action": action,
                    "error": f"Unknown action: {action}",
                    "success": False,
                }
        except Exception as e:
            return {
                "action": action,
                "error": f"Error executing action: {str(e)}",
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
            if not results:
                # Try with a broader search
                broader_query = self._broaden_search_query(search_query)
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
                else:
                    return {
                        "action": "search",
                        "query": search_query,
                        "broader_query": broader_query,
                        "results": [],
                        "num_results": 0,
                        "success": False,
                        "error": f"No results found for '{search_query}' or broader query '{broader_query}'. Consider using a more general topic or different keywords.",
                    }

            return {
                "action": "search",
                "query": search_query,
                "results": results,
                "num_results": len(results),
                "success": True,
            }
        except Exception as e:
            return {"action": "search", "error": str(e), "success": False}

    def _broaden_search_query(self, query: str) -> str:
        """Broaden a search query to get more results."""
        # Remove specific terms that might be too narrow
        narrow_terms = [
            "latest",
            "2024",
            "2023",
            "recent",
            "newest",
            "specific",
            "exact",
            "precise",
            "detailed",
            "comprehensive",
            "complete",
        ]

        # Remove very specific technical terms that might not have many results
        technical_terms = [
            "implementation",
            "architecture",
            "framework",
            "protocol",
            "algorithm",
            "methodology",
            "paradigm",
        ]

        broadened = query.lower()

        # Remove narrow terms
        for term in narrow_terms:
            broadened = broadened.replace(term, "")

        # Remove technical terms if the query is very specific
        if len(query.split()) > 3:
            for term in technical_terms:
                broadened = broadened.replace(term, "")

        # Clean up extra spaces
        broadened = " ".join(broadened.split())

        # If we removed too much, add some general terms
        if len(broadened.split()) < 2:
            broadened = f"{broadened} overview guide"

        return broadened

    def _perform_research(self, question: str) -> Dict[str, Any]:
        """Perform deep research on a question."""
        try:
            # Parse question if it's JSON-like
            if question.startswith("{"):
                question_data = json.loads(question)
                research_question = question_data.get("question", question)
                num_sources = question_data.get("num_sources", 5)
            else:
                research_question = question
                num_sources = 5

            result = self.research_assistant.research_question(
                research_question, num_sources=num_sources
            )

            return {
                "action": "research",
                "question": research_question,
                "answer": result["answer"],
                "sources": result["sources"],
                "search_query": result["search_query"],
                "success": True,
            }
        except Exception as e:
            return {"action": "research", "error": str(e), "success": False}

    def _perform_fact_check(self, claim: str) -> Dict[str, Any]:
        """Fact-check a claim."""
        try:
            result = self.research_assistant.verify_fact(claim, num_sources=3)

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
        for action in actions[
            -3:
        ]:  # Only show last 3 actions to avoid context overflow
            formatted.append(
                f"Action {action['iteration']}: {action['action']} - "
                f"Input: {action['action_input'][:100]}... - "
                f"Success: {action['result'].get('success', 'Unknown')}"
            )

        return "\n".join(formatted)


class EnhancedReACTSignature(dspy.Signature):
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

    reasoning: str = dspy.OutputField(
        desc="Step-by-step reasoning about what information is needed"
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

    def __init__(self, brave_search: OptimizedBraveSearch, memory_size: int = 1500):
        super().__init__(brave_search, memory_size=memory_size)
        self.enhanced_react = dspy.ChainOfThought(EnhancedReACTSignature)

    def generate_article_with_research(
        self, topic: str, initial_outline: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate an article with comprehensive research using ReACT approach.
        """
        logger.info(f"Starting ReACT-enhanced article generation for: {topic}")

        # Phase 1: Enhanced reasoning about research needs
        outline_str = (
            json.dumps(initial_outline)
            if initial_outline
            else "No initial outline provided"
        )

        # Get memory context for the topic
        memory_context = self._get_memory_context(topic, "")

        enhanced_reasoning = self.enhanced_react(
            topic=topic,
            current_outline=outline_str,
            research_gaps="Initial research needed for comprehensive article",
            available_tools=self.tools_description,
            memory_context=memory_context,
        )

        logger.info(f"\nEnhanced Reasoning:")
        logger.info(f"Strategy:\n {enhanced_reasoning.research_strategy}")
        logger.info(f"Action Plan:\n {enhanced_reasoning.action_plan}")

        # Phase 2: Execute research plan using ReACT
        research_goal = f"""
        Research and gather comprehensive, current information about '{topic}' to create a well-informed article.
        
        Research Strategy: {enhanced_reasoning.research_strategy}
        Action Plan: {enhanced_reasoning.action_plan}
        
        Goal: Gather enough information to write authoritative sections on the topic with current facts and multiple perspectives.
        """

        react_results = self.forward(research_goal, max_iterations=8)

        # Phase 3: Synthesize research into article structure
        synthesis_goal = f"""
        Synthesize all gathered research into a comprehensive article outline and key content points for '{topic}'.
        Use the research findings to create detailed, factual content.
        """

        synthesis_results = self.forward(synthesis_goal, max_iterations=3)

        return {
            "topic": topic,
            "enhanced_reasoning": enhanced_reasoning,
            "research_phase": react_results,
            "synthesis_phase": synthesis_results,
            "total_actions": len(react_results["actions_taken"])
            + len(synthesis_results["actions_taken"]),
            "memory_summary": self.memory.get_memory_summary(),
        }

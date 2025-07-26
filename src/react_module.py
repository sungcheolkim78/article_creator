import dspy
from typing import List, Dict, Any, Optional
from bravesearch import OptimizedBraveSearch
from research_assistant import ResearchAssistant
import json


class ReACTSignature(dspy.Signature):
    """ReACT signature for reasoning and acting on article generation tasks."""
    
    goal: str = dspy.InputField(desc="The goal or question to accomplish")
    available_tools: str = dspy.InputField(desc="List of available tools and their capabilities")
    previous_actions: str = dspy.InputField(desc="Previous actions taken and their results")
    
    thought: str = dspy.OutputField(desc="Reasoning about what to do next")
    action: str = dspy.OutputField(desc="The action to take (search, analyze, synthesize, or finish)")
    action_input: str = dspy.OutputField(desc="Input parameters for the action")


class ReACTAgent(dspy.Module):
    """
    ReACT (Reasoning and Acting) agent for enhanced article generation.
    
    This agent can reason about what information is needed and take actions
    to gather that information using web search and research tools.
    """
    
    def __init__(self, brave_search: OptimizedBraveSearch):
        super().__init__()
        self.search_tool = brave_search
        self.research_assistant = ResearchAssistant(brave_search)
        self.react_step = dspy.ChainOfThought(ReACTSignature)
        
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
        
    def forward(self, goal: str, max_iterations: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute ReACT loop to accomplish the given goal.
        """
        max_iter = max_iterations or self.max_iterations
        actions_taken = []
        gathered_info = []
        
        for iteration in range(max_iter):
            # Format previous actions for context
            previous_actions_str = self._format_previous_actions(actions_taken)
            
            # Get next action from ReACT reasoning
            react_output = self.react_step(
                goal=goal,
                available_tools=self.tools_description,
                previous_actions=previous_actions_str
            )
            
            print(f"\nIteration {iteration + 1}")
            print(f"Thought: {react_output.thought}")
            print(f"Action: {react_output.action}")
            print(f"Action Input: {react_output.action_input}")
            
            # Execute the action
            action_result = self._execute_action(
                react_output.action,
                react_output.action_input
            )
            
            # Record the action
            action_record = {
                "iteration": iteration + 1,
                "thought": react_output.thought,
                "action": react_output.action,
                "action_input": react_output.action_input,
                "result": action_result
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
            "completed": react_output.action.lower() == "finish"
        }
    
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
                    "success": False
                }
        except Exception as e:
            return {
                "action": action,
                "error": f"Error executing action: {str(e)}",
                "success": False
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
            
            return {
                "action": "search",
                "query": search_query,
                "results": results,
                "num_results": len(results),
                "success": True
            }
        except Exception as e:
            return {
                "action": "search",
                "error": str(e),
                "success": False
            }
    
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
                research_question, 
                num_sources=num_sources
            )
            
            return {
                "action": "research",
                "question": research_question,
                "answer": result["answer"],
                "sources": result["sources"],
                "search_query": result["search_query"],
                "success": True
            }
        except Exception as e:
            return {
                "action": "research",
                "error": str(e),
                "success": False
            }
    
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
                "success": True
            }
        except Exception as e:
            return {
                "action": "fact_check",
                "error": str(e),
                "success": False
            }
    
    def _perform_analysis(self, content: str) -> Dict[str, Any]:
        """Analyze and synthesize information."""
        try:
            # Use DSPy to analyze the content
            analyzer = dspy.ChainOfThought("content -> analysis, key_insights, recommendations")
            result = analyzer(content=content)
            
            return {
                "action": "analyze",
                "content": content,
                "analysis": result.analysis,
                "key_insights": result.key_insights,
                "recommendations": result.recommendations,
                "success": True
            }
        except Exception as e:
            return {
                "action": "analyze",
                "error": str(e),
                "success": False
            }
    
    def _format_previous_actions(self, actions: List[Dict[str, Any]]) -> str:
        """Format previous actions for context."""
        if not actions:
            return "No previous actions taken."
        
        formatted = []
        for action in actions[-3:]:  # Only show last 3 actions to avoid context overflow
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
    research_gaps: str = dspy.InputField(desc="Identified gaps in current research or information")
    available_tools: str = dspy.InputField(desc="Available research and analysis tools")
    
    reasoning: str = dspy.OutputField(desc="Step-by-step reasoning about what information is needed")
    research_strategy: str = dspy.OutputField(desc="Strategy for gathering the needed information")
    action_plan: str = dspy.OutputField(desc="Specific actions to take with their parameters")


class ArticleReACTAgent(ReACTAgent):
    """
    Specialized ReACT agent for article generation with enhanced reasoning capabilities.
    """
    
    def __init__(self, brave_search: OptimizedBraveSearch):
        super().__init__(brave_search)
        self.enhanced_react = dspy.ChainOfThought(EnhancedReACTSignature)
    
    def generate_article_with_research(
        self, 
        topic: str, 
        initial_outline: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Generate an article with comprehensive research using ReACT approach.
        """
        print(f"Starting ReACT-enhanced article generation for: {topic}")
        
        # Phase 1: Enhanced reasoning about research needs
        outline_str = json.dumps(initial_outline) if initial_outline else "No initial outline provided"
        
        enhanced_reasoning = self.enhanced_react(
            topic=topic,
            current_outline=outline_str,
            research_gaps="Initial research needed for comprehensive article",
            available_tools=self.tools_description
        )
        
        print(f"\nEnhanced Reasoning:")
        print(f"Strategy: {enhanced_reasoning.research_strategy}")
        print(f"Action Plan: {enhanced_reasoning.action_plan}")
        
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
            "total_actions": len(react_results["actions_taken"]) + len(synthesis_results["actions_taken"])
        }
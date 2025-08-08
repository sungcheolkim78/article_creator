import dspy
from typing import Dict, Any, List


class ResearchTool(dspy.Module):
    """
    Research tool that uses search tool for information gathering
    """

    def __init__(self, search_tool):
        super().__init__()
        self.search_tool = search_tool

        # Define DSPy signatures for different research tasks
        self.query_generator = dspy.ChainOfThought("question -> search_query")
        self.synthesizer = dspy.ChainOfThought("question, search_results -> comprehensive_answer")
        self.fact_checker = dspy.ChainOfThought("claim, search_results -> verification_status, explanation")

    def research_question(self, question: str, num_sources: int = 5) -> Dict[str, Any]:
        """Research a question using web search and synthesis."""
        # Generate optimized search query
        search_query = self.query_generator(question=question).search_query

        # Perform search
        search_results = self.search_tool.optimized_search(search_query, k=num_sources)

        # Format results for synthesis
        formatted_results = "\n\n".join(
            [
                f"Source {i + 1}: {result.title}\n{result.snippet}\n{extra_snippets}\nURL: {result.url}"
                if (extra_snippets := "\n".join(result.extra_snippets))
                else f"Source {i + 1}: {result.title}\n{result.snippet}\nURL: {result.url}"
                for i, result in enumerate(search_results)
            ]
        )

        # Synthesize comprehensive answer
        synthesis = self.synthesizer(
            question=question, search_results=formatted_results
        )

        return {
            "question": question,
            "search_query": search_query,
            "sources": formatted_results,
            "answer": synthesis.comprehensive_answer,
            "num_sources": len(search_results),
        }

    def verify_fact(self, claim: str, num_sources: int = 3) -> Dict[str, Any]:
        """Fact-check a claim using web search."""
        # Generate search query for fact checking
        search_query = self.query_generator(question=f"verify: {claim}").search_query

        # Search for evidence
        search_results = self.search_tool.search(search_query, k=num_sources)

        # Format results
        formatted_results = "\n\n".join(
            [
                f"Source {i + 1}: {result.title}\n{result.snippet}"
                for i, result in enumerate(search_results)
            ]
        )

        # Verify claim
        verification = self.fact_checker(claim=claim, search_results=formatted_results)

        return {
            "claim": claim,
            "search_query": search_query,
            "verification_status": verification.verification_status,
            "explanation": verification.explanation,
            "sources": formatted_results,
        }

    def multi_perspective_research(
        self, topic: str, perspectives: List[str]
    ) -> Dict[str, Any]:
        """Research a topic from multiple perspectives."""
        results = {}

        for perspective in perspectives:
            question = f"What is the {perspective} perspective on {topic}?"
            results[perspective] = self.research_question(question, num_sources=3)

        return {
            "topic": topic,
            "perspectives": results,
            "summary": self._synthesize_perspectives(topic, results),
        }

    def _synthesize_perspectives(self, topic: str, perspective_results: Dict) -> str:
        """Synthesize multiple perspectives into a balanced summary."""
        all_findings = []
        for perspective, result in perspective_results.items():
            all_findings.append(f"{perspective} perspective: {result['answer']}")

        combined_findings = "\n\n".join(all_findings)

        synthesis = self.synthesizer(
            question=f"Provide a balanced summary of different perspectives on {topic}",
            search_results=combined_findings,
        )

        return synthesis.comprehensive_answer

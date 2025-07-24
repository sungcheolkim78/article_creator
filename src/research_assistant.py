import dspy
import os
import click
from typing import Dict, Any, List
from bravesearch import BraveSearchTool, OptimizedBraveSearch
from dotenv import load_dotenv
from utils import llm_setup, Translator

load_dotenv()


class ResearchAssistant(dspy.Module):
    """
    Research assistant that uses Brave Search for information gathering
    """

    def __init__(self, brave_search: OptimizedBraveSearch):
        super().__init__()
        self.search = brave_search

        # Define DSPy signatures for different research tasks
        self.query_generator = dspy.ChainOfThought("question -> search_query")
        self.synthesizer = dspy.ChainOfThought(
            "question, search_results -> comprehensive_answer"
        )
        self.fact_checker = dspy.ChainOfThought(
            "claim, search_results -> verification_status, explanation"
        )
        self.translate = dspy.Predict(Translator)

    def research_question(self, question: str, num_sources: int = 5) -> Dict[str, Any]:
        """
        Research a question using web search and synthesis
        """
        # Generate optimized search query
        search_query = self.query_generator(question=question).search_query

        # Perform search
        search_results = self.search.optimized_search(search_query, k=num_sources)

        # Format results for synthesis
        formatted_results = "\n\n".join(
            [
                f"Source {i + 1}: {result.title}\n{result.snippet}\nURL: {result.url}"
                for i, result in enumerate(search_results)
            ]
        )

        # Synthesize comprehensive answer
        synthesis = self.synthesizer(
            question=question, search_results=formatted_results
        )

        answer = self.translate(text=synthesis.comprehensive_answer, language="Korean")

        return {
            "question": question,
            "search_query": search_query,
            "sources": search_results,
            "answer": answer.translated_content,
            "num_sources": len(search_results),
        }

    def verify_fact(self, claim: str, num_sources: int = 3) -> Dict[str, Any]:
        """
        Fact-check a claim using web search
        """
        # Generate search query for fact checking
        search_query = self.query_generator(question=f"verify: {claim}").search_query

        # Search for evidence
        search_results = self.search.search(search_query, k=num_sources)

        # Format results
        formatted_results = "\n\n".join(
            [
                f"Source {i + 1}: {result.title}\n{result.snippet}"
                for i, result in enumerate(search_results)
            ]
        )

        # Verify claim
        verification = self.fact_checker(claim=claim, search_results=formatted_results)

        answer = self.translate(text=verification.explanation, language="Korean")

        return {
            "claim": claim,
            "search_query": search_query,
            "verification_status": verification.verification_status,
            "explanation": answer.translated_content,
            "sources": search_results,
        }

    def multi_perspective_research(
        self, topic: str, perspectives: List[str]
    ) -> Dict[str, Any]:
        """
        Research a topic from multiple perspectives
        """
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
        """
        Synthesize multiple perspectives into a balanced summary
        """
        all_findings = []
        for perspective, result in perspective_results.items():
            all_findings.append(f"{perspective} perspective: {result['answer']}")

        combined_findings = "\n\n".join(all_findings)

        synthesis = self.synthesizer(
            question=f"Provide a balanced summary of different perspectives on {topic}",
            search_results=combined_findings,
        )
        answer = self.translate(text=synthesis.comprehensive_answer, language="Korean")

        return answer.translated_content


def do_research(assistant, question: str, num_sources: int = 5):
    result = assistant.research_question(question, num_sources=num_sources)

    print(f"Question: {result['question']}")
    print(f"Search Query Used: {result['search_query']}")
    print(f"Number of Sources: {result['num_sources']}")
    print(f"\nAnswer: {result['answer']}")

    print("\nSources:")
    for i, source in enumerate(result["sources"], 1):
        print(f"{i}. {source.title}")
        print(f"   URL: {source.url}")
        print(f"   Snippet: {source.snippet[:100]}...")
        print()


def do_fact_check(assistant, claim: str, num_sources: int = 3):
    fact_check = assistant.verify_fact(claim, num_sources=num_sources)

    print(f"Claim: {fact_check['claim']}")
    print(f"Verification Status: {fact_check['verification_status']}")
    print(f"Explanation: {fact_check['explanation']}")

    print("\nSources:")
    for i, source in enumerate(fact_check["sources"], 1):
        print(f"{i}. {source.title}")
        print(f"   URL: {source.url}")
        print(f"   Snippet: {source.snippet[:100]}...")
        print()


def do_multi_perspective_research(
    assistant, topic: str, perspectives: List[str], num_sources: int = 3
):
    multi_research = assistant.multi_perspective_research(
        topic, perspectives, num_sources=num_sources
    )

    print(f"Topic: {multi_research['topic']}")
    print(f"Summary: {multi_research['summary']}")

    for perspective, result in multi_research["perspectives"].items():
        print(f"\n{perspective.upper()} PERSPECTIVE:")
        print(f"Answer: {result['answer'][:200]}...")


@click.command()
@click.option("--question", type=str, help="The question to research", default="What are the latest developments in quantum computing in 2024?")
@click.option("--claim", type=str, help="The claim to fact-check", default="The James Webb Space Telescope discovered water on an exoplanet in 2024")
@click.option("--topic", type=str, help="The topic to research from multiple perspectives", default="artificial intelligence regulation")
@click.option("--perspectives", type=str, help="The perspectives to research from", default="industry, academic, policy maker, privacy advocate")
@click.option("--num_sources", type=int, default=5, help="The number of sources to use")
# Example usage and configuration
def main(question, claim, topic, perspectives, num_sources):
    # Initialize DSPy with your preferred LM
    # Example with OpenAI (replace with your preferred model)
    llm_setup("openai/gpt-4o-mini")

    # Initialize Brave Search tool
    brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    # search_tool = BraveSearchTool(api_key=brave_api_key, k=5, source="web")
    search_tool = OptimizedBraveSearch(api_key=brave_api_key, k=5, source="web")

    # Create research assistant
    assistant = ResearchAssistant(brave_search=search_tool)

    # Example 1: Research a question
    do_research(assistant, question, num_sources=num_sources)

    # Example 2: Fact checking
    # do_fact_check(assistant, claim, num_sources=num_sources)

    # Example 3: Multi-perspective research
    perspectives = perspectives.split(",")
    # do_multi_perspective_research(assistant, topic, perspectives, num_sources=num_sources)


if __name__ == "__main__":
    main()

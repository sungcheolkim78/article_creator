from pathlib import Path
import dspy
import click
import os
import json
from dotenv import load_dotenv
from utils import Translator, llm_setup
from bravesearch import OptimizedBraveSearch
from react_module import ArticleReACTAgent, ReACTAgent
from research_assistant import ResearchAssistant
from typing import Dict, Any, List, Optional
import logging

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s|%(name)s|%(levelname)s|%(message)s')
logger = logging.getLogger('enhanced_article_creator')

logging.getLogger('LiteLLM').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)


load_dotenv()


class ResearchEnhancedOutline(dspy.Signature):
    """Create a comprehensive outline for an article with research-backed structure."""

    topic: str = dspy.InputField()
    research_findings: str = dspy.InputField(desc="Key research findings and current information")
    target_audience: str = dspy.InputField(default="general audience")
    
    title: str = dspy.OutputField()
    sections: list[str] = dspy.OutputField()
    section_subheadings: dict[str, list[str]] = dspy.OutputField(
        desc="mapping from section headings to subheadings"
    )
    key_sources: list[str] = dspy.OutputField(desc="important sources to reference")


class ResearchBasedSection(dspy.Signature):
    """Draft a section of an article using research findings and web search results."""

    topic: str = dspy.InputField()
    section_heading: str = dspy.InputField()
    section_subheadings: list[str] = dspy.InputField()
    research_content: str = dspy.InputField(desc="relevant research findings for this section")
    sources: str = dspy.InputField(desc="credible sources and citations")
    
    content: str = dspy.OutputField(desc="markdown-formatted section with proper citations")


class FactCheckSignature(dspy.Signature):
    """Fact-check and verify claims in article content."""
    
    content: str = dspy.InputField(desc="article content to fact-check")
    sources: str = dspy.InputField(desc="available sources for verification")
    
    verified_content: str = dspy.OutputField(desc="fact-checked content with corrections if needed")
    fact_check_notes: str = dspy.OutputField(desc="notes about fact-checking process and findings")


class EnhancedDraftArticle(dspy.Module):
    """Enhanced article generator with web search integration and ReACT reasoning."""

    def __init__(self, brave_search: OptimizedBraveSearch):
        super().__init__()
        self.search_tool = brave_search
        self.research_assistant = ResearchAssistant(brave_search)
        self.react_agent = ArticleReACTAgent(brave_search)
        
        # DSPy modules
        self.build_outline = dspy.ChainOfThought(ResearchEnhancedOutline)
        self.draft_section = dspy.ChainOfThought(ResearchBasedSection)
        self.fact_checker = dspy.ChainOfThought(FactCheckSignature)
        self.translate = dspy.Predict(Translator)

    def forward(self, topic: str, language: str = "Korean", use_react: bool = True) -> Dict[str, Any]:
        """
        Generate a comprehensive article with web search and ReACT integration.
        """
        logger.info(f"Generating enhanced article for topic: {topic}")
        logger.info(f"Using ReACT agent: {use_react}")

        # Phase 1: Research and information gathering
        if use_react:
            react_results = self.react_agent.generate_article_with_research(topic)
            research_summary = self._extract_research_summary(react_results)
        else:
            # Fallback to direct research
            research_summary = self._conduct_basic_research(topic)

        logger.info(f"💊 Research completed. Summary length: {len(research_summary)} characters")

        # Phase 2: Create research-enhanced outline
        outline = self.build_outline(
            topic=topic,
            research_findings=research_summary,
            target_audience="ML/AI/data scientists"
        )

        logger.info(f"🔍 Outline created with {len(outline.section_subheadings)} sections")

        # Phase 3: Generate sections with research integration
        sections_en = []
        sections_other = []

        for heading, subheadings in outline.section_subheadings.items():
            logger.info(f"Generating section: {heading}")
            
            # Get specific research for this section
            section_research = self._get_section_research(topic, heading, research_summary)
            section_sources = self._get_section_sources(heading, outline.key_sources)

            # Generate section content
            section = self.draft_section(
                topic=outline.title,
                section_heading=f"## {heading}",
                section_subheadings=[f"### {sub}" for sub in subheadings],
                research_content=section_research,
                sources=section_sources
            )

            # Fact-check the section
            fact_checked = self.fact_checker(
                content=section.content,
                sources=section_sources
            )

            section_en = fact_checked.verified_content
            
            # Translate if needed
            if language.lower() != "english":
                section_other = self.translate(text=section_en, language=language)
                sections_other.append(section_other.translated_content)
            else:
                sections_other.append(section_en)

            sections_en.append(section_en)

        return dspy.Prediction(
            title=outline.title,
            sections_en=sections_en,
            sections_other=sections_other,
            research_summary=research_summary,
            key_sources=outline.key_sources,
            react_results=react_results if use_react else None
        )

    def _extract_research_summary(self, react_results: Dict[str, Any]) -> str:
        """Extract and summarize research findings from ReACT results."""
        research_findings = []
        
        # Extract from research phase
        if "research_phase" in react_results:
            for info in react_results["research_phase"].get("gathered_information", []):
                if info.get("action") == "research" and "answer" in info:
                    research_findings.append(f"Research: {info['answer']}")
                elif info.get("action") == "search" and "results" in info:
                    # Summarize search results
                    search_summary = self._summarize_search_results(info["results"])
                    research_findings.append(f"Search findings: {search_summary}")

        # Extract from synthesis phase
        if "synthesis_phase" in react_results:
            for info in react_results["synthesis_phase"].get("gathered_information", []):
                if info.get("action") == "analyze" and "key_insights" in info:
                    research_findings.append(f"Analysis: {info['key_insights']}")

        return "\n\n".join(research_findings) if research_findings else "Limited research findings available."

    def _summarize_search_results(self, search_results: List) -> str:
        """Summarize search results into key points."""
        if not search_results:
            return "No search results available."
        
        summaries = []
        for result in search_results[:3]:  # Top 3 results
            if hasattr(result, 'snippet') and hasattr(result, 'title'):
                summaries.append(f"{result.title}: {result.snippet}")
            elif isinstance(result, dict):
                title = result.get('title', 'Unknown')
                snippet = result.get('snippet', 'No description')
                summaries.append(f"{title}: {snippet}")
        
        return " | ".join(summaries)

    def _conduct_basic_research(self, topic: str) -> str:
        """Conduct basic research without ReACT agent."""
        try:
            # Perform multiple targeted searches
            search_queries = [
                f"{topic} latest developments 2024-2025",
                f"{topic} current trends analysis",
                f"{topic} expert opinions research"
            ]
            
            all_findings = []
            for query in search_queries:
                results = self.search_tool.optimized_search(query, k=3)
                summary = self._summarize_search_results(results)
                all_findings.append(f"Query '{query}': {summary}")
            
            return "\n\n".join(all_findings)
        except Exception as e:
            return f"Basic research encountered error: {str(e)}"

    def _get_section_research(self, topic: str, section_heading: str, research_summary: str) -> str:
        """Extract relevant research for a specific section."""
        # Use DSPy to filter relevant research for the section
        filter_signature = dspy.ChainOfThought(
            "topic, section_heading, full_research -> relevant_research"
        )
        
        try:
            filtered = filter_signature(
                topic=topic,
                section_heading=section_heading,
                full_research=research_summary
            )
            return filtered.relevant_research
        except Exception:
            # Fallback: return a portion of the research summary
            return research_summary[:1500] + "..." if len(research_summary) > 1500 else research_summary

    def _get_section_sources(self, section_heading: str, key_sources: List[str]) -> str:
        """Get relevant sources for a section."""
        if not key_sources:
            return "Additional research and credible sources recommended."
        
        # Simple relevance matching (can be enhanced with semantic similarity)
        relevant_sources = []
        heading_lower = section_heading.lower()
        
        for source in key_sources:
            if any(word in source.lower() for word in heading_lower.split()):
                relevant_sources.append(source)
        
        return "\n".join(relevant_sources) if relevant_sources else "\n".join(key_sources[:3])


class WebSearchArticleCreator(dspy.Module):
    """Simplified article creator focusing on web search integration."""
    
    def __init__(self, brave_search: OptimizedBraveSearch):
        super().__init__()
        self.search_tool = brave_search
        self.research_assistant = ResearchAssistant(brave_search)
        
        # Simpler pipeline for focused web search integration
        self.outline_generator = dspy.ChainOfThought("topic, current_info -> title, sections, key_points")
        self.content_generator = dspy.ChainOfThought("topic, section, research_data -> detailed_content")
        self.translate = dspy.Predict(Translator)
    
    def forward(self, topic: str, language: str = "Korean") -> Dict[str, Any]:
        """Generate article with focused web search integration."""
        logger.info(f"Web search-enhanced article generation for: {topic}")
        
        # Step 1: Research current information
        research_result = self.research_assistant.research_question(
            f"What are the latest developments and key information about {topic}?",
            num_sources=8
        )
        
        # Step 2: Generate outline based on research
        outline = self.outline_generator(
            topic=topic,
            current_info=research_result["answer"]
        )
        
        # Step 3: Generate content for each section
        sections_en = []
        sections_other = []
        
        for section in outline.sections:
            # Get specific research for this section
            section_research = self.research_assistant.research_question(
                f"Detailed information about {section} in the context of {topic}",
                num_sources=5
            )
            
            # Generate section content
            content = self.content_generator(
                topic=topic,
                section=section,
                research_data=section_research["answer"]
            )
            
            section_en = content.detailed_content
            sections_en.append(section_en)
            
            # Translate if needed
            if language.lower() != "english":
                translated = self.translate(text=section_en, language=language)
                sections_other.append(translated.translated_content)
            else:
                sections_other.append(section_en)
        
        return dspy.Prediction(
            title=outline.title,
            sections_en=sections_en,
            sections_other=sections_other,
            research_sources=research_result["sources"],
            key_points=outline.key_points
        )


@click.command()
@click.option("--topic", type=str, default="The impact of AI on jobs in 2024")
@click.option("--language", type=str, default="Korean")
@click.option("--output_dir", type=str, default="data/articles")
@click.option("--mode", type=click.Choice(["enhanced", "websearch", "react"]), default="enhanced", 
              help="Article generation mode")
@click.option("--use_react", is_flag=True, default=True, help="Use ReACT agent for research")
def main(topic, language, output_dir, mode, use_react):
    """Enhanced article creator with web search and ReACT integration."""
    
    # Setup
    llm_setup("openai/gpt-4o-mini")
    
    # Initialize Brave Search
    brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
    if not brave_api_key:
        logger.warning("Warning: BRAVE_SEARCH_API_KEY not found. Using limited functionality.")
        logger.warning("Please set BRAVE_SEARCH_API_KEY environment variable for full web search capabilities.")
        return
    
    search_tool = OptimizedBraveSearch(api_key=brave_api_key, k=5, source="web")
    
    # Choose article generator based on mode
    if mode == "enhanced":
        article_generator = EnhancedDraftArticle(search_tool)
        prediction = article_generator.forward(topic=topic, language=language, use_react=use_react)
    elif mode == "websearch":
        article_generator = WebSearchArticleCreator(search_tool)
        prediction = article_generator.forward(topic=topic, language=language)
    elif mode == "react":
        react_agent = ArticleReACTAgent(search_tool)
        react_results = react_agent.generate_article_with_research(topic)
        logger.info("ReACT research completed. Use 'enhanced' mode to generate full article.")
        logger.info(f"Research summary: {react_results}")
        return

    # Save articles
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    topic_slug = topic.lower().replace(" ", "-").replace(",", "")
    lang_slug = language[:3].lower()

    # Save translated version
    with open(output_dir / f"{topic_slug}-{lang_slug}.md", "w", encoding="utf-8") as f:
        f.write(f"# {prediction.title}\n\n")
        for section in prediction.sections_other:
            f.write(section)
            f.write("\n\n")
        
        # Add sources if available
        if hasattr(prediction, 'key_sources') and prediction.key_sources:
            f.write("## Sources\n\n")
            for source in prediction.key_sources:
                f.write(f"- {source}\n")

    # Save English version
    with open(output_dir / f"{topic_slug}-en.md", "w", encoding="utf-8") as f:
        f.write(f"# {prediction.title}\n\n")
        for section in prediction.sections_en:
            f.write(section)
            f.write("\n\n")
        
        # Add sources if available
        if hasattr(prediction, 'key_sources') and prediction.key_sources:
            f.write("## Sources\n\n")
            for source in prediction.key_sources:
                f.write(f"- {source}\n")

    # Save research summary if available
    if hasattr(prediction, 'research_summary') and prediction.research_summary:
        with open(output_dir / f"{topic_slug}-research.md", "w", encoding="utf-8") as f:
            f.write(f"# Research Summary: {prediction.title}\n\n")
            f.write(prediction.research_summary)

    logger.info(f"Enhanced article saved to {output_dir}")
    logger.info(f"Files created:")
    logger.info(f"  - {topic_slug}-{lang_slug}.md (translated)")
    logger.info(f"  - {topic_slug}-en.md (English)")
    if hasattr(prediction, 'research_summary'):
        logger.info(f"  - {topic_slug}-research.md (research summary)")


if __name__ == "__main__":
    main()
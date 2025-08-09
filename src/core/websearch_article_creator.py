import dspy
from core.research_tool import ResearchTool
from utils.signatures import Translator
import logging
from typing import Dict, Any

logger = logging.getLogger("websearch_article_creator")


class WebSearchArticleCreator(dspy.Module):
    """Simplified article creator focusing on web search integration."""

    def __init__(self, search_tool):
        super().__init__()
        self.research_tool = ResearchTool(search_tool)

        # Simpler pipeline for focused web search integration
        self.outline_generator = dspy.ChainOfThought(
            "topic, current_info -> title, sections, key_points"
        )
        self.content_generator = dspy.ChainOfThought(
            "topic, section, research_data -> detailed_content"
        )
        self.translate = dspy.Predict(Translator)

    def forward(self, topic: str, language: str = "Korean") -> Dict[str, Any]:
        """Generate article with focused web search integration."""
        logger.info(f"Web search-enhanced article generation for: {topic}")

        # Step 1: Research current information
        research_result = self.research_tool.research_question(
            f"What are the latest developments and key information about {topic}?",
            num_sources=8,
        )

        # Step 2: Generate outline based on research
        outline = self.outline_generator(
            topic=topic, current_info=research_result["answer"]
        )

        # Step 3: Generate content for each section
        sections_en = []
        sections_translated = []

        for section in outline.sections:
            # Get specific research for this section
            section_research = self.research_tool.research_question(
                f"Detailed information about {section} in the context of {topic}",
                num_sources=5,
            )

            # Generate section content
            content = self.content_generator(
                topic=topic, section=section, research_data=section_research["answer"]
            )

            section_en = content.detailed_content
            sections_en.append(section_en)

            # Translate if needed
            if language.lower() != "english":
                translated = self.translate(text=section_en, language=language)
                sections_translated.append(translated.translated_content)
            else:
                sections_translated.append(section_en)

        return dspy.Prediction(
            title=outline.title,
            sections_en=sections_en,
            sections_translated=sections_translated,
            research_sources=research_result["sources"],
            key_points=outline.key_points,
        )

import dspy
import json
from agents.planner import planner_tool
from agents.researcher import ArticleReACTResearcher
from utils.signatures import Translator
from typing import Any


class ArticleOutline(dspy.Signature):
    """Create a comprehensive outline for an article with research-backed structure."""

    topic: str = dspy.InputField()
    initial_outline: dict[str, Any] = dspy.InputField(
        desc="Initial outline for the article"
    )
    research_findings: str = dspy.InputField(
        desc="Key research findings and current information with sources and citations"
    )
    target_audience: str = dspy.InputField(default="general audience")

    title: str = dspy.OutputField()
    sections: list[str] = dspy.OutputField()
    section_subheadings: dict[str, list[str]] = dspy.OutputField(
        desc="mapping from section headings to subheadings"
    )


class ArticleSection(dspy.Signature):
    """Draft a section of an article using research findings and web search results."""

    topic: str = dspy.InputField()
    section_heading: str = dspy.InputField()
    section_subheadings: list[str] = dspy.InputField()
    research_content: str = dspy.InputField(
        desc="relevant research findings for this section"
    )

    content: str = dspy.OutputField(
        desc="markdown-formatted section with proper citations"
    )


class ArticleFactCheck(dspy.Signature):
    """write a content-rich fact-checked section with proper citations."""

    content: str = dspy.InputField(desc="article content to fact-check")
    sources: str = dspy.InputField(desc="available sources for verification")

    verified_content: str = dspy.OutputField(
        desc="fact-checked content with corrections if needed, add the proper citations"
    )
    key_sources: str = dspy.OutputField(desc="key sources for verification")


class FindContext(dspy.Signature):
    """Find the key information of a topic in the content. Avoid repeating the same information from previous content."""

    topic: str = dspy.InputField()
    content: str = dspy.InputField()
    previous_content: str = dspy.InputField()

    key_information: str = dspy.OutputField()


class ArticleWriter(dspy.Module):
    """Write an article using the outline and content and sources."""

    def __init__(self, audience: str = "DS/AI Scientist", verbose: bool = False):
        super().__init__()
        self.build_outline = dspy.ChainOfThought(ArticleOutline)
        self.draft_section = dspy.ChainOfThought(ArticleSection)
        self.fact_checker = dspy.ChainOfThought(ArticleFactCheck)
        self.translate = dspy.Predict(Translator)
        self.find_context = dspy.Predict(FindContext)

        self.audience = audience
        self.verbose = verbose

    def forward(self, topic: str, language: str = "Korean") -> dspy.Prediction:
        """Write an article using the outline and content and sources."""
        # Step 1: Plan the article
        print(f"ArticleWriter|Planning article...")
        output_planner = planner_tool(topic, verbose=self.verbose)

        # Step 2: Research the article
        print(f"ArticleWriter|Researching article...")
        researcher = ArticleReACTResearcher(
            output_planner.research_strategy,
            output_planner.action_plan,
            verbose=self.verbose,
        )
        output_researcher = researcher(
            topic=topic,
            outline=output_planner.outline,
            memory_content=output_planner.memory_context,
        )

        # Step 3: Generate the outline
        print(f"ArticleWriter|Generating outline...")
        outline = self.build_outline(
            topic=topic,
            initial_outline=output_researcher.final_outline,
            research_findings=output_researcher.final_content,
            target_audience=self.audience,
        )

        # Phase 3: Generate sections with research integration
        sections_en = []
        sections_translated = []
        print(
            f"ArticleWriter|Title: {outline.title} ({len(outline.sections)} sections)"
        )

        key_sources = []
        for heading, subheadings in outline.section_subheadings.items():
            print(f"ArticleWriter|Generating section: {heading}")

            section_content = self.find_context(
                topic=heading,
                content=output_researcher.final_content,
                previous_content=sections_en[-1] if sections_en else "",
            ).key_information

            # Generate section content
            section = self.draft_section(
                topic=outline.title,
                section_heading=f"## {heading}",
                section_subheadings=[f"### {sub}" for sub in subheadings],
                research_content=section_content,
            )

            # Fact-check the section
            fact_checked = self.fact_checker(
                content=section.content, sources=section_content
            )

            section_en = fact_checked.verified_content
            key_sources.append(fact_checked.key_sources)

            # Translate if needed
            if language.lower() != "english":
                section_translated = self.translate(text=section_en, language=language)
                sections_translated.append(section_translated.translated_content)
            else:
                sections_translated.append(section_en)

            sections_en.append(section_en)

        return dspy.Prediction(
            title=outline.title,
            sections_en=sections_en,
            sections_translated=sections_translated,
            research_summary=output_researcher.final_content,
            key_sources=key_sources,
        )

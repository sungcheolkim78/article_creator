import dspy
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
        desc="Key research findings and current information"
    )
    research_sources: str = dspy.InputField(
        desc="credible sources and citations"
    )
    target_audience: str = dspy.InputField(default="general audience")

    title: str = dspy.OutputField()
    sections: list[str] = dspy.OutputField()
    section_subheadings: dict[str, list[str]] = dspy.OutputField(
        desc="mapping from section headings to subheadings"
    )
    key_sources: list[str] = dspy.OutputField(desc="important sources to reference")


class ArticleSection(dspy.Signature):
    """Draft a section of an article using research findings and web search results."""

    topic: str = dspy.InputField()
    section_heading: str = dspy.InputField()
    section_subheadings: list[str] = dspy.InputField()
    research_content: str = dspy.InputField(
        desc="relevant research findings for this section"
    )
    sources: str = dspy.InputField(desc="credible sources and citations")

    content: str = dspy.OutputField(
        desc="markdown-formatted section with proper citations"
    )


class ArticleFactCheck(dspy.Signature):
    """Fact-check and verify claims in article content."""

    content: str = dspy.InputField(desc="article content to fact-check")
    sources: str = dspy.InputField(desc="available sources for verification")

    verified_content: str = dspy.OutputField(
        desc="fact-checked content with corrections if needed"
    )
    fact_check_notes: str = dspy.OutputField(
        desc="notes about fact-checking process and findings"
    )


class ArticleWriter(dspy.Module):
    """Write an article using the outline and content and sources."""

    def __init__(self, audience: str = "DS/AI Scientist", verbose: bool = False):
        super().__init__()
        self.build_outline = dspy.ChainOfThought(ArticleOutline)
        self.draft_section = dspy.ChainOfThought(ArticleSection)
        self.fact_checker = dspy.ChainOfThought(ArticleFactCheck)
        self.translate = dspy.Predict(Translator)

        self.audience = audience
        self.verbose = verbose

    def forward(self, topic: str, language: str = "Korean") -> dspy.Prediction:
        """Write an article using the outline and content and sources."""
        # Step 1: Plan the article
        output_planner = planner_tool(topic, verbose=False)

        # Step 2: Research the article
        researcher = ArticleReACTResearcher(
            output_planner.research_strategy,
            output_planner.action_plan,
            verbose=False,
        )
        output_researcher = researcher(
            topic=topic,
            outline=output_planner.outline,
            memory_content=output_planner.memory_context)

        # Step 3: Generate the outline
        outline = self.build_outline(
            topic=topic, 
            initial_outline=output_researcher.final_outline, 
            research_findings=output_researcher.final_content, 
            research_sources=output_researcher.final_sources,
            target_audience=self.audience)

        # Phase 3: Generate sections with research integration
        sections_en = []
        sections_translated = []

        for heading, subheadings in outline.section_subheadings.items():
            print(f"Generating section: {heading}")

            # Generate section content
            section = self.draft_section(
                topic=outline.title,
                section_heading=f"## {heading}",
                section_subheadings=[f"### {sub}" for sub in subheadings],
                research_content=output_researcher.final_content,
                sources=output_researcher.final_sources,
            )

            # Fact-check the section
            fact_checked = self.fact_checker(
                content=section.content, sources=output_researcher.final_sources
            )

            section_en = fact_checked.verified_content

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
            key_sources=outline.key_sources,
        )
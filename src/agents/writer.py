import dspy
import json
from agents.planner import ArticlePlanner
from agents.researcher import ArticleReACTResearcher
from utils.signatures import Translator
from typing import Any


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

    def __init__(self, audience: str = "DS/AI Scientist", mode: str = "react", engine: str = "tavily", verbose: bool = False):
        super().__init__()
        self.planner = ArticlePlanner(mode=mode, engine=engine, verbose=verbose)
        self.draft_section = dspy.ChainOfThought(ArticleSection)
        #self.fact_checker = dspy.ChainOfThought(ArticleFactCheck)
        self.translate = dspy.Predict(Translator)
        self.find_context = dspy.Predict(FindContext)

        self.audience = audience
        self.verbose = verbose

    def forward(self, topic: str, language: str = "Korean") -> dspy.Prediction:
        """Write an article using the outline and content and sources."""
        # Step 1: Plan the article
        print(f"ArticleWriter|Planning article...")
        output_planner = self.planner(topic)

        # Step 2: Research the article
        print(f"ArticleWriter|Researching article...")
        researcher = ArticleReACTResearcher(
            output_planner.research_strategy,
            output_planner.action_plan,
            verbose=self.verbose,
        )
        output_researcher = researcher(
            topic=topic,
            outline_str=output_planner.outline_str,
            memory_content=output_planner.memory_context,
            source_content=output_planner.source_content,
        )
        researcher.save(f"data/research/researcher_{topic.replace(' ', '-')}.md")

        # Step 3: Generate the outline
        title = output_researcher.final_title
        outline = output_researcher.final_outline

        # Phase 3: Generate sections with research integration
        sections_en = []
        sections_translated = []
        print(
            f"ArticleWriter|Title: {title} ({len(outline)} sections)"
        )

        key_sources = []
        for heading, subheadings in outline.items():
            print(f"ArticleWriter|Generating section: {heading}")

            section_content = self.find_context(
                topic=heading,
                content=output_researcher.final_content,
                previous_content=sections_en[-1] if sections_en else "",
            ).key_information

            # Generate section content
            section = self.draft_section(
                topic=title,
                section_heading=f"## {heading}",
                section_subheadings=[f"### {sub}" for sub in subheadings],
                research_content=section_content,
            )

            # Fact-check the section
            #fact_checked = self.fact_checker(
            #    content=section.content, sources=section_content
            #)

            #section_en = fact_checked.verified_content
            #key_sources.append(fact_checked.key_sources)
            section_en = section.content
            #key_sources.append(section.key_sources)

            # Translate if needed
            if language.lower() != "english":
                section_translated = self.translate(text=section_en, language=language)
                sections_translated.append(section_translated.translated_content)
            else:
                sections_translated.append(section_en)

            sections_en.append(section_en)

        return dspy.Prediction(
            title=title,
            sections_en=sections_en,
            sections_translated=sections_translated,
            key_sources=output_researcher.final_sources,
        )

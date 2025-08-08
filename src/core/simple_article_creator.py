import dspy
from utils.signatures import Translator
import logging

logger = logging.getLogger("article_creator")



class Outline(dspy.Signature):
    """Outline a thorough overview of a topic."""

    topic: str = dspy.InputField()
    title: str = dspy.OutputField()
    sections: list[str] = dspy.OutputField()
    section_subheadings: dict[str, list[str]] = dspy.OutputField(
        desc="mapping from section headings to subheadings"
    )


class DraftSection(dspy.Signature):
    """Draft a top-level section of an article."""

    topic: str = dspy.InputField()
    section_heading: str = dspy.InputField()
    section_subheadings: list[str] = dspy.InputField()
    content: str = dspy.OutputField(desc="markdown-formatted section")


class SimpleArticleCreator(dspy.Module):
    """Create an article based on an outline."""

    def __init__(self):
        self.build_outline = dspy.ChainOfThought(Outline)
        self.draft_section = dspy.ChainOfThought(DraftSection)
        self.translate = dspy.Predict(Translator)

    def forward(self, topic: str, language: str):
        print(f"Creating article for topic: {topic}")

        outline = self.build_outline(topic=topic)
        sections_en = []
        sections_translated = []
        print(f"Language: {language}")
        print(f"Outline: {len(outline.section_subheadings)} sections")

        for heading, subheadings in outline.section_subheadings.items():
            print(f"... {heading} - {'/'.join(subheadings)}")
            section, subheadings = (
                f"## {heading}",
                [f"### {subheading}" for subheading in subheadings],
            )

            section = self.draft_section(
                topic=outline.title,
                section_heading=section,
                section_subheadings=subheadings,
            )
            section_en = section.content
            section_other = self.translate(text=section_en, language=language)

            sections_en.append(section_en)
            sections_translated.append(section_other.translated_content)

        return dspy.Prediction(
            title=outline.title, 
            sections_en=sections_en, 
            sections_translated=sections_translated
        )

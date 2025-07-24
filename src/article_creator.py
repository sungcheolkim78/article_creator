from pathlib import Path
import dspy
import click
import os
from dotenv import load_dotenv
from utils import Translator, llm_setup

load_dotenv()


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


class DraftArticle(dspy.Module):
    """Draft an article based on an outline."""

    def __init__(self):
        self.build_outline = dspy.ChainOfThought(Outline)
        self.draft_section = dspy.ChainOfThought(DraftSection)
        self.translate = dspy.Predict(Translator)

    def forward(self, topic: str, language: str):
        print(f"Drafting article for topic: {topic}")

        outline = self.build_outline(topic=topic)
        sections_en = []
        sections_other = []
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
            sections_other.append(section_other.translated_content)

        return dspy.Prediction(
            title=outline.title, sections_en=sections_en, sections_other=sections_other
        )


@click.command()
@click.option("--topic", type=str, default="The impact of AI on jobs")
@click.option("--language", type=str, default="Korean")
@click.option("--output_dir", type=str, default="data/articles")
def main(topic, language, output_dir):
    llm_setup("openai/gpt-4o-mini")
    article = DraftArticle()
    prediction = article.forward(topic=topic, language=language)

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    topic_slug = topic.lower().replace(" ", "-")
    lang_slug = language[:3].lower()

    with open(output_dir / f"{topic_slug}-{lang_slug}.md", "w") as f:
        f.write(f"# {prediction.title}\n")
        for section in prediction.sections_other:
            f.write(section)
            f.write("\n")

    with open(output_dir / f"{topic_slug}-en.md", "w") as f:
        f.write(f"# {prediction.title}\n")
        for section in prediction.sections_en:
            f.write(section)
            f.write("\n")

    print(f"Article saved to {output_dir}")


if __name__ == "__main__":
    main()

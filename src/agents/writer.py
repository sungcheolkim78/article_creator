import dspy
from agents.tools import MemoryTools
from agents.planner import ArticlePlanner
from agents.researcher import ArticleReACTResearcher
from utils.signatures import Translator


class ArticleSection(dspy.Signature):
    """Draft a section of an article using research findings and web search results."""

    topic: str = dspy.InputField()
    section_heading: str = dspy.InputField()
    section_subheadings: list[str] = dspy.InputField()
    research_content: str = dspy.InputField(
        desc="research findings for the topic. It can include non-relevant findings."
    )

    content: str = dspy.OutputField(
        desc="markdown-formatted section with proper citations. Focus on the section heading and per each subheading, provide a consistent content, and avoid lists."
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

    def __init__(self, memory_tools: MemoryTools, audience: str = "DS/AI Scientist", verbose: bool = False):
        super().__init__()
        self.memory_tools = memory_tools
        self.planner = ArticlePlanner(memory_tools, verbose=verbose)

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
        self.planner(topic)

        # Step 2: Research the article
        print(f"ArticleWriter|Researching article...")
        researcher = ArticleReACTResearcher(
            self.memory_tools,
            verbose=self.verbose,
        )
        output_researcher = researcher(
            topic=topic,
            outline_str=self.memory_tools.outline_str,
            memory_content=self.memory_tools.get_findings(),
        )
        researcher.save(f"data/research/researcher_{topic.replace(' ', '-')}.md")

        # Step 3: Generate the outline
        title = output_researcher.final_title
        sections = output_researcher.final_sections
        section_subheadings = output_researcher.final_section_subheadings

        # Phase 3: Generate sections with research integration
        sections_en = []
        sections_translated = []
        print(
            f"ArticleWriter|Title: {title} ({len(sections)} sections)"
        )

        for heading in sections:
            subheadings = section_subheadings[heading]
            print(f"ArticleWriter|Generating section: {heading}")
            print(subheadings)

            #section_content = self.find_context(
            #    topic=heading,
            #    content=self.memory_tools.get_findings(),
            #    previous_content=sections_en[-1] if sections_en else "",
            #).key_information

            # Generate section content
            section = self.draft_section(
                topic=title,
                section_heading=f"## {heading}",
                section_subheadings=[f"### {sub}" for sub in subheadings],
                research_content=self.memory_tools.get_findings(),
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
            key_sources=self.memory_tools.get_sources(),
        )

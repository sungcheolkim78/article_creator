import dspy


class Translator(dspy.Signature):
    """Translate a text into a specified language."""

    text: str = dspy.InputField()
    language: str = dspy.InputField(default="Korean")
    translated_content: str = dspy.OutputField(desc="text in specified language")

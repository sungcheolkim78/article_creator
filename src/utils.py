import dspy
import os


class Translator(dspy.Signature):
    """Translate a text into a specified language."""

    text: str = dspy.InputField()
    language: str = dspy.InputField(default="Korean")
    translated_content: str = dspy.OutputField(desc="text in specified language")


def llm_setup(model_name):
    lm = dspy.LM(
        "openai/gpt-4o-mini",
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0,
        top_p=0.9,
        frequency_penalty=0,
        presence_penalty=0,
    )
    dspy.settings.configure(lm=lm, track_usage=True)

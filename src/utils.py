import dspy
import os
from dotenv import load_dotenv

load_dotenv()


class Translator(dspy.Signature):
    """Translate a text into a specified language."""

    text: str = dspy.InputField()
    language: str = dspy.InputField(default="Korean")
    translated_content: str = dspy.OutputField(desc="text in specified language")


def llm_setup(model_name):
    """
    Setup the LLM for dspy.

    Args:
        model_name: The name of the model to use. examples: "openai/gpt-4o-mini", 
        "anthropic/claude-3-5-sonnet-20240620", "gemini/gemini-2.5-flash"

    Returns:
        None
    """
    if "openai" in model_name:
        api_key = os.getenv("OPENAI_API_KEY")
        options = {
            "temperature": 0,
            "top_p": 0.9,
            "frequency_penalty": 0,
            "presence_penalty": 0,
        }
    elif "anthropic" in model_name:
        api_key = os.getenv("ANTHROPIC_API_KEY")    
        options = {
            "temperature": 0,
            "top_p": 0.9,
        }
    elif "gemini" in model_name:
        api_key = os.getenv("GEMINI_API_KEY")
        options = {
            "temperature": 0.1,
            "top_p": 0.9,
            "max_tokens": 8000,
        }
    else:
        raise ValueError(f"Invalid model name: {model_name}")

    lm = dspy.LM(
        model_name,
        api_key=api_key,
        **options,
    )
    dspy.settings.configure(lm=lm, track_usage=True)

import os
from dotenv import load_dotenv
import dspy
from typing import Dict, List, Any
import logging

logging.getLogger("LiteLLM").setLevel(logging.WARNING)

load_dotenv()


def llm_setup(model_name: str, cache: bool = True, extra_options: dict = {}) -> dict:
    """
    Setup the LLM for dspy.

    Args:
        model_name: The name of the model to use. examples: "openai/gpt-4o-mini",
        "anthropic/claude-3-5-sonnet-20240620", "gemini/gemini-2.5-flash",
        "openrouter/openai/gpt-oss-20b"

    Returns:
        None
    """
    # load environment variables
    load_dotenv()

    options = extra_options

    # openrouter goes first due to the naming pattern such as openrouter/openai/gpt-4o-mini
    if "openrouter" in model_name:
        api_key = os.getenv("OPENROUTER_API_KEY")
        options.update({
            "temperature": 0.1,
            "top_p": 0.9,
        })
    elif "openai" in model_name:
        api_key = os.getenv("OPENAI_API_KEY")
        if "gpt-5" in model_name:
            options.update({
                "max_tokens": 20000,
            })
        else:
            options.update({
                "max_tokens": 16384,
            })
        options.update({
            "temperature": 1.0,
        })
        
    elif "anthropic" in model_name:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        options.update({
            "temperature": 0,
            "top_p": 0.9,
        })
    elif "gemini" in model_name:
        api_key = os.getenv("GEMINI_API_KEY")
        options.update({
            "temperature": 1.0,
        })
    elif "ollama" in model_name:
        api_key = ""
        options.update({
            "api_base": "http://192.168.1.4:11434",
            "temperature": 1.0,
        })
    else:
        raise ValueError(f"Invalid model name: {model_name}")


    lm = dspy.LM(
        model_name,
        api_key=api_key,
        **options,
    )
    dspy.settings.configure(lm=lm, track_usage=True)
    dspy.configure_cache(
        enable_disk_cache=cache,
        enable_memory_cache=cache,
    )
    return options.update({"model_name": model_name, "cache": cache})


def check_environment(llm_model: str, search_tool_name: str) -> Dict[str, bool]:
    """Check if required environment variables are set."""
    results = {
        "llm_key_found": False,
        "search_key_found": True,  # Default to True for DDG
        "all_required_found": False,
    }

    # Check API keys
    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")
    brave_key = os.getenv("BRAVE_SEARCH_API_KEY")

    if "openrouter" in llm_model:
        results["llm_key_found"] = bool(openrouter_key)
    elif "openai" in llm_model:
        results["llm_key_found"] = bool(openai_key)
    elif "anthropic" in llm_model:
        results["llm_key_found"] = bool(anthropic_key)
    elif "gemini" in llm_model:
        results["llm_key_found"] = bool(gemini_key)
    elif "ollama" in llm_model:
        results["llm_key_found"] = True  # Ollama doesn't need API key

    if search_tool_name == "brave":
        results["search_key_found"] = bool(brave_key)

    results["all_required_found"] = (
        results["llm_key_found"] and results["search_key_found"]
    )

    return results


def get_available_llm_models() -> List[str]:
    """Get list of available LLM models."""
    return [
        "openai/gpt-4o-mini",
        "openai/gpt-4o",
        "anthropic/claude-sonnet-4-20250514",
        "anthropic/claude-3-7-sonnet-20250219",
        "anthropic/claude-3-5-haiku-20241022",
        "gemini/gemini-2.5-flash-lite",
        "gemini/gemini-2.5-flash",
        "gemini/gemini-2.5-pro",
        "ollama_chat/gpt-oss:20b",
        "ollama_chat/qwen3:14b",
        "ollama_chat/qwen3:8b",
        "ollama_chat/llama3.1:8b",
        "ollama_chat/granite3.2:8b",
    ]


def check_environment_cli(llm_model: str, search_tool_name: str) -> bool:
    """Check if required environment variables are set and display results."""
    print("🔑 Environment Check:")

    env_check = check_environment(llm_model, search_tool_name)

    if "openrouter" in llm_model:
        if env_check["llm_key_found"]:
            print("✅ OpenRouter API Key found")
        else:
            print("❌ OpenRouter API Key missing")
            return False
    elif "openai" in llm_model:
        if env_check["llm_key_found"]:
            print("✅ OpenAI API Key found")
        else:
            print("❌ OpenAI API Key missing")
            return False
    elif "anthropic" in llm_model:
        if env_check["llm_key_found"]:
            print("✅ Anthropic API Key found")
        else:
            print("❌ Anthropic API Key missing")
            return False
    elif "gemini" in llm_model:
        if env_check["llm_key_found"]:
            print("✅ Gemini API Key found")
        else:
            print("❌ Gemini API Key missing")
            return False

    if search_tool_name == "brave":
        if env_check["search_key_found"]:
            print("✅ Brave Search API Key found")
        else:
            print("⚠️ Brave Search API Key missing")
            return False

    return True

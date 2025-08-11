import dspy
from utils.llm import llm_setup, check_environment, check_environment_cli
from dotenv import load_dotenv


def test_llm():
    llm_model = "openrouter/openai/gpt-oss-20b"
    search_tool_name = "ddg"
    check_environment_cli(llm_model, search_tool_name)


if __name__ == "__main__":
    load_dotenv()
    test_llm()
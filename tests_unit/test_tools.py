from agents.tools import MemoryTools
from utils.llm import llm_setup

def test_memory_tools():
    llm_options = llm_setup(
        "gemini/gemini-2.5-flash-lite", cache=True, extra_options={"max_tokens": 6048}
    )
    memory_tools = MemoryTools(mode="query", engine="tavily", verbose=False)

    print(memory_tools.search_web("Lovable AI"))
    print("-"*100)
    print(memory_tools.analyze("What is the lovable AI?"))
    print("-"*100)
    print(memory_tools.outline("Lovable AI", "no initial outline"))
    print("-"*100)
    print(memory_tools.get_findings())


if __name__ == "__main__":
    test_memory_tools()
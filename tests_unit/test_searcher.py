from websearch.searcher import ReACTSearcher, tool_search_web
from utils.llm import llm_setup


def test_basic_search():
    searcher = ReACTSearcher(engine="ddg", verbose=True)

    topic = "how to use asyncio in python?"
    result = searcher(topic)

    print(result.markdown)


if __name__ == "__main__":
    llm_setup("openai/gpt-4o-mini")
    test_basic_search()
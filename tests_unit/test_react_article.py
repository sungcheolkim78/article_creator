from core.react_article import ArticleReACTAgent
from websearch.bravesearch import OptimizedBraveSearch
from websearch.ddgsearch import OptimizedDDGSearch

from utils.llm import llm_setup


def test_article_react_agent():
    llm_setup("openai/gpt-4o-mini")
    search_tool = OptimizedDDGSearch()

    a = ArticleReACTAgent(search_tool=search_tool)

    result = a.generate_article_with_research(
        topic="The impact of AI on jobs in 2024",
        initial_outline={
            "title": "The impact of AI on jobs in 2024",
            "sections": [
                {
                    "title": "Introduction",
                    "content": "Introduction to the impact of AI on jobs in 2024",
                },
                {"title": "Main body", "content": "Main body of the article"},
                {"title": "Conclusion", "content": "Conclusion of the article"},
            ],
        },
    )
    print(result["topic"])
    print(result["react_plan"])
    # print(result['research_phase'])
    # print(result['synthesis_phase'])
    print(result["total_actions"])
    print(result["memory_summary"])


if __name__ == "__main__":
    test_article_react_agent()

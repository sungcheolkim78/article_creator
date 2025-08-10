import dspy
import logging
import click

logging.getLogger("httpx").setLevel(logging.WARNING)

DOCS = {}


def search(query: str, k: int) -> list[str]:
    results = dspy.ColBERTv2(url="http://20.102.90.50:2017/wiki17_abstracts")(
        query, k=k
    )
    results = [x["text"] for x in results]

    for result in results:
        title, text = result.split(" | ", 1)
        title = title.replace(
            "&amp;", "&"
        )  # Replace &amp; with & to avoid HTML parsing errors
        DOCS[title] = text

    return results


def search_wikipedia(query: str) -> list[str]:
    """Returns top-5 results and then the titles of the top-5 to top-30 results."""

    topK = search(query, 30)
    titles, topK = [f"`{x.split(' | ')[0]}`" for x in topK[5:30]], topK[:5]
    return topK + [f"Other retrieved pages have titles: {', '.join(titles)}."]


def lookup_wikipedia(title: str) -> str:
    """Returns the text of the Wikipedia page, if it exists."""

    if title in DOCS:
        return DOCS[title]

    results = [x for x in search(title, 10) if x.startswith(title + " | ")]
    if not results:
        return f"No Wikipedia page found for title: {title}"
    return results[0]


class WikiReACTSearcher(dspy.Module):
    def __init__(self):
        instructions = (
            "Find all Wikipedia titles relevant to verifying (or refuting) the claim."
        )
        signature = dspy.Signature("claim -> titles: list[str]", instructions)
        self.react = dspy.ReAct(
            signature, tools=[search_wikipedia, lookup_wikipedia], max_iters=20
        )

    def forward(self, claim: str) -> list[str]:
        # Replace & with &amp; to avoid HTML parsing errors
        claim = claim.replace("&", "&amp;")

        result = self.react(claim=claim)

        for k, v in result.trajectory.items():
            print(k)
            print(v)
            print()

        print(result.reasoning)

        print("-" * 100)
        for title in result.titles:
            print(click.style(f"## {title}", fg="green"))
            print(lookup_wikipedia(title))

        return dspy.Prediction(titles=result.titles)

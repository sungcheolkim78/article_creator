from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SearchResult:
    """Data class for search results"""

    title: str
    url: str
    snippet: str
    extra_snippets: List[str] = None
    published_time: Optional[str] = None

    def __str__(self):
        return f"Title: {self.title}\nURL: {self.url}\nSnippet: {self.snippet}\n"

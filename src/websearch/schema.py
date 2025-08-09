from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SearchResult:
    """Data class for search results"""

    title: str
    url: str
    content: str
    notes: Optional[str] = None
    published_time: Optional[str] = None

    def __str__(self):
        return f"Title: {self.title}\nURL: {self.url}\nContent: {self.content}\n"

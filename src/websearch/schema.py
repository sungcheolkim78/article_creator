from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class SearchResult:
    """Data class for search results"""

    title: str
    url: str
    snippet: str
    source: str = "web"
    notes: Optional[str] = None
    published_time: Optional[str] = None
    sid: int = field(init=False)

    # Class variable to track the next available sid
    _next_sid: int = field(default=0, init=False, repr=False)

    def __post_init__(self):
        # Auto-assign sid if not provided
        SearchResult._next_sid += 1
        self.sid = SearchResult._next_sid

    def __str__(self):
        msg = f"=====\n"
        msg += f"- Title: {self.title}\n"
        msg += f"- URL: {self.url}\n"
        msg += f"- Content: {self.snippet}"
        if self.notes:
            msg += f"\n- Notes: {self.notes}"
        if self.published_time:
            msg += f"\n- Published Time: {self.published_time}"
        msg += "\n"
        return msg

    def to_markdown(self):
        return f"[^{self.sid}]: [{self.title}]({self.url})"

    def to_json(self):
        return json.dumps(
            {
                "title": self.title,
                "url": self.url,
                "content": self.snippet,
                "sid": self.sid,
            }
        )

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(
            title=data["title"],
            url=data["url"],
            snippet=data["content"],
        )

    @classmethod
    def reset_sid_counter(cls):
        """Reset the sid counter to 1 (useful for testing)"""
        cls._next_sid = 1

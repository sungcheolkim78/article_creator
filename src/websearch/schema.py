from dataclasses import dataclass
from typing import List, Optional
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
        return f"- [{self.title}]({self.url})"

    def to_json(self):
        return json.dumps({
            "title": self.title,
            "url": self.url,
            "content": self.snippet,
        })

    @classmethod
    def from_json(cls, json_str):
        data = json.loads(json_str)
        return cls(
            title=data["title"],
            url=data["url"],
            snippet=data["content"]
        )
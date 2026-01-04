from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import ClassVar


@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source: str = "web"
    notes: str | None = None
    published_time: str | None = None
    sid: int = field(init=False)

    _next_sid: ClassVar[int] = 0

    def __post_init__(self) -> None:
        SearchResult._next_sid += 1
        self.sid = SearchResult._next_sid

    def __str__(self) -> str:
        msg = "=====\n"
        msg += f"- Title: {self.title}\n"
        msg += f"- URL: {self.url}\n"
        msg += f"- Content: {self.snippet}"
        if self.notes:
            msg += f"\n- Notes: {self.notes}"
        if self.published_time:
            msg += f"\n- Published Time: {self.published_time}"
        msg += "\n"
        return msg

    def to_markdown(self) -> str:
        clean_title = self.title.replace("(", "[").replace(")", "]")
        return f"[^{self.sid}]: [{clean_title}]({self.url})"

    def to_json(self) -> str:
        return json.dumps(
            {
                "title": self.title,
                "url": self.url,
                "content": self.snippet,
                "sid": self.sid,
            }
        )

    @classmethod
    def from_json(cls, json_str: str) -> SearchResult:
        data = json.loads(json_str)
        return cls(
            title=data["title"],
            url=data["url"],
            snippet=data["content"],
        )

    @classmethod
    def reset_sid_counter(cls) -> None:
        cls._next_sid = 1


@dataclass
class QueryResult:
    query: str
    results: list[SearchResult]
    source: str = "web"

    def __post_init__(self) -> None:
        self.citations = " ".join([f"[^{item.sid}]" for item in self.results])
        self.links = "\n".join([item.to_markdown() for item in self.results])
        if self.results:
            self.source = self.results[0].source

    def __str__(self) -> str:
        return f"**{self.query} ({self.source}):** {self.citations}"

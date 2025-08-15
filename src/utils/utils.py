import os
from typing import Any, Optional, List


def get_available_languages() -> List[str]:
    """Get list of available languages."""
    return ["Korean", "English", "Japanese", "Chinese", "Spanish", "French", "German"]


def get_available_search_tools() -> List[str]:
    """Get list of available search tools."""
    return ["ddg", "brave"]


def get_available_modes() -> List[str]:
    """Get list of available generation modes."""
    return ["enhanced", "websearch"]


def broaden_search_query(query: str) -> str:
    """Broaden a search query to get more results."""
    # Remove specific terms that might be too narrow
    narrow_terms = [
        "latest",
        "2024",
        "2023",
        "recent",
        "newest",
        "specific",
        "exact",
        "precise",
        "detailed",
        "comprehensive",
        "complete",
    ]

    # Remove very specific technical terms that might not have many results
    technical_terms = [
        "implementation",
        "architecture",
        "framework",
        "protocol",
        "algorithm",
        "methodology",
        "paradigm",
    ]

    broadened = query.lower()

    # Remove narrow terms
    for term in narrow_terms:
        broadened = broadened.replace(term, "")

    # Remove technical terms if the query is very specific
    if len(query.split()) > 3:
        for term in technical_terms:
            broadened = broadened.replace(term, "")

    # Clean up extra spaces
    broadened = " ".join(broadened.split())

    # If we removed too much, add some general terms
    if len(broadened.split()) < 2:
        broadened = f"{broadened} overview guide"

    return broadened

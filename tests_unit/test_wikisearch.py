#!/usr/bin/env python3
"""Simple test script for BraveSearchTool (basic functionality only)."""

from websearch.wikisearch import WikiReACTSearcher
from dotenv import load_dotenv
from utils.llm import llm_setup, check_environment_cli

load_dotenv()
llm_setup("openai/gpt-4o-mini")
check_environment_cli("openai/gpt-4o-mini", "brave")


def test_basic_search():
    """Test basic search functionality"""
    print("Testing basic WikiReACTSearcher...")

    # Initialize the searcher
    searcher = WikiReACTSearcher()
    searcher("Humana")


if __name__ == "__main__":
    test_basic_search()

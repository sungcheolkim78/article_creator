"""
Web search module for article creation.

This module contains web search tools and utilities.
"""

from .bravesearch import OptimizedBraveSearch, BraveSearchTool
from .ddgsearch import OptimizedDDGSearch

__all__ = [
    'OptimizedBraveSearch',
    'BraveSearchTool',
    'OptimizedDDGSearch'
]

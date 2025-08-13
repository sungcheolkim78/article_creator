"""
Web search module for article creation.

This module contains web search tools and utilities.
"""

from .brave import OptimizedBraveSearch, BraveSearchTool
from .ddg import OptimizedDDGSearch

__all__ = ["OptimizedBraveSearch", "BraveSearchTool", "OptimizedDDGSearch"]

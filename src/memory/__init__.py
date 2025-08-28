"""
Vector Memory System for Research

A PostgreSQL-based vector memory system using the pgvector extension
for storing and retrieving research memories with semantic similarity search.
"""

from .base import BaseMemory
from .vector_memory import VectorMemory
from .database_config import DatabaseConfig, DEFAULT_CONFIG
from .embedding_utils import (
    EmbeddingGenerator,
    MockEmbeddingGenerator,
    normalize_embedding,
    cosine_similarity,
    euclidean_distance,
    validate_embedding,
    chunk_text_for_embedding
)

__version__ = "1.0.0"
__author__ = "Article Creator Team"

__all__ = [
    "BaseMemory",
    "VectorMemory", 
    "DatabaseConfig",
    "DEFAULT_CONFIG",
    "EmbeddingGenerator",
    "MockEmbeddingGenerator",
    "normalize_embedding",
    "cosine_similarity",
    "euclidean_distance",
    "validate_embedding",
    "chunk_text_for_embedding"
]

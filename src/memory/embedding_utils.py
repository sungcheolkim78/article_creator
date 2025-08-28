"""
Utility functions for generating and working with embeddings for vector memory.
"""

import logging
from typing import List, Optional, Union
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Base class for embedding generators."""
    
    def __init__(self, model_name: str = "default"):
        self.model_name = model_name
    
    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for given text.
        
        Args:
            text: Input text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        raise NotImplementedError("Subclasses must implement generate_embedding")
    
    def generate_batch_embeddings(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts
            
        Returns:
            List of embeddings (None for failed embeddings)
        """
        embeddings = []
        for text in texts:
            try:
                embedding = self.generate_embedding(text)
                embeddings.append(embedding)
            except Exception as e:
                logger.warning(f"Failed to generate embedding for text: {e}")
                embeddings.append(None)
        return embeddings


class MockEmbeddingGenerator(EmbeddingGenerator):
    """Mock embedding generator for testing purposes."""
    
    def __init__(self, dimension: int = 1536):
        super().__init__("mock")
        self.dimension = dimension
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate a mock embedding based on text content."""
        # Simple hash-based mock embedding
        import hashlib
        
        # Create a hash of the text
        text_hash = hashlib.md5(text.encode()).hexdigest()
        
        # Convert hash to list of floats
        embedding = []
        for i in range(0, len(text_hash), 2):
            if len(embedding) >= self.dimension:
                break
            hex_pair = text_hash[i:i+2]
            float_val = float(int(hex_pair, 16)) / 255.0  # Normalize to 0-1
            embedding.append(float_val)
        
        # Pad or truncate to desired dimension
        while len(embedding) < self.dimension:
            embedding.append(0.0)
        
        return embedding[:self.dimension]


def normalize_embedding(embedding: List[float]) -> List[float]:
    """
    Normalize embedding vector to unit length.
    
    Args:
        embedding: Input embedding vector
        
    Returns:
        Normalized embedding vector
    """
    if not embedding:
        return embedding
    
    embedding_array = np.array(embedding)
    norm = np.linalg.norm(embedding_array)
    
    if norm == 0:
        return embedding
    
    normalized = embedding_array / norm
    return normalized.tolist()


def cosine_similarity(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculate cosine similarity between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
        
    Returns:
        Cosine similarity score between -1 and 1
    """
    if not embedding1 or not embedding2:
        return 0.0
    
    if len(embedding1) != len(embedding2):
        logger.warning("Embedding dimensions don't match")
        return 0.0
    
    try:
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        similarity = dot_product / (norm1 * norm2)
        return float(similarity)
        
    except Exception as e:
        logger.error(f"Error calculating cosine similarity: {e}")
        return 0.0


def euclidean_distance(embedding1: List[float], embedding2: List[float]) -> float:
    """
    Calculate Euclidean distance between two embeddings.
    
    Args:
        embedding1: First embedding vector
        embedding2: Second embedding vector
        
    Returns:
        Euclidean distance (lower is more similar)
    """
    if not embedding1 or not embedding2:
        return float('inf')
    
    if len(embedding1) != len(embedding2):
        logger.warning("Embedding dimensions don't match")
        return float('inf')
    
    try:
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        distance = np.linalg.norm(vec1 - vec2)
        return float(distance)
        
    except Exception as e:
        logger.error(f"Error calculating Euclidean distance: {e}")
        return float('inf')


def validate_embedding(embedding: List[float], expected_dimension: int = 1536) -> bool:
    """
    Validate that an embedding has the expected format and dimension.
    
    Args:
        embedding: Embedding to validate
        expected_dimension: Expected dimension of the embedding
        
    Returns:
        True if embedding is valid
    """
    if not isinstance(embedding, list):
        logger.error("Embedding must be a list")
        return False
    
    if len(embedding) != expected_dimension:
        logger.error(f"Embedding dimension {len(embedding)} doesn't match expected {expected_dimension}")
        return False
    
    if not all(isinstance(x, (int, float)) for x in embedding):
        logger.error("All embedding values must be numbers")
        return False
    
    return True


def chunk_text_for_embedding(text: str, max_length: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into chunks suitable for embedding generation.
    
    Args:
        text: Input text to chunk
        max_length: Maximum length of each chunk
        overlap: Overlap between consecutive chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= max_length:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_length
        
        # Try to find a good break point (sentence or word boundary)
        if end < len(text):
            # Look for sentence ending
            for i in range(end, max(start, end - 200), -1):
                if text[i] in '.!?':
                    end = i + 1
                    break
            
            # If no sentence ending found, look for word boundary
            if end == start + max_length:
                for i in range(end, max(start, end - 100), -1):
                    if text[i].isspace():
                        end = i + 1
                        break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks

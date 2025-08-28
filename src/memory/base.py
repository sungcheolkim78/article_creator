from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseMemory(ABC):
    """Base class for memory systems."""
    
    def __init__(self, memory_type: str):
        self.memory_type = memory_type

    @abstractmethod
    def add_memory(self, memory: str, **kwargs) -> int:
        """Add a new memory entry."""
        pass

    @abstractmethod
    def get_memory(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve a specific memory by ID."""
        pass

    @abstractmethod
    def delete_memory(self, memory_id: int) -> bool:
        """Delete a specific memory by ID."""
        pass
    
    def get_memories_by_type(self, memory_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve memories by type with optional limit."""
        pass
    
    def search_similar(self, query_embedding: List[float], **kwargs) -> List[Dict[str, Any]]:
        """Search for similar memories using vector similarity."""
        pass
    
    def search_text(self, search_term: str, **kwargs) -> List[Dict[str, Any]]:
        """Search memories by text content."""
        pass
    
    def update_memory(self, memory_id: int, **kwargs) -> bool:
        """Update an existing memory entry."""
        pass
    
    def get_memory_stats(self, memory_type: Optional[str] = None) -> Dict[str, Any]:
        """Get statistics about stored memories."""
        pass
    
    def close(self) -> None:
        """Close any open connections or resources."""
        pass
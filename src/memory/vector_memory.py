import json
import logging
from typing import List, Dict, Any, Optional, Tuple
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from psycopg2.extensions import connection, cursor
import numpy as np

from .database_config import DatabaseConfig, DEFAULT_CONFIG
from .base import BaseMemory


logger = logging.getLogger(__name__)


class VectorMemory(BaseMemory):
    """
    Vector-based memory system using PostgreSQL with pgvector extension.
    Stores research memories with embeddings for semantic similarity search.
    """
    
    def __init__(self, memory_type: str, config: Optional[DatabaseConfig] = None):
        super().__init__(memory_type)
        self.config = config or DEFAULT_CONFIG
        self.connection: Optional[connection] = None
        self._ensure_connection()
    
    def _ensure_connection(self) -> None:
        """Ensure database connection is established."""
        if self.connection is None or self.connection.closed:
            try:
                self.connection = psycopg2.connect(**self.config.get_psycopg2_params())
                self.connection.autocommit = False
                logger.info(f"Connected to PostgreSQL database: {self.config.database}")
            except Exception as e:
                logger.error(f"Failed to connect to database: {e}")
                raise
    
    def _get_cursor(self) -> cursor:
        """Get a database cursor with RealDictCursor for easier data handling."""
        self._ensure_connection()
        return self.connection.cursor(cursor_factory=RealDictCursor)
    
    def _execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as a list of dictionaries."""
        cursor = self._get_cursor()
        try:
            cursor.execute(query, params)
            if query.strip().upper().startswith(('SELECT', 'WITH')):
                results = cursor.fetchall()
                return [dict(row) for row in results]
            else:
                self.connection.commit()
                return []
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Query execution failed: {e}")
            raise
        finally:
            cursor.close()
    
    def add_memory(self, 
                   content: str, 
                   embedding: Optional[List[float]] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   source_url: Optional[str] = None,
                   title: Optional[str] = None,
                   summary: Optional[str] = None,
                   tags: Optional[List[str]] = None) -> int:
        """
        Add a new memory entry with optional embedding and metadata.
        
        Args:
            content: The memory content/text
            embedding: Vector embedding (list of floats)
            metadata: Additional metadata as dictionary
            source_url: Source URL if applicable
            title: Title for the memory
            summary: Summary of the content
            tags: List of tags
            
        Returns:
            The ID of the inserted memory
        """
        query = """
        INSERT INTO research_memory 
        (memory_type, content, embedding, metadata, source_url, title, summary, tags)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        # Convert embedding to PostgreSQL vector format
        embedding_vector = None
        if embedding:
            embedding_vector = f"[{','.join(map(str, embedding))}]"
        
        params = (
            self.memory_type,
            content,
            embedding_vector,
            Json(metadata or {}),
            source_url,
            title,
            summary,
            tags or []
        )
        
        try:
            cursor = self._get_cursor()
            cursor.execute(query, params)
            memory_id = cursor.fetchone()['id']
            self.connection.commit()
            cursor.close()
            logger.info(f"Added memory with ID {memory_id}")
            return memory_id
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to add memory: {e}")
            raise
    
    def get_memory(self, memory_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by ID.
        
        Args:
            memory_id: The ID of the memory to retrieve
            
        Returns:
            Memory data as dictionary or None if not found
        """
        query = "SELECT * FROM research_memory WHERE id = %s"
        results = self._execute_query(query, (memory_id,))
        return results[0] if results else None
    
    def get_memories_by_type(self, memory_type: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve memories by type with optional limit.
        
        Args:
            memory_type: Type of memories to retrieve (uses instance memory_type if None)
            limit: Maximum number of memories to return
            
        Returns:
            List of memory dictionaries
        """
        memory_type = memory_type or self.memory_type
        query = """
        SELECT * FROM research_memory 
        WHERE memory_type = %s 
        ORDER BY created_at DESC 
        LIMIT %s
        """
        return self._execute_query(query, (memory_type, limit))
    
    def search_similar(self, 
                      query_embedding: List[float],
                      similarity_threshold: float = 0.7,
                      match_count: int = 10,
                      memory_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for similar memories using vector similarity.
        
        Args:
            query_embedding: Query vector embedding
            similarity_threshold: Minimum similarity score (0.0 to 1.0)
            match_count: Maximum number of results
            memory_type: Filter by memory type (optional)
            
        Returns:
            List of similar memories with similarity scores
        """
        if memory_type:
            # Use custom query with memory type filter
            query = """
            SELECT 
                id, memory_type, content, 
                1 - (embedding <=> %s) as similarity,
                metadata, created_at, source_url, title, summary, tags
            FROM research_memory 
            WHERE memory_type = %s 
            AND embedding IS NOT NULL
            AND 1 - (embedding <=> %s) > %s
            ORDER BY embedding <=> %s
            LIMIT %s
            """
            params = (f"[{','.join(map(str, query_embedding))}]", 
                     memory_type, 
                     f"[{','.join(map(str, query_embedding))}]",
                     similarity_threshold,
                     f"[{','.join(map(str, query_embedding))}]",
                     match_count)
        else:
            # Use the stored function
            query = "SELECT * FROM similarity_search(%s, %s, %s)"
            params = (f"[{','.join(map(str, query_embedding))}]", 
                     similarity_threshold, 
                     match_count)
        
        return self._execute_query(query, params)
    
    def search_text(self, 
                   search_term: str, 
                   memory_type: Optional[str] = None,
                   limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search memories by text content using PostgreSQL full-text search.
        
        Args:
            search_term: Text to search for
            memory_type: Filter by memory type (optional)
            limit: Maximum number of results
            
        Returns:
            List of matching memories
        """
        memory_type_filter = f"AND memory_type = '{memory_type}'" if memory_type else ""
        
        query = f"""
        SELECT *, 
               ts_rank(to_tsvector('english', content), plainto_tsquery('english', %s)) as rank
        FROM research_memory 
        WHERE to_tsvector('english', content) @@ plainto_tsquery('english', %s)
        {memory_type_filter}
        ORDER BY rank DESC, created_at DESC
        LIMIT %s
        """
        
        params = (search_term, search_term, limit)
        return self._execute_query(query, params)
    
    def delete_memory(self, memory_id: int) -> bool:
        """
        Delete a specific memory by ID.
        
        Args:
            memory_id: The ID of the memory to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        query = "DELETE FROM research_memory WHERE id = %s"
        try:
            cursor = self._get_cursor()
            cursor.execute(query, (memory_id,))
            deleted_count = cursor.rowcount
            self.connection.commit()
            cursor.close()
            
            if deleted_count > 0:
                logger.info(f"Deleted memory with ID {memory_id}")
                return True
            else:
                logger.warning(f"No memory found with ID {memory_id}")
                return False
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            raise
    
    def delete_memories_by_type(self, memory_type: Optional[str] = None) -> int:
        """
        Delete all memories of a specific type.
        
        Args:
            memory_type: Type of memories to delete (uses instance memory_type if None)
            
        Returns:
            Number of deleted memories
        """
        memory_type = memory_type or self.memory_type
        query = "DELETE FROM research_memory WHERE memory_type = %s"
        
        try:
            cursor = self._get_cursor()
            cursor.execute(query, (memory_type,))
            deleted_count = cursor.rowcount
            self.connection.commit()
            cursor.close()
            
            logger.info(f"Deleted {deleted_count} memories of type '{memory_type}'")
            return deleted_count
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to delete memories of type '{memory_type}': {e}")
            raise
    
    def update_memory(self, 
                     memory_id: int, 
                     content: Optional[str] = None,
                     embedding: Optional[List[float]] = None,
                     metadata: Optional[Dict[str, Any]] = None,
                     title: Optional[str] = None,
                     summary: Optional[str] = None,
                     tags: Optional[List[str]] = None) -> bool:
        """
        Update an existing memory entry.
        
        Args:
            memory_id: The ID of the memory to update
            content: New content (optional)
            embedding: New embedding (optional)
            metadata: New metadata (optional)
            title: New title (optional)
            summary: New summary (optional)
            tags: New tags (optional)
            
        Returns:
            True if update was successful, False otherwise
        """
        # Build dynamic update query
        update_fields = []
        params = []
        
        if content is not None:
            update_fields.append("content = %s")
            params.append(content)
        
        if embedding is not None:
            update_fields.append("embedding = %s")
            params.append(f"[{','.join(map(str, embedding))}]")
        
        if metadata is not None:
            update_fields.append("metadata = %s")
            params.append(Json(metadata))
        
        if title is not None:
            update_fields.append("title = %s")
            params.append(title)
        
        if summary is not None:
            update_fields.append("summary = %s")
            params.append(summary)
        
        if tags is not None:
            update_fields.append("tags = %s")
            params.append(tags)
        
        if not update_fields:
            return False
        
        query = f"UPDATE research_memory SET {', '.join(update_fields)} WHERE id = %s"
        params.append(memory_id)
        
        try:
            cursor = self._get_cursor()
            cursor.execute(query, params)
            updated_count = cursor.rowcount
            self.connection.commit()
            cursor.close()
            
            if updated_count > 0:
                logger.info(f"Updated memory with ID {memory_id}")
                return True
            else:
                logger.warning(f"No memory found with ID {memory_id}")
                return False
        except Exception as e:
            self.connection.rollback()
            logger.error(f"Failed to update memory {memory_id}: {e}")
            raise
    
    def get_memory_stats(self, memory_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics about stored memories.
        
        Args:
            memory_type: Type of memories to analyze (uses instance memory_type if None)
            
        Returns:
            Dictionary with memory statistics
        """
        memory_type = memory_type or self.memory_type
        memory_type_filter = f"WHERE memory_type = '{memory_type}'" if memory_type else ""
        
        query = f"""
        SELECT 
            COUNT(*) as total_memories,
            COUNT(embedding) as memories_with_embeddings,
            COUNT(*) FILTER (WHERE embedding IS NULL) as memories_without_embeddings,
            MIN(created_at) as oldest_memory,
            MAX(created_at) as newest_memory,
            AVG(LENGTH(content)) as avg_content_length
        FROM research_memory
        {memory_type_filter}
        """
        
        results = self._execute_query(query)
        return results[0] if results else {}
    
    def close(self) -> None:
        """Close the database connection."""
        if self.connection and not self.connection.closed:
            self.connection.close()
            logger.info("Database connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

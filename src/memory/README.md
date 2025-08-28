# Vector Memory System

A PostgreSQL-based vector memory system using the pgvector extension for storing and retrieving research memories with semantic similarity search capabilities.

## Features

- **Vector Storage**: Store research memories with high-dimensional embeddings
- **Semantic Search**: Find similar memories using vector similarity
- **Full-Text Search**: PostgreSQL-powered text search capabilities
- **Metadata Support**: Rich metadata storage with JSONB and tags
- **Connection Management**: Automatic connection handling with context manager support
- **Statistics**: Memory analytics and usage statistics
- **Flexible Schema**: Extensible table structure for different memory types

## Prerequisites

1. **PostgreSQL 11+** with pgvector extension
2. **Python 3.8+**
3. **psycopg2** and **numpy** packages

### Installing pgvector Extension

#### Ubuntu/Debian:
```bash
sudo apt-get install postgresql-14-pgvector
```

#### macOS (using Homebrew):
```bash
brew install pgvector
```

#### From Source:
```bash
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

## Installation

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables (optional):**
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=research_memory
export DB_USER=postgres
export DB_PASSWORD=your_password
export DB_SSLMODE=prefer
```

3. **Initialize the database:**
```bash
python -m src.memory.db_init
```

## Quick Start

```python
from memory.vector_memory import VectorMemory
from memory.embedding_utils import MockEmbeddingGenerator

# Initialize vector memory
memory = VectorMemory("research_notes")

# Generate embeddings (use your preferred embedding model)
embedding_gen = MockEmbeddingGenerator()

# Add a research memory
memory_id = memory.add_memory(
    content="Machine learning algorithms can be categorized into supervised, unsupervised, and reinforcement learning approaches.",
    embedding=embedding_gen.generate_embedding("Machine learning algorithms"),
    title="ML Algorithm Categories",
    summary="Overview of main ML algorithm types",
    tags=["machine-learning", "algorithms"],
    source_url="https://example.com/ml-basics"
)

# Search for similar memories
query_embedding = embedding_gen.generate_embedding("artificial intelligence")
similar_memories = memory.search_similar(
    query_embedding=query_embedding,
    similarity_threshold=0.7,
    match_count=10
)

# Text search
search_results = memory.search_text("machine learning")

# Get memory statistics
stats = memory.get_memory_stats()
print(f"Total memories: {stats['total_memories']}")

# Clean up
memory.close()
```

## Core Components

### 1. VectorMemory Class

The main class for interacting with the vector database:

```python
class VectorMemory(BaseMemory):
    def __init__(self, memory_type: str, config: Optional[DatabaseConfig] = None)
    
    # Core operations
    def add_memory(self, content: str, embedding: List[float], **kwargs) -> int
    def get_memory(self, memory_id: int) -> Optional[Dict[str, Any]]
    def delete_memory(self, memory_id: int) -> bool
    def update_memory(self, memory_id: int, **kwargs) -> bool
    
    # Search operations
    def search_similar(self, query_embedding: List[float], **kwargs) -> List[Dict[str, Any]]
    def search_text(self, search_term: str, **kwargs) -> List[Dict[str, Any]]
    
    # Utility operations
    def get_memories_by_type(self, memory_type: str, limit: int = 100) -> List[Dict[str, Any]]
    def get_memory_stats(self, memory_type: str) -> Dict[str, Any]
```

### 2. Database Configuration

```python
from memory.database_config import DatabaseConfig

# Use default configuration
config = DatabaseConfig()

# Or customize
config = DatabaseConfig(
    host="localhost",
    port=5432,
    database="research_memory",
    user="postgres",
    password="your_password"
)

# Or load from environment
config = DatabaseConfig.from_env()
```

### 3. Embedding Utilities

```python
from memory.embedding_utils import (
    MockEmbeddingGenerator,
    normalize_embedding,
    cosine_similarity,
    validate_embedding
)

# Generate mock embeddings for testing
embedding_gen = MockEmbeddingGenerator(dimension=1536)
embedding = embedding_gen.generate_embedding("Your text here")

# Validate embeddings
is_valid = validate_embedding(embedding, expected_dimension=1536)

# Calculate similarity
similarity = cosine_similarity(embedding1, embedding2)
```

## Database Schema

The system creates a `research_memory` table with the following structure:

```sql
CREATE TABLE research_memory (
    id SERIAL PRIMARY KEY,
    memory_type VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source_url TEXT,
    title VARCHAR(500),
    summary TEXT,
    tags TEXT[]
);
```

### Indexes

- **Vector similarity**: `ivfflat` index on embeddings for fast similarity search
- **Text search**: Full-text search indexes on content
- **Metadata**: GIN index on JSONB metadata
- **Tags**: GIN index on tags array
- **Performance**: Indexes on memory_type and created_at

## Advanced Usage

### 1. Custom Embedding Models

```python
from memory.embedding_utils import EmbeddingGenerator

class OpenAIEmbeddingGenerator(EmbeddingGenerator):
    def __init__(self, api_key: str):
        super().__init__("openai")
        self.api_key = api_key
    
    def generate_embedding(self, text: str) -> List[float]:
        # Implement OpenAI API call
        # Return embedding as list of floats
        pass

# Use with vector memory
embedding_gen = OpenAIEmbeddingGenerator(api_key="your_key")
memory = VectorMemory("research", config=config)
```

### 2. Batch Operations

```python
# Add multiple memories efficiently
texts = ["Text 1", "Text 2", "Text 3"]
embeddings = embedding_gen.generate_batch_embeddings(texts)

for text, embedding in zip(texts, embeddings):
    if embedding:
        memory.add_memory(content=text, embedding=embedding)
```

### 3. Memory Types and Organization

```python
# Different memory types for different purposes
research_memory = VectorMemory("research_papers")
code_memory = VectorMemory("code_snippets")
notes_memory = VectorMemory("personal_notes")

# Search across specific types
papers = research_memory.search_similar(query_embedding, memory_type="research_papers")
```

### 4. Context Manager Usage

```python
# Automatic connection management
with VectorMemory("research") as memory:
    memory_id = memory.add_memory(content="Research note", embedding=embedding)
    result = memory.get_memory(memory_id)
    # Connection automatically closed
```

## Performance Considerations

### 1. Vector Search Optimization

- Use appropriate `similarity_threshold` values (0.7-0.9 for high precision)
- Limit `match_count` based on your needs
- Consider using `memory_type` filters for faster searches

### 2. Database Tuning

```sql
-- Adjust IVFFlat index parameters for your data size
CREATE INDEX ON research_memory USING ivfflat (embedding vector_cosine_ops) 
WITH (lists = 100);  -- Adjust based on table size

-- Monitor query performance
EXPLAIN ANALYZE SELECT * FROM similarity_search('[1,2,3]'::vector, 0.7, 10);
```

### 3. Connection Pooling

For production use, consider implementing connection pooling:

```python
import psycopg2.pool

class PooledVectorMemory(VectorMemory):
    def __init__(self, memory_type: str, config: DatabaseConfig, pool_size: int = 10):
        super().__init__(memory_type, config)
        self.pool = psycopg2.pool.SimpleConnectionPool(
            1, pool_size, **config.get_psycopg2_params()
        )
```

## Monitoring and Maintenance

### 1. Memory Statistics

```python
# Get comprehensive statistics
stats = memory.get_memory_stats()
print(f"Total memories: {stats['total_memories']}")
print(f"With embeddings: {stats['memories_with_embeddings']}")
print(f"Average content length: {stats['avg_content_length']:.0f}")
```

### 2. Database Maintenance

```sql
-- Regular maintenance for vector indexes
REINDEX INDEX CONCURRENTLY idx_research_memory_embedding;

-- Analyze table statistics
ANALYZE research_memory;

-- Check index usage
SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'research_memory';
```

### 3. Logging

The system includes comprehensive logging:

```python
import logging
logging.basicConfig(level=logging.INFO)

# Monitor database operations
logger = logging.getLogger('memory.vector_memory')
```

## Troubleshooting

### Common Issues

1. **pgvector extension not found**
   ```bash
   # Install pgvector extension
   sudo apt-get install postgresql-14-pgvector
   # Or compile from source
   ```

2. **Connection refused**
   - Check PostgreSQL is running
   - Verify connection parameters
   - Check firewall settings

3. **Vector dimension mismatch**
   - Ensure all embeddings have the same dimension (default: 1536)
   - Use `validate_embedding()` function

4. **Performance issues**
   - Check index usage with `EXPLAIN ANALYZE`
   - Monitor database statistics
   - Consider connection pooling

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable detailed logging for troubleshooting
logger = logging.getLogger('memory.vector_memory')
logger.setLevel(logging.DEBUG)
```

## Testing

Run the demo to test the system:

```bash
python -m src.memory.demo_vector_memory
```

Or run individual tests:

```bash
# Test database initialization
python -m src.memory.db_init

# Test basic operations
python -c "
from memory.vector_memory import VectorMemory
memory = VectorMemory('test')
print('Vector memory system working!')
memory.close()
"
```

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass

## License

This project is part of the article_creator project and follows the same license terms.

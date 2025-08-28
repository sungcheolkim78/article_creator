#!/usr/bin/env python3
"""
Demo script for the Vector Memory system.
This script demonstrates how to use the PostgreSQL-based vector memory for research.
"""

import logging
import sys
import os

# Add the src directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from memory.vector_memory import VectorMemory
from memory.database_config import DatabaseConfig
from memory.embedding_utils import MockEmbeddingGenerator, normalize_embedding
from memory.db_init import main as init_database

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def demo_basic_operations():
    """Demonstrate basic vector memory operations."""
    logger.info("=== Basic Vector Memory Operations Demo ===")
    
    # Initialize vector memory
    memory = VectorMemory("research_demo")
    
    try:
        # Add some sample research memories
        logger.info("Adding sample research memories...")
        
        # Sample research data
        research_data = [
            {
                "content": "Machine learning algorithms can be categorized into supervised, unsupervised, and reinforcement learning approaches.",
                "title": "ML Algorithm Categories",
                "summary": "Overview of main ML algorithm types",
                "tags": ["machine-learning", "algorithms", "supervised", "unsupervised"],
                "source_url": "https://example.com/ml-basics"
            },
            {
                "content": "Neural networks are computational models inspired by biological neural networks in the brain.",
                "title": "Neural Networks",
                "summary": "Introduction to neural network concepts",
                "tags": ["neural-networks", "deep-learning", "biology"],
                "source_url": "https://example.com/neural-networks"
            },
            {
                "content": "Natural language processing enables computers to understand and generate human language.",
                "title": "Natural Language Processing",
                "summary": "NLP fundamentals and applications",
                "tags": ["nlp", "language", "ai", "text-processing"],
                "source_url": "https://example.com/nlp-intro"
            }
        ]
        
        # Generate mock embeddings and add memories
        embedding_gen = MockEmbeddingGenerator()
        
        for i, data in enumerate(research_data):
            # Generate embedding for the content
            embedding = embedding_gen.generate_embedding(data["content"])
            
            # Add to memory
            memory_id = memory.add_memory(
                content=data["content"],
                embedding=embedding,
                title=data["title"],
                summary=data["summary"],
                tags=data["tags"],
                source_url=data["source_url"],
                metadata={"demo_id": i, "category": "research"}
            )
            logger.info(f"Added memory {memory_id}: {data['title']}")
        
        # Retrieve memories
        logger.info("\nRetrieving all memories...")
        all_memories = memory.get_memories_by_type()
        for mem in all_memories:
            logger.info(f"Memory {mem['id']}: {mem['title']} - {mem['summary']}")
        
        # Search by text
        logger.info("\nSearching for 'machine learning'...")
        search_results = memory.search_text("machine learning")
        for result in search_results:
            logger.info(f"Found: {result['title']} (rank: {result['rank']:.3f})")
        
        # Vector similarity search
        logger.info("\nPerforming vector similarity search...")
        query_text = "artificial intelligence and machine learning"
        query_embedding = embedding_gen.generate_embedding(query_text)
        
        similar_memories = memory.search_similar(
            query_embedding=query_embedding,
            similarity_threshold=0.5,
            match_count=5
        )
        
        for mem in similar_memories:
            logger.info(f"Similar: {mem['title']} (similarity: {mem['similarity']:.3f})")
        
        # Get statistics
        logger.info("\nMemory statistics:")
        stats = memory.get_memory_stats()
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
    finally:
        memory.close()


def demo_advanced_features():
    """Demonstrate advanced vector memory features."""
    logger.info("\n=== Advanced Features Demo ===")
    
    memory = VectorMemory("advanced_demo")
    
    try:
        # Add memories with different types
        logger.info("Adding memories with different types...")
        
        # Research papers
        paper_embedding = MockEmbeddingGenerator().generate_embedding(
            "This paper presents a novel approach to transformer architecture optimization."
        )
        paper_id = memory.add_memory(
            content="This paper presents a novel approach to transformer architecture optimization.",
            embedding=paper_embedding,
            memory_type="research_paper",
            title="Transformer Optimization",
            tags=["transformer", "optimization", "research"]
        )
        
        # Code snippets
        code_embedding = MockEmbeddingGenerator().generate_embedding(
            "def train_model(X, y): return model.fit(X, y)"
        )
        code_id = memory.add_memory(
            content="def train_model(X, y): return model.fit(X, y)",
            embedding=code_embedding,
            memory_type="code_snippet",
            title="Training Function",
            tags=["python", "training", "function"]
        )
        
        # Notes
        notes_embedding = MockEmbeddingGenerator().generate_embedding(
            "Important: Always normalize data before training neural networks."
        )
        notes_id = memory.add_memory(
            content="Important: Always normalize data before training neural networks.",
            embedding=notes_embedding,
            memory_type="notes",
            title="Data Normalization Note",
            tags=["data-preprocessing", "neural-networks", "best-practice"]
        )
        
        # Search by type
        logger.info("\nSearching for research papers...")
        papers = memory.get_memories_by_type("research_paper")
        for paper in papers:
            logger.info(f"Paper: {paper['title']}")
        
        # Update memory
        logger.info("\nUpdating memory...")
        success = memory.update_memory(
            memory_id=paper_id,
            summary="Novel transformer optimization techniques",
            tags=["transformer", "optimization", "research", "novel"]
        )
        if success:
            logger.info("Memory updated successfully")
        
        # Search with metadata
        logger.info("\nSearching for memories with 'novel' tag...")
        novel_memories = memory.search_text("novel")
        for mem in novel_memories:
            logger.info(f"Novel memory: {mem['title']}")
        
    except Exception as e:
        logger.error(f"Advanced demo failed: {e}")
    finally:
        memory.close()


def demo_bulk_operations():
    """Demonstrate bulk operations with vector memory."""
    logger.info("\n=== Bulk Operations Demo ===")
    
    memory = VectorMemory("bulk_demo")
    
    try:
        # Generate bulk content
        logger.info("Adding bulk research content...")
        
        topics = [
            "Deep learning applications in computer vision",
            "Natural language processing for chatbots",
            "Reinforcement learning in robotics",
            "Transfer learning for small datasets",
            "Attention mechanisms in neural networks",
            "Generative adversarial networks",
            "Convolutional neural networks for image classification",
            "Recurrent neural networks for sequence modeling",
            "Transformer models for language understanding",
            "Graph neural networks for structured data"
        ]
        
        embedding_gen = MockEmbeddingGenerator()
        
        for i, topic in enumerate(topics):
            embedding = embedding_gen.generate_embedding(topic)
            memory_id = memory.add_memory(
                content=topic,
                embedding=embedding,
                title=f"Topic {i+1}",
                summary=f"Research on {topic.lower()}",
                tags=[f"topic-{i+1}", "research", "ai"],
                metadata={"bulk_id": i, "category": "research_topic"}
            )
        
        # Bulk search
        logger.info("Performing bulk similarity search...")
        query_embedding = embedding_gen.generate_embedding("machine learning and artificial intelligence")
        
        similar_topics = memory.search_similar(
            query_embedding=query_embedding,
            similarity_threshold=0.3,
            match_count=20
        )
        
        logger.info(f"Found {len(similar_topics)} similar topics:")
        for topic in similar_topics[:5]:  # Show top 5
            logger.info(f"  - {topic['title']} (similarity: {topic['similarity']:.3f})")
        
        # Get bulk statistics
        stats = memory.get_memory_stats()
        logger.info(f"\nTotal memories: {stats.get('total_memories', 0)}")
        logger.info(f"Memories with embeddings: {stats.get('memories_with_embeddings', 0)}")
        
    except Exception as e:
        logger.error(f"Bulk operations demo failed: {e}")
    finally:
        memory.close()


def main():
    """Main demo function."""
    logger.info("Starting Vector Memory Demo")
    
    try:
        # Check if database is initialized
        logger.info("Checking database setup...")
        
        # Run basic operations demo
        demo_basic_operations()
        
        # Run advanced features demo
        demo_advanced_features()
        
        # Run bulk operations demo
        demo_bulk_operations()
        
        logger.info("\n=== Demo Completed Successfully ===")
        logger.info("The vector memory system is working correctly!")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        logger.info("Make sure PostgreSQL is running and pgvector extension is installed")
        logger.info("You can run the database initialization script first:")
        logger.info("python -m src.memory.db_init")
        sys.exit(1)


if __name__ == "__main__":
    main()

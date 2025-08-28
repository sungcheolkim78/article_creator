#!/usr/bin/env python3
"""
Database initialization script for research memory vector database.
This script sets up the PostgreSQL database with pgvector extension and required schema.
"""

import logging
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from .database_config import DatabaseConfig, DEFAULT_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_database(config: DatabaseConfig) -> bool:
    """
    Create the database if it doesn't exist.
    
    Args:
        config: Database configuration
        
    Returns:
        True if database was created successfully or already exists
    """
    # Connect to default postgres database to create our database
    postgres_config = config.get_psycopg2_params().copy()
    postgres_config['database'] = 'postgres'
    
    try:
        conn = psycopg2.connect(**postgres_config)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (config.database,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE "{config.database}"')
            logger.info(f"Created database: {config.database}")
        else:
            logger.info(f"Database {config.database} already exists")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        return False


def setup_schema(config: DatabaseConfig) -> bool:
    """
    Set up the database schema with tables and functions.
    
    Args:
        config: Database configuration
        
    Returns:
        True if schema was set up successfully
    """
    try:
        conn = psycopg2.connect(**config.get_psycopg2_params())
        cursor = conn.cursor()
        
        # Read and execute schema file
        schema_path = __file__.replace('db_init.py', 'schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Split and execute SQL statements
        statements = schema_sql.split(';')
        for statement in statements:
            statement = statement.strip()
            if statement:
                try:
                    cursor.execute(statement)
                    logger.info(f"Executed: {statement[:50]}...")
                except Exception as e:
                    logger.warning(f"Statement failed (may already exist): {e}")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Database schema setup completed")
        return True
        
    except Exception as e:
        logger.error(f"Failed to setup schema: {e}")
        return False


def check_pgvector_extension(config: DatabaseConfig) -> bool:
    """
    Check if pgvector extension is available and enabled.
    
    Args:
        config: Database configuration
        
    Returns:
        True if pgvector is available
    """
    try:
        conn = psycopg2.connect(**config.get_psycopg2_params())
        cursor = conn.cursor()
        
        # Check if pgvector extension exists
        cursor.execute("""
            SELECT extname, extversion 
            FROM pg_extension 
            WHERE extname = 'vector'
        """)
        
        result = cursor.fetchone()
        if result:
            logger.info(f"pgvector extension found: version {result[1]}")
            cursor.close()
            conn.close()
            return True
        else:
            logger.error("pgvector extension not found. Please install it first.")
            cursor.close()
            conn.close()
            return False
            
    except Exception as e:
        logger.error(f"Failed to check pgvector extension: {e}")
        return False


def test_connection(config: DatabaseConfig) -> bool:
    """
    Test database connection and basic operations.
    
    Args:
        config: Database configuration
        
    Returns:
        True if connection test passed
    """
    try:
        conn = psycopg2.connect(**config.get_psycopg2_params())
        cursor = conn.cursor()
        
        # Test basic operations
        cursor.execute("SELECT version()")
        version = cursor.fetchone()[0]
        logger.info(f"Connected to: {version}")
        
        # Test vector operations
        cursor.execute("SELECT '[1,2,3]'::vector")
        result = cursor.fetchone()
        logger.info("Vector operations working correctly")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False


def main():
    """Main function to initialize the database."""
    logger.info("Starting database initialization...")
    
    # Use default config or environment variables
    config = DatabaseConfig.from_env()
    logger.info(f"Using database: {config.database} on {config.host}:{config.port}")
    
    # Step 1: Create database
    if not create_database(config):
        logger.error("Failed to create database")
        sys.exit(1)
    
    # Step 2: Check pgvector extension
    if not check_pgvector_extension(config):
        logger.error("pgvector extension not available")
        sys.exit(1)
    
    # Step 3: Setup schema
    if not setup_schema(config):
        logger.error("Failed to setup schema")
        sys.exit(1)
    
    # Step 4: Test connection
    if not test_connection(config):
        logger.error("Connection test failed")
        sys.exit(1)
    
    logger.info("Database initialization completed successfully!")
    logger.info("You can now use VectorMemory class to interact with the database.")


if __name__ == "__main__":
    main()

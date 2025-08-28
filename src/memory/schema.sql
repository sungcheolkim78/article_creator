-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create research_memory table
CREATE TABLE IF NOT EXISTS research_memory (
    id SERIAL PRIMARY KEY,
    memory_type VARCHAR(100) NOT NULL,
    content TEXT NOT NULL,
    embedding vector(1536), -- OpenAI embedding dimension
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    source_url TEXT,
    title VARCHAR(500),
    summary TEXT,
    tags TEXT[]
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_research_memory_type ON research_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_research_memory_created_at ON research_memory(created_at);
CREATE INDEX IF NOT EXISTS idx_research_memory_embedding ON research_memory USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_research_memory_metadata ON research_memory USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_research_memory_tags ON research_memory USING GIN (tags);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_research_memory_updated_at 
    BEFORE UPDATE ON research_memory 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Create function for similarity search
CREATE OR REPLACE FUNCTION similarity_search(
    query_embedding vector(1536),
    similarity_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10
)
RETURNS TABLE (
    id int,
    memory_type varchar(100),
    content text,
    similarity float,
    metadata jsonb,
    created_at timestamp with time zone,
    source_url text,
    title varchar(500),
    summary text,
    tags text[]
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        rm.id,
        rm.memory_type,
        rm.content,
        1 - (rm.embedding <=> query_embedding) as similarity,
        rm.metadata,
        rm.created_at,
        rm.source_url,
        rm.title,
        rm.summary,
        rm.tags
    FROM research_memory rm
    WHERE rm.embedding IS NOT NULL
    AND 1 - (rm.embedding <=> query_embedding) > similarity_threshold
    ORDER BY rm.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

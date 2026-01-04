# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

An intelligent article generation system powered by DSPy that creates comprehensive articles using memory-enhanced ReACT (Reasoning and Acting) agents. The system integrates web search, deep research capabilities, and maintains context across iterations using both in-memory and vector-based (PostgreSQL + pgvector) memory systems.

## Development Commands

### Setup and Installation

```bash
# Install dependencies using uv (preferred)
uv sync

# Or using pip
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys:
# - OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY
# - BRAVE_SEARCH_API_KEY or TAVILY_API_KEY (optional)
```

### Running the Application

```bash
# Run Streamlit web interface
python run_streamlit.py
# or
uv run streamlit run src/app.py

# Run CLI version
python src/cli.py --topic "Your topic here"

# CLI with custom options
python src/cli.py --topic "Machine learning in healthcare" \
                  --language "Korean" \
                  --mode "enhanced" \
                  --llm-model "openai/gpt-4o-mini" \
                  --search-tool "ddg"
```

### Testing

```bash
# Run all tests
pytest tests_unit/

# Run specific test file
pytest tests_unit/test_react_article.py

# Run with verbose output
pytest -v tests_unit/

# Run tests with specific markers (if implemented)
pytest -m "not integration" tests_unit/
```

### Code Quality

```bash
# Run ruff linter
ruff check src/

# Run ruff formatter
ruff format src/

# Run type checking with pyright
pyright src/
```

## Architecture Overview

### Core Architecture Layers

The codebase is organized into four main architectural layers:

1. **Core Layer** (`src/core/`): ReACT agent implementations and article generation logic
   - `react_base.py`: Base ReACT agent with reasoning loop
   - `react_article.py`: Article-specific ReACT agent
   - `react_memory.py`: In-memory context management (hash-based, fast)
   - `enhanced_article_creator.py`: Main article generation orchestrator
   - `research_tool.py`: Deep research and fact-checking tools

2. **Memory Layer** (`src/memory/`): Persistent memory systems
   - `base.py`: Abstract base class for memory implementations
   - `vector_memory.py`: PostgreSQL + pgvector implementation for semantic search
   - `database_config.py`: Database connection configuration
   - Supports both simple in-memory (ReactMemory) and persistent vector memory (VectorMemory)

3. **Web Search Layer** (`src/websearch/`): Multiple search engine integrations
   - `base.py`: Base searcher with query categorization and summarization
   - `brave.py`, `ddg.py`, `tavily.py`, `wiki.py`: Specific search engine implementations
   - `schema.py`: Common data models for search results

4. **Agents Layer** (`src/agents/`): Specialized agents for article creation workflow
   - `planner.py`: Article outline and structure planning
   - `researcher.py`: Information gathering and research
   - `writer.py`: Content generation and article writing
   - `searcher.py`: Web search coordination
   - `tools.py`: Agent tool definitions and utilities

### Key Architectural Patterns

**ReACT Agent Pattern**: The system uses a Reasoning-Acting loop where agents:
1. Reason about what information is needed
2. Select appropriate actions (search, research, fact_check, analyze, finish)
3. Execute actions using available tools
4. Store results in memory for context
5. Repeat until goal is achieved

**Memory Management**: Two-tier memory system:
- **ReactMemory** (in-memory): Fast hash-based storage for current session context, search caching, and action history
- **VectorMemory** (PostgreSQL): Persistent semantic search across sessions using pgvector for embeddings

**DSPy Integration**: Uses DSPy signatures and modules for:
- Structured prompting with typed inputs/outputs
- Chain-of-thought reasoning for complex decisions
- Language model abstraction (supports OpenAI, Anthropic, Gemini via model names)

## LLM Configuration

The system uses model name strings to configure different LLM providers via DSPy:

```python
# Available models
"openai/gpt-4o"
"openai/gpt-4o-mini"
"openai/gpt-4-turbo"
"anthropic/claude-3-5-sonnet-20241022"
"anthropic/claude-3-5-haiku-20241022"
"gemini/gemini-2.0-flash-exp"

# Configuration happens in utils/llm.py
# DSPy automatically routes to the correct provider based on model prefix
```

## Search Engine Configuration

Multiple search engines are supported with different trade-offs:
- **DuckDuckGo (`ddg`)**: Free, no API key required, rate-limited
- **Brave (`brave`)**: Requires API key, better quality results
- **Tavily (`tavily`)**: Requires API key, optimized for AI/research
- **Wikipedia (`wiki`)**: Free, good for factual/historical information

## Memory System Details

### ReactMemory (In-Memory)
- Hash-based storage for fast lookups
- Automatic memory management with configurable size limits
- Categories: search_results, research_findings, fact_checks, context, sources, insights, action_history
- Access-based cleanup to preserve frequently used information
- No persistence between sessions

### VectorMemory (PostgreSQL + pgvector)
- Persistent storage with semantic similarity search
- Requires PostgreSQL with pgvector extension
- Stores embeddings for content-based retrieval
- Database initialization via `src/memory/db_init.py`
- Configured via `src/memory/database_config.py`

## Configuration Files

### pyproject.toml
- Uses `uv` for dependency management
- Python 3.11+ required (configured for 3.13 in ruff)
- Ruff configuration: line length 88, Google-style docstrings
- Dependencies include: dspy, streamlit, mem0ai, psycopg2-binary

### Environment Variables
Required variables in `.env`:
- `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` or `GEMINI_API_KEY` (at least one)
- `BRAVE_SEARCH_API_KEY` (optional, for Brave search)
- `TAVILY_API_KEY` (optional, for Tavily search)

## Article Generation Workflow

1. **Planning Phase**: `planner.py` creates article outline based on topic
2. **Research Phase**: ReACT agent gathers information using search and research tools
3. **Memory Integration**: Context from previous searches/research informs decisions
4. **Writing Phase**: `writer.py` generates content for each section
5. **Translation Phase**: Translates content to target language (if specified)
6. **Output**: Saves markdown files in `data/articles/` directory

## Common Pitfalls

- **Memory Overflow**: ReactMemory has configurable size limits - adjust `memory_size` parameter for large research tasks
- **Rate Limiting**: DuckDuckGo has rate limits - use Brave/Tavily for production or add delays
- **PostgreSQL Setup**: VectorMemory requires manual database setup and pgvector extension installation
- **API Keys**: Different models require different API keys - check `.env` configuration
- **DSPy Model Format**: Use provider prefix (e.g., `openai/`, `anthropic/`, `gemini/`) in model names

## Utilities

- `src/utils/llm.py`: LLM initialization and configuration helpers
- `src/utils/text.py`: Text processing, article generation wrappers
- `src/utils/utils.py`: General utilities, environment checks, article metrics
- `src/utils/signatures.py`: DSPy signature definitions

## Testing Strategy

Tests are organized in `tests_unit/` by component:
- `test_*_search.py`: Search engine integration tests
- `test_planner.py`, `test_researcher.py`, `test_writer.py`: Agent tests
- `test_react_article.py`: End-to-end ReACT agent tests
- `test_memory_fix.py`: Memory system tests
- `demo_*.py`: Demonstration scripts (not unit tests)

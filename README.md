# Article Creator with Memory-Enhanced ReACT Agent

An intelligent article generation system powered by DSPy and enhanced with memory capabilities for maintaining context and search sources across iterations.

## Features

### 🧠 Memory-Enhanced ReACT Agent
- **Persistent Memory**: Maintains context and search sources across multiple iterations
- **Intelligent Retrieval**: Similarity-based search for relevant previous information
- **Source Tracking**: Automatic tracking of all search results and research sources
- **Memory Management**: Automatic cleanup and size management to prevent overflow

### 🔍 Advanced Research Capabilities
- **Web Search Integration**: Powered by Brave Search for current information
- **Deep Research**: Multi-source research with synthesis and fact-checking
- **Context-Aware Reasoning**: Uses memory context to inform research decisions
- **Article Generation**: Specialized agent for comprehensive article creation

### 📝 Article Generation
- **Multi-Phase Research**: Enhanced reasoning, research, and synthesis phases
- **Source Attribution**: All information properly attributed to sources
- **Structured Output**: Organized article outlines with detailed content
- **Memory Persistence**: Research findings persist across article generation sessions

## Installation

### Prerequisites

1. **Python 3.11+**: Required for the project
2. **OpenAI API Key**: For DSPy language model integration
3. **Brave Search API Key**: For web search capabilities

### Setup

1. **Clone the repository**:
```bash
git clone <repository-url>
cd article_creator
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
# or using uv
uv sync
```

3. **Set up environment variables**:
```bash
export OPENAI_API_KEY="your-openai-api-key"
export BRAVE_API_KEY="your-brave-search-api-key"
```

## Quick Start

### Basic ReACT Agent with Memory

```python
from src.react_module import ReACTAgent
from src.bravesearch import OptimizedBraveSearch

# Initialize with memory
search_tool = OptimizedBraveSearch()
agent = ReACTAgent(brave_search=search_tool, memory_size=1000)

# Research with memory persistence
result = agent.forward(
    goal="Research current trends in AI agents",
    max_iterations=5
)

print(f"Memory items: {result['memory_summary']['memory_size']}")
```

### Article Generation with Memory

```python
from src.react_module import ArticleReACTAgent

# Initialize article agent
article_agent = ArticleReACTAgent(brave_search=search_tool, memory_size=1000)

# Generate article with memory-enhanced research
result = article_agent.generate_article_with_research(
    topic="The Future of AI Agents in Software Development",
    initial_outline={
        "title": "AI Agents in Development",
        "sections": ["Introduction", "Current State", "Future Trends", "Conclusion"]
    }
)
```

## Demo Scripts

### Memory Demo
Run the comprehensive memory demo to see all features in action:

```bash
python demo_memory_react.py
```

This demo showcases:
- Basic memory functionality
- Article generation with memory
- Memory persistence across sessions
- Memory statistics and insights

### Enhanced Article Demo
Run the enhanced article generation demo:

```bash
python demo_enhanced_article.py
```

## Memory System

The memory system provides sophisticated capabilities for maintaining context:

### Memory Categories
- **Search Results**: Cached web search results indexed by query
- **Research Findings**: Deep research results organized by topic
- **Fact Checks**: Verified claims and verification status
- **Context**: Relevant contextual information with relevance scores
- **Sources**: Source URLs with metadata for attribution
- **Insights**: Key learnings categorized by type

### Key Features
- **Similarity-Based Retrieval**: Find relevant information using keyword matching
- **Automatic Management**: Configurable size limits with access-based cleanup
- **Context Integration**: Memory context included in ReACT reasoning
- **Source Tracking**: All information properly attributed to sources

For detailed memory documentation, see [MEMORY_FEATURES.md](MEMORY_FEATURES.md).

## Configuration

### Memory Size
Configure memory size based on your needs:

```python
# Small memory for simple tasks
agent = ReACTAgent(brave_search=search_tool, memory_size=100)

# Large memory for complex research
agent = ReACTAgent(brave_search=search_tool, memory_size=5000)
```

### DSPy Configuration
The system uses DSPy for language model integration:

```python
import dspy

# Configure with OpenAI
lm = dspy.OpenAI(model="gpt-4o-mini", max_tokens=1000)
dspy.settings.configure(lm=lm)
```

## Project Structure

```
article_creator/
├── src/
│   ├── react_module.py          # Memory-enhanced ReACT agent
│   ├── bravesearch.py           # Brave Search integration
│   ├── research_assistant.py    # Research and fact-checking
│   ├── enhanced_article_creator.py  # Enhanced article generation
│   └── utils.py                 # Utility functions
├── data/
│   └── articles/                # Generated articles
├── demo_memory_react.py         # Memory demo script
├── demo_enhanced_article.py     # Article generation demo
├── MEMORY_FEATURES.md           # Memory system documentation
└── ENHANCED_FEATURES.md         # Enhanced features documentation
```

## API Reference

### ReACTAgent
- `forward(goal, max_iterations)`: Execute ReACT loop with memory
- `memory`: Access to memory system for custom operations

### ArticleReACTAgent
- `generate_article_with_research(topic, initial_outline)`: Generate article with research
- Inherits all ReACTAgent capabilities

### Memory System
- `get_relevant_search_results(query, max_results)`: Get similar search results
- `get_research_findings(topic)`: Get research findings for topic
- `get_memory_summary()`: Get memory statistics
- See [MEMORY_FEATURES.md](MEMORY_FEATURES.md) for full API reference

## Benefits

### Efficiency
- **Reduced Redundant Searches**: Similar queries use cached results
- **Faster Research**: Previous findings are reused
- **Context Preservation**: Information persists across iterations

### Quality
- **Better Reasoning**: Context from previous actions informs decisions
- **Source Tracking**: All information is properly attributed
- **Consistency**: Related research builds on previous findings

### Scalability
- **Memory Management**: Automatic cleanup prevents memory overflow
- **Configurable Limits**: Adjust memory size based on needs
- **Performance Optimization**: Efficient retrieval algorithms

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support:
- Check the documentation in [MEMORY_FEATURES.md](MEMORY_FEATURES.md) and [ENHANCED_FEATURES.md](ENHANCED_FEATURES.md)
- Run the demo scripts to see examples
- Review the source code for implementation details

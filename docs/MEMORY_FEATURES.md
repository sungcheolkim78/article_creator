# Memory-Enhanced ReACT Agent

This document describes the memory capabilities added to the ReACT agent, enabling it to maintain context and search sources across iterations.

## Overview

The memory-enhanced ReACT agent includes a sophisticated memory system that allows it to:

- **Store and retrieve search results** based on query similarity
- **Maintain research findings** organized by topic
- **Cache fact-check results** for future reference
- **Track contextual information** with relevance scoring
- **Manage source URLs and metadata** for attribution
- **Store key insights** categorized by type
- **Automatically manage memory size** to prevent overflow

## Memory System Architecture

### Memory Class

The `Memory` class provides the core memory functionality:

```python
class Memory:
    def __init__(self, max_memory_size: int = 1000):
        self.memory_store = {
            "search_results": {},      # Store search results by query hash
            "research_findings": {},   # Store research findings by topic
            "fact_checks": {},         # Store fact verification results
            "context": [],             # Store contextual information
            "sources": {},             # Store source URLs and metadata
            "insights": [],            # Store key insights and learnings
            "action_history": []       # Store action patterns and outcomes
        }
```

### Memory Storage Categories

1. **Search Results**: Cached web search results indexed by query hash
2. **Research Findings**: Deep research results organized by topic
3. **Fact Checks**: Verified claims and their verification status
4. **Context**: Relevant contextual information with relevance scores
5. **Sources**: Source URLs with metadata (title, content snippets, etc.)
6. **Insights**: Key learnings and insights categorized by type
7. **Action History**: Patterns and outcomes of previous actions

## Key Features

### 1. Intelligent Memory Retrieval

The memory system uses similarity-based retrieval to find relevant information:

```python
# Get relevant search results based on query similarity
relevant_searches = memory.get_relevant_search_results("AI agents", max_results=3)

# Get research findings for a specific topic
findings = memory.get_research_findings("machine learning")

# Get relevant context for a query
context = memory.get_relevant_context("AI frameworks", max_context=2)
```

### 2. Automatic Memory Management

The system automatically manages memory size to prevent overflow:

- **Access-based cleanup**: Least accessed items are removed first
- **Configurable size limits**: Set maximum memory size during initialization
- **Category-based management**: Each memory category is managed independently

### 3. Context-Aware Reasoning

The ReACT agent now includes memory context in its reasoning:

```python
# Memory context is automatically included in ReACT reasoning
react_output = self.react_step(
    goal=goal,
    available_tools=self.tools_description,
    previous_actions=previous_actions_str,
    memory_context=memory_context  # New field
)
```

### 4. Source Tracking

All search results and research findings are automatically tracked with their sources:

```python
# Sources are automatically extracted and stored
for search_result in result.get("results", []):
    if "url" in search_result:
        self.memory.add_source(
            url=search_result["url"],
            source_info={
                "title": search_result.get("title", ""),
                "snippet": search_result.get("snippet", ""),
                "query": action_input
            }
        )
```

## Usage Examples

### Basic ReACT Agent with Memory

```python
from react_module import ReACTAgent
from bravesearch import OptimizedBraveSearch

# Initialize with memory
search_tool = OptimizedBraveSearch()
agent = ReACTAgent(brave_search=search_tool, memory_size=1000)

# First goal - builds memory
result1 = agent.forward(
    goal="Research AI agents and their applications",
    max_iterations=3
)

# Second goal - uses memory for context
result2 = agent.forward(
    goal="Research AI agent frameworks",
    max_iterations=3
)

# Memory summary
print(f"Memory items: {result2['memory_summary']['memory_size']}")
```

### Article Generation with Memory

```python
from react_module import ArticleReACTAgent

# Initialize article agent with memory
article_agent = ArticleReACTAgent(brave_search=search_tool, memory_size=1000)

# Generate article with memory-enhanced research
result = article_agent.generate_article_with_research(
    topic="The Future of AI Agents",
    initial_outline={"title": "AI Agents", "sections": [...]}
)

# Access memory insights
insights = article_agent.memory.get_recent_insights(max_insights=5)
```

## Memory API Reference

### Core Methods

#### Storage Methods

- `add_search_result(query, results, metadata)`: Store search results
- `add_research_finding(topic, finding)`: Store research findings
- `add_fact_check(claim, verification)`: Store fact check results
- `add_context(context, relevance_score)`: Store contextual information
- `add_source(url, source_info)`: Store source information
- `add_insight(insight, category)`: Store key insights

#### Retrieval Methods

- `get_relevant_search_results(query, max_results)`: Get similar search results
- `get_research_findings(topic)`: Get research findings for topic
- `get_fact_check(claim)`: Get fact check result for claim
- `get_relevant_context(query, max_context)`: Get relevant context
- `get_recent_insights(category, max_insights)`: Get recent insights
- `get_memory_summary()`: Get memory statistics

### Memory Summary Structure

```python
{
    "total_search_results": 15,
    "total_research_findings": 8,
    "total_fact_checks": 3,
    "total_context_items": 12,
    "total_sources": 25,
    "total_insights": 6,
    "memory_size": 69
}
```

## Benefits

### 1. Improved Efficiency

- **Reduced redundant searches**: Similar queries use cached results
- **Faster research**: Previous findings are reused
- **Context preservation**: Information persists across iterations

### 2. Enhanced Quality

- **Better reasoning**: Context from previous actions informs decisions
- **Source tracking**: All information is properly attributed
- **Consistency**: Related research builds on previous findings

### 3. Scalability

- **Memory management**: Automatic cleanup prevents memory overflow
- **Configurable limits**: Adjust memory size based on needs
- **Performance optimization**: Efficient retrieval algorithms

## Configuration

### Memory Size

Configure memory size during agent initialization:

```python
# Small memory for simple tasks
agent = ReACTAgent(brave_search=search_tool, memory_size=100)

# Large memory for complex research
agent = ReACTAgent(brave_search=search_tool, memory_size=5000)
```

### Memory Persistence

For production use, consider implementing memory persistence:

```python
# Example: Save memory to disk
import pickle

def save_memory(agent, filename):
    with open(filename, 'wb') as f:
        pickle.dump(agent.memory.memory_store, f)

def load_memory(agent, filename):
    with open(filename, 'rb') as f:
        agent.memory.memory_store = pickle.load(f)
```

## Demo

Run the memory demo to see the features in action:

```bash
python demo_memory_react.py
```

The demo showcases:
- Basic memory functionality
- Article generation with memory
- Memory persistence across sessions
- Memory statistics and insights

## Future Enhancements

Potential improvements to the memory system:

1. **Vector-based similarity**: Use embeddings for better similarity matching
2. **Persistent storage**: Database integration for long-term memory
3. **Memory compression**: Intelligent summarization of stored information
4. **Temporal awareness**: Time-based memory decay and relevance
5. **Multi-agent memory**: Shared memory across multiple agents 
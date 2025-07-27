# DDGSearchTool - DuckDuckGo Search Integration for DSPy

This module provides DuckDuckGo search functionality integrated with the DSPy framework, similar to the BraveSearchTool but using the `duckduckgo_search` library.

## Features

- **DDGSearchTool**: Basic search functionality with DuckDuckGo
- **OptimizedDDGSearch**: Advanced search with query optimization and filtering
- **DSPy Integration**: Compatible with DSPy's retrieval modules
- **Multiple Search Types**: Text search, news search, and filtered search
- **Structured Results**: Returns `SearchResult` objects with title, URL, snippet, and metadata

## Installation

```bash
pip install duckduckgo-search dspy-ai
```

## Usage

### Basic Search

```python
from src.ddgsearch import DDGSearchTool

# Initialize the search tool
search_tool = DDGSearchTool(k=5)  # Get 5 results

# Perform a search
results = search_tool.search("Python programming")

# Access results
for result in results:
    print(f"Title: {result.title}")
    print(f"URL: {result.url}")
    print(f"Snippet: {result.snippet}")
    print(f"Published: {result.published_time}")
```

### News Search

```python
# Search for news articles
news_results = search_tool.search_news("artificial intelligence")

for result in news_results:
    print(f"News: {result.title}")
    print(f"URL: {result.url}")
```

### Advanced Search with Filters

```python
from src.ddgsearch import OptimizedDDGSearch

# Initialize optimized search tool
optimized_tool = OptimizedDDGSearch(k=3)

# Search with filters
filtered_results = optimized_tool.search_with_filters(
    query="machine learning",
    region_filter="us-en",  # US English results
    time_filter="m"         # Last month
)
```

### DSPy Integration

```python
import dspy
from src.ddgsearch import DDGSearchTool

# Use as a DSPy retrieval module
retriever = DDGSearchTool(k=3)

# DSPy will automatically call the forward method
snippets = retriever.forward("Python tutorials")
```

## Configuration Options

### DDGSearchTool Parameters

- `k` (int): Number of results to return (default: 5)
- `region` (str): Search region (default: "us-en")
- `safesearch` (str): Safe search level - "on", "moderate", "off" (default: "moderate")
- `backend` (str): Search backend - "auto", "html", "lite", "bing" (default: "auto")
- `max_results` (int): Maximum results to fetch (default: None)

### Search Filters

- `region_filter`: Specify region for filtered searches
- `time_filter`: Time limit - "d" (day), "w" (week), "m" (month), "y" (year)

## SearchResult Object

```python
@dataclass
class SearchResult:
    title: str           # Page title
    url: str            # Page URL
    snippet: str        # Page description/snippet
    extra_snippets: List[str] = None  # Additional snippets (not available in DuckDuckGo)
    published_time: Optional[str] = None  # Publication date (if available)
```

## Comparison with BraveSearchTool

| Feature | DDGSearchTool | BraveSearchTool |
|---------|---------------|-----------------|
| API Key Required | ❌ No | ✅ Yes |
| Rate Limits | ✅ Generous | ⚠️ API dependent |
| News Search | ✅ Yes | ✅ Yes |
| Query Optimization | ✅ Yes (OptimizedDDGSearch) | ✅ Yes (OptimizedBraveSearch) |
| Extra Snippets | ❌ No | ✅ Yes |
| Region Support | ✅ Yes | ✅ Yes |
| Time Filtering | ✅ Yes | ✅ Yes |

## Error Handling

The tools handle errors gracefully and return empty lists when:
- Network connection issues occur
- Invalid search queries are provided
- API rate limits are exceeded
- JSON parsing errors occur

## Example Output

```
=== DDGSearchTool Example ===

1. Basic Search:
  1. python - How to use pigpio to control a servo motor with a keyboard ...
     Apr 10, 2015 · I'm not sure if anyone will write the code for you. It's too broad a question. You ne...

  2. How to program a USB device with Debian/Python
     Apr 19, 2016 · The specific application I have in mind is a JMRI type system to access a model railr...

2. News Search:
  1. Trump administration's new artificial intelligence plan focuses on deregulation, beating China
     The White House on Wednesday released its promised "AI Action Plan," a sweeping agenda aimed at prom...
```

## Notes

- The `duckduckgo_search` library shows a deprecation warning suggesting to use `ddgs` instead
- The OptimizedDDGSearch requires an LM (Language Model) to be configured for query optimization
- DuckDuckGo doesn't provide extra snippets like Brave Search does
- All searches are performed through DuckDuckGo's public search interface 
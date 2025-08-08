# Refactoring Summary: Common Utility Functions

## Overview
This refactoring extracted common functions from `cli.py` and `app.py` into shared utility functions in `utils/utils.py` to eliminate code duplication and improve maintainability.

## Changes Made

### 1. Enhanced `utils/utils.py`
Added the following shared utility functions:

#### Core Functions
- `setup_search_tool()` - Setup search tools (Brave/DuckDuckGo)
- `generate_article()` - Main article generation logic
- `calculate_article_metrics()` - Calculate article statistics
- `save_article_to_file()` - Save articles to files
- `check_environment()` - Check required environment variables

#### Configuration Functions
- `get_available_llm_models()` - List of supported LLM models
- `get_available_languages()` - List of supported languages
- `get_available_search_tools()` - List of available search tools
- `get_available_modes()` - List of generation modes

### 2. Refactored `cli.py`
**Removed duplicate functions:**
- `setup_search_tool()` → Uses shared function
- `generate_article()` → Uses shared function
- `save_article_to_file()` → Uses shared function
- `check_environment()` → Uses shared function

**Simplified functions:**
- `display_article_metrics()` → Now uses `calculate_article_metrics()`
- `check_environment_cli()` → Wrapper around shared function with CLI-specific output

**Updated imports:**
- Now imports shared functions from `utils.utils`
- Uses configuration functions for argument choices

### 3. Refactored `app.py`
**Removed duplicate functions:**
- `setup_search_tool()` → Uses shared function
- `generate_article()` → Uses shared function
- `save_article_to_file()` → Uses shared function

**Simplified functions:**
- `display_article_metrics()` → Now uses `calculate_article_metrics()`
- `check_environment_streamlit()` → Wrapper around shared function with Streamlit-specific output

**Updated imports:**
- Now imports shared functions from `utils.utils`
- Uses configuration functions for selectbox choices

## Benefits

### 1. Code Reduction
- **Before:** ~438 lines in `cli.py` + ~548 lines in `app.py` = 986 lines
- **After:** ~313 lines in `cli.py` + ~423 lines in `app.py` = 736 lines
- **Reduction:** ~250 lines (25% reduction)

### 2. Maintainability
- Single source of truth for core logic
- Changes to article generation only need to be made in one place
- Consistent behavior between CLI and Streamlit interfaces

### 3. Consistency
- Both interfaces now use identical core functions
- Same error handling and validation logic
- Unified configuration management

### 4. Extensibility
- Easy to add new LLM models, languages, or search tools
- Centralized configuration makes updates simple
- New interfaces can reuse existing utility functions

## Key Design Decisions

### 1. Lazy Imports
Used lazy imports in `utils/utils.py` to avoid circular import issues:
```python
# Import here to avoid circular imports
from bravesearch import OptimizedBraveSearch
from ddgsearch import OptimizedDDGSearch
```

### 2. Interface-Specific Wrappers
Created interface-specific wrapper functions for environment checking:
- `check_environment_cli()` for CLI output
- `check_environment_streamlit()` for Streamlit output

### 3. Configuration Functions
Centralized configuration in utility functions:
- `get_available_llm_models()`
- `get_available_languages()`
- `get_available_search_tools()`
- `get_available_modes()`

### 4. Error Handling
Maintained consistent error handling across both interfaces while allowing for interface-specific error display.

## Testing
Both `cli.py` and `app.py` maintain their original functionality while sharing common code. The refactoring is backward compatible and doesn't change the user experience.

## Future Improvements
1. Add unit tests for the shared utility functions
2. Consider creating a dedicated configuration module
3. Add logging to the shared functions for better debugging
4. Consider creating interface-specific display adapters

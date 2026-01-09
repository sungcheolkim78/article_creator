# Code Review: `src/agents/researcher.py`

## Overview
The `ArticleReACTResearcher` class implements a ReACT-based research agent for article generation. This review identifies issues and suggests improvements.

## Critical Issues

### 1. **Class-Level State Mutation (Line 24)**
```python
ReACTGoal.instructions += "\n" + self.memory_tools.research_strategy + "\n" + self.memory_tools.action_plan
```
**Problem**: Mutating a class-level attribute in `__init__` causes shared state across instances. If multiple `ArticleReACTResearcher` instances are created, they will overwrite each other's instructions.

**Impact**: High - Can cause incorrect behavior in multi-instance scenarios.

**Fix**: Create instance-specific instructions or use a different pattern.

### 2. **Unsafe File Operations (Line 54)**
```python
def save(self, filepath: str):
    with open(filepath, "w") as f:
        f.write(...)
```
**Problem**: 
- No error handling for file I/O failures
- Doesn't create parent directories if they don't exist
- No encoding specification (should use UTF-8)

**Impact**: Medium - Can fail silently or crash on file system issues.

### 3. **Missing Error Handling**
- `forward()` method has no try/except around `self.react()` call
- No validation of input parameters
- No handling for missing attributes in `output`

**Impact**: Medium - Unhandled exceptions can crash the application.

## Code Quality Issues

### 4. **Typo in Docstring (Line 10)**
```python
"The goal is to research the topic and create a comprehensive outline and collect orgarnized information."
```
**Fix**: "orgarnized" → "organized"

### 5. **Magic Number (Line 41)**
```python
iterations = len(output.trajectory) // 4
```
**Problem**: Unclear why division by 4. Should be documented or extracted to a constant.

**Suggestion**: Add comment explaining the trajectory structure or use a named constant.

### 6. **Inconsistent Logging (Lines 36-46)**
**Problem**: Uses `print()` statements instead of proper logging, mixing with `click.style()` for formatting.

**Impact**: Low - But inconsistent with logging patterns elsewhere in codebase.

**Suggestion**: Use `logger` for debug/info messages, keep `print()` only for user-facing output if needed.

### 7. **Unused Imports**
```python
from pathlib import Path
from datetime import datetime
```
**Problem**: These imports are never used in the file.

**Impact**: Low - Just clutter.

### 8. **Missing Type Hints**
- `save()` method parameter `filepath` has type hint, but return type is missing
- Could add more specific type hints for better IDE support

### 9. **Missing Docstrings**
- `ArticleReACTResearcher` class lacks a docstring
- `forward()` and `save()` methods lack docstrings

## Potential Improvements

### 10. **Performance Considerations**
- The ReACT loop runs up to 10 iterations, which could be slow
- No caching or optimization similar to what was done in `ReACTSearcher`
- Consider adding similar batch/parallel processing if applicable

### 11. **Code Organization**
- The `ReACTGoal` signature is defined in this file but might be better placed in a shared location if reused
- Consider extracting trajectory parsing logic into a helper method

### 12. **Accessing Potentially Missing Attributes**
```python
output.final_title
output.final_sections
output.final_section_subheadings
```
**Problem**: No validation that these attributes exist before accessing.

**Suggestion**: Add error handling or use `getattr()` with defaults.

## Recommendations Priority

### High Priority
1. Fix class-level state mutation (Issue #1)
2. Add error handling to `forward()` and `save()` (Issue #3)
3. Fix file operations in `save()` (Issue #2)

### Medium Priority
4. Fix typo (Issue #4)
5. Document magic number (Issue #5)
6. Remove unused imports (Issue #7)
7. Add docstrings (Issue #9)

### Low Priority
8. Improve logging consistency (Issue #6)
9. Add missing type hints (Issue #8)
10. Consider performance optimizations (Issue #10)

## Suggested Refactored Code Structure

```python
class ArticleReACTResearcher(dspy.Module):
    """ReACT-based researcher for article generation.
    
    Uses ReACT reasoning to research topics and create comprehensive
    article outlines with organized information.
    """
    
    # Constants
    TRAJECTORY_ENTRIES_PER_ITERATION = 4
    
    def __init__(self, memory_tools: MemoryTools, verbose: bool = False):
        # Create instance-specific instructions
        instructions = (
            ReACTGoal.instructions or ""
            + "\n" + memory_tools.research_strategy
            + "\n" + memory_tools.action_plan
        )
        # Store instructions per instance, don't mutate class
        self._instructions = instructions
        
        # ... rest of init
```



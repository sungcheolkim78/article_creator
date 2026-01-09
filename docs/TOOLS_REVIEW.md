# Code Review: `src/agents/tools.py`

## Overview
The `MemoryTools` class provides article generation tools with memory capabilities. This review identifies issues and suggests improvements.

## Critical Issues

### 1. **Type Mismatch in `analyze()` Method (Line 103)**
```python
output: str = self.analyzer(
    question=question, web_search_results=self.search_results
).analysis_content
```
**Problem**: `self.search_results` is a `list[str]`, but `AnalyzedInfo.web_search_results` expects a `str` (line 204).

**Impact**: High - Will cause runtime errors or incorrect behavior when the analyzer tries to process a list instead of a string.

**Fix**: Convert list to string, e.g., `"\n\n".join(self.search_results)`

### 2. **Unsafe Property Access in `outline_str` (Lines 166-174)**
```python
@property
def outline_str(self) -> str:
    outline_str = json.dumps(
        {
            "title": self.title,
            "sections": self.sections,
            "section_subheadings": self.section_subheadings,
        }
    )
```
**Problem**: Accesses `self.title`, `self.sections`, and `self.section_subheadings` which are only set when `outline()` is called. If accessed before calling `outline()`, will raise `AttributeError`.

**Impact**: High - Will crash if `outline_str` is accessed before `outline()` is called.

**Fix**: Add validation or use `getattr()` with defaults.

### 3. **Typo: "infomation_gap" → "information_gap" (Lines 132, 229)**
```python
).infomation_gap  # type: ignore[attr-defined]
```
**Problem**: Typo in attribute name - should be "information_gap" not "infomation_gap".

**Impact**: Medium - May cause confusion and potential bugs if the actual attribute name differs.

**Fix**: Correct the spelling to "information_gap".

### 4. **Missing Error Handling**
Multiple methods lack error handling:
- `search_web()` - No try/except around searcher creation or execution
- `analyze()` - No error handling for analyzer failures
- `outline()` - No error handling for outliner failures
- `research_gap()` - No error handling
- `plan()` - No error handling

**Impact**: Medium - Unhandled exceptions can crash the application.

**Fix**: Add try/except blocks with appropriate error handling and logging.

## Code Quality Issues

### 5. **Missing Input Validation**
- No validation for empty strings in `search_web()`, `analyze()`, `outline()`, etc.
- No validation for `mode` parameter in `__init__` (only checked in `search_web()`)
- No validation for `engine` parameter

**Impact**: Medium - Invalid inputs can cause unexpected behavior.

### 6. **Inconsistent Attribute Access**
- Some methods use direct attribute access (e.g., `outcome.title`)
- Others use type ignores (e.g., `# type: ignore[attr-defined]`)
- No validation that attributes exist before access

**Impact**: Low - But inconsistent and could lead to runtime errors.

### 7. **Docstring Grammar Issues**
- Line 201: "generate a analysis" → "generate an analysis"
- Line 225: "Given a outline" → "Given an outline"
- Line 236: "create an comprehensive" → "create a comprehensive"

**Impact**: Low - Just documentation quality.

### 8. **Missing Type Hints**
- `tool_list()` returns `list[Callable]` but could be more specific
- Some return types could be more precise

**Impact**: Low - Reduces IDE support and type checking benefits.

### 9. **Potential AttributeError in `get_sources()` (Line 162)**
```python
content = "\n".join([item.to_markdown() for item in self.sources])
```
**Problem**: Assumes all items in `self.sources` have a `to_markdown()` method. No validation.

**Impact**: Medium - Will fail if sources contain unexpected types.

### 10. **Unused Attributes**
- `self.memory_content` (line 51) - Set but never used
- `self.search_summary` (line 52) - Set but never used
- `self.source_content` (line 53) - Set but never used

**Impact**: Low - Just dead code.

### 11. **Inefficient String Concatenation in `available_tools` (Lines 177-182)**
```python
available_tools = "The available tools are:"
available_tools += f"\ntool_search_web: {self.search_web.__doc__ or ''}"
```
**Problem**: Multiple string concatenations. Could use list join or f-string.

**Impact**: Low - Minor performance issue.

### 12. **Missing Docstrings**
- `get_findings()` - Has docstring but could be more detailed
- `get_sources()` - Has docstring but could be more detailed
- `tool_list()` - No docstring
- `report()` - No docstring

**Impact**: Low - Reduces code maintainability.

## Recommendations Priority

### High Priority
1. Fix type mismatch in `analyze()` (Issue #1)
2. Fix unsafe property access in `outline_str` (Issue #2)
3. Fix typo "infomation_gap" (Issue #3)
4. Add error handling to critical methods (Issue #4)

### Medium Priority
5. Add input validation (Issue #5)
6. Fix potential AttributeError in `get_sources()` (Issue #9)
7. Remove or use unused attributes (Issue #10)

### Low Priority
8. Fix docstring grammar (Issue #7)
9. Improve type hints (Issue #8)
10. Add missing docstrings (Issue #12)
11. Optimize string concatenation (Issue #11)

## Suggested Code Improvements

### Fix for `analyze()` method:
```python
@execution_time
def analyze(self, question: str) -> str:
    """Generate a comprehensive analysis of the question with internal web search results."""
    logger.debug("Using analyze tool")
    
    if not question:
        raise ValueError("question cannot be empty")
    
    # Convert list to string for the analyzer
    web_search_results_str = "\n\n".join(self.search_results) if self.search_results else ""
    
    try:
        output: str = self.analyzer(
            question=question, web_search_results=web_search_results_str
        ).analysis_content  # type: ignore[attr-defined]
    except Exception as e:
        logger.error("Analysis failed: %s", e)
        raise
    
    output_str = f"## Analysis of |{question}|\n\n{output}"
    self.analysis_results.append(output_str)
    return output_str
```

### Fix for `outline_str` property:
```python
@property
def outline_str(self) -> str:
    """Get the current outline as a JSON string."""
    title = getattr(self, "title", "")
    sections = getattr(self, "sections", [])
    section_subheadings = getattr(self, "section_subheadings", {})
    
    return json.dumps(
        {
            "title": title,
            "sections": sections,
            "section_subheadings": section_subheadings,
        }
    )
```



---
name: code-pruner
description: Prune unreachable code branches based on known parameter values. Use when the user wants to simplify code by removing execution paths that cannot occur given specific parameter constraints. Works with any programming language.
---

# Code Pruner

Removes unreachable code branches based on known parameter values.

## Usage

Given a code file and parameter constraints, this skill analyzes control flow and removes branches that cannot execute.

### Input Format

**Code file:** Path to the source file

**Parameter constraints:** Describe in natural language, e.g.:
- "`enableJsonResponse` is always true"
- "`mode` equals 'production'"
- "`count` is greater than 0"
- "`user` is null"

### What Gets Pruned

- `if/else` branches with known outcomes
- Switch/case arms that cannot match
- Early returns that always/never trigger
- Loop bodies that never execute (e.g., `while(false)`)
- Dead code after unconditional returns

### Output

Clean, pruned code with:
- Unreachable branches removed
- Remaining code properly indented
- Comments indicating what was pruned (optional)

## Process

### Step 1: Parse Constraints
Identify which variables have known values from the user's description.

### Step 2: Load Code File
**CRITICAL: Read the entire file at once.** Do NOT read line-by-line or in chunks.
- Use `read` without offset/limit to load complete file into context
- This enables global analysis and avoids repeated context rebuilding
- If file exceeds context window, use `exec` with `cat` or `head/tail` to extract relevant sections

### Step 3: Systematic Code Analysis
With the complete file in context:

**3.1 Locate all conditional expressions containing target variables**
- Scan for: `if (variable)`, `if (variable == ...)`, `if (!variable)`, `when (variable)`, `switch (variable)`, etc.
- Identify method signatures using the variable as parameter
- Note constructor parameters and field declarations

**3.2 Evaluate each condition with known values**
- For `if (variable)` where value is truthy: false branch is unreachable
- For `if (!variable)` where value is truthy: entire block is unreachable
- For `when` / `switch` / `case`: keep only matching arm, remove others
- For ternary operators: apply same logic

**3.3 Identify cascade deletions**
- Mark methods only called from unreachable branches
- Mark fields only accessed from unreachable code
- Track: deleted branches → their callers → exclusively used symbols

**3.4 Verify preserved code integrity**
- Ensure remaining code has no dangling references
- Check imports are still needed

### Step 4: Prune Unreachable Paths
Remove in order:
1. Unreachable branches (if/else/when/case)
2. Unreachable methods and functions
3. Unused fields, properties, and parameters
4. Unused imports and declarations

### Step 5: Generate Output
Output the complete pruned code. For large files, consider:
- Outputting only the modified sections with line markers
- Or using diff format to reduce token generation

## Example

**Input:**
```python
def process(data, skip_validation=False):
    if not skip_validation:
        validate(data)
    if data.get('type') == 'A':
        handle_a(data)
    else:
        handle_b(data)
```

**Constraint:** "`skip_validation` is true, `data['type']` is 'A'"

**Output:**
```python
def process(data, skip_validation=False):
    handle_a(data)
```

## Notes

- Preserves function signatures (parameters remain for compatibility)
- Does not evaluate complex expressions beyond simple comparisons
- Side effects in pruned branches are lost — review output carefully

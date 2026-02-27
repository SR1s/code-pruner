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

### Step 2: Systematic Code Analysis

**2.1 Locate all conditional expressions containing target variables**
- Search for: `if (variable)`, `if (variable == ...)`, `if (!variable)`, `when (variable)`, etc.
- Include: method calls using the variable as parameter

**2.2 Evaluate each condition with known values**
- For `if (enableJsonResponse)` where value is `true`: false branch is unreachable
- For `if (!enableJsonResponse)` where value is `true`: entire block is unreachable
- For `when` / `switch`: keep only matching case, remove others

**2.3 Identify cascade deletions**
- If a method becomes unreachable (only called from deleted branches), mark for removal
- If a field becomes unused, mark for removal
- Track dependencies: deleted code → callers → fields/methods only they used

**2.4 Verify preserved code integrity**
- Ensure remaining code references only existing symbols
- Check that required imports are still valid

### Step 3: Prune Unreachable Paths
Remove in order:
1. Unreachable branches (if/else/when)
2. Unreachable methods (no valid callers)
3. Unused fields and parameters
4. Unused imports

### Step 4: Generate Clean Output
Output simplified code with proper formatting.

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

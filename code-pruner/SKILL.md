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

1. **Parse constraints** — Identify which variables have known values
2. **Analyze control flow** — Evaluate conditions using known values
3. **Prune unreachable paths** — Remove branches that cannot execute
4. **Generate clean output** — Output simplified code

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

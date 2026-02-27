---
name: code-pruner
description: Prune unreachable code branches based on known parameter values. Use when the user wants to simplify code by removing execution paths that cannot occur given specific parameter constraints. Works with any programming language. Optimized version using line-based replacements for speed.
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
- Methods that become unreachable (only called from pruned code)

## Process

### Step 1: Parse Constraints
Identify which variables have known values from the user's description.

### Step 2: Load Code File
**CRITICAL: Read the entire file at once.** Do NOT read line-by-line or in chunks.
- Use `read` without offset/limit to load complete file into context
- This enables global analysis and avoids repeated context rebuilding

### Step 3: Find Target Code Locations
Scan the code for all locations where target variables are used:
- `if (variable)` / `if (!variable)` expressions
- `when` / `switch` statements
- Method calls using the variable
- Constructor parameters

### Step 4: Generate Replacement Instructions

**Output format: JSON replacement instructions**

Instead of generating the full diff, output a JSON object with line-based replacements:

```json
{
  "target_variable": "enableJsonResponse",
  "replacements": [
    {
      "start_line": 174,
      "end_line": 178,
      "new_code": "",
      "reason": "Delete if (!enableJsonResponse) block - always false"
    },
    {
      "start_line": 404,
      "end_line": 416,
      "new_code": "",
      "reason": "Delete closeSseStream method - only early return when enableJsonResponse=true"
    }
  ]
}
```

**Fields:**
- `start_line`: First line to replace (1-indexed)
- `end_line`: Last line to replace (exclusive, 1-indexed)
- `new_code`: Replacement code (empty string to delete)
- `reason`: Explanation for the change

**Benefits:**
- Model output: O(number of changes) tokens, not O(file size)
- External tool applies replacements in milliseconds
- Human can review the JSON decisions

### Step 5: Execute Replacements

Save the JSON to a file and run the line replacer:
```bash
python3 /root/.openclaw/workspace/line_replacer.py <file.kt> <replacements.json>
```

This will:
1. Apply replacements from end to start (avoiding line number shifts)
2. Generate unified diff
3. Save pruned file

## Example

**Input:**
```kotlin
// File: Server.kt, Constraint: enableJsonResponse = true

fun handleRequest() {
    if (!enableJsonResponse) {
        setupSse()
    }
    if (enableJsonResponse) {
        return JsonResponse()
    }
}
```

**Output (JSON):**
```json
{
  "target_variable": "enableJsonResponse",
  "replacements": [
    {
      "start_line": 4,
      "end_line": 6,
      "new_code": "",
      "reason": "Delete if (!enableJsonResponse) block - always false"
    },
    {
      "start_line": 7,
      "end_line": 9,
      "new_code": "return JsonResponse()",
      "reason": "Simplify if (enableJsonResponse) - condition always true"
    }
  ]
}
```

## Notes

- Line numbers must be accurate (use 1-indexed line numbers)
- Replacements are applied from end to start to avoid offset issues
- Side effects in pruned branches are lost — review output carefully
- For complex transformations, `new_code` can contain replacement code

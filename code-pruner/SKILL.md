---
name: code-pruner
description: Prune unreachable code branches based on known parameter values. Use when the user wants to simplify code by removing execution paths that cannot occur given specific parameter constraints. Works with any programming language. Optimized version using built-in edit tool for speed.
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

**Output format: JSON with old_string for direct edit**

Output a JSON object containing all replacements with the exact text to be replaced:

```json
{
  "target_variable": "enableJsonResponse",
  "replacements": [
    {
      "start_line": 174,
      "end_line": 178,
      "old_string": "if (!enableJsonResponse) {\n            activeStream?.let { stream ->\n                emitOnStream(streamId, stream.session, message)\n            }\n        }",
      "new_code": "",
      "reason": "Delete if (!enableJsonResponse) block - always false"
    },
    {
      "start_line": 191,
      "end_line": 203,
      "old_string": "if (enableJsonResponse) {\n            activeStream.call.response.header(...)\n            ...\n        }",
      "new_code": "activeStream.call.response.header(...)\n            ...",
      "reason": "Simplify if (enableJsonResponse) - remove wrapper, keep body"
    }
  ]
}
```

**Fields:**
- `start_line`: First line to replace (1-indexed, for reference)
- `end_line`: Last line to replace (1-indexed, for reference)
- `old_string`: **Exact text** to be replaced (must match file content precisely)
- `new_code`: Replacement code (empty string to delete)
- `reason`: Explanation for the change

**Important:** The `old_string` must match the file content exactly, including indentation and whitespace.

### Step 5: Execute Replacements Using Built-in Edit Tool

Apply replacements from **end to start** (highest line number first) to avoid line number shifts:

For each replacement in reverse order:
1. Use `edit` tool with `old_string` and `new_code`
2. Verify the edit succeeded

Example tool call:
```
edit(file_path="/path/to/file.kt", 
     old_string="if (!enableJsonResponse) {\n            activeStream?.let { stream ->\n                emitOnStream(streamId, stream.session, message)\n            }\n        }",
     new_code="")
```

### Step 6: Generate Diff

After all edits are applied, generate a unified diff showing all changes:
- Use `exec` with `diff -u` to compare original and modified files
- Or use `read` to show key sections

## Example

**Input:**
```kotlin
// File: Server.kt
// Constraint: enableJsonResponse = true

fun handleRequest() {
    if (!enableJsonResponse) {
        setupSse()
    }
    if (enableJsonResponse) {
        return JsonResponse()
    }
}
```

**Output (JSON with old_string):**
```json
{
  "target_variable": "enableJsonResponse",
  "replacements": [
    {
      "start_line": 4,
      "end_line": 6,
      "old_string": "    if (!enableJsonResponse) {\n        setupSse()\n    }",
      "new_code": "",
      "reason": "Delete if (!enableJsonResponse) block - always false"
    },
    {
      "start_line": 7,
      "end_line": 9,
      "old_string": "    if (enableJsonResponse) {\n        return JsonResponse()\n    }",
      "new_code": "    return JsonResponse()",
      "reason": "Simplify if (enableJsonResponse) - remove wrapper, keep body"
    }
  ]
}
```

**Execution:**
Apply edits in reverse order (line 9 first, then line 4) using `edit` tool.

## Notes

- Always include exact `old_string` with proper indentation
- Apply replacements from end to start to avoid line number shifts
- `old_string` must match file content precisely for `edit` to work
- Side effects in pruned branches are lost — review output carefully

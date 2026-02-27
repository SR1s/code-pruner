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
- **External-inaccessible methods** only called from pruned code (see Step 3.3)

### Output

**Unified diff format** showing only changes:
- Lines removed: prefixed with `-`
- Lines added/kept: prefixed with `+` or context
- Reduces token generation vs full file output

Optional: Provide full pruned file if explicitly requested.

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

**3.3 Identify cascade deletions (single file scope, external-inaccessible only)**
- Mark unreachable branches first
- Then mark methods **only called from unreachable code AND not externally accessible**
- **External accessibility check**: Skip `public` methods; only consider `private`, `internal`, or file-scoped methods
- Mark fields **only accessed from unreachable code**
- Track: deleted branches → their callers (if not public) → exclusively used symbols
- **Iterate**: After marking deletions, re-check if newly deleted code reveals more deletable methods
- **Stop when**: No new deletable methods found in current iteration

**3.4 Verify preserved code integrity**
- Ensure remaining code has no dangling references
- Check imports are still needed

### Step 4: Prune Unreachable Paths
Remove in order:
1. Unreachable branches (if/else/when/case)
2. Unreachable methods and functions (external-inaccessible only)
3. Unused fields, properties, and parameters
4. Unused imports and declarations

### Step 5: Generate Diff Output

**Output format: Unified diff**

Generate a unified diff showing only the changes:
```diff
--- original.kt
+++ pruned.kt
@@ -10,7 +10,6 @@
 import io.modelcontextprotocol.kotlin.sdk.types.JSONRPCMessage
-import io.modelcontextprotocol.kotlin.sdk.types.JSONRPCEmptyMessage
 import io.modelcontextprotocol.kotlin.sdk.types.JSONRPCResponse
```

**Benefits:**
- Token count ~ O(number of changed lines), not O(file size)
- Human can review what was removed
- Can be applied with `patch` command if needed

**If user requests full file:** Provide complete pruned code separately.

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

**Output (diff format):**
```diff
--- original.py
+++ pruned.py
@@ -1,8 +1,5 @@
 def process(data, skip_validation=False):
-    if not skip_validation:
-        validate(data)
-    if data.get('type') == 'A':
-        handle_a(data)
+    handle_a(data)
-    else:
-        handle_b(data)
```

## Notes

- Preserves function signatures (parameters remain for compatibility)
- Does not evaluate complex expressions beyond simple comparisons
- Side effects in pruned branches are lost — review output carefully
- **Limitation**: Only removes external-inaccessible methods; `public` methods are preserved even if seemingly unused

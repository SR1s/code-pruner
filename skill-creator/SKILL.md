---
name: skill-creator
description: Create new skills and iteratively improve them. Use when users want to create a skill from scratch, update or optimize an existing skill, or test skill performance. This skill guides the complete skill development lifecycle from intent capture to packaging.
---

# Skill Creator

A skill for creating new skills and iteratively improving them.

## The Core Loop

1. **Capture intent** — Understand what the skill should do
2. **Draft the skill** — Write SKILL.md and resources
3. **Create test cases** — 2-3 realistic prompts to verify functionality
4. **Run tests** — Execute with and without the skill
5. **Evaluate** — Review outputs, identify issues
6. **Improve** — Rewrite based on feedback
7. **Repeat** until satisfied
8. **Package** — Create distributable .skill file

## Creating a Skill

### Step 1: Capture Intent

Ask the user:
1. What should this skill enable Claude to do?
2. When should this skill trigger? (user phrases/contexts)
3. What's the expected output format?
4. Should we set up test cases? (Recommended for objective outputs like file transforms, data extraction, code generation)

### Step 2: Interview and Research

Ask about edge cases, input/output formats, example files, success criteria, and dependencies.

### Step 3: Write SKILL.md

Structure:
```yaml
---
name: skill-name
description: What it does AND when to use it. Be specific and slightly "pushy" to ensure triggering.
---

# Skill Title

Brief description.

## Usage

Instructions for using the skill.

## Resources

- scripts/ — if included
- references/ — if included  
- assets/ — if included
```

**Writing guidelines:**
- Use imperative form
- Keep under 500 lines
- Explain the "why", not just "what"
- Avoid heavy-handed MUSTs — explain reasoning instead
- Include concrete examples

### Step 4: Create Test Cases

Save to `evals/evals.json`:
```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User's task prompt",
      "expected_output": "Description of expected result",
      "files": []
    }
  ]
}
```

## Running Tests

### OpenClaw Adaptation

Since OpenClaw uses `sessions_spawn` instead of Claude Code's Task tool:

**With-skill run:**
```
Spawn a subagent with:
- Task: <eval prompt>
- Context: Load the skill from <skill-path>
- Save outputs to: <workspace>/iteration-N/eval-ID/with_skill/
```

**Baseline run:**
```
Spawn a subagent with:
- Task: Same prompt
- No skill context
- Save outputs to: <workspace>/iteration-N/eval-ID/without_skill/
```

Launch both in parallel using `sessions_spawn`.

### Test Workspace Structure

```
skill-workspace/
├── iteration-1/
│   ├── eval-1/
│   │   ├── with_skill/
│   │   │   └── outputs/
│   │   └── without_skill/
│   │       └── outputs/
│   └── eval-2/
│       └── ...
└── iteration-2/
    └── ...
```

## Evaluating Results

### Manual Review

Present results to the user:
1. Show the prompt
2. Show both outputs (with vs without skill)
3. Ask for feedback

### Simple Assertions (Optional)

For objective criteria, create `eval_metadata.json`:
```json
{
  "eval_id": 1,
  "eval_name": "descriptive-name",
  "prompt": "The user's task prompt",
  "assertions": [
    {"name": "output file exists", "check": "file_exists", "target": "output.docx"},
    {"name": "contains header", "check": "file_contains", "target": "output.docx", "text": "Header Text"}
  ]
}
```

Run checks with simple scripts rather than complex grading agents.

## Improving the Skill

Based on feedback:

1. **Generalize** — Don't overfit to test cases; find patterns
2. **Keep lean** — Remove parts that waste time
3. **Explain why** — Help the model understand reasoning
4. **Bundle repeated work** — If tests keep writing similar helper scripts, add them to `scripts/`

## Packaging

Create distributable .skill file:

```bash
cd /path/to/skill-parent
zip -r my-skill.skill my-skill/
```

Or use the package script:
```bash
python3 /root/.openclaw/skills/skill-creator/scripts/package-skill.py ./my-skill ./dist
```

## Skill Structure Reference

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter: name, description
│   └── Markdown instructions
└── Bundled Resources (optional)
    ├── scripts/    - Executable code
    ├── references/ - Documentation loaded on demand
    └── assets/     - Templates, icons, fonts
```

## Progressive Disclosure

1. **Metadata** (name + description) — Always in context
2. **SKILL.md body** — Loaded when skill triggers
3. **Bundled resources** — Loaded only when needed

Keep SKILL.md under 500 lines. Split into references/ when approaching limit.

## What NOT to Include

- README.md
- INSTALLATION_GUIDE.md
- QUICK_REFERENCE.md
- CHANGELOG.md

The skill should only contain what an AI agent needs to do the job.

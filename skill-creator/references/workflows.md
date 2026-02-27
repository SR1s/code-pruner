# Workflows

Patterns for designing multi-step skill workflows.

## Sequential Workflows

For processes that must happen in order:

1. **Validate inputs** - Check prerequisites before starting
2. **Execute steps** - Perform each operation in sequence
3. **Handle errors** - Stop or recover based on failure mode
4. **Return results** - Summarize what was done

## Conditional Logic

When decisions depend on context:

- Use explicit condition checks (file exists? command available?)
- Provide fallback paths for common failure modes
- Document decision criteria in the skill

## Error Handling Patterns

- **Fail fast**: Stop immediately on critical errors
- **Graceful degradation**: Continue with reduced functionality
- **Retry with backoff**: For transient failures (network, etc.)

## Checkpoint Pattern

For long-running workflows:

1. Save progress after each major step
2. Allow resume from last checkpoint
3. Clean up partial results on failure

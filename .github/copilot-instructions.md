# Engineering Instructions

## Working Style

- Be concise.
- Work on one task at a time.
- Do not make changes beyond the requested scope.
- Do not refactor unrelated code.
- Prefer the smallest change that solves the current problem.
- Do not introduce new abstractions, dependencies, or architectural
  changes unless they are necessary.

## Before Making Changes

- Understand the requested outcome before modifying code.
- Inspect the relevant existing implementation first.
- Identify existing patterns and conventions and follow them.
- If an important assumption is uncertain, surface it rather than
  silently inventing an answer.
- Prefer modifying existing patterns over introducing new ones.

## Implementation

- Make incremental changes.
- Preserve existing behavior unless changing it is explicitly part
  of the task.
- Keep the diff as small and reviewable as practical.
- Do not "clean up" neighboring code unless it is required for the task.

## Verification

After making a change:

1. Run the narrowest relevant tests/checks first.
2. Inspect the resulting diff.
3. Verify the requested behavior.
4. Report what changed and what was verified.
5. Call out anything that remains uncertain.

Do not claim success based only on code inspection when the behavior
can be tested.

## Debugging

When something fails:

- Do not immediately rewrite the implementation.
- Inspect the failure and form a hypothesis.
- Identify the most likfely cause.
- Test that hypothesis with the smallest useful experiment.
- Change one relevant variable at a time when practical.

## Product Context

Before proposing significant implementation work, establish:

1. What outcome are we trying to improve?
2. What evidence do we have about the current state?
3. What is the smallest intervention likely to affect that outcome?
4. What assumptions does the proposed change depend on?
5. What could regress or break?
6. How will we verify the change?
7. How will we know whether the original outcome improved?

Do not confuse implementing a feature with solving the underlying problem.
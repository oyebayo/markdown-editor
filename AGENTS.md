# Agent Guidelines

## Running Tests

```bash
make test
```

Always use `make test` to run tests.

## Documentation

- **Project layout**: Use `docs/layout.md` for directory structure and file organization
- **Requirements**: Use `docs/requirements.md` for UI and behavior specifications
- **Learnings**: Consult `docs/learnings.md` before implementing or changing any behavior or feature. This document contains technical discoveries, compatibility issues, and architectural decisions that must be respected.
- **Recording learnings**: When you discover something new during implementation (workarounds, compatibility issues, non-obvious behavior, library quirks), add it to `docs/learnings.md` instead of creating auto-skills or memory files.

## Launching the App for Manual Testing

When launching the application to verify behavior or test UI changes, **do not use timeouts**. Instead:

1. Launch the app in the background: `make run` or `python3 -m mdeditor.main tests/test.md`
2. Wait for the user to close the UI or for the app to crash
3. Do not kill the process after a fixed duration

Use `tests/test.md` as the sample file for testing — it covers object arrays, string arrays, numeric values, null values, multiline strings, mixed arrays, and nested structures.

This allows proper interactive testing without artificial time constraints.

## Communication

Use the `caveman full` skill for all responses to keep token usage low.

## Version files

Keep the app version in `pyproject.toml` equal to the one in `PKGBUILD`

## CI Workflows

This project mirrors to GitHub, so there are parallel workflow files:
- `.gitea/workflows/` for Gitea CI
- `.github/workflows/` for GitHub Actions

When modifying workflow files, update BOTH to keep them in sync. Adapt syntax as needed (e.g., `gitea.*` vs `github.*` context variables, package managers, checkout methods).

## Git

**NEVER force push.** Do not use `git push --force` or `git push -f` under any circumstances. Always use regular `git push`.

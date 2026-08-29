# Issue tracker: GitHub

Issues and PRDs for this repo live as GitHub issues in `hilt21/hilt21`. Use the `gh` CLI for all operations.

## Conventions

- **Create an issue**: `gh issue create --repo hilt21/hilt21 --title "..." --body-file <file>`.
- **Read an issue**: `gh issue view <number> --repo hilt21/hilt21 --comments`, also fetching labels when needed.
- **List issues**: `gh issue list --repo hilt21/hilt21 --state open --json number,title,body,labels,comments` with appropriate label and state filters.
- **Comment on an issue**: `gh issue comment <number> --repo hilt21/hilt21 --body "..."`.
- **Apply or remove labels**: use `gh issue edit` with `--add-label` or `--remove-label`.
- **Close an issue**: `gh issue close <number> --repo hilt21/hilt21 --comment "..."`.

## Pull requests as a triage surface

**PRs as a request surface: no.**

GitHub shares one number space across issues and pull requests. Resolve an ambiguous number with `gh pr view`, then fall back to `gh issue view`.

## Skill operations

- When a skill says **publish to the issue tracker**, create a GitHub issue in `hilt21/hilt21`.
- When a skill says **fetch the relevant ticket**, read that issue and its comments from `hilt21/hilt21`.
- Map and child-ticket workflows should use GitHub sub-issues and native dependencies when available; otherwise use task-list and `Blocked by:` fallbacks.

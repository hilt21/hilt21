# Domain Docs

This repository uses a single domain context.

## Before exploring

- Read `CONTEXT.md` at the repository root when it exists.
- Read relevant decisions under `docs/adr/` when that directory exists.
- If either location is absent, proceed silently; domain documentation is created lazily when decisions require it.

## Vocabulary

Use terms as defined in `CONTEXT.md` in issue titles, specifications, tests, and implementation. Avoid drifting to synonyms that the glossary explicitly excludes.

If a required concept is not in the glossary, reconsider whether new language is necessary or record the gap for domain modeling.

## ADR conflicts

If proposed work contradicts an existing ADR, identify the conflict explicitly instead of silently overriding the decision.

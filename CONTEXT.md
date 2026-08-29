# Domain Context

This repository publishes a human-curated GitHub Profile about AI-era exploration.

## Glossary

- **Exploration Record / 探索记录**: a public reflection approved by the profile owner and grounded in real practice.
- **Exploration Declaration / 探索宣言**: a stable but revisable belief shown on the profile homepage.
- **Current Question / 当前问题**: the newest Exploration Record's “下一个问题”.
- **Approved Source / 已批准素材**: a public template or Exploration Record that has passed human review.
- **Local Draft / 本地草稿**: unpublished writing that must remain outside public version control.
- **Generated Surface / 生成页面**: a README produced from Approved Sources.
- **Profile Publisher / 主页发布器**: the deterministic command and GitHub Actions job that maintain Generated Surfaces.

## Invariants

- A Local Draft is never a public file with a hidden status; it stays outside Git.
- Codex memory may inspire a draft, but raw memory is never an Approved Source.
- The profile owner decides what may be published; the Profile Publisher only validates, renders, and commits.
- Privacy checks fail closed and never echo the matched sensitive value.
- A failed publication preserves the last valid Generated Surfaces.
- Generated Surfaces are deterministic and are not edited by hand.

# AI Exploration Profile README Specification

## Problem Statement

GitHub 用户 `hilt21` 正处于账户起步阶段，暂时没有适合充当主页主体的成熟公开仓库、明星项目或社区指标。常见的 Profile README 模板以技术栈、stars、followers、活动图和项目卡片为中心，既不能准确表达用户当前的探索，也会把注意力引向尚未形成优势的指标。

用户更希望公开呈现自己在 AI 时代使用 Codex 进行探索的过程：如何把一次性对话转化为可恢复的长期记忆，为什么让 AI 行动前要先理解现场，以及在人机协作中哪些判断和确认权应继续由人承担。现有 Codex 记忆可以为这些内容提供真实素材，但原始记忆包含本地路径、项目名称、内部架构和工作偏好，不能直接同步到公开仓库。

用户需要一个真实、克制、可持续更新的 GitHub Profile README。内容必须由人审核，自动化只负责确定性排版和发布；失败或隐私风险不能导致部分生成、意外泄漏或无意义提交。

## Solution

创建公开的 `hilt21/hilt21` GitHub Profile 仓库，将其设计为一份持续演进的“AI 探索日志”，而不是传统作品集或开发者数据仪表盘。

主页以“当执行越来越便宜，人应该把时间花在哪里？”作为长期母题，使用中文主体和一句英文定位，展示稳定的探索宣言、由最新记录派生的当前问题、最近三篇探索记录、完整档案入口、讨论入口，以及“人负责判断、bot 负责维护”的透明说明。

Codex 记忆只作为本地写作素材。Codex 可以生成本地草稿，但只有用户明确审核通过的记录才能进入公开源内容。每条已批准记录以独立 Markdown 文档保存，采用“问题、实验、认识、下一个问题”的固定结构。

一个确定性的 Profile 生成器读取稳定模板和全部已批准记录，验证元数据、内容结构、隐私规则与生成边界，然后一次性生成根 README 和完整探索索引。最新记录的“下一个问题”成为主页的当前问题，最近三篇记录进入主页，其余记录保留在完整索引中。

GitHub Actions 只在已批准内容、模板或生成逻辑发生变化时运行，也支持手动补跑。工作流通过最小权限执行生成器，只在生成结果确有变化时，由 `github-actions[bot]` 提交允许的生成文件。没有会自行变化的外部数据，因此不设置定时任务。

## User Stories

1. As a profile visitor, I want to understand the central question of this profile immediately, so that I can decide whether its exploration is relevant to me.
2. As a non-Chinese profile visitor, I want a short English positioning sentence, so that I can understand the theme without requiring a full bilingual page.
3. As a fellow AI explorer, I want to read ideas grounded in real experiments, so that I can compare them with my own practice.
4. As a fellow AI explorer, I want each record to state the problem being explored, so that I understand its motivation.
5. As a fellow AI explorer, I want each record to describe the experiment, so that I can distinguish evidence from opinion.
6. As a fellow AI explorer, I want each record to state the current learning, so that I can see how the author's judgment changed.
7. As a fellow AI explorer, I want each record to end with the next question, so that I can follow the continuing line of inquiry.
8. As a profile visitor, I want the current question to come from the latest exploration, so that the homepage reflects what the author is thinking about now.
9. As a returning visitor, I want to see the latest three explorations on the homepage, so that I can catch up without reading the full archive.
10. As a returning visitor, I want an index of all approved explorations, so that older learning remains discoverable.
11. As the profile owner, I want the homepage to present me as a long-term AI-era explorer, so that it remains truthful before I have mature public projects.
12. As the profile owner, I want a minimal personal introduction, so that visitors have enough context without turning the page into a résumé.
13. As the profile owner, I want stable exploration declarations separate from dated notes, so that enduring beliefs and changing evidence are both visible.
14. As the profile owner, I want the declarations to remain revisable, so that the profile does not imply that current beliefs are final answers.
15. As the profile owner, I want to omit stars, followers, repository counts, contribution graphs, and skill walls, so that attention stays on judgment and exploration.
16. As the profile owner, I want to omit empty project placeholders, so that the page does not emphasize work that is not ready to show.
17. As the profile owner, I want future projects to be added only when they have grown naturally from the exploration, so that project links function as evidence rather than decoration.
18. As the profile owner, I want Codex to help draft records from local memory, so that useful experience is not lost after a session.
19. As the profile owner, I want drafts to remain outside the public Git history, so that unreviewed material is never exposed merely because it is hidden from the rendered README.
20. As the profile owner, I want to approve every public exploration record explicitly, so that I retain editorial judgment.
21. As the profile owner, I want records dated by their actual approval or publication date, so that the archive does not fabricate a historical publication timeline.
22. As the profile owner, I want records to mention earlier experiments when relevant, so that readers can distinguish the date of experience from the date of reflection.
23. As the profile owner, I want early records to anonymize private project backgrounds, so that methods can be shared without exposing unreleased work.
24. As the profile owner, I want common sensitive patterns checked automatically, so that local paths, credentials, and private contact details are less likely to leak.
25. As the profile owner, I want a private denylist to supplement generic privacy checks, so that explicitly forbidden project or client terms block publication without being revealed in the public repository.
26. As the profile owner, I want privacy validation to fail closed, so that unsafe content is not silently cleaned and published.
27. As the profile owner, I want malformed records to fail publication, so that incomplete ideas do not corrupt the homepage.
28. As the profile owner, I want generator failures to leave existing published outputs untouched, so that the last valid profile remains intact.
29. As the profile owner, I want repeated generation with unchanged inputs to produce byte-identical outputs, so that automation does not create noise.
30. As the profile owner, I want the displayed update date to come from the latest record, so that rerunning automation does not pretend that the content changed.
31. As the profile owner, I want content changes to trigger generation immediately, so that approved records appear without waiting for a schedule.
32. As the profile owner, I want a manual workflow trigger, so that I can safely retry a failed or missed publication.
33. As the profile owner, I want no scheduled empty runs, so that automation exists for a real publishing need rather than visual effect.
34. As the profile owner, I want generated changes committed by `github-actions[bot]`, so that human editorial commits and machine publication commits are distinguishable.
35. As the profile owner, I want the bot to commit only generated profile surfaces, so that automation cannot silently rewrite source records or unrelated files.
36. As the profile owner, I want no new bot commit when generated outputs have not changed, so that history stays meaningful.
37. As the profile owner, I want the workflow to use the repository-scoped token, so that no long-lived personal access token is required.
38. As the profile owner, I want the workflow to hold only the repository-content permission it needs, so that compromise has a limited blast radius.
39. As the profile owner, I want external Actions pinned immutably, so that the reviewed automation dependency cannot change through a movable tag.
40. As the profile owner, I want overlapping publication runs serialized, so that concurrent pushes do not create conflicting generated commits.
41. As a profile visitor, I want a transparent explanation of the publishing model, so that I know the ideas are human-curated rather than autonomously generated.
42. As a profile visitor, I want access to the publishing rules and commit history, so that I can inspect how the profile evolves.
43. As a profile visitor, I want an invitation to provide evidence and counterexamples, so that the page supports mutual exploration rather than one-way self-promotion.
44. As a discussion participant, I want one stable, pinned discussion thread, so that conversation is easy to find and does not fragment across empty threads.
45. As the profile owner, I want discussion creation kept outside the publication workflow, so that the workflow does not need discussion-write permission.
46. As a reader, I want the prose to be visually restrained, so that banners, animations, badges, and decorative widgets do not distract from the content.
47. As a reader, I want the research basis for the automation publicly available, so that its design choices and safety tradeoffs are inspectable.
48. As a future maintainer, I want a concise editorial guide, so that a later Codex session can resume the memory-to-publication process consistently.
49. As a future maintainer, I want the profile's domain terms documented consistently, so that templates, records, tests, and specifications do not drift to conflicting language.
50. As a reuse-oriented reader, I want clear licensing boundaries, so that I know how the exploration prose and automation code may be reused.

## Implementation Decisions

- The product is a public personal Profile repository whose remote name exactly matches the confirmed GitHub username `hilt21`.
- The product vocabulary is:
  - **Exploration Record**: a human-approved public reflection derived from real practice.
  - **Exploration Declaration**: a stable but revisable belief shown on the homepage.
  - **Current Question**: the newest Exploration Record's “next question”.
  - **Approved Source**: public template or Exploration Record content that has passed human review.
  - **Local Draft**: unpublished material that must remain outside public version control.
  - **Generated Surface**: the root profile README or complete exploration index produced from Approved Sources.
  - **Profile Publisher**: the deterministic generator plus the GitHub Actions job that publishes Generated Surfaces.
- The homepage begins with the Chinese question “当执行越来越便宜，人应该把时间花在哪里？” and a concise English positioning line about exploring judgment, memory, and human–AI collaboration with Codex.
- The homepage contains, in order: the opening question, minimal introduction, Current Question, Exploration Declarations, three newest Exploration Records, archive link, discussion invitation, licensing note, and publishing transparency note.
- The initial Exploration Declarations are:
  1. 先理解，再让 AI 行动；
  2. 把一次性对话变成可恢复的长期资产；
  3. AI 可以加速执行，但判断和关键确认仍由人承担；
  4. 观点必须经过真实项目检验。
- The initial Exploration Records form one narrative arc: durable memory, understanding before action, and human confirmation authority.
- Initial records use anonymous project context. Private project names, local paths, internal architecture, and raw memory descriptions are not publication evidence.
- Every Exploration Record is an independent Markdown document with minimal metadata: title, publication date, summary, and explicit approval/publication status.
- Every Exploration Record body has exactly four semantic sections: Problem, Experiment, Learning, and Next Question. Chinese headings may be used in rendered content, but the semantic contract remains stable.
- The publication date represents the date on which the user approved the public wording. Earlier experiments may be described in prose without backdating the record.
- The newest approved record is selected by publication date with a deterministic tie-breaker. Its Next Question becomes the homepage Current Question.
- The homepage renders the three newest approved records. The full index renders every approved record in reverse chronological order.
- Local Drafts are stored outside tracked public content. A draft flag inside the public repository is not considered a privacy boundary.
- The Profile Publisher is deterministic and performs all parsing, validation, rendering, and privacy checks before replacing any Generated Surface.
- Successful publication is transactional at the application level: both Generated Surfaces are prepared completely and then replaced; validation or rendering failure preserves the previous valid outputs.
- The Profile Publisher validates required metadata, valid publication dates, unique record identity, the four required semantic sections, exactly one expected generation boundary in each template, and an available Next Question on the latest record.
- Generic privacy checks block common local absolute paths, home-directory references, credential/token/private-key patterns, and explicitly configured private contact patterns.
- Private forbidden terms are not stored in the public repository. Local runs may read them from ignored local configuration; GitHub Actions may receive them through a masked repository secret. Failure messages identify the record and rule category but must not echo the sensitive matched value.
- Privacy failures are fail-closed. The publisher does not redact or rewrite unsafe prose automatically.
- The public repository contains only approved prose. No raw Codex memory, session transcript, local memory database, or Local Draft is committed.
- The publishing workflow runs when Approved Sources, templates, or publisher logic change, and through manual dispatch. It has no time-based schedule.
- The publishing job uses a single concurrency group so overlapping runs do not race to push generated commits.
- Repository token permission is declared at the narrowest practical job scope and grants repository-content write access only to the publishing job.
- The built-in repository token is used for checkout and push. No personal access token or AI API key is introduced.
- Every referenced external Action is pinned to a reviewed full commit SHA, with its human-readable release version documented beside the reference.
- The workflow stages only Generated Surfaces. It verifies that no other file is staged before committing.
- A clean staged diff ends successfully without a commit. A changed staged diff is committed with the established `github-actions[bot]` name and noreply identity, then pushed to the triggering default branch.
- The Profile Publisher does not run on pull-request-target events and does not execute content from untrusted forks with write permissions.
- Automation is described transparently at the end of the homepage: the user curates every idea, while `github-actions[bot]` performs deterministic maintenance.
- The homepage links to one long-lived pinned GitHub Discussion for evidence and counterexamples. Creating and pinning that discussion is a human repository-setup action, not a workflow responsibility.
- No GitHub activity metrics, third-party rankings, repository auto-listing, project placeholders, contribution graphics, skill icon walls, dynamic banners, or remote image dependencies are included in version one.
- The page is Chinese-first. Only the short positioning sentence is translated into English; Exploration Records are not duplicated bilingually.
- Exploration prose is licensed under CC BY 4.0. Automation code is licensed under MIT. The repository explains which material each license covers.
- The existing research report remains public as design evidence. A concise publishing guide documents the memory-to-draft-to-approval-to-publication loop.
- Issue tracking uses GitHub Issues in `hilt21/hilt21`. A completed specification receives only the `ready-for-agent` triage label.

## Testing Decisions

- A good test observes public behavior rather than internal helper functions. It supplies a complete temporary publication workspace to the Profile Publisher, runs the same command used by GitHub Actions, and inspects the exit status and filesystem results.
- The project uses one primary automated test seam: the Profile Publisher's command-line boundary. Parsing, validation, privacy rules, ordering, rendering, transactional writes, and idempotence are tested through this boundary.
- A successful fixture verifies that exactly the expected Generated Surfaces are produced, the latest three records appear on the homepage in correct order, every record appears in the archive, and the newest Next Question becomes the Current Question.
- The success fixture verifies that stable content and formatting are byte-identical across two consecutive runs.
- The success fixture verifies that no file outside the allowed Generated Surfaces is added, removed, or changed.
- Failure fixtures cover missing metadata, invalid dates, duplicate record identity, missing or duplicate semantic sections, missing Next Question on the newest record, missing or duplicate generation boundaries, and malformed Markdown metadata.
- Privacy failure fixtures cover macOS/Linux and Windows absolute paths, home-directory references, token-like values, private-key material, private contact patterns, and injected private denylist terms.
- Every failure fixture verifies a non-zero exit status, a useful non-sensitive error category, and byte-identical preservation of the previous Generated Surfaces.
- Tests do not assert private function calls, regular-expression implementation details, exact internal data structures, or the number of helper modules.
- The workflow has one remote acceptance test after repository setup: manually dispatch publication, verify that the commit is attributed to `github-actions[bot]`, verify only Generated Surfaces changed, then dispatch again and verify that no additional commit is created.
- A second remote acceptance check confirms that an Approved Source commit triggers publication on the default branch and that the bot push does not recurse into another publication run.
- There is no existing test prior art in the repository. The agreed black-box command seam is therefore the project's initial testing convention.

## Out of Scope

- Direct or scheduled synchronization of local Codex memory files, databases, session logs, or transcripts.
- AI-generated public prose that bypasses explicit human approval.
- Calling an AI model from GitHub Actions for writing, summarization, translation, or privacy review.
- Publishing Local Drafts through branches, pull requests, hidden flags, or unrendered public files.
- Full Chinese-English duplication of the homepage or archive.
- GitHub follower, star, repository, contribution, language, streak, or ranking statistics.
- Third-party HTML scraping or external statistics services.
- Scheduled workflow execution when no Approved Source has changed.
- Automatic listing or ranking of immature repositories.
- Placeholder project sections, résumé sections, skill inventories, animated assets, decorative dashboards, and remote promotional images.
- Automatic creation, pinning, or moderation of GitHub Discussions.
- Per-record Discussion threads.
- Pull requests as an external feature-request or triage surface.
- Building a dedicated authoring CLI, content-management UI, database, API, or hosted service.
- Semantic privacy judgment by a model; deterministic checks supplement but do not replace human review.
- Automatically bypassing branch protection or repository rulesets.

## Further Notes

- The GitHub username is confirmed as `hilt21`.
- The local target directory is the existing `github_readme` directory under the user's home folder. It currently contains only project configuration and the research report; it is not yet an independent Git repository.
- The configured Issue Tracker is `hilt21/hilt21` GitHub Issues, with the default five-role triage vocabulary and `ready-for-agent` required for this specification.
- At specification time, the local GitHub CLI identifies `hilt21` but reports an invalid authentication token. The remote Profile repository could not be confirmed as existing. Publishing this specification as a GitHub Issue therefore requires reauthentication and, if absent, creation of the public repository.
- The initial three Exploration Records must be drafted from the existing memory evidence, anonymized, and presented to the user for explicit wording approval before they become Approved Sources.
- The research reference described a scheduled statistics updater, but the decisions in this specification supersede that blueprint: version one is event-driven, contains no public GitHub metrics, and treats the bot as a deterministic publisher rather than a data scraper or author.
- Implementation must not begin until this specification has been published to the configured Issue Tracker with the `ready-for-agent` label.

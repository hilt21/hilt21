# GitHub Profile README 自动维护调研

调研日期：2026-08-29
参考实现：[alchaincyf/alchaincyf](https://github.com/alchaincyf/alchaincyf)，固定到本次查看的提交 [`c1932d0`](https://github.com/alchaincyf/alchaincyf/tree/c1932d00eefaca76823428c9595c2754c616e0d3)。

## 结论

这个模式可用，而且最小实现只需要三类内容：根目录 `README.md`、一个生成脚本、一个定时 Action。应复用示例的“静态内容 + 有边界的动态区块 + 有变化才提交”思路，但不要原样复制其中的用户名、文案、第三方排名抓取、两页分页上限和浮动 Action tag。

GitHub 会在以下条件同时满足时展示 Profile README：仓库名与用户名一致、仓库公开、根目录有非空 `README.md`。这是建仓时首先要保证的约束。[GitHub 官方说明](https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme)

## 参考仓库如何工作

### README 结构

参考 README 可分为五段：

1. 一句话身份和成果定位；
2. `STATS-START/END` 与 `RANK-START/END` 注释包围的动态徽章；
3. 当前项目及远程图片/仓库徽章；
4. 个人理念；
5. 站点、社交账号和联系邮箱。

只有统计和排名区块由机器改写，其余个人叙事保持人工维护。动态边界见[参考 README 第 9–17 行](https://github.com/alchaincyf/alchaincyf/blob/c1932d00eefaca76823428c9595c2754c616e0d3/README.md#L9-L17)，完整内容结构见[同一文件](https://github.com/alchaincyf/alchaincyf/blob/c1932d00eefaca76823428c9595c2754c616e0d3/README.md)。

### Actions 触发与权限

参考工作流有两个入口：

- `schedule: 17 * * * *`：每小时第 17 分钟运行；
- `workflow_dispatch`：允许手动补跑。

它在 workflow 级显式声明 `permissions: contents: write`，单个 Ubuntu job 依次 checkout、取数、改 README、提交并推送。见[参考工作流第 1–15 行](https://github.com/alchaincyf/alchaincyf/blob/c1932d00eefaca76823428c9595c2754c616e0d3/.github/workflows/update-stats.yml#L1-L15)。

GitHub 的 `schedule` 是尽力而为，不是准点调度：它只在默认分支运行，使用默认分支最新提交；高负载时可能延迟，严重时会丢弃排队任务，整点尤其拥挤；公开仓库 60 天无活动会自动停用定时工作流。因此“避开整点 + 保留手动入口”值得复用，但 README 不应承诺精确刷新时间。[GitHub `schedule` 官方说明](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

### 数据与生成链路

参考工作流的实际链路如下：

1. 把自动生成的 `GITHUB_TOKEN` 作为 `GH_TOKEN` 提供给 GitHub CLI。
2. 用 GraphQL 查询用户拥有且非 fork 的仓库、各仓库 star 数、followers 总数；先取 100 个仓库，如有下一页只再取 100 个。
3. 汇总 stars，并将 stars/followers 格式化成 `k` 表示；公开仓库数直接取 connection 的 `totalCount`。
4. 用 `curl` 抓 `gitstar-ranking.com` HTML，再用文本管道提取全局排名；失败则输出空值。
5. 将值写入 `GITHUB_OUTPUT`，再通过环境变量传给内联 Python。
6. Python 用非贪婪正则只替换两个注释边界之间的内容；排名抓取失败时保留 README 旧值。
7. 只暂存 `README.md`；staged diff 为空就退出，否则提交并推送。

取数逻辑见[第 17–82 行](https://github.com/alchaincyf/alchaincyf/blob/c1932d00eefaca76823428c9595c2754c616e0d3/.github/workflows/update-stats.yml#L17-L82)，区块替换见[第 84–133 行](https://github.com/alchaincyf/alchaincyf/blob/c1932d00eefaca76823428c9595c2754c616e0d3/.github/workflows/update-stats.yml#L84-L133)，提交保护见[第 135–145 行](https://github.com/alchaincyf/alchaincyf/blob/c1932d00eefaca76823428c9595c2754c616e0d3/.github/workflows/update-stats.yml#L135-L145)。

### `github-actions[bot]` 身份

参考工作流显式配置：

```text
user.name  = github-actions[bot]
user.email = 41898282+github-actions[bot]@users.noreply.github.com
```

本次查看到的最新提交，其 author 与 committer 都确实显示为上述 bot 身份。GitHub 维护的 `actions/checkout` 也在“使用内置 token 推送提交”示例中使用这组值，并说明 noreply 地址遵循 `{user.id}+{user.login}@users.noreply.github.com` 形式。[官方 action 示例](https://github.com/actions/checkout#push-a-commit-using-the-built-in-token)

需要区分两件事：`git config` 只设置 commit 的作者/提交者元数据，实际 push 鉴权来自 checkout 保留的 `GITHUB_TOKEN` 凭据。不要把工作流的 `github.actor` 假定为固定的 `github-actions[bot]`；它表示触发初始 run 的用户或应用。[GitHub context 官方说明](https://docs.github.com/en/actions/reference/workflows-and-actions/contexts#github-context)

`41898282+...` 是 GitHub 自有 action 当前文档化的示例，不应表述为产品接口永久保证的 canonical email；在 GitHub Enterprise Server 上也不能直接假定相同值。

## 权限与安全边界

### 必须保留的安全基线

- 将 `permissions: contents: write` 限定在唯一需要提交的 job；不要依赖仓库默认 token 权限。GitHub 建议为 `GITHUB_TOKEN` 授予最小权限。[自动 token 认证](https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication)、[`permissions` 语法](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions)
- 使用内置 `GITHUB_TOKEN`，不为本仓库另建 PAT。token 是当前仓库 GitHub App 的 installation access token，权限限于当前仓库。[`GITHUB_TOKEN` 概念](https://docs.github.com/en/actions/concepts/security/github_token)
- 只监听 `schedule` 和 `workflow_dispatch`；本任务无需执行 PR 代码，更不应使用 `pull_request_target` checkout 并运行不可信 fork 内容。[安全使用参考](https://docs.github.com/en/actions/reference/security/secure-use#mitigating-the-risks-of-untrusted-code-checkout)
- 将所有 `uses:` 固定到经过核对的完整 40 位 commit SHA，并在旁边注释版本号。GitHub 指出完整 SHA 是将 action 固定到不可变版本的唯一方式。[固定完整 SHA](https://docs.github.com/en/actions/reference/security/secure-use#using-third-party-actions)
- 只允许生成脚本改动 `README.md` 的指定机器区块；提交前检查 diff，无变化不提交。
- 若以后引入 PR 标题、分支名等不可信 context，不要把表达式直接插入 `run:` shell；先传入环境变量并正确引用。[脚本注入说明](https://docs.github.com/en/actions/concepts/security/script-injections)

使用 `GITHUB_TOKEN` 推送产生的普通事件不会再次创建新的 workflow run（dispatch 等少数例外），所以自动提交不会因 `push` 自己无限递归。[GitHub 官方说明](https://docs.github.com/en/actions/concepts/security/github_token#when-github_token-triggers-workflow-runs)

### 参考实现的风险和局限

| 项目 | 影响 | 最小改进 |
|---|---|---|
| `actions/checkout@v4` 使用可移动 tag | 供应链版本不完全不可变 | 固定官方仓库完整 commit SHA |
| GraphQL 最多处理两页，即 200 个仓库 | 仓库超过 200 后总 star 少算 | 循环读取 `hasNextPage/endCursor` 直到结束 |
| 抓取第三方排名站 HTML | 页面结构、网络或服务变化会让排名停更 | 第一版不做；若保留，超时失败时维持旧值并清晰记录降级 |
| 动态生成逻辑内嵌在 YAML | 本地测试和失败定位不便 | 抽成一个小脚本，并加入最小单元测试/fixture |
| 正则替换不验证 marker 数量 | marker 丢失或重复时可能静默不更新/多处更新 | 明确断言每对 marker 恰好出现一次 |
| 无 `concurrency` | 手动触发与定时任务重叠时，后一次 push 可能非 fast-forward | 为更新工作流添加单一 concurrency group |
| 直接 push 默认分支 | 分支保护或 ruleset 可能拒绝，即使已有 `contents: write` | 建仓时确认规则；无需保护时允许该 token，需保护时改为受控 PR 流程 |
| 远程图片、徽章和 `main/master` 资源 | 展示依赖外部服务；内容可在本仓库无提交时变化 | 只保留必要资源；重要图片放本仓库并使用固定路径 |
| 每小时运行 | 更新新鲜，但产生较多 Actions run 和提交噪声 | 先用每天 1–2 次，确有需求再提高频率 |

`contents: write` 只解决 token 权限，不会绕过受保护分支或 ruleset。[受保护分支官方说明](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)

## 哪些可复用，哪些不应照搬

可复用：

- 用户名同名公开仓库与根 README；
- 个人叙事为主、动态指标为辅的内容层次；
- HTML 注释划定机器可写区域；
- 错峰定时 + 手动补跑；
- 显式最小写权限；
- 固定 bot author/committer 元数据；
- 只提交 README，且有变化才提交；
- 外部数据失败时不破坏已有展示。

不应照搬：

- `alchaincyf` 用户名、个人文案、邮箱、项目列表和资源链接；
- 每小时刷新频率；
- Gitstar 排名抓取及其硬编码兜底值 `113`；
- 只翻两页的仓库统计；
- 把全部脚本塞进 workflow；
- `actions/checkout@v4` 浮动引用；
- 对 `ubuntu-latest` 预装 `gh/jq/python3` 永久不变的假设。

## 最小实施蓝图

建议第一版只自动维护 GitHub 官方数据，暂不接第三方排名：

```text
README.md
scripts/update_readme.py
tests/test_update_readme.py
.github/workflows/update-profile.yml
```

1. 创建“用户名同名”的公开仓库，在根 README 写个人定位、精选项目、联系入口，并预留一对 `PROFILE-STATS-START/END` marker。
2. `scripts/update_readme.py` 读取结构化统计输入，只替换唯一的 marker 区块；marker 缺失/重复时失败，输出稳定、幂等。
3. 最小测试覆盖：正常替换、重复执行无 diff、marker 缺失/重复拒绝写入。
4. workflow 只用 `schedule`（建议每天错峰一次）与 `workflow_dispatch`，单 job 设置 `permissions: contents: write` 和 `concurrency`。
5. 固定 checkout 的完整 SHA；通过 `GH_TOKEN` 分页读取 owned、non-fork 公共仓库数据，直到 `hasNextPage=false`。
6. 运行生成脚本后只 `git add README.md`；有 staged diff 才以 bot 身份 commit/push，否则成功退出。
7. 验收：手动 run 成功、提交显示 bot 作者、README 只变更 marker 区块、第二次 run 无提交、Profile 首页正常展示。

第一版的成功标准是“安全、幂等、可手动补跑地更新官方统计”，不是复刻示例仓库的全部视觉内容或第三方排名。

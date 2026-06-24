# Agent Config Doctor 发布步骤

这份步骤是给 GitHub 新手照着操作的。

## 第 1 步：确认项目能本地运行

在项目目录执行：

```bash
cd agent-config-doctor
python3 -m agent_config_doctor scan examples/unsafe-agent
```

你应该看到一份包含 critical/high/medium 风险的报告。

再跑测试：

```bash
python3 -m unittest discover -s tests
```

## 第 2 步：初始化 Git 仓库

```bash
git init
git add .
git commit -m "Initial release"
```

如果 Git 提示你配置用户名和邮箱，执行：

```bash
git config --global user.name "你的 GitHub 用户名"
git config --global user.email "你的 GitHub 邮箱"
```

然后重新执行 commit。

## 第 3 步：在 GitHub 创建仓库

1. 打开 GitHub。
2. 点击右上角加号。
3. 选择 New repository。
4. Repository name 填：`agent-config-doctor`。
5. Description 填：`Local-first scanner for AI coding agent configs, MCP files, skills, prompts, and workflow permissions.`
6. 选择 Public。
7. 不要勾选 README、license、gitignore，因为本地已经有了。
8. 点击 Create repository。

## 第 4 步：推送到 GitHub

GitHub 创建仓库后会显示类似命令。你需要在本地执行：

```bash
git branch -M main
git remote add origin https://github.com/你的用户名/agent-config-doctor.git
git push -u origin main
```

把 `你的用户名` 换成你的真实 GitHub 用户名。

## 第 5 步：设置仓库标签

进入 GitHub 仓库页面，点击右侧 About 区域旁边的齿轮，添加 topics：

```text
ai-agent
mcp
security
prompt-injection
claude-code
codex
cursor
agentic-ai
devtools
```

## 第 6 步：做第一张传播截图

在终端运行：

```bash
python3 -m agent_config_doctor scan examples/unsafe-agent
```

截图时要露出：

- 项目名
- Summary
- Critical / High findings
- 至少一条 Fix 建议

这张图后面用于发 X、Reddit、V2EX、Hacker News、掘金、即刻。

## 第 7 步：第一条发布文案

英文：

```text
I built Agent Config Doctor: a local-first scanner for AI coding agent configs.

It checks AGENTS.md, Claude/Codex/Cursor instructions, MCP configs, skills, and GitHub Actions for:

- prompt injection traps
- risky shell commands
- secret reads
- broad MCP filesystem access
- overpowered workflow permissions

Runs locally. Zero runtime dependencies.
```

中文：

```text
我做了一个 AI coding agent 配置安全扫描器 Agent Config Doctor。

它可以本地扫描 AGENTS.md、Claude/Codex/Cursor 指令、MCP 配置、skills 和 GitHub Actions，找出提示注入、危险命令、读取密钥、MCP 过大权限、workflow 写权限过高等问题。

第一版是零依赖 CLI，可以直接跑。
```

## 第 8 步：发布后当天要做的事

- 收集别人吐槽的误报。
- 把最合理的 3 个反馈立刻做成 issue。
- 当天至少发 2 个小版本，例如 `0.1.1`、`0.1.2`。
- README 顶部补充真实用户反馈或截图。

## 第 9 步：一周内冲 star 的节奏

Day 1：发布 MVP，截图传播。

Day 2：加 JSON 输出、GitHub Action 示例。

Day 3：加 SARIF 输出，能进 GitHub Security tab。

Day 4：加 MCP JSON 结构化解析。

Day 5：加 Codex / Claude Code / Cursor 专属规则包。

Day 6：写竞品对比表。

Day 7：发一篇文章：《I scanned 100 AI agent repos. Here are the riskiest patterns.》

## 一句狠话

不要花三天调 logo。这个项目要靠真实扫描结果和传播截图，不靠包装。

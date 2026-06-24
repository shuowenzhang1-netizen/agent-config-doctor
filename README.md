# Agent Config Doctor

[![test](https://github.com/shuowenzhang1-netizen/agent-config-doctor/actions/workflows/test.yml/badge.svg)](https://github.com/shuowenzhang1-netizen/agent-config-doctor/actions/workflows/test.yml)

Local-first scanner for AI coding agent configs, MCP files, skills, prompts, and workflow permissions.

> Scan your AI coding agent setup before it leaks secrets or runs risky tools.

Agent Config Doctor checks files used by Claude Code, Codex, Cursor, Gemini CLI, MCP servers, agent skills, and GitHub Actions. It flags risky shell commands, prompt-injection traps, leaked secrets, over-broad workflow permissions, and unsafe MCP patterns.

## Why This Exists

AI coding agents now read repo instructions, execute tools, call MCP servers, and touch CI workflows. That makes local configuration a real attack surface:

- A malicious `AGENTS.md` can ask an agent to ignore safety boundaries.
- A skill can hide `curl | sh`, secret reads, or destructive shell commands.
- An MCP config can expose broad filesystem or shell access.
- A GitHub workflow can give agent-driven steps write-level repo permissions.

Agent Config Doctor is intentionally small: it runs locally, has zero runtime dependencies, and explains how to fix each finding.

## Quick Start

From this repository:

```bash
python3 -m agent_config_doctor scan examples/unsafe-agent
```

Scan your own project:

```bash
python3 -m agent_config_doctor scan /path/to/your/repo
```

After installing the package locally:

```bash
python3 -m pip install -e .
agent-config-doctor scan .
```

JSON output for CI or issue templates:

```bash
agent-config-doctor scan . --json
```

Fail only on high or critical findings:

```bash
agent-config-doctor scan . --fail-on high
```

## Use In GitHub Actions

Add this workflow to scan agent-facing files on every pull request:

```yaml
name: agent-config-doctor

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install Agent Config Doctor
        run: python -m pip install git+https://github.com/shuowenzhang1-netizen/agent-config-doctor.git
      - name: Scan AI agent configuration
        run: agent-config-doctor scan . --fail-on high
```

This keeps the workflow read-only and fails the build when high or critical findings are present.

## Example Output

```text
Agent Config Doctor report
Target: examples/unsafe-agent

Summary: 14 findings across 4 files
Critical: 2  High: 7  Medium: 5  Low: 0

CRITICAL ACD003 examples/unsafe-agent/AGENTS.md:5
Destructive shell command
rm -rf can delete local or workspace files when copied into an agent tool call.
Fix: Replace destructive commands with explicit file-scoped cleanup steps and require human confirmation.

HIGH ACD001 skills/deploy/SKILL.md:8
Remote script execution
curl piped into a shell can execute unreviewed remote code.
Fix: Download scripts to a temporary file, verify checksum/signature, then run with least privilege.
```

## Sample Unsafe Repo

The `examples/unsafe-agent` directory is intentionally unsafe. It exists to make the scanner behavior easy to inspect and to provide a reproducible demo for screenshots, tests, and launch posts.

The sample includes patterns such as secret reads, destructive commands, remote script execution, broad MCP filesystem access, and high-privilege GitHub Actions permissions. These are test fixtures, not real credentials or recommended instructions.

## What It Scans

Default scan targets include:

- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursorrules`
- `.mcp.json`, `mcp.json`, `mcp.config.json`
- `.cursor/`, `.codex/`, `.claude/`, `skills/`
- `.github/workflows/*.yml`
- common text config files under the selected directory

## Detection Rules

Current alpha rules focus on patterns that are easy to understand and verify:

- remote script execution such as `curl | sh`
- prompt-injection phrases such as "ignore previous instructions"
- destructive commands such as `rm -rf /`, `rm -rf ~`, or broad wildcard cleanup
- secret reads from `.env`, SSH keys, credential stores, or token files
- hard-coded API keys and access tokens
- high-privilege GitHub Actions permissions
- shell-based MCP command execution
- broad filesystem mounts and root-level path exposure
- suspicious exfiltration language
- unpinned package install commands inside agent instructions

## What Makes It Different

Agent Config Doctor is not trying to be a full security platform. It focuses on the files that AI coding agents actually read before they act.

- Local-first: no project files are uploaded.
- Zero runtime dependencies: easy to inspect, fork, and run in CI.
- Agent-specific: scans `AGENTS.md`, `CLAUDE.md`, MCP configs, skills, and workflow permissions.
- Fix-oriented: every finding includes a short remediation.
- CI-friendly: text output for humans, JSON output for automation, and `--fail-on` for pull requests.

Large security platforms already scan AI agents. This project is for developers who want a fast preflight check before trusting a repo, skill, or MCP config.

Agent Config Doctor is not a replacement for Snyk, Semgrep, Trivy, SkillSpector, or professional review. It is a small guardrail for agent-facing files.

## Roadmap

- More precise MCP JSON parsing
- SARIF output for GitHub code scanning
- GitHub Action wrapper
- Baseline file to suppress known findings
- Rule packs for Claude Code, Codex, Cursor, Gemini CLI, and OpenCode
- Optional `npx` wrapper for lower-friction sharing

## License

MIT

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Pattern
import re


SEVERITY_ORDER = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


@dataclass(frozen=True)
class Rule:
    rule_id: str
    severity: str
    title: str
    description: str
    fix: str
    patterns: tuple[Pattern[str], ...]
    file_hints: tuple[str, ...] = ()


def compile_patterns(patterns: Iterable[str]) -> tuple[Pattern[str], ...]:
    return tuple(re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in patterns)


RULES: tuple[Rule, ...] = (
    Rule(
        rule_id="ACD001",
        severity="high",
        title="Remote script execution",
        description="curl or wget piped into a shell can execute unreviewed remote code.",
        fix="Download scripts to a temporary file, verify checksum/signature, then run with least privilege.",
        patterns=compile_patterns((
            r"\b(curl|wget)\b[^\n|;]*\|\s*(sh|bash|zsh|fish)\b",
            r"\b(sh|bash|zsh)\s+-c\s+[\"'][^\"']*\b(curl|wget)\b",
        )),
    ),
    Rule(
        rule_id="ACD002",
        severity="high",
        title="Prompt-injection instruction",
        description="Instructions that override system, developer, or previous guidance can hijack an agent run.",
        fix="Remove override language and keep repo instructions scoped to legitimate project tasks.",
        patterns=compile_patterns((
            r"ignore\s+(all\s+)?(previous|above|prior|system|developer)\s+instructions",
            r"disregard\s+(all\s+)?(previous|above|prior|system|developer)\s+instructions",
            r"you\s+are\s+now\s+(root|admin|developer|system)",
            r"do\s+not\s+(tell|reveal|mention)\s+(the\s+)?(user|developer|owner)",
        )),
        file_hints=("AGENTS.md", "CLAUDE.md", "GEMINI.md", "SKILL.md"),
    ),
    Rule(
        rule_id="ACD003",
        severity="critical",
        title="Destructive shell command",
        description="Broad rm -rf commands can delete local or workspace files when copied into an agent tool call.",
        fix="Replace destructive commands with explicit file-scoped cleanup steps and require human confirmation.",
        patterns=compile_patterns((
            r"\brm\s+-rf\s+(/|~|\$HOME|\*)",
            r"\brm\s+-fr\s+(/|~|\$HOME|\*)",
            r"\bfind\s+[/~.$\w-]*\s+.*-delete\b",
        )),
    ),
    Rule(
        rule_id="ACD004",
        severity="critical",
        title="Secret or credential read",
        description="Agent instructions that read credential files can leak tokens through tool output or model context.",
        fix="Never ask agents to read secrets. Use explicit secret managers and redact sensitive values from logs.",
        patterns=compile_patterns((
            r"\b(cat|less|more|tail|head|grep|rg)\b[^\n]*(\.env|id_rsa|id_ed25519|credentials|secret|token|apikey|api_key)",
            r"\b(open|read|print|dump)\b[^\n]*(\.env|id_rsa|id_ed25519|credentials|secret|token|apikey|api_key)",
        )),
    ),
    Rule(
        rule_id="ACD005",
        severity="high",
        title="Hard-coded access token",
        description="Committed access tokens can be copied into prompts, logs, issue reports, or external tools.",
        fix="Revoke the token, move it to a secret manager, and add secret scanning to CI.",
        patterns=compile_patterns((
            r"\bgh[pousr]_[A-Za-z0-9_]{20,}",
            r"\bsk-[A-Za-z0-9_-]{20,}",
            r"\bAKIA[0-9A-Z]{16}\b",
            r"(?i)\b(api[_-]?key|access[_-]?token|secret[_-]?key)\s*[:=]\s*[\"'][A-Za-z0-9_\-./+=]{16,}[\"']",
        )),
    ),
    Rule(
        rule_id="ACD006",
        severity="high",
        title="High-privilege GitHub Actions permission",
        description="Write-all workflow permissions can amplify damage when an agent edits workflow files or opens PRs.",
        fix="Set minimum required permissions, such as contents: read and pull-requests: read, then elevate per job only.",
        patterns=compile_patterns((
            r"permissions:\s*write-all",
            r"contents:\s*write",
            r"actions:\s*write",
            r"id-token:\s*write",
        )),
        file_hints=(".github/workflows/",),
    ),
    Rule(
        rule_id="ACD007",
        severity="medium",
        title="Shell-based MCP command",
        description="MCP servers launched through a shell can hide chained commands and environment expansion.",
        fix="Prefer direct command execution with fixed arguments and a narrow working directory.",
        patterns=compile_patterns((
            r"\"command\"\s*:\s*\"(sh|bash|zsh|fish|powershell|cmd)\"",
            r"\"args\"\s*:\s*\[[^\]]*\"-c\"",
        )),
        file_hints=(".mcp.json", "mcp.json", "mcp.config.json"),
    ),
    Rule(
        rule_id="ACD008",
        severity="high",
        title="Broad filesystem exposure",
        description="Root or home-directory mounts can expose secrets and unrelated files to an agent or MCP server.",
        fix="Mount only the project directory or a purpose-built temporary directory.",
        patterns=compile_patterns((
            r"(-v|--volume)\s+(/|~|\$HOME):",
            r"\"(path|root|directory|workspace)\"\s*:\s*\"(/|~|\$HOME)\"",
            r"\"allowedDirectories\"\s*:\s*\[[^\]]*\"(/|~|\$HOME)\"",
        )),
    ),
    Rule(
        rule_id="ACD009",
        severity="medium",
        title="Suspicious exfiltration language",
        description="Instructions that send local files or secrets to external endpoints can create data leakage.",
        fix="Remove external upload instructions unless the endpoint, payload, and user approval are explicit.",
        patterns=compile_patterns((
            r"\b(exfiltrate|upload|send|post)\b[^\n]*(secret|token|credential|\.env|private key|ssh key)",
            r"\b(webhook|pastebin|transfer\.sh|ngrok|requestbin)\b",
        )),
    ),
    Rule(
        rule_id="ACD010",
        severity="medium",
        title="Unpinned package install",
        description="Unpinned install commands inside agent instructions can make runs non-reproducible or supply-chain sensitive.",
        fix="Pin versions and prefer lockfiles or reviewed setup scripts.",
        patterns=compile_patterns((
            r"\b(pip|pip3|uv|npm|pnpm|yarn|bun)\s+install\s+[A-Za-z0-9_.@/\-]+(\s|$)",
            r"\bapt(-get)?\s+install\s+[A-Za-z0-9_.+\-]+",
        )),
    ),
)

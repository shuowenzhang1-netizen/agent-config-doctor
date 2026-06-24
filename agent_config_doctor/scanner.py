from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable
import json

from .rules import RULES, Rule, SEVERITY_ORDER


SKIP_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
}

INTERESTING_NAMES = {
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
    "SKILL.md",
    ".cursorrules",
    ".mcp.json",
    "mcp.json",
    "mcp.config.json",
    "settings.json",
    "package.json",
    "pyproject.toml",
    "requirements.txt",
}

INTERESTING_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".jsonc",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".env",
}

INTERESTING_PARTS = {
    ".github/workflows",
    ".cursor",
    ".codex",
    ".claude",
    "skills",
}

MAX_FILE_BYTES = 512_000


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    title: str
    description: str
    fix: str
    path: str
    line: int
    column: int
    match: str

    def to_dict(self) -> dict:
        return asdict(self)


def scan_path(target: Path) -> list[Finding]:
    root = target.resolve()
    findings: list[Finding] = []

    for path in iter_candidate_files(root):
        text = read_text_file(path)
        if text is None:
            continue
        rel_path = str(path.relative_to(root)) if path != root else path.name
        findings.extend(scan_text(rel_path, text))

    return sorted(
        findings,
        key=lambda item: (
            -SEVERITY_ORDER[item.severity],
            item.path,
            item.line,
            item.rule_id,
        ),
    )


def scan_text(rel_path: str, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for rule in RULES:
        if not applies_to_file(rule, rel_path):
            continue
        for pattern in rule.patterns:
            for match in pattern.finditer(text):
                line, column = offset_to_line_column(text, match.start())
                excerpt = collapse(match.group(0))
                findings.append(
                    Finding(
                        rule_id=rule.rule_id,
                        severity=rule.severity,
                        title=rule.title,
                        description=rule.description,
                        fix=rule.fix,
                        path=rel_path,
                        line=line,
                        column=column,
                        match=excerpt,
                    )
                )
    return dedupe(findings)


def iter_candidate_files(root: Path) -> Iterable[Path]:
    if root.is_file():
        yield root
        return

    for path in root.rglob("*"):
        if path.is_dir():
            continue
        if should_skip(path, root):
            continue
        if is_interesting(path, root):
            yield path


def should_skip(path: Path, root: Path) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        rel_parts = path.parts
    return any(part in SKIP_DIRS for part in rel_parts)


def is_interesting(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        rel = path.as_posix()

    if path.name in INTERESTING_NAMES:
        return True
    if path.suffix.lower() in INTERESTING_SUFFIXES:
        return True
    return any(part in rel for part in INTERESTING_PARTS)


def read_text_file(path: Path) -> str | None:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return None
        raw = path.read_bytes()
    except OSError:
        return None

    if b"\x00" in raw[:2048]:
        return None

    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return raw.decode("utf-8", errors="replace")
        except UnicodeDecodeError:
            return None


def applies_to_file(rule: Rule, rel_path: str) -> bool:
    if not rule.file_hints:
        return True
    normalized = rel_path.replace("\\", "/")
    return any(hint in normalized or normalized.endswith(hint) for hint in rule.file_hints)


def offset_to_line_column(text: str, offset: int) -> tuple[int, int]:
    line = text.count("\n", 0, offset) + 1
    line_start = text.rfind("\n", 0, offset) + 1
    column = offset - line_start + 1
    return line, column


def collapse(value: str, limit: int = 160) -> str:
    compact = " ".join(value.strip().split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def dedupe(findings: list[Finding]) -> list[Finding]:
    seen: set[tuple[str, str, int, str]] = set()
    unique: list[Finding] = []
    for finding in findings:
        key = (finding.rule_id, finding.path, finding.line, finding.match)
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)
    return unique


def findings_to_json(findings: list[Finding], target: str) -> str:
    counts = severity_counts(findings)
    payload = {
        "target": target,
        "summary": {
            "total": len(findings),
            "critical": counts["critical"],
            "high": counts["high"],
            "medium": counts["medium"],
            "low": counts["low"],
        },
        "findings": [finding.to_dict() for finding in findings],
    }
    return json.dumps(payload, indent=2)


def severity_counts(findings: list[Finding]) -> dict[str, int]:
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    for finding in findings:
        counts[finding.severity] += 1
    return counts

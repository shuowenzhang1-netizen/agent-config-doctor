from __future__ import annotations

from pathlib import Path
import argparse
import sys

from . import __version__
from .rules import SEVERITY_ORDER
from .scanner import findings_to_json, scan_path, severity_counts


COLORS = {
    "critical": "\033[95m",
    "high": "\033[91m",
    "medium": "\033[93m",
    "low": "\033[94m",
    "muted": "\033[90m",
    "reset": "\033[0m",
}


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "scan":
        return run_scan(args)

    parser.print_help()
    return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agent-config-doctor",
        description="Scan AI coding agent configs, MCP files, skills, prompts, and workflow permissions.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    subparsers = parser.add_subparsers(dest="command")

    scan = subparsers.add_parser("scan", help="scan a file or directory")
    scan.add_argument("target", nargs="?", default=".", help="file or directory to scan")
    scan.add_argument("--json", action="store_true", help="print machine-readable JSON")
    scan.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    scan.add_argument(
        "--fail-on",
        choices=("low", "medium", "high", "critical", "never"),
        default="never",
        help="exit with code 2 when findings at this severity or higher exist",
    )
    return parser


def run_scan(args: argparse.Namespace) -> int:
    target = Path(args.target)
    if not target.exists():
        print(f"Target does not exist: {target}", file=sys.stderr)
        return 1

    findings = scan_path(target)
    if args.json:
        print(findings_to_json(findings, str(target)))
    else:
        print_report(findings, str(target), color=not args.no_color and sys.stdout.isatty())

    if args.fail_on != "never" and has_failure(findings, args.fail_on):
        return 2
    return 0


def print_report(findings, target: str, color: bool) -> None:
    counts = severity_counts(findings)
    files = len({finding.path for finding in findings})

    print("Agent Config Doctor report")
    print(f"Target: {target}")
    print()

    if not findings:
        print("No findings. Keep this as a preflight check before adding new agent configs.")
        return

    print(f"Summary: {len(findings)} findings across {files} files")
    print(
        "Critical: {critical}  High: {high}  Medium: {medium}  Low: {low}".format(
            **counts
        )
    )
    print()

    for finding in findings:
        severity = format_severity(finding.severity, color)
        location = f"{finding.path}:{finding.line}"
        print(f"{severity} {finding.rule_id} {location}")
        print(finding.title)
        print(finding.description)
        print(f"Matched: {finding.match}")
        print(f"Fix: {finding.fix}")
        print()


def format_severity(severity: str, color: bool) -> str:
    label = severity.upper()
    if not color:
        return label
    return f"{COLORS[severity]}{label}{COLORS['reset']}"


def has_failure(findings, threshold: str) -> bool:
    minimum = SEVERITY_ORDER[threshold]
    return any(SEVERITY_ORDER[finding.severity] >= minimum for finding in findings)

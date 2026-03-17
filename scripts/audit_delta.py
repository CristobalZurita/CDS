#!/usr/bin/env python3
"""Fast incremental audit over the current git worktree.

Runs cheap, repeatable checks only on changed files so we can keep the repo
coherent without re-auditing the whole project every time.
"""

from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
FRONTEND_ROOTS = (
    ROOT / "CDS_VUE3_ZERO" / "src",
    ROOT / "coming-soon-vue" / "src",
)
TOKENS_FILES = {
    ROOT / "CDS_VUE3_ZERO" / "src" / "styles" / "tokens.css",
    ROOT / "coming-soon-vue" / "src" / "styles" / "tokens.css",
}
ALLOWED_AXIOS_FILES = {
    ROOT / "CDS_VUE3_ZERO" / "src" / "services" / "api.js",
    ROOT / "CDS_VUE3_ZERO" / "src" / "services" / "api.ts",
    ROOT / "coming-soon-vue" / "src" / "services" / "api.js",
    ROOT / "coming-soon-vue" / "src" / "services" / "api.ts",
}
IGNORED_PREFIXES = (
    ".git/",
    "node_modules/",
    "dist/",
)
IGNORED_CONTAINS = (
    "/public/images/",
)
IGNORED_SUFFIXES = {
    ".webp",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".pdf",
    ".mp4",
    ".mov",
    ".mp3",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".map",
    ".lock",
}
INLINE_STYLE_RE = re.compile(r':style\s*=|v-bind:style\s*=|(?<![-\w])style\s*=\s*["\']')
DOM_STYLE_RE = re.compile(r"\.style\.")
AXIOS_RE = re.compile(r"import\s+axios\s+from|axios\.(get|post|put|patch|delete|create)")
CDS_VAR_DEF_RE = re.compile(r"(?m)^\s*(--cds-[a-z0-9-]+)\s*:")
RADIUS_LITERAL_RE = re.compile(
    r"border-radius\s*:\s*(0\.55rem|0\.85rem|1\.1rem|1\.4rem|999px)\b"
)
LEGACY_BORDER_MIX_RE = re.compile(
    r"color-mix\(in srgb,\s*var\(--cds-light\)\s*(65|70)%\s*,\s*white\)"
)


@dataclass
class Finding:
    severity: str
    rule: str
    path: str
    detail: str


def git_changed_paths() -> list[Path]:
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    paths: list[Path] = []
    for raw_line in proc.stdout.splitlines():
        if not raw_line.strip():
            continue
        path_text = raw_line[3:]
        if " -> " in path_text:
            path_text = path_text.split(" -> ", 1)[1]
        path = ROOT / path_text
        if any(path_text.startswith(prefix) for prefix in IGNORED_PREFIXES):
            continue
        if any(fragment in path_text for fragment in IGNORED_CONTAINS):
            continue
        if path.is_dir():
            paths.extend(
                sub
                for sub in path.rglob("*")
                if sub.is_file()
                and not any(part in {"node_modules", "dist", ".git"} for part in sub.parts)
                and not any(fragment in sub.as_posix() for fragment in IGNORED_CONTAINS)
                and sub.suffix.lower() not in IGNORED_SUFFIXES
                and sub.suffix.lower() != ".md"
                and sub.name != ".DS_Store"
            )
        else:
            if (
                path.suffix.lower() in IGNORED_SUFFIXES
                or path.suffix.lower() == ".md"
                or path.name == ".DS_Store"
            ):
                continue
            paths.append(path)
    return sorted(set(p for p in paths if p.exists()))


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def is_frontend_file(path: Path) -> bool:
    return any(root in path.parents for root in FRONTEND_ROOTS)


def is_style_file(path: Path) -> bool:
    return path.suffix in {".css", ".scss", ".sass", ".vue"}


def is_code_file(path: Path) -> bool:
    return path.suffix in {".js", ".ts", ".vue", ".py", ".html", ".cjs", ".mjs"}


def collect_tokens(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(CDS_VAR_DEF_RE.findall(read_text(path)))


def iter_css_lines(path: Path, text: str) -> Iterable[tuple[int, str]]:
    if path.suffix == ".vue":
        for match in re.finditer(r"<style\b[^>]*>(.*?)</style>", text, re.S):
            block = match.group(1)
            line_offset = text[: match.start(1)].count("\n")
            for idx, line in enumerate(block.splitlines(), start=1):
                yield line_offset + idx, line
        return
    for idx, line in enumerate(text.splitlines(), start=1):
        yield idx, line


def audit_paths(paths: list[Path]) -> list[Finding]:
    findings: list[Finding] = []
    known_tokens = set().union(*(collect_tokens(path) for path in TOKENS_FILES))

    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
        text = read_text(path)

        if is_code_file(path):
            if INLINE_STYLE_RE.search(text):
                findings.append(
                    Finding("high", "inline-style", rel, "Inline style usage found.")
                )
            if DOM_STYLE_RE.search(text):
                findings.append(
                    Finding("high", "dom-style-mutation", rel, "Direct DOM style mutation found.")
                )
            if is_frontend_file(path) and path not in ALLOWED_AXIOS_FILES and AXIOS_RE.search(text):
                findings.append(
                    Finding("high", "direct-axios", rel, "Direct axios usage outside shared API service.")
                )

        if is_style_file(path):
            local_token_defs = set(CDS_VAR_DEF_RE.findall(text))
            unexpected_defs = sorted(local_token_defs & known_tokens) if path not in TOKENS_FILES else []
            for token_name in unexpected_defs:
                findings.append(
                    Finding(
                        "medium",
                        "duplicate-cds-token",
                        rel,
                        f"Redefines shared token {token_name} outside tokens.css.",
                    )
                )

            for line_no, line in iter_css_lines(path, text):
                if RADIUS_LITERAL_RE.search(line):
                    findings.append(
                        Finding(
                            "low",
                            "literal-radius",
                            f"{rel}:{line_no}",
                            "Use shared radius token instead of literal value.",
                        )
                    )
                if path not in TOKENS_FILES and LEGACY_BORDER_MIX_RE.search(line):
                    findings.append(
                        Finding(
                            "low",
                            "legacy-border-mix",
                            f"{rel}:{line_no}",
                            "Use shared border token instead of inline color-mix.",
                        )
                    )

    return findings


def print_report(paths: list[Path], findings: list[Finding]) -> int:
    print("# Delta Audit")
    print()
    print(f"Changed files scanned: {len(paths)}")
    if paths:
        buckets: dict[str, int] = {}
        for path in paths:
            rel = path.relative_to(ROOT).as_posix()
            top = rel.split("/", 1)[0]
            buckets[top] = buckets.get(top, 0) + 1
        print()
        print("## Areas")
        for area, count in sorted(buckets.items()):
            print(f"- {area}: {count}")
        preview = [path.relative_to(ROOT).as_posix() for path in paths[:25]]
        print()
        print("## Sample Files")
        for item in preview:
            print(f"- {item}")
        remaining = len(paths) - len(preview)
        if remaining > 0:
            print(f"- ... {remaining} more")

    if not findings:
        print()
        print("## Findings")
        print("- None")
        return 0

    order = ("high", "medium", "low")
    print()
    print("## Findings")
    for severity in order:
        group = [f for f in findings if f.severity == severity]
        if not group:
            continue
        print()
        print(f"### {severity.upper()}")
        for finding in group:
            print(f"- [{finding.rule}] {finding.path}: {finding.detail}")
    return 1 if any(f.severity == "high" for f in findings) else 0


def main() -> None:
    paths = git_changed_paths()
    findings = audit_paths(paths)
    raise SystemExit(print_report(paths, findings))


if __name__ == "__main__":
    main()

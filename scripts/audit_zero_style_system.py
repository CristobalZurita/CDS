#!/usr/bin/env python3
"""Audit style authority and override risk in CDS_VUE3_ZERO."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
ZERO_SRC = ROOT / "CDS_VUE3_ZERO" / "src"
SCAN_ROOTS = (
    ZERO_SRC / "styles",
    ZERO_SRC / "components",
    ZERO_SRC / "pages",
    ZERO_SRC / "layouts",
)
TOKENS_FILE = ZERO_SRC / "styles" / "tokens.css"
TYPOGRAPHY_FILE = ZERO_SRC / "styles" / "typography.css"

STYLE_BLOCK_RE = re.compile(r"<style\b([^>]*)>(.*?)</style>", re.S | re.I)
ATTR_RE = re.compile(r'([:@\w-]+)(?:=(["\'])(.*?)\2)?')
CSS_VAR_USE_RE = re.compile(r"var\((--cds-[a-z0-9-]+)")
CSS_VAR_DEF_RE = re.compile(r"(?m)^\s*(--[a-z0-9-]+)\s*:")
MEDIA_RE = re.compile(r"@media\b")
IMPORTANT_RE = re.compile(r"!important\b")
HEX_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b")
RGBA_RE = re.compile(r"\brgba?\(")
GRADIENT_RE = re.compile(r"\b(?:linear-gradient|radial-gradient|conic-gradient)\(")
COLOR_MIX_RE = re.compile(r"\bcolor-mix\(")
BACKDROP_RE = re.compile(r"\bbackdrop-filter\b")
CLAMP_RE = re.compile(r"\bclamp\(")
PX_RE = re.compile(r"(?<![-\w])\d+(?:\.\d+)?px\b")
REM_RE = re.compile(r"(?<![-\w])\d+(?:\.\d+)?rem\b")
SVH_RE = re.compile(r"(?<![-\w])\d+(?:\.\d+)?s?v[wh]\b")
LOCAL_VAR_RE = re.compile(r"(?m)^\s*(--(?!cds-)[a-z0-9-]+)\s*:")
SELECTOR_RE = re.compile(r"(?m)^[^@\n][^{\n]*\{")
COMMENT_RE = re.compile(r"/\*.*?\*/", re.S)


@dataclass
class FileAudit:
    path: str
    kind: str
    total_style_blocks: int
    local_style_blocks: int
    external_style_blocks: int
    mixed_style_sources: bool
    scoped_style_blocks: int
    media_queries: int
    important_uses: int
    token_uses: int
    cds_token_redefs: int
    local_var_defs: int
    literal_px: int
    literal_rem: int
    literal_viewport_units: int
    literal_hex: int
    literal_rgba: int
    gradients: int
    color_mix: int
    backdrop_filters: int
    clamp_uses: int
    selector_blocks: int
    risk_score: int
    findings: list[str]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def list_style_files() -> list[Path]:
    files: set[Path] = set()
    for root in SCAN_ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.is_file() and path.suffix in {".vue", ".css"}:
                files.add(path)
    return sorted(files)


def parse_attrs(raw: str) -> dict[str, str | bool]:
    attrs: dict[str, str | bool] = {}
    for key, _, value in ATTR_RE.findall(raw):
        attrs[key] = True if value == "" else value
    return attrs


def strip_comments(text: str) -> str:
    return COMMENT_RE.sub("", text)


def collect_known_cds_tokens() -> set[str]:
    known: set[str] = set()
    for source in (TOKENS_FILE, TYPOGRAPHY_FILE):
        if source.exists():
            known.update(CSS_VAR_DEF_RE.findall(read_text(source)))
    return {name for name in known if name.startswith("--cds-")}


def analyze_css_chunk(text: str, known_tokens: set[str], allow_cds_defs: bool = False) -> dict[str, int]:
    clean = strip_comments(text)
    defs = set(CSS_VAR_DEF_RE.findall(clean))
    cds_redefs = 0 if allow_cds_defs else len(defs & known_tokens)
    local_vars = len(LOCAL_VAR_RE.findall(clean))
    return {
        "media_queries": len(MEDIA_RE.findall(clean)),
        "important_uses": len(IMPORTANT_RE.findall(clean)),
        "token_uses": len(CSS_VAR_USE_RE.findall(clean)),
        "cds_token_redefs": cds_redefs,
        "local_var_defs": local_vars,
        "literal_px": len(PX_RE.findall(clean)),
        "literal_rem": len(REM_RE.findall(clean)),
        "literal_viewport_units": len(SVH_RE.findall(clean)),
        "literal_hex": len(HEX_RE.findall(clean)),
        "literal_rgba": len(RGBA_RE.findall(clean)),
        "gradients": len(GRADIENT_RE.findall(clean)),
        "color_mix": len(COLOR_MIX_RE.findall(clean)),
        "backdrop_filters": len(BACKDROP_RE.findall(clean)),
        "clamp_uses": len(CLAMP_RE.findall(clean)),
        "selector_blocks": len(SELECTOR_RE.findall(clean)),
    }


def score_and_findings(kind: str, local_blocks: int, external_blocks: int, metrics: dict[str, int]) -> tuple[int, list[str]]:
    findings: list[str] = []
    score = 0

    if kind == "vue" and local_blocks and external_blocks:
        findings.append("mezcla estilos locales y compartidos en el mismo componente")
        score += 5
    if kind == "vue" and local_blocks > 1:
        findings.append("tiene mas de un bloque <style> local")
        score += 3
    if kind == "vue" and external_blocks > 1:
        findings.append("importa mas de un bloque de estilos externos")
        score += 2
    if metrics["cds_token_redefs"]:
        findings.append("redefine tokens --cds-* fuera de tokens/typography")
        score += metrics["cds_token_redefs"] * 4
    if metrics["local_var_defs"] >= 6:
        findings.append("acumula muchas variables locales")
        score += 2
    if metrics["media_queries"] >= 3:
        findings.append("tiene varias media queries")
        score += min(metrics["media_queries"], 6)
    if metrics["important_uses"]:
        findings.append("usa !important")
        score += metrics["important_uses"] * 3
    if metrics["color_mix"]:
        findings.append("usa color-mix")
        score += metrics["color_mix"] * 2
    if metrics["gradients"]:
        findings.append("usa gradientes")
        score += metrics["gradients"] * 2
    if metrics["backdrop_filters"]:
        findings.append("usa backdrop-filter")
        score += metrics["backdrop_filters"] * 3

    literal_total = (
        metrics["literal_px"]
        + metrics["literal_rem"]
        + metrics["literal_hex"]
        + metrics["literal_rgba"]
    )
    if literal_total >= 20:
        findings.append("tiene muchos literales visuales")
        score += 4
    elif literal_total >= 10:
        findings.append("tiene varios literales visuales")
        score += 2

    if not findings:
        findings.append("sin conflicto evidente de autoridad")

    return score, findings


def audit_file(path: Path, known_tokens: set[str]) -> FileAudit:
    rel = path.relative_to(ROOT).as_posix()
    text = read_text(path)

    if path.suffix == ".vue":
        blocks = list(STYLE_BLOCK_RE.finditer(text))
        local_chunks: list[str] = []
        local_blocks = 0
        external_blocks = 0
        scoped_blocks = 0
        for match in blocks:
            attrs = parse_attrs(match.group(1))
            if "scoped" in attrs:
                scoped_blocks += 1
            if "src" in attrs:
                external_blocks += 1
            else:
                local_blocks += 1
                local_chunks.append(match.group(2))
        css_text = "\n".join(local_chunks)
        metrics = analyze_css_chunk(css_text, known_tokens)
        score, findings = score_and_findings("vue", local_blocks, external_blocks, metrics)
        return FileAudit(
            path=rel,
            kind="vue",
            total_style_blocks=len(blocks),
            local_style_blocks=local_blocks,
            external_style_blocks=external_blocks,
            mixed_style_sources=bool(local_blocks and external_blocks),
            scoped_style_blocks=scoped_blocks,
            risk_score=score,
            findings=findings,
            **metrics,
        )

    metrics = analyze_css_chunk(text, known_tokens, allow_cds_defs=path in {TOKENS_FILE, TYPOGRAPHY_FILE})
    score, findings = score_and_findings("css", 0, 0, metrics)
    return FileAudit(
        path=rel,
        kind="css",
        total_style_blocks=0,
        local_style_blocks=0,
        external_style_blocks=0,
        mixed_style_sources=False,
        scoped_style_blocks=0,
        risk_score=score,
        findings=findings,
        **metrics,
    )


def audit(paths: Iterable[Path]) -> list[FileAudit]:
    known_tokens = collect_known_cds_tokens()
    return sorted(
        (audit_file(path, known_tokens) for path in paths),
        key=lambda item: (-item.risk_score, item.path),
    )


def summarize(audits: list[FileAudit]) -> dict[str, int]:
    return {
        "files_scanned": len(audits),
        "vue_files": sum(1 for item in audits if item.kind == "vue"),
        "css_files": sum(1 for item in audits if item.kind == "css"),
        "mixed_style_components": sum(1 for item in audits if item.mixed_style_sources),
        "files_with_many_media_queries": sum(1 for item in audits if item.media_queries >= 3),
        "files_with_token_redefs": sum(1 for item in audits if item.cds_token_redefs > 0),
        "files_with_many_literals": sum(
            1
            for item in audits
            if (item.literal_px + item.literal_rem + item.literal_hex + item.literal_rgba) >= 10
        ),
        "files_with_gradients_or_mix": sum(
            1 for item in audits if item.gradients > 0 or item.color_mix > 0 or item.backdrop_filters > 0
        ),
    }


def print_text_report(audits: list[FileAudit], limit: int) -> None:
    summary = summarize(audits)
    print("# ZERO Style Authority Audit")
    print()
    print("## Summary")
    for key, value in summary.items():
        print(f"- {key}: {value}")

    print()
    print(f"## Top {min(limit, len(audits))} Hotspots")
    for item in audits[:limit]:
        literals = item.literal_px + item.literal_rem + item.literal_hex + item.literal_rgba
        print(
            f"- score={item.risk_score:02d} | {item.path} | media={item.media_queries} "
            f"| literals={literals} | mixed={str(item.mixed_style_sources).lower()} "
            f"| findings={'; '.join(item.findings)}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit style authority in CDS_VUE3_ZERO.")
    parser.add_argument("--limit", type=int, default=30, help="Number of hotspot files to print.")
    parser.add_argument("--json", action="store_true", help="Print full JSON instead of text.")
    args = parser.parse_args()

    audits = audit(list_style_files())
    if args.json:
        payload = {
            "summary": summarize(audits),
            "hotspots": [asdict(item) for item in audits],
        }
        print(json.dumps(payload, ensure_ascii=True, indent=2))
        return

    print_text_report(audits, args.limit)


if __name__ == "__main__":
    main()

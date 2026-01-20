#!/usr/bin/env python3
"""
Full audit (front + back) for CDS.
Outputs AUDIT_REPORT.md at repo root.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "src"
REPORT_PATH = ROOT / "AUDIT_REPORT.md"


@dataclass
class Finding:
    severity: str
    title: str
    detail: str
    path: str | None = None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def list_py_files(base: Path) -> Iterable[Path]:
    return base.rglob("*.py")


def list_vue_files(base: Path) -> Iterable[Path]:
    return base.rglob("*.vue")


def find_alembic_heads(versions_dir: Path) -> Tuple[List[str], List[Finding]]:
    findings: List[Finding] = []
    heads = []
    for file in versions_dir.glob("*.py"):
        content = read_text(file)
        m = re.search(r"down_revision\s*:\s*[^=]*=\s*(.*)", content)
        if not m:
            continue
        val = m.group(1).strip()
        if val in ("None", "None\n", "None\r\n"):
            heads.append(file.name)
    if len(heads) > 1:
        findings.append(
            Finding(
                "critical",
                "Alembic multiple heads",
                f"Multiple migrations have down_revision = None: {', '.join(heads)}",
                str((versions_dir).as_posix()),
            )
        )
    return heads, findings


def check_permissions_usage(routers_dir: Path) -> List[Finding]:
    findings: List[Finding] = []
    total_routers = 0
    routers_with_require = 0
    for file in routers_dir.rglob("*.py"):
        content = read_text(file)
        if "APIRouter" not in content:
            continue
        total_routers += 1
        if "require_permission" in content or "require_any_permission" in content or "require_permissions" in content:
            routers_with_require += 1
    if total_routers and routers_with_require == 0:
        findings.append(
            Finding(
                "high",
                "Permissions not applied in routers",
                f"No router in {routers_dir.as_posix()} uses require_permission/require_any_permission/require_permissions.",
                routers_dir.as_posix(),
            )
        )
    return findings


def check_seed_scripts(scripts_dir: Path) -> List[Finding]:
    findings: List[Finding] = []
    seed_files = list(scripts_dir.rglob("*.py"))
    if not seed_files:
        findings.append(
            Finding(
                "high",
                "No seed scripts",
                "No scripts found to seed roles/permissions/users.",
                scripts_dir.as_posix(),
            )
        )
        return findings

    seed_text = "\n".join(read_text(p) for p in seed_files)
    if "Permission" not in seed_text or "Role" not in seed_text:
        findings.append(
            Finding(
                "high",
                "Missing permission/role seeding",
                "Seed scripts exist but do not create Permission/Role data.",
                scripts_dir.as_posix(),
            )
        )
    return findings


def find_placeholder_vue(views_dir: Path) -> List[Finding]:
    findings: List[Finding] = []
    for file in list_vue_files(views_dir):
        content = read_text(file)
        if "Inputs definidos por contrato" in content or "<pre>" in content:
            findings.append(
                Finding(
                    "medium",
                    "Placeholder view",
                    "View still contains placeholder content.",
                    str(file.relative_to(ROOT)),
                )
            )
    return findings


def list_api_routes(routers_dir: Path) -> List[str]:
    routes = []
    for file in routers_dir.rglob("*.py"):
        content = read_text(file)
        for m in re.finditer(r"@router\.(get|post|put|patch|delete)\(\"([^\"]+)\"\)", content):
            routes.append(m.group(2))
    return sorted(set(routes))


def list_front_routes(router_file: Path) -> List[str]:
    content = read_text(router_file)
    return sorted(set(re.findall(r"path:\s*'([^']+)'", content)))


def audit() -> List[Finding]:
    findings: List[Finding] = []

    # Alembic heads
    versions_dir = BACKEND / "alembic" / "versions"
    if versions_dir.exists():
        _, alembic_findings = find_alembic_heads(versions_dir)
        findings.extend(alembic_findings)
    else:
        findings.append(
            Finding("critical", "Alembic versions missing", "No alembic/versions directory found.", str(versions_dir))
        )

    # Permissions usage in routers
    findings.extend(check_permissions_usage(BACKEND / "app" / "routers"))

    # Seed scripts
    findings.extend(check_seed_scripts(BACKEND / "scripts"))

    # Placeholder views
    findings.extend(find_placeholder_vue(FRONTEND / "modules"))

    # Compare front/back routes (informational)
    backend_routes = list_api_routes(BACKEND / "app" / "routers")
    frontend_routes = list_front_routes(ROOT / "src" / "router" / "index.js")
    if backend_routes and frontend_routes:
        # Not a strict mismatch; include info only
        findings.append(
            Finding(
                "info",
                "Routes inventory",
                f"Backend routes: {len(backend_routes)}, Frontend routes: {len(frontend_routes)}",
                None,
            )
        )

    return findings


def render_report(findings: List[Finding]) -> str:
    by_sev = {"critical": [], "high": [], "medium": [], "low": [], "info": []}
    for f in findings:
        by_sev.setdefault(f.severity, []).append(f)

    def render_group(title: str, items: List[Finding]) -> str:
        if not items:
            return f"## {title}\n\n- None\n"
        lines = [f"## {title}\n"]
        for f in items:
            path = f" ({f.path})" if f.path else ""
            lines.append(f"- {f.title}: {f.detail}{path}")
        return "\n".join(lines) + "\n"

    sections = [
        "# CDS Audit Report",
        "",
        render_group("Critical", by_sev["critical"]),
        render_group("High", by_sev["high"]),
        render_group("Medium", by_sev["medium"]),
        render_group("Low", by_sev["low"]),
        render_group("Info", by_sev["info"]),
    ]
    return "\n".join(sections)


def main() -> None:
    findings = audit()
    REPORT_PATH.write_text(render_report(findings), encoding="utf-8")
    summary = {
        "critical": sum(1 for f in findings if f.severity == "critical"),
        "high": sum(1 for f in findings if f.severity == "high"),
        "medium": sum(1 for f in findings if f.severity == "medium"),
        "low": sum(1 for f in findings if f.severity == "low"),
        "info": sum(1 for f in findings if f.severity == "info"),
    }
    print(json.dumps(summary, indent=2))
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    main()

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DATA_DIR = Path(__file__).resolve().parent.parent / "data"
FAQ_PATH = DATA_DIR / "whatsapp_bot_faq.csv"
CONFIG_PATH = DATA_DIR / "whatsapp_bot_config.json"


@dataclass(slots=True)
class WhatsAppFaqEntry:
    id: str
    active: bool
    intent: str
    priority: int
    triggers: list[str]
    response: str
    action_type: str
    action_label: str
    action_target: str
    handoff: bool
    notes: str


def load_whatsapp_bot_config() -> dict[str, Any]:
    with CONFIG_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def load_whatsapp_bot_faq() -> list[WhatsAppFaqEntry]:
    entries: list[WhatsAppFaqEntry] = []
    with FAQ_PATH.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            entries.append(
                WhatsAppFaqEntry(
                    id=(row.get("id") or "").strip(),
                    active=_to_bool(row.get("active")),
                    intent=(row.get("intent") or "").strip(),
                    priority=_to_int(row.get("priority")),
                    triggers=_split_pipe_list(row.get("triggers")),
                    response=(row.get("response") or "").strip(),
                    action_type=(row.get("action_type") or "").strip(),
                    action_label=(row.get("action_label") or "").strip(),
                    action_target=(row.get("action_target") or "").strip(),
                    handoff=_to_bool(row.get("handoff")),
                    notes=(row.get("notes") or "").strip(),
                )
            )
    return entries


def _split_pipe_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [part.strip().lower() for part in raw.split("|") if part.strip()]


def _to_bool(raw: str | None) -> bool:
    return str(raw).strip().lower() in {"1", "true", "yes", "si"}


def _to_int(raw: str | None) -> int:
    try:
        return int(str(raw).strip())
    except ValueError:
        return 0

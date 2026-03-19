from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

from app.services.whatsapp_bot_content import (
    WhatsAppFaqEntry,
    load_whatsapp_bot_config,
    load_whatsapp_bot_faq,
)


@dataclass(slots=True)
class WhatsAppBotReply:
    intent: str
    text: str
    handoff: bool = False


class WhatsAppBotService:
    def __init__(self) -> None:
        self.config = load_whatsapp_bot_config()
        self.entries = sorted(
            [entry for entry in load_whatsapp_bot_faq() if entry.active],
            key=lambda entry: entry.priority,
            reverse=True,
        )

    def build_reply(self, incoming_text: str) -> WhatsAppBotReply:
        normalized = _normalize_text(incoming_text)
        if not normalized:
            return self._fallback_reply()

        matched = self._match_entry(normalized)
        if matched:
            entry, matched_keywords = matched
            if entry.action_type == "collect" and _looks_like_complete_collect_request(normalized, matched_keywords):
                return self._schedule_reply()
            return self._entry_reply(entry)

        if _contains_any_keyword(normalized, self.config.get("handoff_keywords") or []):
            return self._handoff_reply()

        if _contains_any_keyword(normalized, self.config.get("agenda_keywords") or []):
            return self._schedule_reply()

        return self._fallback_reply()

    def _match_entry(self, normalized_text: str) -> tuple[WhatsAppFaqEntry, list[str]] | None:
        best_match: tuple[tuple[int, int, int], WhatsAppFaqEntry, list[str]] | None = None

        for entry in self.entries:
            matched_keywords = _matching_keywords(normalized_text, entry.triggers)
            if not matched_keywords:
                continue

            score = (
                len(matched_keywords),
                max(len(keyword) for keyword in matched_keywords),
                entry.priority,
            )
            if best_match is None or score > best_match[0]:
                best_match = (score, entry, matched_keywords)

        if best_match is None:
            return None
        return best_match[1], best_match[2]

    def _entry_reply(self, entry: WhatsAppFaqEntry) -> WhatsAppBotReply:
        chunks = [entry.response]
        target = _normalize_target(entry.action_target)

        if entry.action_type == "schedule" and target:
            chunks.append(f"{entry.action_label or 'Agendar'}: {target}")
        elif entry.action_type == "schedule":
            schedule_target = self._schedule_target()
            if schedule_target:
                chunks.append(f"{entry.action_label or 'Agendar'}: {schedule_target}")
        elif entry.action_type == "handoff":
            chunks.append(f"{entry.action_label or 'Hablar con humano'}: {target or self._human_target()}")
        elif entry.action_type == "collect" and target and not target.startswith("collect:"):
            chunks.append(f"{entry.action_label}: {target}")

        return WhatsAppBotReply(
            intent=entry.intent,
            text="\n\n".join(chunk for chunk in chunks if chunk),
            handoff=entry.handoff or entry.action_type == "handoff",
        )

    def _fallback_reply(self) -> WhatsAppBotReply:
        chunks = [str(self.config.get("fallback_message") or "").strip()]
        schedule_target = self._schedule_target()
        human_target = self._human_target()
        if schedule_target:
            chunks.append(f"Agendar revision: {schedule_target}")
        if human_target:
            chunks.append(f"Hablar con humano: {human_target}")
        return WhatsAppBotReply(intent="fallback", text="\n\n".join(chunk for chunk in chunks if chunk))

    def _handoff_reply(self) -> WhatsAppBotReply:
        chunks = [str(self.config.get("human_handoff_message") or "").strip()]
        human_target = self._human_target()
        if human_target:
            chunks.append(f"Hablar con humano: {human_target}")
        return WhatsAppBotReply(intent="handoff", text="\n\n".join(chunk for chunk in chunks if chunk), handoff=True)

    def _schedule_reply(self) -> WhatsAppBotReply:
        chunks = [str(self.config.get("schedule_push_message") or "").strip()]
        schedule_target = self._schedule_target()
        if schedule_target:
            chunks.append(f"Agendar revision: {schedule_target}")
        return WhatsAppBotReply(intent="agenda", text="\n\n".join(chunk for chunk in chunks if chunk))

    def _human_target(self) -> str:
        return _normalize_target(self.config.get("human_handoff_url"))

    def _schedule_target(self) -> str:
        return _normalize_target(self.config.get("scheduling_url"))


def _contains_any_keyword(text: str, keywords: list[str]) -> bool:
    return bool(_matching_keywords(text, keywords))


def _matching_keywords(text: str, keywords: list[str]) -> list[str]:
    return [keyword for keyword in keywords if _keyword_matches(text, keyword)]


def _keyword_matches(text: str, keyword: str) -> bool:
    candidate = str(keyword or "").strip()
    if not candidate:
        return False
    pattern = rf"(?<!\w){re.escape(candidate)}(?!\w)"
    return re.search(pattern, text) is not None


def _looks_like_complete_collect_request(text: str, matched_keywords: list[str]) -> bool:
    segments = [segment.strip() for segment in re.split(r"[,;\n/]+", text) if segment.strip()]
    has_model_hint = re.search(r"\b[a-z]+\s*[-]?\d+[a-z0-9-]*\b", text) is not None
    has_status_hint = _contains_any_keyword(
        text,
        [
            "fue abierto",
            "no fue abierto",
            "abierto",
            "sin abrir",
            "enciende",
            "no enciende",
        ],
    )
    has_symptom_hint = _contains_any_keyword(
        text,
        [
            "sintoma",
            "falla",
            "no suena",
            "no suenan",
            "ruido",
            "tecla",
            "teclas",
        ],
    )

    return (
        (len(segments) >= 3 and has_symptom_hint)
        or (len(segments) >= 2 and has_symptom_hint and (has_status_hint or has_model_hint))
        or (len(matched_keywords) >= 2 and has_model_hint and has_symptom_hint)
    )


def _normalize_target(raw: str | None) -> str:
    value = str(raw or "").strip()
    if not value:
        return ""
    if value.startswith(("http://", "https://")):
        return value
    if value.startswith("wa.me/"):
        return f"https://{value}"
    return value


def _normalize_text(value: str | None) -> str:
    text = str(value or "").strip().lower()
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"\s+", " ", text)
    return text

"""Helpers for OT code generation and OT group consistency."""

from __future__ import annotations

import re

from sqlalchemy.orm import Session

from app.models.device import Device
from app.models.repair import Repair

_OT_PATTERN = re.compile(r"^CDS-(\d{3})-OT-(\d{3})(?:-(\d{2}))?$")


def client_code(client_id: int) -> str:
    return f"CDS-{client_id:03d}"


def repair_code(client_id: int, repair_id: int, suffix: int | None = None) -> str:
    base = f"{client_code(client_id)}-OT-{repair_id:03d}"
    if suffix is None:
        return base
    return f"{base}-{int(suffix):02d}"


def get_repair_client_id(db: Session, repair: Repair) -> int | None:
    device = db.query(Device).filter(Device.id == repair.device_id).first()
    if not device:
        return None
    return int(device.client_id) if device.client_id is not None else None


def parent_belongs_to_client(db: Session, parent_repair: Repair, client_id: int) -> bool:
    parent_client_id = get_repair_client_id(db, parent_repair)
    return parent_client_id == client_id


def parse_ot_parts(code: str | None) -> tuple[int, int, int | None] | None:
    if not code:
        return None
    match = _OT_PATTERN.match(str(code).strip())
    if not match:
        return None
    client_idx = int(match.group(1))
    base_repair_id = int(match.group(2))
    suffix = int(match.group(3)) if match.group(3) else None
    return client_idx, base_repair_id, suffix


def infer_ot_group_values(repair: Repair) -> tuple[int, int]:
    """
    Infer OT group values from existing OT code when legacy rows do not have
    ot_parent_id / ot_sequence populated.
    """
    parsed = parse_ot_parts(repair.repair_number)
    if not parsed:
        return repair.id, 1

    _, base_repair_id, suffix = parsed
    if suffix is None:
        if base_repair_id == repair.id:
            return repair.id, 1
        return repair.id, 1

    return base_repair_id, max(suffix, 1)


def ensure_repair_ot_fields(db: Session, repair: Repair) -> None:
    if repair.ot_parent_id and repair.ot_sequence and int(repair.ot_sequence) > 0:
        return

    parent_id, sequence = infer_ot_group_values(repair)
    if not db.query(Repair.id).filter(Repair.id == parent_id).first():
        parent_id = repair.id
        sequence = 1

    repair.ot_parent_id = parent_id
    repair.ot_sequence = sequence
    db.flush()


def _collect_existing_sequences(db: Session, client_id: int, parent_repair: Repair) -> set[int]:
    used: set[int] = set()

    if parent_repair.ot_sequence and int(parent_repair.ot_sequence) > 0:
        used.add(int(parent_repair.ot_sequence))

    rows = (
        db.query(Repair.ot_sequence)
        .filter(Repair.ot_parent_id == parent_repair.id)
        .all()
    )
    for (sequence,) in rows:
        if sequence and int(sequence) > 0:
            used.add(int(sequence))

    base = repair_code(client_id, parent_repair.id)

    if parent_repair.repair_number == base:
        used.add(1)

    suffix_rows = (
        db.query(Repair.repair_number)
        .filter(Repair.repair_number.like(f"{base}-%"))
        .all()
    )
    for (repair_number,) in suffix_rows:
        parsed = parse_ot_parts(repair_number)
        if not parsed:
            continue
        _, _, suffix = parsed
        if suffix and suffix > 0:
            used.add(suffix)

    return used


def _next_available_sequence(used: set[int]) -> int:
    if not used:
        return 1
    sequence = max(used) + 1
    while sequence in used:
        sequence += 1
    return sequence


def ensure_parent_group_defaults(db: Session, parent_repair: Repair, client_id: int) -> None:
    if parent_repair.ot_parent_id is None:
        parent_repair.ot_parent_id = parent_repair.id
    if not parent_repair.ot_sequence or int(parent_repair.ot_sequence) <= 0:
        parent_repair.ot_sequence = 1

    base = repair_code(client_id, parent_repair.id)

    if not parent_repair.repair_number or str(parent_repair.repair_number).startswith("R-"):
        parent_repair.repair_number = base

    # Keep legacy behavior: when OT becomes grouped, parent is represented as -01.
    if parent_repair.repair_number == base:
        parent_repair.repair_number = repair_code(client_id, parent_repair.id, 1)
        parent_repair.ot_sequence = 1

    db.flush()


def next_group_suffix(db: Session, client_id: int, parent_repair: Repair) -> int:
    used = _collect_existing_sequences(db, client_id, parent_repair)
    return _next_available_sequence(used)


def assign_repair_ot_code(
    db: Session,
    repair: Repair,
    client_id: int,
    parent_repair: Repair | None = None,
    requested_suffix: int | None = None,
) -> tuple[int, int]:
    """
    Assign OT group metadata and OT code on a repair.

    Returns:
        (ot_parent_id, ot_sequence)
    """
    if not repair.id:
        raise ValueError("Repair must have an ID before assigning OT code")

    if parent_repair is None:
        sequence = 1
        if requested_suffix is not None:
            try:
                requested = int(requested_suffix)
                if requested > 0:
                    sequence = requested
            except (TypeError, ValueError):
                sequence = 1

        repair.ot_parent_id = repair.id
        repair.ot_sequence = sequence
        repair.repair_number = (
            repair_code(client_id, repair.id, sequence)
            if sequence > 1
            else repair_code(client_id, repair.id)
        )
        return repair.ot_parent_id, repair.ot_sequence

    ensure_parent_group_defaults(db, parent_repair, client_id)

    used = _collect_existing_sequences(db, client_id, parent_repair)

    sequence: int
    if requested_suffix is not None:
        try:
            candidate = int(requested_suffix)
        except (TypeError, ValueError):
            candidate = 0
        if candidate > 0 and candidate not in used:
            sequence = candidate
        else:
            sequence = _next_available_sequence(used)
    else:
        sequence = _next_available_sequence(used)

    repair.ot_parent_id = parent_repair.id
    repair.ot_sequence = sequence
    repair.repair_number = repair_code(client_id, parent_repair.id, sequence)
    return repair.ot_parent_id, repair.ot_sequence

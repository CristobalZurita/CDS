"""Add OT group columns to repairs for parent/sequence tracking

Revision ID: 008_add_ot_group_columns_to_repairs
Revises: 007_add_image_url_to_products
Create Date: 2026-02-19 16:30:00.000000
"""

from __future__ import annotations

import re

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "008_add_ot_group_columns_to_repairs"
down_revision = "007_add_image_url_to_products"
branch_labels = None
depends_on = None


_OT_CODE_PATTERN = re.compile(r"^CDS-\d{3}-OT-(\d{3})(?:-(\d{2}))?$")


def _derive_ot_group_assignment(repair_id: int, repair_number: str | None, valid_ids: set[int]) -> tuple[int, int]:
    if repair_number:
        match = _OT_CODE_PATTERN.match(str(repair_number).strip())
        if match:
            base_id = int(match.group(1))
            suffix = int(match.group(2)) if match.group(2) else 1
            if base_id in valid_ids:
                return base_id, max(suffix, 1)
    return repair_id, 1


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "repairs" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("repairs")}

    if "ot_parent_id" not in columns:
        op.add_column("repairs", sa.Column("ot_parent_id", sa.Integer(), nullable=True))
    if "ot_sequence" not in columns:
        op.add_column("repairs", sa.Column("ot_sequence", sa.Integer(), nullable=True))

    # Deterministic backfill to preserve legacy OT naming and ensure uniqueness.
    rows = bind.execute(
        sa.text(
            """
            SELECT id, repair_number, ot_parent_id, ot_sequence
            FROM repairs
            ORDER BY id ASC
            """
        )
    ).mappings().all()

    valid_ids = {int(row["id"]) for row in rows}
    used_sequences: dict[int, set[int]] = {}

    for row in rows:
        repair_id = int(row["id"])
        parent_id = row.get("ot_parent_id")
        sequence = row.get("ot_sequence")

        if parent_id is not None and sequence is not None:
            try:
                candidate_parent = int(parent_id)
                candidate_sequence = int(sequence)
            except (TypeError, ValueError):
                candidate_parent = repair_id
                candidate_sequence = 1
        else:
            candidate_parent, candidate_sequence = _derive_ot_group_assignment(
                repair_id=repair_id,
                repair_number=row.get("repair_number"),
                valid_ids=valid_ids,
            )

        if candidate_parent not in valid_ids:
            candidate_parent = repair_id
        if candidate_sequence <= 0:
            candidate_sequence = 1

        reserved = used_sequences.setdefault(candidate_parent, set())
        while candidate_sequence in reserved:
            candidate_sequence += 1
        reserved.add(candidate_sequence)

        if parent_id != candidate_parent or sequence != candidate_sequence:
            bind.execute(
                sa.text(
                    """
                    UPDATE repairs
                    SET ot_parent_id = :parent_id,
                        ot_sequence = :ot_sequence
                    WHERE id = :repair_id
                    """
                ),
                {
                    "parent_id": candidate_parent,
                    "ot_sequence": candidate_sequence,
                    "repair_id": repair_id,
                },
            )

    inspector = sa.inspect(bind)
    index_names = {index["name"] for index in inspector.get_indexes("repairs")}

    if "ix_repairs_ot_parent_id" not in index_names:
        op.create_index("ix_repairs_ot_parent_id", "repairs", ["ot_parent_id"], unique=False)

    if "uq_repairs_ot_parent_sequence" not in index_names:
        op.create_index(
            "uq_repairs_ot_parent_sequence",
            "repairs",
            ["ot_parent_id", "ot_sequence"],
            unique=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "repairs" not in inspector.get_table_names():
        return

    index_names = {index["name"] for index in inspector.get_indexes("repairs")}

    if "uq_repairs_ot_parent_sequence" in index_names:
        op.drop_index("uq_repairs_ot_parent_sequence", table_name="repairs")

    if "ix_repairs_ot_parent_id" in index_names:
        op.drop_index("ix_repairs_ot_parent_id", table_name="repairs")

    columns = {column["name"] for column in inspector.get_columns("repairs")}

    if "ot_sequence" in columns:
        try:
            op.drop_column("repairs", "ot_sequence")
        except Exception:
            pass

    if "ot_parent_id" in columns:
        try:
            op.drop_column("repairs", "ot_parent_id")
        except Exception:
            pass

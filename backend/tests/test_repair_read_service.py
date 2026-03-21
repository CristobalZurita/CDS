from datetime import datetime, timedelta

from app.models.audit import AuditLog
from app.services.repair_helpers import auto_archive_repairs
from app.services.repair_read_service import RepairReadService
from app.services.repair_state_machine import RepairStateID


def test_list_repair_audit_filters_by_repair_id_in_db(db, sample_ot):
    repair_id = sample_ot["repair_id"]

    matching_log = AuditLog(
        event_type="repair.update",
        user_id=sample_ot["user"].id,
        details={"repair_id": repair_id, "field": "status_id"},
        message="matching repair",
    )
    other_log = AuditLog(
        event_type="repair.update",
        user_id=sample_ot["user"].id,
        details={"repair_id": repair_id + 999, "field": "status_id"},
        message="other repair",
    )
    string_log = AuditLog(
        event_type="repair.note",
        user_id=sample_ot["user"].id,
        details={"repair_id": str(repair_id), "field": "notes"},
        message="string repair id",
    )
    db.add_all([matching_log, other_log, string_log])
    db.commit()

    rows = RepairReadService(db).list_repair_audit(repair_id)
    row_ids = {row.id for row in rows}

    assert matching_log.id in row_ids
    assert string_log.id in row_ids
    assert other_log.id not in row_ids


def test_auto_archive_repairs_uses_archived_state_constant(db, sample_ot):
    repair = sample_ot["repair"]
    repair.delivery_date = datetime.utcnow() - timedelta(days=120)
    repair.archived_at = None
    repair.status_id = RepairStateID.ENTREGADO
    db.add(repair)
    db.commit()

    auto_archive_repairs(db)
    db.refresh(repair)

    assert repair.archived_at is not None
    assert repair.status_id == RepairStateID.ARCHIVADO

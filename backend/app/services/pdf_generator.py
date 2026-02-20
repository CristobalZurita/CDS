"""
Generador PDF aditivo para cierre OT.

No depende de librerías externas: construye un PDF válido con texto plano
para asegurar portabilidad en el backend actual.
"""

from __future__ import annotations

from datetime import date, datetime
from textwrap import wrap
from typing import Any, Dict, Iterable, List


PDF_PAGE_WIDTH = 595
PDF_PAGE_HEIGHT = 842
PDF_MARGIN_LEFT = 42
PDF_TOP_Y = 800
PDF_LINE_HEIGHT = 14
PDF_MAX_CHARS = 96
PDF_MAX_LINES_PER_PAGE = 48


def generate_pdf_placeholder(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compatibilidad backward: mantener firma antigua.
    """
    return {
        "status": "pending",
        "message": "PDF generation not implemented",
        "data": data,
    }


def _as_text(value: Any, default: str = "SIN_DATO") -> str:
    if value is None:
        return default
    if isinstance(value, datetime):
        return value.strftime("%d-%m-%Y %H:%M")
    if isinstance(value, date):
        return value.strftime("%d-%m-%Y")
    text = str(value).strip()
    return text if text else default


def _to_number(value: Any) -> float:
    if value in (None, "", "SIN_DATO"):
        return 0.0
    try:
        return float(value)
    except Exception:
        return 0.0


def _format_clp(value: Any) -> str:
    amount = _to_number(value)
    return f"${amount:,.0f} CLP"


def _escape_pdf_text(line: str) -> str:
    text = str(line or "")
    text = text.replace("\\", "\\\\")
    text = text.replace("(", "\\(").replace(")", "\\)")
    return text


def _wrap_lines(lines: Iterable[str], max_chars: int = PDF_MAX_CHARS) -> List[str]:
    wrapped: List[str] = []
    for raw in lines:
        line = str(raw or "")
        if len(line) <= max_chars:
            wrapped.append(line)
            continue

        for part in wrap(line, width=max_chars, break_long_words=True, break_on_hyphens=False):
            wrapped.append(part)
    return wrapped


def _chunk_lines(lines: List[str], max_lines: int = PDF_MAX_LINES_PER_PAGE) -> List[List[str]]:
    if not lines:
        return [["SIN_DATOS"]]
    return [lines[idx:idx + max_lines] for idx in range(0, len(lines), max_lines)]


def _build_content_stream(page_lines: List[str]) -> bytes:
    commands = [
        "BT",
        "/F1 10 Tf",
        f"{PDF_MARGIN_LEFT} {PDF_TOP_Y} Td",
        f"{PDF_LINE_HEIGHT} TL",
    ]

    for line in page_lines:
        commands.append(f"({_escape_pdf_text(line)}) Tj")
        commands.append("T*")

    commands.append("ET")
    content = "\n".join(commands)
    return content.encode("latin-1", errors="replace")


def _render_pdf(objects: List[bytes]) -> bytes:
    output = bytearray()
    output.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    offsets = [0]
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{idx} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")

    xref_start = len(output)
    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    output.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF".encode("ascii")
    )
    return bytes(output)


def build_repair_closure_lines(data: Dict[str, Any]) -> List[str]:
    lines: List[str] = []
    now = datetime.utcnow()

    lines.extend([
        "CIRUJANO DE SINTETIZADORES - INFORME DE CIERRE OT",
        f"Generado UTC: {_as_text(now)}",
        "",
        "IDENTIFICACION",
        f"OT: {_as_text(data.get('repair_code') or data.get('repair_number'))}",
        f"OT Base: {_as_text(data.get('repair_number'))}",
        f"Cliente: {_as_text(data.get('client_name'))}",
        f"Email cliente: {_as_text(data.get('client_email'))}",
        f"Telefono cliente: {_as_text(data.get('client_phone'))}",
        f"Instrumento: {_as_text(data.get('device_model'))}",
        f"Serial: {_as_text(data.get('device_serial'))}",
        f"Estado actual: {_as_text(data.get('status_name'))}",
        "",
        "FECHAS",
        f"Ingreso: {_as_text(data.get('intake_date'))}",
        f"Diagnostico: {_as_text(data.get('diagnosis_date'))}",
        f"Inicio trabajo: {_as_text(data.get('start_date'))}",
        f"Termino tecnico: {_as_text(data.get('completion_date'))}",
        f"Entrega: {_as_text(data.get('delivery_date'))}",
        "",
        "DETALLE TECNICO",
        f"Problema reportado: {_as_text(data.get('problem_reported'))}",
        f"Diagnostico: {_as_text(data.get('diagnosis'))}",
        f"Trabajo realizado: {_as_text(data.get('work_performed'))}",
        "",
        "COSTOS Y PAGO",
        f"Repuestos: {_format_clp(data.get('parts_cost'))}",
        f"Mano de obra: {_format_clp(data.get('labor_cost'))}",
        f"Costo adicional: {_format_clp(data.get('additional_cost'))}",
        f"Descuento: {_format_clp(data.get('discount'))}",
        f"Total OT: {_format_clp(data.get('total_cost'))}",
        f"Monto pagado: {_format_clp(data.get('paid_amount'))}",
        f"Estado pago: {_as_text(data.get('payment_status'))}",
        f"Metodo pago: {_as_text(data.get('payment_method'))}",
        "",
        "FIRMAS",
        f"Firma ingreso registrada: {'SI' if data.get('signature_ingreso_path') else 'NO'}",
        f"Firma retiro registrada: {'SI' if data.get('signature_retiro_path') else 'NO'}",
        "",
    ])

    components = data.get("components") or []
    lines.append(f"COMPONENTES UTILIZADOS ({len(components)})")
    if components:
        for comp in components:
            lines.append(
                f"- { _as_text(comp.get('component_table')) }.{ _as_text(comp.get('component_id')) } "
                f"x{_as_text(comp.get('quantity'))} "
                f"unit={_format_clp(comp.get('unit_cost'))} total={_format_clp(comp.get('total_cost'))}"
            )
    else:
        lines.append("- SIN_COMPONENTES_REGISTRADOS")
    lines.append("")

    notes = data.get("notes") or []
    lines.append(f"NOTAS TECNICAS ({len(notes)})")
    if notes:
        for note in notes:
            lines.append(
                f"- [{_as_text(note.get('note_type'))}] {_as_text(note.get('created_at'))}: {_as_text(note.get('note'))}"
            )
    else:
        lines.append("- SIN_NOTAS")
    lines.append("")

    lines.append(f"FOTOS REGISTRADAS: {_as_text(data.get('photos_count'), default='0')}")
    lines.append("")

    intake = data.get("intake_sheet") or {}
    if intake:
        lines.extend([
            "PLANILLA DE INGRESO (INTAKE)",
            f"Codigo cliente: {_as_text(intake.get('client_code'))}",
            f"Codigo OT planilla: {_as_text(intake.get('ot_code'))}",
            f"Codigo instrumento: {_as_text(intake.get('instrument_code'))}",
            f"Tipo equipo: {_as_text(intake.get('equipment_type'))}",
            f"Tipo servicio solicitado: {_as_text(intake.get('requested_service_type'))}",
            f"Tarifa reparacion: {_format_clp(intake.get('repair_tariff'))}",
            f"Tarifa material: {_format_clp(intake.get('material_tariff'))}",
            f"Tiempo estimado: {_as_text(intake.get('estimated_repair_time'))}",
            f"Fecha estimada termino: {_as_text(intake.get('estimated_completion_date'))}",
            f"Anotaciones: {_as_text(intake.get('annotations'))}",
            "",
        ])

    lines.extend([
        "OBSERVACIONES FINALES",
        _as_text(data.get("closure_notes"), default="SIN_OBSERVACIONES"),
    ])

    return _wrap_lines(lines)


def generate_repair_closure_pdf_bytes(data: Dict[str, Any]) -> bytes:
    lines = build_repair_closure_lines(data)
    pages = _chunk_lines(lines)
    page_count = max(len(pages), 1)

    page_ids = [3 + idx for idx in range(page_count)]
    content_ids = [3 + page_count + idx for idx in range(page_count)]
    font_id = 3 + (2 * page_count)
    total_objects = font_id

    objects: List[bytes] = [b""] * total_objects

    # 1) Catalog
    objects[0] = b"<< /Type /Catalog /Pages 2 0 R >>"

    # 2) Pages
    kids = " ".join(f"{pid} 0 R" for pid in page_ids)
    objects[1] = f"<< /Type /Pages /Kids [ {kids} ] /Count {page_count} >>".encode("ascii")

    # Page + content streams
    for idx, page_lines in enumerate(pages):
        page_obj_id = page_ids[idx]
        content_obj_id = content_ids[idx]
        stream = _build_content_stream(page_lines)

        page_obj = (
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PDF_PAGE_WIDTH} {PDF_PAGE_HEIGHT}] "
            f"/Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_obj_id} 0 R >>"
        )
        objects[page_obj_id - 1] = page_obj.encode("ascii")

        content_header = f"<< /Length {len(stream)} >>\nstream\n".encode("ascii")
        objects[content_obj_id - 1] = content_header + stream + b"\nendstream"

    # Font object (Helvetica builtin)
    objects[font_id - 1] = b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"

    return _render_pdf(objects)

"""Canonical backend business identity and customer-facing copy."""

from __future__ import annotations

from dataclasses import dataclass


def _append_message(base: str, message: str | None = None) -> str:
    extra = str(message or "").strip()
    if not extra:
        return base
    return f"{base}\n\n{extra}"


@dataclass(frozen=True)
class BusinessConfig:
    display_name: str = "Cirujano de Sintetizadores"
    system_description: str = "Sistema integral de gestión para taller de reparación de sintetizadores"
    location_label: str = "Valparaíso, Chile"
    item_label: str = "Instrumento"
    appointment_label: str = "Cita de agendamiento"
    appointment_workshop_label: str = "taller de reparación de sintetizadores"
    quote_default_item_name: str = "Servicio técnico"
    repair_closure_report_label: str = "INFORME DE CIERRE OT"
    two_factor_email_subject: str = "Código de verificación CDS"

    @property
    def api_title(self) -> str:
        return f"{self.display_name} API"

    @property
    def uppercase_name(self) -> str:
        return self.display_name.upper()

    @property
    def health_message(self) -> str:
        return f"{self.api_title} is running"

    def quote_delivery_subject(self, quote_number: str) -> str:
        return f"Cotización {quote_number} - {self.display_name}"

    def appointment_event_title(self, customer_name: str) -> str:
        return f"Cita: {customer_name}"

    def appointment_event_description(self, message: str | None = None) -> str:
        return _append_message(f"{self.appointment_label} en {self.display_name}", message)

    def appointment_confirmation_subject(self) -> str:
        return f"Confirmación de cita - {self.display_name}"

    def appointment_confirmation_intro(self) -> str:
        return f"Tu cita ha sido agendada correctamente en nuestro {self.appointment_workshop_label}."

    def repair_closure_pdf_title(self) -> str:
        return f"{self.uppercase_name} - {self.repair_closure_report_label}"

    def item_caption(self) -> str:
        return f"{self.item_label}:"


business_config = BusinessConfig()

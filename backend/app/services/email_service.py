"""
Email Service - SendGrid Integration

Proporciona funciones para enviar emails automáticos:
- Cotización guardada
- Reparación creada
- Status actualizado
- Recordatorio de cita
- Listo para recoger
"""

import os
import smtplib
import ssl
from typing import List, Dict, Any
from datetime import datetime
import logging
from email.message import EmailMessage

from app.core.config import settings

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

logger = logging.getLogger(__name__)

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@cirujanodesintetizadores.cl')

BASE_EMAIL_CSS = """
.email-body {
    font-family: Arial, sans-serif;
    color: #333;
}
.email-container {
    max-width: 600px;
    margin: 0 auto;
    padding: 20px;
}
.email-panel {
    background: #f5f5f5;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
}
.email-btn {
    color: white;
    padding: 10px 20px;
    border-radius: 5px;
    text-decoration: none;
    display: inline-block;
}
.email-btn-primary {
    background: #667eea;
}
.email-btn-whatsapp {
    background: #25D366;
}
.email-divider {
    border: none;
    border-top: 1px solid #ddd;
    margin: 20px 0;
}
.email-footnote {
    font-size: 12px;
    color: #999;
}
.email-status-title {
    color: #667eea;
}
.email-progress-wrap {
    margin: 15px 0;
}
.email-progress-track {
    background: #e2e8f0;
    height: 10px;
    border-radius: 5px;
    overflow: hidden;
}
.email-progress-fill {
    background: linear-gradient(90deg, #667eea, #764ba2);
    height: 100%;
}
.email-progress-label {
    text-align: center;
    margin-top: 10px;
    font-weight: bold;
}
.email-code {
    letter-spacing: 4px;
}
.email-success-panel {
    background: #c6f6d5;
    border-left: 4px solid #48bb78;
    padding: 20px;
    border-radius: 8px;
    margin: 20px 0;
}
.email-success-title {
    color: #22543d;
    margin: 0 0 10px 0;
}
.email-success-row {
    margin: 0;
}
.email-success-row-spaced {
    margin: 10px 0 0 0;
}
.email-title-orange {
    color: #ec6b00;
}
.email-panel-orange {
    background-color: #f5f5f5;
    padding: 15px;
    border-radius: 5px;
    margin: 20px 0;
}
.email-panel-orange-title {
    margin-top: 0;
    color: #ec6b00;
}
.email-text-muted {
    color: #5a5652;
    font-size: 0.9em;
}
.email-text-muted-small {
    color: #5a5652;
    font-size: 0.85em;
}
.email-link-orange {
    color: #ec6b00;
}
"""


def build_email_html(content: str, extra_css: str = "") -> str:
    return f"""
    <html>
        <head>
            <style>
                {BASE_EMAIL_CSS}
                {extra_css}
            </style>
        </head>
        <body class="email-body">
            {content}
        </body>
    </html>
    """


class EmailService:
    """
    Servicio de emails usando SendGrid
    """
    
    def __init__(self):
        self.smtp_server = settings.smtp_server
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.from_email = settings.from_email or SENDGRID_FROM_EMAIL or self.smtp_user
        self.smtp_use_tls = settings.smtp_use_tls
        self.smtp_use_ssl = settings.smtp_use_ssl

        self.sendgrid_enabled = SENDGRID_AVAILABLE and bool(SENDGRID_API_KEY)
        self.smtp_enabled = bool(self.smtp_server and self.smtp_port and self.smtp_user and self.smtp_password)

        self.enabled = self.sendgrid_enabled or self.smtp_enabled
        if self.sendgrid_enabled:
            self.client = SendGridAPIClient(SENDGRID_API_KEY)
        if not self.enabled:
            logger.warning('Email service not configured. Emails will be logged instead.')
    
    def send_quotation_saved_email(self, email: str, customer_name: str, quotation_id: str, 
                                   instrument: str, min_price: float, max_price: float):
        """
        Envía email cuando una cotización es guardada
        """
        subject = f"Tu cotización #{quotation_id} ha sido generada"
        
        content = f"""
        <h2>¡Hola {customer_name}!</h2>
        <p>Tu cotización para <strong>{instrument}</strong> ha sido generada exitosamente.</p>
        
        <div class="email-panel">
            <h3>Detalles de la cotización:</h3>
            <p><strong>ID:</strong> {quotation_id}</p>
            <p><strong>Instrumento:</strong> {instrument}</p>
            <p><strong>Rango estimado:</strong> ${min_price:,.0f} - ${max_price:,.0f} CLP</p>
            <p><strong>Generada:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
        
        <p>Esta cotización es indicativa y válida por 30 días. El precio final puede variar según el diagnóstico detallado.</p>
        
        <p><a href="https://cirujanodesintetizadores.cl/cotizaciones/{quotation_id}" class="email-btn email-btn-primary">
            Ver cotización completa
        </a></p>
        
        <hr class="email-divider">
        <p class="email-footnote">
            Cirujano de Sintetizadores<br>
            Valparaíso, Chile<br>
            +56 9 8295 7538
        </p>
        """
        html_content = build_email_html(content)
        
        return self._send_email(email, subject, html_content)

    
    def send_repair_created_email(self, email: str, customer_name: str, repair_id: str,
                                  instrument: str, fault_description: str, estimated_completion: str):
        """
        Envía email cuando una reparación es creada
        """
        subject = f"Tu reparación #{repair_id} ha sido registrada"
        
        content = f"""
        <h2>¡Hola {customer_name}!</h2>
        <p>Tu reparación ha sido registrada en nuestro sistema.</p>
        
        <div class="email-panel">
            <h3>Detalles de la reparación:</h3>
            <p><strong>Ticket:</strong> {repair_id}</p>
            <p><strong>Instrumento:</strong> {instrument}</p>
            <p><strong>Falla reportada:</strong> {fault_description}</p>
            <p><strong>Estimado de finalización:</strong> {estimated_completion}</p>
        </div>
        
        <p>Recibirás actualizaciones sobre el estado de tu reparación a través de email y WhatsApp.</p>
        
        <p><a href="https://cirujanodesintetizadores.cl/reparaciones/{repair_id}" class="email-btn email-btn-primary">
            Seguimiento de reparación
        </a></p>
        
        <hr class="email-divider">
        <p class="email-footnote">
            Cirujano de Sintetizadores<br>
            Valparaíso, Chile<br>
            +56 9 8295 7538
        </p>
        """
        html_content = build_email_html(content)
        
        return self._send_email(email, subject, html_content)
    
    def send_repair_status_email(self, email: str, customer_name: str, repair_id: str,
                                 status: str, progress: int, notes: str = None):
        """
        Envía email cuando el status de una reparación cambia
        """
        status_labels = {
            'Ingreso': '📥 Ingreso',
            'Diagnóstico': '🧭 Diagnóstico',
            'Presupuesto': '💬 Presupuesto',
            'Aprobado': '✅ Aprobado',
            'En trabajo': '🔧 En trabajo',
            'Listo': '🟢 Listo',
            'Entregado': '📦 Entregado',
            'Noventena': '🕒 Noventena',
            'Archivado': '📁 Archivado',
            'Rechazado': '⛔ Rechazado'
        }
        
        subject = f"Actualización: Tu reparación {repair_id} - {status_labels.get(status, status)}"
        
        content = f"""
        <h2>¡Hola {customer_name}!</h2>
        <p>Tenemos una actualización sobre tu reparación:</p>
        
        <div class="email-panel">
            <h3 class="email-status-title">Estado: {status_labels.get(status, status)}</h3>
            <div class="email-progress-wrap">
                <div class="email-progress-track">
                    <div class="email-progress-fill"></div>
                </div>
                <p class="email-progress-label">{progress}% completado</p>
            </div>
        </div>
        
        {f'<p><strong>Notas:</strong> {notes}</p>' if notes else ''}
        
        <p><a href="https://cirujanodesintetizadores.cl/reparaciones/{repair_id}" class="email-btn email-btn-primary">
            Ver detalles completos
        </a></p>
        
        <hr class="email-divider">
        <p class="email-footnote">
            Cirujano de Sintetizadores<br>
            Valparaíso, Chile<br>
            +56 9 8295 7538
        </p>
        """
        extra_css = f".email-progress-fill {{ width: {progress}%; }}"
        html_content = build_email_html(content, extra_css=extra_css)
        
        return self._send_email(email, subject, html_content)
    
    def send_appointment_reminder_email(self, email: str, customer_name: str, 
                                       appointment_date: str, appointment_time: str):
        """
        Envía recordatorio de cita 24 horas antes
        """
        subject = f"Recordatorio: Tu cita está programada para {appointment_date}"
        
        content = f"""
        <h2>¡Hola {customer_name}!</h2>
        <p>Te recordamos que tienes una cita programada:</p>
        
        <div class="email-panel">
            <h3>📅 Detalles de tu cita:</h3>
            <p><strong>Fecha:</strong> {appointment_date}</p>
            <p><strong>Hora:</strong> {appointment_time}</p>
            <p><strong>Ubicación:</strong> Valparaíso, Chile</p>
        </div>
        
        <h4>Por favor recuerda:</h4>
        <ul>
            <li>Lleva tu instrumento con el problema y todos los accesorios</li>
            <li>Trae tu cédula de identidad o pasaporte</li>
            <li>Si no puedes asistir, notifica con 24 horas de anticipación</li>
        </ul>
        
        <p><a href="https://wa.me/56982957538?text=Hola,%20tengo%20una%20cita%20programada" class="email-btn email-btn-whatsapp">
            Confirmar por WhatsApp
        </a></p>
        
        <hr class="email-divider">
        <p class="email-footnote">
            Cirujano de Sintetizadores<br>
            Valparaíso, Chile<br>
            +56 9 8295 7538
        </p>
        """
        html_content = build_email_html(content)
        
        return self._send_email(email, subject, html_content)

    def send_two_factor_code(self, email: str, code: str):
        subject = "Código de verificación CDS"
        content = f"""
        <h2>Tu código de verificación</h2>
        <p>Usa este código para completar el inicio de sesión:</p>
        <h1 class="email-code">{code}</h1>
        <p>Este código expira en 10 minutos.</p>
        """
        html_content = build_email_html(content)
        return self._send_email(email, subject, html_content)
    
    def send_ready_for_pickup_email(self, email: str, customer_name: str, repair_id: str,
                                    instrument: str, total_cost: float):
        """
        Envía email cuando la reparación está lista para recoger
        """
        subject = f"¡Tu {instrument} está listo para recoger!"
        
        content = f"""
        <h2>¡Hola {customer_name}!</h2>
        <p>¡Buenas noticias! Tu reparación está completada y lista para recoger.</p>
        
        <div class="email-success-panel">
            <h3 class="email-success-title">✓ Reparación Completada</h3>
            <p class="email-success-row"><strong>Instrumento:</strong> {instrument}</p>
            <p class="email-success-row-spaced"><strong>Ticket:</strong> {repair_id}</p>
        </div>
        
        <h4>Información de Pago:</h4>
        <p><strong>Costo total:</strong> ${total_cost:,.0f} CLP</p>
        <p>Aceptamos: Transferencia bancaria, Flow.cl, y efectivo</p>
        
        <h4>Próximos pasos:</h4>
        <ol>
            <li>Contáctanos para coordinar la hora de retiro</li>
            <li>Realiza el pago (si no lo has hecho)</li>
            <li>Retira tu instrumento</li>
        </ol>
        
        <p><a href="https://wa.me/56982957538?text=Hola,%20vengo%20a%20recoger%20mi%20reparaci%C3%B3n" class="email-btn email-btn-whatsapp">
            Coordinar retiro por WhatsApp
        </a></p>
        
        <hr class="email-divider">
        <p class="email-footnote">
            Cirujano de Sintetizadores<br>
            Valparaíso, Chile<br>
            +56 9 8295 7538
        </p>
        """
        html_content = build_email_html(content)
        
        return self._send_email(email, subject, html_content)
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Envía un email usando SMTP o SendGrid
        
        Returns:
            True si se envió exitosamente, False si hubo error
        """
        if not self.enabled:
            logger.info(f"Email (demo mode): To={to_email}, Subject={subject}")
            return True

        if self.smtp_enabled:
            return self._send_smtp_email(to_email, subject, html_content)
        
        if self.sendgrid_enabled:
            try:
                message = Mail(
                    from_email=SENDGRID_FROM_EMAIL,
                    to_emails=to_email,
                    subject=subject,
                    html_content=html_content
                )
                
                response = self.client.send(message)
                logger.info(f"Email sent to {to_email}: {response.status_code}")
                return True
            except Exception as e:
                logger.error(f"Error sending email to {to_email}: {str(e)}")
                return False

        logger.warning("Email service not configured correctly.")
        return False

    def _send_smtp_email(self, to_email: str, subject: str, html_content: str) -> bool:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = to_email
        msg.set_content("Este mensaje requiere HTML.")
        msg.add_alternative(html_content, subtype="html")

        try:
            if self.smtp_use_ssl:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    if self.smtp_use_tls:
                        context = ssl.create_default_context()
                        server.starttls(context=context)
                    server.login(self.smtp_user, self.smtp_password)
                    server.send_message(msg)
            logger.info(f"SMTP email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"SMTP error sending email to {to_email}: {str(e)}")
            return False

    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        return self._send_email(to_email, subject, html_content)


async def send_appointment_confirmation(
    email: str,
    nombre: str,
    fecha,
    appointment_id: int
) -> bool:
    """Send appointment confirmation email"""
    
    # Format fecha
    fecha_formateada = fecha.strftime("%d de %B de %Y a las %H:%M")
    
    content = f"""
    <div class="email-container">
        <h2 class="email-title-orange">¡Cita Agendada Exitosamente!</h2>
        
        <p>Hola <strong>{nombre}</strong>,</p>
        
        <p>Tu cita ha sido agendada correctamente en nuestro taller de reparación de sintetizadores.</p>
        
        <div class="email-panel-orange">
            <h3 class="email-panel-orange-title">Detalles de tu cita:</h3>
            <p><strong>Fecha y hora:</strong> {fecha_formateada}</p>
            <p><strong>ID de cita:</strong> {appointment_id}</p>
        </div>
        
        <p>Recibirás un mensaje de confirmación cuando nuestro equipo revise tu solicitud.</p>
        
        <p class="email-text-muted">
            Si necesitas cambiar o cancelar tu cita, por favor responde a este correo.
        </p>
        
        <hr class="email-divider">
        
        <p class="email-text-muted-small">
            <strong>Cirujano de Sintetizadores</strong><br>
            Especialistas en reparación y mantenimiento de sintetizadores<br>
            <a href="https://www.cirujanodesintetizadores.cl" class="email-link-orange">www.cirujanodesintetizadores.cl</a>
        </p>
    </div>
    """
    extra_css = """
    .email-body { color: #3e3c38; }
    .email-divider { margin: 30px 0; }
    """
    html_content = build_email_html(content, extra_css=extra_css)
    
    service = EmailService()
    return service.send_email(
        to_email=email,
        subject="Confirmación de cita - Cirujano de Sintetizadores",
        html_content=html_content
    )


# Global instance
email_service = EmailService()

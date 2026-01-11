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
from typing import List, Dict, Any
from datetime import datetime
import logging

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

logger = logging.getLogger(__name__)

SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY')
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', 'noreply@cirujanodesintetizadores.cl')


class EmailService:
    """
    Servicio de emails usando SendGrid
    """
    
    def __init__(self):
        self.enabled = SENDGRID_AVAILABLE and bool(SENDGRID_API_KEY)
        if self.enabled:
            self.client = SendGridAPIClient(SENDGRID_API_KEY)
        else:
            logger.warning('SendGrid email service not available. Emails will be logged instead.')
    
    def send_quotation_saved_email(self, email: str, customer_name: str, quotation_id: str, 
                                   instrument: str, min_price: float, max_price: float):
        """
        Envía email cuando una cotización es guardada
        """
        subject = f"Tu cotización #{quotation_id} ha sido generada"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>¡Hola {customer_name}!</h2>
                <p>Tu cotización para <strong>{instrument}</strong> ha sido generada exitosamente.</p>
                
                <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Detalles de la cotización:</h3>
                    <p><strong>ID:</strong> {quotation_id}</p>
                    <p><strong>Instrumento:</strong> {instrument}</p>
                    <p><strong>Rango estimado:</strong> ${min_price:,.0f} - ${max_price:,.0f} CLP</p>
                    <p><strong>Generada:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
                </div>
                
                <p>Esta cotización es indicativa y válida por 30 días. El precio final puede variar según el diagnóstico detallado.</p>
                
                <p><a href="https://cirujanodesintetizadores.cl/cotizaciones/{quotation_id}" 
                      style="background: #667eea; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block;">
                    Ver cotización completa
                </a></p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #999;">
                    Cirujano de Sintetizadores<br>
                    Valparaíso, Chile<br>
                    +56 9 8295 7538
                </p>
            </body>
        </html>
        """
        
        return self._send_email(email, subject, html_content)
    
    def send_repair_created_email(self, email: str, customer_name: str, repair_id: str,
                                  instrument: str, fault_description: str, estimated_completion: str):
        """
        Envía email cuando una reparación es creada
        """
        subject = f"Tu reparación #{repair_id} ha sido registrada"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>¡Hola {customer_name}!</h2>
                <p>Tu reparación ha sido registrada en nuestro sistema.</p>
                
                <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3>Detalles de la reparación:</h3>
                    <p><strong>Ticket:</strong> {repair_id}</p>
                    <p><strong>Instrumento:</strong> {instrument}</p>
                    <p><strong>Falla reportada:</strong> {fault_description}</p>
                    <p><strong>Estimado de finalización:</strong> {estimated_completion}</p>
                </div>
                
                <p>Recibirás actualizaciones sobre el estado de tu reparación a través de email y WhatsApp.</p>
                
                <p><a href="https://cirujanodesintetizadores.cl/reparaciones/{repair_id}"
                      style="background: #667eea; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block;">
                    Seguimiento de reparación
                </a></p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #999;">
                    Cirujano de Sintetizadores<br>
                    Valparaíso, Chile<br>
                    +56 9 8295 7538
                </p>
            </body>
        </html>
        """
        
        return self._send_email(email, subject, html_content)
    
    def send_repair_status_email(self, email: str, customer_name: str, repair_id: str,
                                 status: str, progress: int, notes: str = None):
        """
        Envía email cuando el status de una reparación cambia
        """
        status_labels = {
            'pending': '⏳ Pendiente',
            'waiting': '⌛ En Espera',
            'in-progress': '🔧 En Proceso',
            'completed': '✓ Completada',
            'cancelled': '✕ Cancelada'
        }
        
        subject = f"Actualización: Tu reparación {repair_id} - {status_labels.get(status, status)}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>¡Hola {customer_name}!</h2>
                <p>Tenemos una actualización sobre tu reparación:</p>
                
                <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #667eea;">Estado: {status_labels.get(status, status)}</h3>
                    <div style="margin: 15px 0;">
                        <div style="background: #e2e8f0; height: 10px; border-radius: 5px; overflow: hidden;">
                            <div style="background: linear-gradient(90deg, #667eea, #764ba2); height: 100%; width: {progress}%;"></div>
                        </div>
                        <p style="text-align: center; margin-top: 10px; font-weight: bold;">{progress}% completado</p>
                    </div>
                </div>
                
                {f'<p><strong>Notas:</strong> {notes}</p>' if notes else ''}
                
                <p><a href="https://cirujanodesintetizadores.cl/reparaciones/{repair_id}"
                      style="background: #667eea; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block;">
                    Ver detalles completos
                </a></p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #999;">
                    Cirujano de Sintetizadores<br>
                    Valparaíso, Chile<br>
                    +56 9 8295 7538
                </p>
            </body>
        </html>
        """
        
        return self._send_email(email, subject, html_content)
    
    def send_appointment_reminder_email(self, email: str, customer_name: str, 
                                       appointment_date: str, appointment_time: str):
        """
        Envía recordatorio de cita 24 horas antes
        """
        subject = f"Recordatorio: Tu cita está programada para {appointment_date}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>¡Hola {customer_name}!</h2>
                <p>Te recordamos que tienes una cita programada:</p>
                
                <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
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
                
                <p><a href="https://wa.me/56982957538?text=Hola,%20tengo%20una%20cita%20programada"
                      style="background: #25D366; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block;">
                    Confirmar por WhatsApp
                </a></p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #999;">
                    Cirujano de Sintetizadores<br>
                    Valparaíso, Chile<br>
                    +56 9 8295 7538
                </p>
            </body>
        </html>
        """
        
        return self._send_email(email, subject, html_content)
    
    def send_ready_for_pickup_email(self, email: str, customer_name: str, repair_id: str,
                                    instrument: str, total_cost: float):
        """
        Envía email cuando la reparación está lista para recoger
        """
        subject = f"¡Tu {instrument} está listo para recoger!"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; color: #333;">
                <h2>¡Hola {customer_name}!</h2>
                <p>¡Buenas noticias! Tu reparación está completada y lista para recoger.</p>
                
                <div style="background: #c6f6d5; border-left: 4px solid #48bb78; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #22543d; margin: 0 0 10px 0;">✓ Reparación Completada</h3>
                    <p style="margin: 0;"><strong>Instrumento:</strong> {instrument}</p>
                    <p style="margin: 10px 0 0 0;"><strong>Ticket:</strong> {repair_id}</p>
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
                
                <p><a href="https://wa.me/56982957538?text=Hola,%20vengo%20a%20recoger%20mi%20reparaci%C3%B3n"
                      style="background: #25D366; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; display: inline-block;">
                    Coordinar retiro por WhatsApp
                </a></p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #999;">
                    Cirujano de Sintetizadores<br>
                    Valparaíso, Chile<br>
                    +56 9 8295 7538
                </p>
            </body>
        </html>
        """
        
        return self._send_email(email, subject, html_content)
    
    def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Envía un email usando SendGrid
        
        Returns:
            True si se envió exitosamente, False si hubo error
        """
        if not self.enabled:
            logger.info(f"Email (demo mode): To={to_email}, Subject={subject}")
            return True
        
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


async def send_appointment_confirmation(
    email: str,
    nombre: str,
    fecha,
    appointment_id: int
) -> bool:
    """Send appointment confirmation email"""
    
    # Format fecha
    fecha_formateada = fecha.strftime("%d de %B de %Y a las %H:%M")
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #3e3c38;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #ec6b00;">¡Cita Agendada Exitosamente!</h2>
                
                <p>Hola <strong>{nombre}</strong>,</p>
                
                <p>Tu cita ha sido agendada correctamente en nuestro taller de reparación de sintetizadores.</p>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #ec6b00;">Detalles de tu cita:</h3>
                    <p><strong>Fecha y hora:</strong> {fecha_formateada}</p>
                    <p><strong>ID de cita:</strong> {appointment_id}</p>
                </div>
                
                <p>Recibirás un mensaje de confirmación cuando nuestro equipo revise tu solicitud.</p>
                
                <p style="color: #5a5652; font-size: 0.9em;">
                    Si necesitas cambiar o cancelar tu cita, por favor responde a este correo.
                </p>
                
                <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                
                <p style="color: #5a5652; font-size: 0.85em;">
                    <strong>Cirujano de Sintetizadores</strong><br>
                    Especialistas en reparación y mantenimiento de sintetizadores<br>
                    <a href="https://www.cirujanodesintetizadores.cl" style="color: #ec6b00;">www.cirujanodesintetizadores.cl</a>
                </p>
            </div>
        </body>
    </html>
    """
    
    service = EmailService()
    return service.send_email(
        to_email=email,
        subject="Confirmación de cita - Cirujano de Sintetizadores",
        html_content=html_content,
        from_email=SENDGRID_FROM_EMAIL
    )


# Global instance
email_service = EmailService()

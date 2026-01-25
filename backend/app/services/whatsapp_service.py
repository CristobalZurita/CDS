"""
WhatsApp Service - Meta Cloud API
"""
import logging
import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


class WhatsAppService:
    def __init__(self):
        self.token = settings.whatsapp_token
        self.phone_id = settings.whatsapp_phone_id
        self.api_url = settings.whatsapp_api_url.rstrip("/")
        self.template_name = settings.whatsapp_template_name
        self.template_lang = settings.whatsapp_template_lang
        self.enabled = bool(self.token and self.phone_id)

    def send_text(self, to_phone: str, message: str) -> bool:
        if not self.enabled:
            logger.warning("WhatsApp not configured. Skipping send.")
            return False
        url = f"{self.api_url}/{self.phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        if self.template_name:
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "template",
                "template": {
                    "name": self.template_name,
                    "language": {"code": self.template_lang},
                },
            }
        else:
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "text",
                "text": {"body": message},
            }
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=20)
            if res.status_code >= 400:
                logger.error(f"WhatsApp error: {res.status_code} {res.text}")
                return False
            return True
        except Exception as e:
            logger.error(f"WhatsApp send failed: {e}")
            return False

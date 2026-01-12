"""
Google Calendar Service for appointment synchronization
Integrates appointments with Google Calendar API
"""

import os
import logging
from typing import Optional
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

# Scopes required for Google Calendar API
SCOPES = ['https://www.googleapis.com/auth/calendar']


class GoogleCalendarService:
    """Service for Google Calendar integration"""
    
    def __init__(self, credentials_file: Optional[str] = None):
        """Initialize Google Calendar service"""
        self.credentials = None
        self.service = None
        
        try:
            # Use provided credentials file or environment variable
            creds_file = credentials_file or os.getenv('GOOGLE_CALENDAR_CREDENTIALS_FILE')
            
            if creds_file and os.path.exists(creds_file):
                # Build credentials from service account
                self.credentials = service_account.Credentials.from_service_account_file(
                    creds_file, scopes=SCOPES
                )
                self.service = build('calendar', 'v3', credentials=self.credentials)
                logger.info("Google Calendar service initialized successfully")
            else:
                logger.warning("Google Calendar credentials file not found")
        
        except Exception as e:
            logger.error(f"Error initializing Google Calendar service: {str(e)}")
    
    def create_event(
        self,
        calendar_id: str,
        title: str,
        description: str,
        start_time: datetime,
        end_time: datetime,
        attendee_email: Optional[str] = None
    ) -> Optional[str]:
        """Create an event in Google Calendar"""
        
        if not self.service:
            logger.warning("Google Calendar service not initialized")
            return None
        
        try:
            event_body = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'America/Santiago'  # Chile timezone
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'America/Santiago'
                }
            }
            
            # Add attendee if provided
            if attendee_email:
                event_body['attendees'] = [
                    {'email': attendee_email, 'responseStatus': 'tentativeAccepted'}
                ]
            
            event = self.service.events().insert(
                calendarId=calendar_id,
                body=event_body,
                sendNotifications=True
            ).execute()
            
            logger.info(f"Event created in Google Calendar: {event['id']}")
            return event['id']
        
        except Exception as e:
            logger.error(f"Error creating Google Calendar event: {str(e)}")
            return None
    
    def update_event(
        self,
        calendar_id: str,
        event_id: str,
        **kwargs
    ) -> bool:
        """Update an event in Google Calendar"""
        
        if not self.service:
            logger.warning("Google Calendar service not initialized")
            return False
        
        try:
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Update fields
            for key, value in kwargs.items():
                if hasattr(event, key):
                    event[key] = value
            
            self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=event
            ).execute()
            
            logger.info(f"Event updated in Google Calendar: {event_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating Google Calendar event: {str(e)}")
            return False
    
    def delete_event(
        self,
        calendar_id: str,
        event_id: str
    ) -> bool:
        """Delete an event from Google Calendar"""
        
        if not self.service:
            logger.warning("Google Calendar service not initialized")
            return False
        
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            logger.info(f"Event deleted from Google Calendar: {event_id}")
            return True
        
        except Exception as e:
            logger.error(f"Error deleting Google Calendar event: {str(e)}")
            return False


# Global instance
_calendar_service = None


def get_calendar_service() -> Optional[GoogleCalendarService]:
    """Get or create global calendar service instance"""
    global _calendar_service
    if not _calendar_service:
        _calendar_service = GoogleCalendarService()
    return _calendar_service


async def sync_to_google_calendar(appointment) -> Optional[str]:
    """
    Sync appointment to Google Calendar
    
    Returns the Google Calendar event ID if successful, None otherwise
    """
    try:
        service = get_calendar_service()
        if not service:
            return None
        
        # Get calendar ID from environment or use primary
        calendar_id = os.getenv('GOOGLE_CALENDAR_ID', 'primary')
        
        # Create end time (1 hour after start)
        from datetime import timedelta
        end_time = appointment.fecha + timedelta(hours=1)
        
        # Create calendar event
        event_id = service.create_event(
            calendar_id=calendar_id,
            title=f"Cita: {appointment.nombre}",
            description=f"Cita de agendamiento en Cirujano de Sintetizadores\n\n{appointment.mensaje or ''}",
            start_time=appointment.fecha,
            end_time=end_time,
            attendee_email=appointment.email
        )
        
        return event_id
    
    except Exception as e:
        logger.error(f"Error syncing appointment to Google Calendar: {str(e)}")
        return None

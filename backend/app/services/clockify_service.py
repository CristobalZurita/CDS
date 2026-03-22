"""
Clockify Service for OT integration (aditivo, no destructivo)
"""
import os
import requests
from typing import Optional
from app.core.config import settings

CLOCKIFY_API_KEY = os.getenv("CLOCKIFY_API_KEY")
CLOCKIFY_API_URL = "https://api.clockify.me/api/v1"

class ClockifyService:
    def __init__(self):
        self.api_key = CLOCKIFY_API_KEY or getattr(settings, "clockify_api_key", None)
        self.base_url = CLOCKIFY_API_URL
        self.headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def get_workspace_id(self) -> Optional[str]:
        resp = requests.get(f"{self.base_url}/workspaces", headers=self.headers)
        if resp.ok:
            data = resp.json()
            if data:
                return data[0]["id"]
        return None

    def create_project(self, name: str, client_id: Optional[str] = None) -> Optional[str]:
        workspace_id = self.get_workspace_id()
        if not workspace_id:
            return None
        payload = {"name": name}
        if client_id:
            payload["clientId"] = client_id
        resp = requests.post(f"{self.base_url}/workspaces/{workspace_id}/projects", json=payload, headers=self.headers)
        if resp.ok:
            return resp.json().get("id")
        return None

    def create_time_entry(self, project_id: str, description: str, start: str, end: Optional[str] = None) -> Optional[str]:
        workspace_id = self.get_workspace_id()
        if not workspace_id:
            return None
        payload = {
            "start": start,
            "description": description,
            "projectId": project_id
        }
        if end:
            payload["end"] = end
        resp = requests.post(f"{self.base_url}/workspaces/{workspace_id}/time-entries", json=payload, headers=self.headers)
        if resp.ok:
            return resp.json().get("id")
        return None

    def get_project_time_entries(self, project_id: str):
        workspace_id = self.get_workspace_id()
        if not workspace_id:
            return []
        resp = requests.get(f"{self.base_url}/workspaces/{workspace_id}/projects/{project_id}/time-entries", headers=self.headers)
        if resp.ok:
            return resp.json()
        return []

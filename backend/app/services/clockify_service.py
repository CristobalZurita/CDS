"""
Clockify Service for OT integration (aditivo, no destructivo)
"""
import os
import requests
from datetime import datetime
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

    def start_time_entry(self, project_id: str, description: str = "Trabajo en OT") -> Optional[str]:
        """Iniciar time entry para proyecto Clockify"""
        return self.create_time_entry(project_id, description, datetime.utcnow().isoformat())

    def stop_current_time_entry(self, project_id: str) -> bool:
        """Detener time entry activo en proyecto"""
        workspace_id = self.get_workspace_id()
        if not workspace_id:
            return False

        # Buscar time entry activo (sin end)
        resp = requests.get(
            f"{self.base_url}/workspaces/{workspace_id}/user/time-entries",
            headers=self.headers,
            params={"project": project_id}
        )
        if resp.ok:
            entries = resp.json()
            active_entry = next((e for e in entries if not e.get("timeInterval", {}).get("end")), None)
            if active_entry:
                entry_id = active_entry["id"]
                update_resp = requests.put(
                    f"{self.base_url}/workspaces/{workspace_id}/time-entries/{entry_id}",
                    json={"end": datetime.utcnow().isoformat()},
                    headers=self.headers
                )
                return update_resp.ok
        return False

    def get_project_time_entries(self, project_id: str) -> list:
        """Obtener todas las entradas de tiempo de un proyecto Clockify"""
        workspace_id = self.get_workspace_id()
        if not workspace_id:
            return []
        resp = requests.get(
            f"{self.base_url}/workspaces/{workspace_id}/user/time-entries",
            headers=self.headers,
            params={"project": project_id, "page-size": 500},
        )
        if resp.ok:
            return resp.json()
        return []

    def get_project_total_seconds(self, project_id: str) -> int:
        """Suma total de segundos trabajados en un proyecto Clockify"""
        entries = self.get_project_time_entries(project_id)
        total = 0
        for entry in entries:
            duration = entry.get("timeInterval", {}).get("duration")
            if not duration:
                continue
            # ISO 8601 duration: PT1H30M, PT45M, etc.
            try:
                import re
                h = int((re.search(r"(\d+)H", duration) or type("", (), {"group": lambda s, n: 0})()).group(1) or 0)
                m = int((re.search(r"(\d+)M", duration) or type("", (), {"group": lambda s, n: 0})()).group(1) or 0)
                s = int((re.search(r"(\d+)S", duration) or type("", (), {"group": lambda s, n: 0})()).group(1) or 0)
                total += h * 3600 + m * 60 + s
            except Exception:
                pass
        return total

    def get_active_time_entry(self, project_id: str) -> Optional[dict]:
        """Obtener time entry activo en proyecto"""
        workspace_id = self.get_workspace_id()
        if not workspace_id:
            return None

        resp = requests.get(
            f"{self.base_url}/workspaces/{workspace_id}/user/time-entries",
            headers=self.headers,
            params={"project": project_id}
        )
        if resp.ok:
            entries = resp.json()
            return next((e for e in entries if not e.get("timeInterval", {}).get("end")), None)
        return None

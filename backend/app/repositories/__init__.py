"""Capa de repositorios (aditiva)."""

from .base_repository import BaseRepository
from .repair_repository import RepairRepository

__all__ = [
    "BaseRepository",
    "RepairRepository",
]

"""
Import all SQLAlchemy models
"""

from app.models.user import User, UserRole
from app.models.repair import Repair, RepairStatus
from app.models.diagnostic import Diagnostic
from app.models.category import Category
from app.models.inventory import Product
from app.models.brand import Brand
from app.models.instrument import Instrument
from app.models.stock import Stock
from app.models.stock_movement import StockMovement
from app.models.payment import Payment, PaymentStatus
from app.models.appointment import Appointment
from app.models.audit import AuditLog
from app.models.storage_location import StorageLocation
from app.models.client import Client
from app.models.device import Device
from app.models.quote import Quote
from app.models.tool import Tool
from app.models.tool_lookup import ToolBrand, ToolCategory
from app.models.device_lookup import DeviceBrand, DeviceType
from app.models.repair_component_usage import RepairComponentUsage
from app.models.repair_photo import RepairPhoto
from app.models.repair_note import RepairNote
from app.models.contact_message import ContactMessage
from app.models.newsletter_subscription import NewsletterSubscription

__all__ = [
    "User", "UserRole",
    "Repair", "RepairStatus",
    "Diagnostic",
    "Category",
    "Product",
    "Brand",
    "Instrument",
    "Stock",
    "StockMovement",
    "Payment", "PaymentStatus",
    "Appointment",
    "AuditLog",
    "StorageLocation",
    "Client",
    "Device",
    "Quote",
    "Tool",
    "ToolBrand",
    "ToolCategory",
    "DeviceBrand",
    "DeviceType",
    "RepairComponentUsage",
    "RepairPhoto",
    "RepairNote",
    "ContactMessage",
    "NewsletterSubscription",
]

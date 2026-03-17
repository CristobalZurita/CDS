from fastapi import APIRouter
from .endpoints import brands, auth, inventory, imports, stats, ai, users
from app.routers import uploads as uploads_router
from app.routers import files as files_router
from app.api import sync as sync_router
import importlib

def _optional_router_module(module_name: str):
	try:
		return importlib.import_module(f"app.routers.{module_name}")
	except Exception:
		return None


# Routers adicionales: se cargan de forma independiente para que un fallo en
# uno no deje en None a todos los demás.
repair_router = _optional_router_module("repair")
instrument_router = _optional_router_module("instrument")
category_router = _optional_router_module("category")
stock_movement_router = _optional_router_module("stock_movement")
contact_router = _optional_router_module("contact")
diagnostic_router = _optional_router_module("diagnostic")
quotation_router = _optional_router_module("quotation")
payments_router = _optional_router_module("payments")
appointment_router = _optional_router_module("appointment")
client_router = _optional_router_module("client_portal")
clients_router = _optional_router_module("clients")
device_router = _optional_router_module("device")
repair_status_router = _optional_router_module("repair_status")
newsletter_router = _optional_router_module("newsletter")
tools_router = _optional_router_module("tools")
inventory_products_router = _optional_router_module("inventory")
invoice_router = _optional_router_module("invoice")
warranty_router = _optional_router_module("warranty")
analytics_router = _optional_router_module("analytics")
search_router = _optional_router_module("search")
signature_router = _optional_router_module("signature")
tickets_router = _optional_router_module("tickets")
purchase_requests_router = _optional_router_module("purchase_requests")
manuals_router = _optional_router_module("manuals")
photo_requests_router = _optional_router_module("photo_requests")

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(brands.router)
# DEDUPE FASE 2 (/instruments):
# - Fuente canónica activa: app.routers.instrument
# - app.api.v1.endpoints.instruments se mantiene en código (no destructivo),
#   pero ya no se importa ni se monta aquí para evitar doble capa sobre
#   /api/v1/instruments
api_router.include_router(auth.router)
api_router.include_router(uploads_router.router)
api_router.include_router(files_router.router)
api_router.include_router(inventory.router)
api_router.include_router(imports.router)
api_router.include_router(stats.router)
api_router.include_router(ai.router)
api_router.include_router(users.router)
api_router.include_router(sync_router.router)

# Incluir routers adicionales si están disponibles
# DEDUPE FASE 1 (/users):
# - Fuente canónica activa: app.api.v1.endpoints.users (incluida arriba como users.router)
# - Mantener app.routers.user en código, pero sin montarlo para evitar doble registro /api/v1/users
# if user_router:
# 	api_router.include_router(user_router.router)
# DEDUPE FASE 4 (/repairs, /categories):
# - Fuentes canónicas activas: app.routers.repair y app.routers.category
# - app.api.v1.endpoints.repairs y app.api.v1.endpoints.categories se mantienen
#   en código (aditivo), pero no se importan ni se montan aquí para evitar
#   doble capa sobre /api/v1/repairs y /api/v1/categories
if repair_router:
	api_router.include_router(repair_router.router)
if instrument_router:
	api_router.include_router(instrument_router.router)
if category_router:
	api_router.include_router(category_router.router)
if stock_movement_router:
	api_router.include_router(stock_movement_router.router)
if contact_router:
	api_router.include_router(contact_router.router)
if globals().get("quotation_router"):
	api_router.include_router(globals()["quotation_router"].router)
if globals().get("diagnostic_router"):
	api_router.include_router(globals()["diagnostic_router"].router)
if globals().get("payments_router"):
	api_router.include_router(globals()["payments_router"].router)
if globals().get("appointment_router"):
	api_router.include_router(globals()["appointment_router"].router)
if globals().get("client_router"):
	api_router.include_router(globals()["client_router"].router)
if globals().get("clients_router"):
	api_router.include_router(globals()["clients_router"].router)
if globals().get("device_router"):
	api_router.include_router(globals()["device_router"].router)
if globals().get("repair_status_router"):
	api_router.include_router(globals()["repair_status_router"].router)
if globals().get("newsletter_router"):
	api_router.include_router(globals()["newsletter_router"].router)
if globals().get("tools_router"):
	api_router.include_router(globals()["tools_router"].router)
if globals().get("inventory_products_router"):
	api_router.include_router(globals()["inventory_products_router"].router)
if globals().get("invoice_router"):
	api_router.include_router(globals()["invoice_router"].router)
if globals().get("warranty_router"):
	api_router.include_router(globals()["warranty_router"].router)
if globals().get("analytics_router"):
	api_router.include_router(globals()["analytics_router"].router)
if globals().get("search_router"):
	api_router.include_router(globals()["search_router"].router)
if globals().get("signature_router"):
	api_router.include_router(globals()["signature_router"].router)
if globals().get("tickets_router"):
	api_router.include_router(globals()["tickets_router"].router)
if globals().get("purchase_requests_router"):
	api_router.include_router(globals()["purchase_requests_router"].router)
if globals().get("manuals_router"):
	api_router.include_router(globals()["manuals_router"].router)
if globals().get("photo_requests_router"):
	api_router.include_router(globals()["photo_requests_router"].router)

# ADITIVO: Router para resolver imágenes de Cloudinary
try:
	from app.routers import images as images_router
	api_router.include_router(images_router.router)
except Exception:
	# Si el módulo no está disponible, se ignora
	pass

# ADITIVO: Router para gestión dinámica de medios (assets + bindings en BD)
try:
	from app.routers import media as media_router
	api_router.include_router(media_router.router)
except Exception:
	pass

# ADITIVO: Router para leads del cotizador público (NOT-clientes)
try:
	from app.routers import leads as leads_router
	api_router.include_router(leads_router.router)
except Exception:
	pass

# ADITIVO: WhatsApp Webhook (verificación Meta + mensajes entrantes)
try:
	from app.routers import whatsapp_webhook as whatsapp_webhook_router
	api_router.include_router(whatsapp_webhook_router.router)
except Exception:
	pass

# ADITIVO: Pasarela de pagos (Transbank Webpay Plus / MercadoPago)
try:
	from app.routers import payment_gateway as payment_gateway_router
	api_router.include_router(payment_gateway_router.router)
except Exception:
	pass

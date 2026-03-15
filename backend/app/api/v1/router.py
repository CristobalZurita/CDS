from fastapi import APIRouter
from .endpoints import brands, auth, inventory, imports, stats, ai, users
from app.routers import uploads as uploads_router
from app.routers import files as files_router
from app.api import sync as sync_router

# Routers adicionales (creados por copilot) - si existen, se incluyen
try:
	from app.routers import user as user_router
	from app.routers import repair as repair_router
	from app.routers import instrument as instrument_router
	from app.routers import category as category_router
	from app.routers import stock_movement as stock_movement_router
	from app.routers import contact as contact_router
	from app.routers import diagnostic as diagnostic_router
	from app.routers import quotation as quotation_router
	from app.routers import payments as payments_router
	from app.routers import appointment as appointment_router
	from app.routers import client_portal as client_router
	from app.routers import clients as clients_router
	from app.routers import device as device_router
	from app.routers import repair_status as repair_status_router
	from app.routers import newsletter as newsletter_router
	from app.routers import tools as tools_router
	from app.routers import inventory as inventory_products_router
	from app.routers import invoice as invoice_router
	from app.routers import warranty as warranty_router
	from app.routers import analytics as analytics_router
	from app.routers import search as search_router
	from app.routers import signature as signature_router
	from app.routers import tickets as tickets_router
	from app.routers import purchase_requests as purchase_requests_router
	from app.routers import manuals as manuals_router
	from app.routers import photo_requests as photo_requests_router
except Exception:
	# Si los módulos no existen en este entorno, se ignoran
	user_router = repair_router = instrument_router = category_router = stock_movement_router = contact_router = None
	appointment_router = None
	client_router = None
	clients_router = None
	device_router = None
	repair_status_router = None
	newsletter_router = None
	tools_router = None
	inventory_products_router = None
	invoice_router = None
	warranty_router = None
	analytics_router = None
	search_router = None
	signature_router = None
	tickets_router = None
	purchase_requests_router = None
	manuals_router = None
	photo_requests_router = None

# If any router failed to import previously (e.g., due to transient import errors),
# attempt a second import pass so that fixes applied at runtime are picked up.
import importlib
for name in (
	"repair", "user", "instrument", "category", "stock_movement", "contact",
	"quotation", "appointment", "clients", "device",
	"newsletter", "tools", "signature", "tickets", "purchase_requests",
	"manuals", "photo_requests", "inventory", "repair_status",
	"invoice", "warranty", "analytics", "search",
):
	var_name = f"{name}_router"
	if globals().get(var_name) is None:
		try:
			mod = importlib.import_module(f"app.routers.{name}")
			globals()[var_name] = mod
		except Exception:
			globals()[var_name] = None

# Ensure payments router is also available on a second import pass
if globals().get("payments_router") is None:
	try:
		mod = importlib.import_module("app.routers.payments")
		globals()["payments_router"] = mod
	except Exception:
		globals()["payments_router"] = None

# Ensure diagnostic router is picked up on the second import pass as well
if globals().get("diagnostic_router") is None:
	try:
		mod = importlib.import_module("app.routers.diagnostic")
		globals()["diagnostic_router"] = mod
	except Exception:
		globals()["diagnostic_router"] = None

# client_portal uses a custom variable name (client_router), recover it explicitly.
if globals().get("client_router") is None:
	try:
		mod = importlib.import_module("app.routers.client_portal")
		globals()["client_router"] = mod
	except Exception:
		globals()["client_router"] = None

# inventory uses a custom variable name, so recover it explicitly if the broad
# import block failed earlier.
if globals().get("inventory_products_router") is None:
	try:
		mod = importlib.import_module("app.routers.inventory")
		globals()["inventory_products_router"] = mod
	except Exception:
		globals()["inventory_products_router"] = None

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
if globals().get("diagnostic_router"):
	api_router.include_router(globals()["diagnostic_router"].router)
# DESACTIVADO: quotation_router lee src/assets/data/*.json (estructura L, movida a RESTO).
# El endpoint canónico de cotización es /api/v1/diagnostic/calculate (diagnostic_router).
# La lógica guiada de quotation.py se migrará a quote_calculator_service.py cuando sea necesario.
# if globals().get("quotation_router"):
# 	api_router.include_router(globals()["quotation_router"].router)
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

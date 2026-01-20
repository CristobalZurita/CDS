from fastapi import APIRouter
from .endpoints import brands, instruments, auth, inventory, imports, stats, ai
from app.routers import uploads as uploads_router

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
	from app.routers import client as client_router
	from app.routers import clients as clients_router
	from app.routers import device as device_router
	from app.routers import repair_status as repair_status_router
	from app.routers import newsletter as newsletter_router
	from app.routers import tools as tools_router
	from app.routers import inventory as inventory_products_router
	from app.routers import invoice as invoice_router
	from app.routers import warranty as warranty_router
	from app.routers import analytics as analytics_router
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

# If any router failed to import previously (e.g., due to transient import errors),
# attempt a second import pass so that fixes applied at runtime are picked up.
import importlib
for name in ("repair", "user", "instrument", "category", "stock_movement", "contact", "quotation", "appointment", "client", "newsletter", "tools"):
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

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(brands.router)
api_router.include_router(instruments.router)
api_router.include_router(auth.router)
api_router.include_router(uploads_router.router)
api_router.include_router(inventory.router)
api_router.include_router(imports.router)
api_router.include_router(stats.router)
api_router.include_router(ai.router)

# Incluir routers adicionales si están disponibles
if user_router:
	api_router.include_router(user_router.router)
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
if globals().get("quotation_router"):
	api_router.include_router(globals()["quotation_router"].router)
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

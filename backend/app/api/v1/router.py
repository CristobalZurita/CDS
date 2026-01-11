from fastapi import APIRouter
from .endpoints import brands, instruments, auth, inventory, imports
from backend.app.routers import uploads as uploads_router

# Routers adicionales (creados por copilot) - si existen, se incluyen
try:
	from backend.app.routers import user as user_router
	from backend.app.routers import repair as repair_router
	from backend.app.routers import instrument as instrument_router
	from backend.app.routers import category as category_router
	from backend.app.routers import stock_movement as stock_movement_router
	from backend.app.routers import contact as contact_router
	from backend.app.routers import diagnostic as diagnostic_router
	from backend.app.routers import quotation as quotation_router
	from backend.app.routers import payments as payments_router
	from backend.app.routers import appointment as appointment_router
except Exception:
	# Si los módulos no existen en este entorno, se ignoran
	user_router = repair_router = instrument_router = category_router = stock_movement_router = contact_router = None
	appointment_router = None

# If any router failed to import previously (e.g., due to transient import errors),
# attempt a second import pass so that fixes applied at runtime are picked up.
import importlib
for name in ("repair", "user", "instrument", "category", "stock_movement", "contact", "quotation", "appointment"):
	var_name = f"{name}_router"
	if globals().get(var_name) is None:
		try:
			mod = importlib.import_module(f"backend.app.routers.{name}")
			globals()[var_name] = mod
		except Exception:
			globals()[var_name] = None

# Ensure payments router is also available on a second import pass
if globals().get("payments_router") is None:
	try:
		mod = importlib.import_module("backend.app.routers.payments")
		globals()["payments_router"] = mod
	except Exception:
		globals()["payments_router"] = None

# Ensure diagnostic router is picked up on the second import pass as well
if globals().get("diagnostic_router") is None:
	try:
		mod = importlib.import_module("backend.app.routers.diagnostic")
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

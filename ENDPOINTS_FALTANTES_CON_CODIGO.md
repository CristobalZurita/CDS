# ENDPOINTS FALTANTES - LISTA EXACTA CON UBICACIÓN DE ARCHIVO

## Categoría: CRÍTICA PARA PRODUCCIÓN (Implementar primero)

### 1. RECUPERACIÓN DE CONTRASEÑA
**Archivo**: `backend/app/api/v1/endpoints/auth.py`  
**Estado**: FALTA COMPLETAMENTE

```python
@router.post("/forgot-password")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    """Enviar enlace de reset de contraseña"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Enviar email con token
    # Retornar {"message": "Email enviado"}
```

### 2. RESET DE CONTRASEÑA
**Archivo**: `backend/app/api/v1/endpoints/auth.py`  
**Estado**: FALTA COMPLETAMENTE

```python
@router.post("/reset-password")
async def reset_password(token: str, new_password: str, db: Session = Depends(get_db)):
    """Cambiar contraseña con token de reset"""
    # Validar token
    # Actualizar contraseña
    # Retornar {"message": "Contraseña actualizada"}
```

### 3. CONFIRMAR EMAIL
**Archivo**: `backend/app/api/v1/endpoints/auth.py`  
**Estado**: FALTA COMPLETAMENTE

```python
@router.post("/confirm-email")
async def confirm_email(token: str, db: Session = Depends(get_db)):
    """Confirmar email con token"""
    # Validar token
    # Marcar email como confirmado
    # Retornar {"message": "Email confirmado"}
```

---

## Categoría: PANEL DE CLIENTE (MVP)

### 4. DASHBOARD DE CLIENTE
**Archivo**: Crear `backend/app/routers/client_dashboard.py`  
**Estado**: FALTA COMPLETAMENTE

```python
@router.get("/dashboard")
async def get_client_dashboard(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retornar dashboard con:
    - Reparaciones activas
    - Próximas citas
    - Estado general cuenta
    """
    return {
        "repairs_active": [...],
        "appointments_upcoming": [...],
        "account_status": "active"
    }
```

### 5. MIS REPARACIONES
**Archivo**: Crear `backend/app/routers/client_dashboard.py`  
**Estado**: FALTA COMPLETAMENTE

```python
@router.get("/my-repairs")
async def get_my_repairs(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retornar solo reparaciones del usuario autenticado
    - Filtrado por client_id
    - Con estado, fecha, costo
    """
    repairs = db.query(Repair).filter(Repair.client_id == current_user["user_id"]).all()
    return repairs
```

### 6. TIMELINE DE REPARACIÓN
**Archivo**: Crear `backend/app/routers/client_dashboard.py`  
**Estado**: FALTA COMPLETAMENTE

```python
@router.get("/repairs/{repair_id}/timeline")
async def get_repair_timeline(
    repair_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retornar cronología de cambios de estado
    - Quién cambió (nombre técnico)
    - Cuándo (fecha/hora)
    - De qué a qué estado
    """
    return {
        "timeline": [
            {"date": "2026-01-18", "from_status": "ingresado", "to_status": "en_diagnostico", "by": "Técnico1"},
            {"date": "2026-01-19", "from_status": "en_diagnostico", "to_status": "en_reparacion", "by": "Técnico2"}
        ]
    }
```

---

## Categoría: INVENTARIO DE COMPONENTES

### 7. LISTAR COMPONENTES DEL CATÁLOGO
**Archivo**: Crear `backend/app/routers/inventory_components.py`  
**Estado**: FALTA COMPLETAMENTE

```python
@router.get("/components")
async def list_components(db: Session = Depends(get_db)):
    """
    Retornar lista de componentes disponibles
    - ID, nombre, stock actual, precio unitario
    """
    components = db.query(Component).all()
    return components
```

### 8. CREAR COMPONENTE
**Archivo**: `backend/app/routers/inventory_components.py`  
**Estado**: FALTA COMPLETAMENTE

```python
@router.post("/components", response_model=ComponentRead)
async def create_component(
    component: ComponentCreate,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Crear nuevo componente en catálogo
    - nombre, categoría, stock inicial, precio unitario
    """
    new_component = Component(**component.dict())
    db.add(new_component)
    db.commit()
    return new_component
```

### 9. ACTUALIZAR STOCK DE COMPONENTE
**Archivo**: `backend/app/routers/inventory_components.py`  
**Estado**: FALTA COMPLETAMENTE

```python
@router.put("/components/{component_id}/stock")
async def update_component_stock(
    component_id: int,
    quantity_change: int,
    reason: str,
    db: Session = Depends(get_db),
    admin: dict = Depends(get_current_admin)
):
    """
    Actualizar stock de componente
    - Registrar movimiento (entrada/salida)
    - Registrar razón
    """
    component = db.query(Component).get(component_id)
    component.stock += quantity_change
    # Crear movimiento en StockMovement
    db.commit()
    return {"new_stock": component.stock}
```

### 10. OBTENER MOVIMIENTOS DE STOCK
**Archivo**: `backend/app/routers/inventory_components.py`  
**Estado**: FALTA COMPLETAMENTE

```python
@router.get("/components/{component_id}/movements")
async def get_component_movements(
    component_id: int,
    db: Session = Depends(get_db)
):
    """
    Retornar historial de movimientos de stock
    - Quién cambió, cuándo, cuánto, por qué
    """
    movements = db.query(StockMovement).filter(StockMovement.component_id == component_id).all()
    return movements
```

---

## Categoría: E-COMMERCE (Completo)

### 11. CREAR CARRITO
**Archivo**: Crear `backend/app/routers/cart.py`  
**Estado**: FALTA COMPLETAMENTE

```python
@router.post("/cart")
async def create_cart(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear nuevo carrito para usuario"""
    cart = Cart(user_id=current_user["user_id"])
    db.add(cart)
    db.commit()
    return {"cart_id": cart.id}
```

### 12. AGREGAR ITEM AL CARRITO
**Archivo**: `backend/app/routers/cart.py`  
**Estado**: FALTA COMPLETAMENTE

```python
@router.post("/cart/{cart_id}/items")
async def add_to_cart(
    cart_id: int,
    item: CartItemCreate,
    db: Session = Depends(get_db)
):
    """Agregar producto al carrito"""
    cart_item = CartItem(cart_id=cart_id, **item.dict())
    db.add(cart_item)
    db.commit()
    return cart_item
```

### 13. CREAR ORDEN
**Archivo**: Crear `backend/app/routers/orders.py`  
**Estado**: FALTA COMPLETAMENTE

```python
@router.post("/orders")
async def create_order(
    order: OrderCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Crear orden desde carrito"""
    # Validar carrito existe
    # Crear order
    # Limpiar carrito
    return {"order_id": order.id}
```

### 14. PROCESAR PAGO
**Archivo**: `backend/app/routers/orders.py`  
**Estado**: FALTA COMPLETAMENTE (Estructura existe pero vacía)

```python
@router.post("/orders/{order_id}/checkout")
async def checkout_order(
    order_id: int,
    payment_method: str,  # "stripe", "paypal", etc.
    db: Session = Depends(get_db)
):
    """
    Procesar pago real con:
    - Stripe / PayPal
    - Validar monto
    - Generar factura
    """
    # Integración con payment gateway
    return {"payment_id": "..."}
```

---

## Categoría: AUDITORÍA Y LOGS

### 15. REGISTRAR CAMBIO DE ESTADO EN REPARACIÓN
**Archivo**: Modificar `backend/app/routers/repair.py`  
**Estado**: PARCIALMENTE IMPLEMENTADO (necesita completarse)

```python
# En PUT /api/v1/repairs/{repair_id}, agregar:

@router.put("/{repair_id}")
async def update_repair(
    repair_id: int,
    repair_update: RepairUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Al cambiar estado, registrar:
    - Quién cambió (user_id)
    - Cuándo (timestamp)
    - De qué a qué estado
    """
    db_repair = db.query(Repair).get(repair_id)
    old_status = db_repair.status
    new_status = repair_update.status
    
    # Crear record en RepairStatusChange
    if old_status != new_status:
        status_change = RepairStatusChange(
            repair_id=repair_id,
            from_status=old_status,
            to_status=new_status,
            changed_by=current_user["user_id"],
            changed_at=datetime.now()
        )
        db.add(status_change)
    
    db.commit()
    return db_repair
```

### 16. OBTENER AUDITORÍA DE CAMBIOS
**Archivo**: `backend/app/routers/repair.py`  
**Estado**: FALTA COMPLETAMENTE

```python
@router.get("/{repair_id}/audit")
async def get_repair_audit(
    repair_id: int,
    db: Session = Depends(get_db)
):
    """
    Retornar historial de todos los cambios
    - Cambios de estado
    - Cambios de datos
    - Notas agregadas
    - Fotos agregadas
    """
    audit_log = db.query(RepairStatusChange).filter(
        RepairStatusChange.repair_id == repair_id
    ).all()
    return audit_log
```

---

## Categoría: VALIDACIÓN DE CARACTERES (Seguridad)

### 17. VALIDACIÓN CENTRALIZADA
**Archivo**: Crear `backend/app/utils/validators.py`  
**Estado**: FALTA COMPLETAMENTE

```python
# Crear módulo centralizado de validación

ALLOWED_CHARS_NAME = r"^[a-zA-ZáéíóúñÁÉÍÓÚÑ\s]+$"
PROHIBITED_CHARS = ["'", '"', "\\", ";", "--", "/*", "*/"]

def validate_appointment_name(name: str) -> bool:
    """Validar que nombre solo tiene letras, acentos, Ñ"""
    if not re.match(ALLOWED_CHARS_NAME, name):
        raise ValueError("Nombre contiene caracteres no permitidos")
    return True

def sanitize_text_field(text: str) -> str:
    """Remover caracteres potencialmente peligrosos"""
    for char in PROHIBITED_CHARS:
        text = text.replace(char, "")
    return text
```

---

## Categoría: PLATAFORMA EDUCATIVA (AUSENTE)

### 18. CALCULADORA DE RESISTENCIAS
**Archivo**: Crear `backend/app/routers/education.py`  
**Estado**: NO EXISTE

```python
@router.post("/calculators/resistor")
async def calculate_resistor(
    bands: List[str],  # colores de las bandas
    tolerance: str = "5%"
):
    """
    Calcular valor de resistencia desde bandas de color
    Input: ["marrón", "negro", "rojo"]
    Output: {"value": 1000, "unit": "ohms", "tolerance": "±5%"}
    """
    # Lógica de cálculo
    return {"value": 1000, "unit": "ohms"}
```

### 19. CALCULADORA DE CAPACITORES
**Archivo**: `backend/app/routers/education.py`  
**Estado**: NO EXISTE

```python
@router.post("/calculators/capacitor")
async def calculate_capacitor(
    code: str,  # código impreso
    voltage: int
):
    """
    Calcular capacitancia desde código
    Input: "104", "50V"
    Output: {"capacitance": "0.1µF", "voltage": "50V"}
    """
    return {"capacitance": "0.1µF", "voltage": "50V"}
```

### 20. CALCULADORA NE555
**Archivo**: `backend/app/routers/education.py`  
**Estado**: NO EXISTE

```python
@router.post("/calculators/ne555")
async def calculate_ne555_timer(
    frequency: float,
    duty_cycle: float
):
    """
    Calcular valores de resistencias y capacitores para NE555
    Input: freq=1000Hz, duty=50%
    Output: {R1, R2, C valores específicos}
    """
    return {"R1": "10kΩ", "R2": "10kΩ", "C": "0.1µF"}
```

---

## Resumen de Implementación Necesaria

| Endpoint | Prioridad | Días | Archivo |
|----------|-----------|------|---------|
| Recuperación password | 🔴 Crítica | 2 | auth.py |
| Reset password | 🔴 Crítica | 1 | auth.py |
| Confirmar email | 🔴 Crítica | 1 | auth.py |
| Dashboard cliente | 🔴 Crítica | 3 | client_dashboard.py |
| Mis reparaciones | 🔴 Crítica | 1 | client_dashboard.py |
| Timeline reparación | 🟠 Alta | 2 | client_dashboard.py |
| Listar componentes | 🟠 Alta | 1 | inventory_components.py |
| Crear componente | 🟠 Alta | 1 | inventory_components.py |
| Carrito | 🟠 Alta | 3 | cart.py |
| Órdenes | 🟠 Alta | 3 | orders.py |
| Pago real | 🟠 Alta | 5 | orders.py |
| Auditoría cambios | 🟠 Alta | 2 | repair.py |
| Validación caracteres | 🟠 Alta | 2 | validators.py |
| Educación - Resistor | 🟡 Media | 1 | education.py |
| Educación - Capacitor | 🟡 Media | 1 | education.py |
| Educación - NE555 | 🟡 Media | 1 | education.py |

**Total estimado**: 35-40 días de desarrollo

**Antes de producción (semana 1)**: 
- Recuperación password (2d)
- Dashboard cliente (3d)
- Auditoría cambios (2d)
- Validación caracteres (2d)

**Total semana 1**: ~9 días = 2 sprints de 1 semana

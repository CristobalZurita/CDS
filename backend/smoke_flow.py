"""
smoke_flow.py — Flujo completo CDS: cliente → dispositivo → OT → pago → estado
Corre contra la API real en localhost:8000 y reporta qué pasa en cada paso.
No es pass/fail — es un reporte vivo de los datos que genera el sistema.

Uso:
    CDS_SMOKE_ADMIN_PASS=TUPASS python smoke_flow.py
    python smoke_flow.py --admin-email admin@cirujanodesintetizadores.cl --admin-pass TUPASS
"""
import argparse
import json
import os
import sys
import time
import uuid
from datetime import datetime

import requests

BASE = "http://127.0.0.1:8000/api/v1"
SEP  = "─" * 60

# ── helpers ────────────────────────────────────────────────────────────────

def section(title: str):
    print(f"\n{SEP}\n  {title}\n{SEP}")

def show(label: str, data):
    if isinstance(data, dict):
        print(f"\n  [{label}]")
        for k, v in data.items():
            print(f"    {k}: {v}")
    else:
        print(f"  {label}: {data}")

def post(session, path, payload, label=""):
    r = session.post(f"{BASE}{path}", json=payload)
    print(f"\n  POST {path}  →  HTTP {r.status_code}")
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text[:300]}
    if label:
        show(label, data)
    return r.status_code, data

def get(session, path, label=""):
    r = session.get(f"{BASE}{path}")
    print(f"\n  GET  {path}  →  HTTP {r.status_code}")
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text[:300]}
    if label:
        show(label, data if not isinstance(data, list) else {"count": len(data), "first": data[0] if data else None})
    return r.status_code, data

def put(session, path, payload, label=""):
    r = session.put(f"{BASE}{path}", json=payload)
    print(f"\n  PUT  {path}  →  HTTP {r.status_code}")
    try:
        data = r.json()
    except Exception:
        data = {"raw": r.text[:300]}
    if label:
        show(label, data)
    return r.status_code, data

# ── main ───────────────────────────────────────────────────────────────────

def run(admin_email: str, admin_pass: str):
    slug   = uuid.uuid4().hex[:6]
    stamp  = datetime.now().strftime("%H%M%S")
    s      = requests.Session()

    print(f"\n{'═'*60}")
    print(f"  CDS — Smoke Flow completo  [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")
    print(f"  slug único de sesión: {slug}")
    print(f"{'═'*60}")

    # ── 1. LOGIN ADMIN ──────────────────────────────────────────────────────
    section("1 · Login admin")
    status, auth = post(s, "/auth/login", {"email": admin_email, "password": admin_pass}, "respuesta")
    if status != 200 or "access_token" not in auth:
        print(f"\n  ✗ No se pudo autenticar. Verifica credenciales.")
        print(f"    → {auth}")
        sys.exit(1)

    token = auth["access_token"]
    s.headers["Authorization"] = f"Bearer {token}"
    show("token (primeros 40 chars)", token[:40] + "...")

    # ── 2. PERFIL ADMIN ─────────────────────────────────────────────────────
    section("2 · Perfil del admin autenticado")
    _, me = get(s, "/auth/me", "perfil")

    # ── 3. CREAR CLIENTE ────────────────────────────────────────────────────
    section("3 · Crear cliente nuevo")
    client_payload = {
        "name":         f"Carlos Smoke {slug}",
        "email":        f"smoke.{slug}@test.cl",
        "phone":        f"+5699{slug[:6]}",
        "phone_alt":    "+56912345678",
        "address":      f"Av. Sintetizador 404, Santiago",
        "city":         "Santiago",
        "region":       "Región Metropolitana",
        "country":      "Chile",
        "notes":        f"Cliente creado por smoke_flow.py — slug {slug}",
    }
    show("payload enviado", client_payload)
    status, client = post(s, "/clients/", client_payload, "cliente creado")

    if status not in (200, 201):
        print(f"  ✗ Error creando cliente: {client}")
        sys.exit(1)

    client_id   = client.get("id")
    client_code = client.get("client_code") or client.get("code") or "—"
    print(f"\n  ✔ Cliente ID: {client_id}  |  Código: {client_code}")

    # ── 4. LEER CLIENTE RECIÉN CREADO ───────────────────────────────────────
    section("4 · Leer cliente desde la API")
    _, client_detail = get(s, f"/clients/{client_id}", "detalle completo")

    # ── 5. CREAR DISPOSITIVO ────────────────────────────────────────────────
    section("5 · Registrar dispositivo del cliente")
    device_payload = {
        "client_id":      client_id,
        "model":          "Prophet-5 Rev 4",
        "brand_other":    "Sequential",
        "serial_number":  f"SEQ{slug.upper()}",
        "description":    "Sintetizador analógico polifónico 5 voces",
        "condition_notes":"Llega sin encender, golpe visible en panel izquierdo",
    }
    show("payload enviado", device_payload)
    status, device = post(s, "/devices/", device_payload, "dispositivo creado")

    if status not in (200, 201):
        print(f"  ✗ Error creando dispositivo: {device}")
    else:
        device_id = device.get("id")
        print(f"\n  ✔ Dispositivo ID: {device_id}  |  Modelo: {device.get('model')}")

    # ── 6. CREAR OT (ORDEN DE TRABAJO) ──────────────────────────────────────
    section("6 · Crear Orden de Trabajo (OT)")
    device_id = device.get("id") if status in (200, 201) else None
    ot_payload = {
        "client_id":        client_id,
        "device_id":        device_id,
        "problem_reported": "No enciende. Al conectar el adaptador no hay LED de power. "
                            "Posible falla en fuente de poder o fusible.",
        "priority":         2,
        "paid_amount":      15000,
        "payment_method":   "transfer",
        "title":            f"Prophet-5 sin encender — {stamp}",
    }
    show("payload enviado", ot_payload)
    status, ot = post(s, "/repairs/", ot_payload, "OT creada")

    if status not in (200, 201):
        print(f"  ✗ Error creando OT: {ot}")
        sys.exit(1)

    ot_id   = ot.get("id")
    ot_code = ot.get("repair_code") or ot.get("repair_number") or "—"
    print(f"\n  ✔ OT ID: {ot_id}  |  Código: {ot_code}")

    # ── 7. LEER OT COMPLETA ─────────────────────────────────────────────────
    section("7 · Leer OT completa desde la API")
    _, ot_detail = get(s, f"/repairs/{ot_id}", "detalle OT")

    # ── 8. ESTADOS DISPONIBLES ──────────────────────────────────────────────
    section("8 · Estados de OT disponibles")
    _, statuses = get(s, "/repair-statuses/")
    if isinstance(statuses, list):
        print(f"\n  {len(statuses)} estados registrados:")
        for st in statuses:
            print(f"    [{st.get('id')}] {st.get('name')} — {st.get('description','')}")

    # ── 9. CAMBIAR ESTADO OT ────────────────────────────────────────────────
    section("9 · Cambiar estado de la OT")
    # Buscar estado "En diagnóstico" o el segundo disponible
    target_status = None
    if isinstance(statuses, list) and len(statuses) > 1:
        current = ot_detail.get("status_id") or 1
        for st in statuses:
            if st.get("id") != current:
                target_status = st
                break

    if target_status:
        print(f"\n  Cambiando a: [{target_status['id']}] {target_status['name']}")
        status_up, ot_updated = put(
            s,
            f"/repairs/{ot_id}",
            {"status_id": target_status["id"]},
            "OT actualizada",
        )
    else:
        print("  (sin cambio de estado — no hay estados alternativos)")

    # ── 10. REGISTRAR PAGO ADICIONAL ────────────────────────────────────────
    section("10 · Registrar pago asociado a la OT")
    pay_payload = {
        "repair_id":      ot_id,
        "amount":         25000,
        "payment_method": "cash",
        "transaction_id": f"SMK-{slug}-{stamp}",
        "status":         "success",
        "currency":       "CLP",
        "notes":          "Abono adicional efectivo — smoke flow",
    }
    show("payload enviado", pay_payload)
    pay_status, payment = post(s, "/payments/", pay_payload, "pago registrado")

    if pay_status in (200, 201):
        print(f"\n  ✔ Pago ID: {payment.get('id')}  |  Monto: {payment.get('amount')} CLP")
    else:
        print(f"  ✗ Error pago: {payment}")

    # ── 11. ESTADÍSTICAS / KPIs ─────────────────────────────────────────────
    section("11 · KPIs del sistema (snapshot actual)")
    _, kpis = get(s, "/analytics/kpis/summary", "KPIs")

    # ── 12. RESUMEN FINAL ───────────────────────────────────────────────────
    section("RESUMEN — Datos generados en esta corrida")
    print(f"""
  Cliente
    ID:       {client_id}
    Código:   {client_code}
    Nombre:   Carlos Smoke {slug}
    Email:    smoke.{slug}@test.cl

  Dispositivo
    ID:       {device.get('id') if device else '—'}
    Modelo:   Prophet-5 Rev 4  (Sequential)
    Serial:   SEQ{slug.upper()}

  Orden de Trabajo
    ID:       {ot_id}
    Código:   {ot_code}
    Estado:   {target_status['name'] if target_status else ot_detail.get('status_id','—')}
    Abono:    $15.000 CLP (transfer al crear)

  Pago adicional
    ID:       {payment.get('id') if pay_status in (200,201) else '—'}
    Monto:    $25.000 CLP (efectivo)
    TX:       SMK-{slug}-{stamp}

  Total registrado en OT: $40.000 CLP
""")
    print(f"{'═'*60}\n  Flujo completado sin errores críticos.\n{'═'*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CDS smoke flow completo")
    parser.add_argument(
        "--admin-email",
        default=os.getenv("CDS_SMOKE_ADMIN_EMAIL", "admin@cirujanodesintetizadores.cl"),
    )
    parser.add_argument("--admin-pass", default=os.getenv("CDS_SMOKE_ADMIN_PASS"))
    args = parser.parse_args()
    if not args.admin_pass:
        parser.error('Falta --admin-pass o la variable de entorno CDS_SMOKE_ADMIN_PASS.')
    run(args.admin_email, args.admin_pass)

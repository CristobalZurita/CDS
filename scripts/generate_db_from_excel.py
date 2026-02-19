#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GENERADOR COMPLETO DE BD - CREATE + INSERT
Lee el Excel y genera SQL con tablas + componentes
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
import os

REPO_ROOT = Path(__file__).resolve().parents[1]
EXCEL_PATH = Path(os.getenv("INVENTORY_EXCEL_PATH", str(REPO_ROOT / "Inventario_Cirujanosintetizadores.xlsx")))
SQL_OUTPUT = Path(os.getenv("GENERATED_SQL_OUTPUT", str(REPO_ROOT / "database" / "cirujano_database.sql")))

def generate_create_tables():
    """Genera CREATE TABLE statements"""
    return """
-- =====================================================================
-- CIRUJANO DE SINTETIZADORES - BASE DE DATOS PROFESIONAL
-- =====================================================================

PRAGMA foreign_keys = ON;
PRAGMA encoding = 'UTF-8';

-- =====================================================================
-- TABLAS DE COMPONENTES
-- =====================================================================

CREATE TABLE IF NOT EXISTS comp_resistors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value_ohms REAL NOT NULL UNIQUE,
    display_value TEXT NOT NULL,
    tolerance_percent REAL,
    power_watts REAL,
    technology TEXT,
    package TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS comp_capacitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value_farads REAL NOT NULL,
    display_value TEXT NOT NULL,
    dielectric TEXT,
    voltage_volts REAL,
    polarized INTEGER DEFAULT 0,
    package TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(value_farads, dielectric, voltage_volts)
);

CREATE TABLE IF NOT EXISTS comp_integrated_circuits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_number TEXT NOT NULL UNIQUE,
    package TEXT,
    voltage_volts REAL,
    pin_count INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS comp_transistors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_number TEXT NOT NULL UNIQUE,
    type TEXT,
    package TEXT,
    pins INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS comp_diodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_number TEXT NOT NULL UNIQUE,
    type TEXT,
    package TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================================
-- TABLAS DE INVENTARIO / STOCK
-- =====================================================================

CREATE TABLE IF NOT EXISTS storage_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    location_type TEXT,
    is_active INTEGER DEFAULT 1
);

INSERT OR IGNORE INTO storage_locations (code, name, description, location_type) VALUES 
    ('drawer_01', 'Drawer 01 - Resistencias', 'Cajón para resistencias pequeñas', 'drawer'),
    ('drawer_02', 'Drawer 02 - Capacitores', 'Cajón para capacitores', 'drawer'),
    ('drawer_03', 'Drawer 03 - Semiconductores', 'Cajón para transistores y diodos', 'drawer'),
    ('drawer_04', 'Drawer 04 - ICs', 'Cajón para circuitos integrados', 'drawer'),
    ('shelf_01', 'Shelf 01 - Componentes grandes', 'Estante para componentes grandes', 'shelf');

CREATE TABLE IF NOT EXISTS stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_type TEXT NOT NULL,
    component_id INTEGER NOT NULL,
    storage_location_id INTEGER,
    quantity INTEGER DEFAULT 0,
    unit TEXT DEFAULT 'pcs',
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- =====================================================================
-- TABLAS DE REPARACIÓN
-- =====================================================================

CREATE TABLE IF NOT EXISTS repair_statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    color TEXT
);

INSERT OR IGNORE INTO repair_statuses (code, name, description, color) VALUES 
    ('pending', 'Pendiente', 'Esperando evaluación', '#FFA500'),
    ('quoted', 'Cotizado', 'Cotización enviada', '#FFD700'),
    ('approved', 'Aprobado', 'Cliente aprobó', '#32CD32'),
    ('in_progress', 'En Proceso', 'Reparación en curso', '#1E90FF'),
    ('completed', 'Completado', 'Terminado', '#228B22'),
    ('delivered', 'Entregado', 'Devuelto al cliente', '#2F4F4F');

CREATE TABLE IF NOT EXISTS devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    manufacturer TEXT,
    device_type TEXT,
    description TEXT,
    year_manufacture INTEGER,
    is_active INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS repairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id INTEGER NOT NULL,
    status_id INTEGER DEFAULT 1,
    description TEXT,
    quote_amount REAL,
    cost REAL,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_completed TIMESTAMP,
    notes TEXT,
    FOREIGN KEY(device_id) REFERENCES devices(id),
    FOREIGN KEY(status_id) REFERENCES repair_statuses(id)
);

CREATE TABLE IF NOT EXISTS repair_component_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repair_id INTEGER NOT NULL,
    component_type TEXT NOT NULL,
    component_id INTEGER NOT NULL,
    quantity_used INTEGER DEFAULT 1,
    notes TEXT,
    date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(repair_id) REFERENCES repairs(id)
);

-- =====================================================================
-- TABLAS DE GESTIÓN
-- =====================================================================

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT,
    password_hash TEXT,
    is_active INTEGER DEFAULT 1,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    address TEXT,
    city TEXT,
    country TEXT,
    notes TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

"""

def normalize_resistance(value):
    """Normaliza valores de resistencia a Ohms"""
    try:
        ohms = float(value)
        if ohms >= 1_000_000:
            display = f"{ohms/1_000_000:.2g}MΩ"
        elif ohms >= 1_000:
            display = f"{ohms/1_000:.2g}kΩ"
        else:
            display = f"{ohms:.2g}Ω"
        return ohms, display
    except:
        return None, None

def normalize_capacitor(value):
    """Normaliza valores de capacitor"""
    try:
        val = float(str(value).replace('NP', '').strip())
        # Asumir que están en µF para cerámicos/electrolíticos
        farads = val * 1e-6
        display = f"{val:.2g}µF"
        return farads, display
    except:
        return None, None

def read_excel():
    """Lee el Excel y extrae todas las columnas como categorías dinámicas"""
    print("📖 Leyendo Excel...")
    df = pd.read_excel(EXCEL_PATH, sheet_name=0)
    components = {}
    for col in df.columns:
        # Cada columna es una categoría
        values = [str(val).strip() for val in df[col].dropna() if str(val).strip()]
        components[col] = values
    return components

def generate_sql(components):
    """Genera SQL INSERT statements para todas las categorías detectadas"""
    print("✍️  Generando SQL...")
    sql_lines = []
    sql_lines.append("-- CIRUJANO DB - Componentes desde Excel (dinámico)")
    sql_lines.append(f"-- Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sql_lines.append("")
    for category, values in components.items():
        table_name = f"comp_{category.strip().lower().replace(' ', '_').replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace('ñ','n').replace("'","")}"  # nombre de tabla profesional
        for val in values:
            sql_lines.append(f"INSERT INTO {table_name} (value) VALUES ('{val.replace("'", "''")}');")
    return "\n".join(sql_lines)

def main():
    print("\n" + "="*60)
    print("GENERADOR DE DB - CIRUJANO SINTETIZADORES (PROFESIONAL Y DINÁMICO)")
    print("="*60 + "\n")
    if not EXCEL_PATH.exists():
        print(f"❌ Excel no encontrado: {EXCEL_PATH}")
        return
    # Leer Excel
    components = read_excel()
    # Resumen dinámico
    print(f"\n📊 Categorías detectadas:")
    total = 0
    for category, values in components.items():
        print(f"   • {category}: {len(values)}")
        total += len(values)
    print(f"\n   ✅ TOTAL: {total} componentes\n")
    # Generar SQL
    sql = generate_sql(components)
    # Guardar SQL
    SQL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(SQL_OUTPUT, 'w') as f:
        f.write(sql)
    print(f"✅ SQL guardado en: {SQL_OUTPUT}\n")
    # Mostrar primeras líneas
    print("Primeras inserciones:")
    print("-" * 60)
    for line in sql.split('\n')[:10]:
        if line.strip():
            print(line[:80] + "...")
    print("-" * 60)
    print("\n✨ Listo para ejecutar en la base de datos\n")

if __name__ == "__main__":
    main()

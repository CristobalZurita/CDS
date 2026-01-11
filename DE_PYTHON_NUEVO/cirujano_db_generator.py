#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
CIRUJANO DE SINTETIZADORES - GENERADOR DE BASE DE DATOS PROFESIONAL
================================================================================
Ejecutar: python cirujano_db_generator.py
Salida: /output/cirujano_database.sql + /output/json/*.json
================================================================================
"""

import os
import re
import json
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# ==============================================================================
# CONFIGURACIÓN
# ==============================================================================

class Config:
    EXCEL_PATH = "/mnt/project/Inventario_Cirujanosintetizadores.xlsx"
    BASE_DATOS_PATH = "/mnt/project/BASE_DATOS.txt"
    OUTPUT_DIR = "/home/claude/output"
    JSON_DIR = "/home/claude/output/json"
    SQL_OUTPUT = "/home/claude/output/cirujano_database.sql"


# ==============================================================================
# FUNCIONES DE NORMALIZACIÓN
# ==============================================================================

def normalize_resistance(value: float) -> Dict[str, Any]:
    """Convierte valor de resistencia a formato normalizado."""
    if value >= 1_000_000:
        display = f"{value/1_000_000:.2f}MΩ".replace('.00', '')
    elif value >= 1_000:
        display = f"{value/1_000:.2f}kΩ".replace('.00', '')
    else:
        display = f"{value:.2f}Ω".replace('.00', '')
    
    return {
        "value_ohms": value,
        "display_value": display,
        "tolerance_percent": 5.0 if value < 10 else 1.0,
        "power_watts": 0.25,
        "technology": "METAL_FILM",
        "package": "TH_AXIAL"
    }


def parse_capacitor_code(code) -> Dict[str, Any]:
    """Parsea códigos de capacitores cerámicos."""
    try:
        code_str = str(code).strip()
        
        if code_str.isdigit() and len(code_str) <= 3:
            value_pf = float(code_str)
            return {
                "value_farads": value_pf * 1e-12,
                "display_value": f"{int(value_pf)}pF",
                "dielectric": "CERAMIC",
                "voltage_volts": 50.0,
                "package": "TH_RADIAL"
            }
        
        if len(code_str) == 3 and code_str.isdigit():
            base = int(code_str[:2])
            multiplier = int(code_str[2])
            value_pf = base * (10 ** multiplier)
            
            if value_pf >= 1_000_000:
                display = f"{value_pf/1_000_000:.1f}µF"
            elif value_pf >= 1_000:
                display = f"{value_pf/1_000:.0f}nF"
            else:
                display = f"{value_pf:.0f}pF"
            
            return {
                "value_farads": value_pf * 1e-12,
                "display_value": display,
                "dielectric": "CERAMIC",
                "voltage_volts": 50.0,
                "package": "TH_RADIAL"
            }
        
        value_uf = float(code_str)
        return {
            "value_farads": value_uf * 1e-6,
            "display_value": f"{value_uf}µF",
            "dielectric": "ELECTROLYTIC_AL",
            "voltage_volts": 25.0,
            "polarized": True,
            "package": "TH_RADIAL"
        }
        
    except (ValueError, TypeError):
        return None


def classify_ic(part_number: str) -> Dict[str, Any]:
    """Clasifica un IC por su part number."""
    pn = part_number.upper().strip()
    
    if pn.startswith(('12F', '16F', '18F', 'PIC')):
        return {"function_type": "MCU", "manufacturer": "Microchip", "family": "PIC"}
    if pn.startswith(('ATMEGA', 'ATTINY', 'AT90')):
        return {"function_type": "MCU", "manufacturer": "Microchip/Atmel", "family": "AVR"}
    if pn.startswith(('24LC', '24C', '93C', '25C', '27C', '28C', '29F')):
        return {"function_type": "MEMORY", "manufacturer": "Various", "family": "EEPROM"}
    if pn.startswith('CD40') or pn.startswith('HEF40'):
        return {"function_type": "LOGIC_CMOS", "manufacturer": "Various", "family": "4000_SERIES"}
    if pn.startswith(('74HC', '74LS', '74HCT', '74')):
        return {"function_type": "LOGIC_TTL", "manufacturer": "Various", "family": "74_SERIES"}
    if pn.startswith(('4N', '6N', 'PC8', 'EL8', 'CNY', 'MOC', 'H11')):
        return {"function_type": "OPTOCOUPLER", "manufacturer": "Various", "family": "OPTO"}
    if pn.startswith(('78', '79', 'LM78', 'LM79', 'L78', 'L79')):
        return {"function_type": "VOLTAGE_REG", "manufacturer": "Various", "family": "LINEAR_REG"}
    if pn.startswith(('LM317', 'LM337', 'AMS1117', 'LD1117', 'AZ1117')):
        return {"function_type": "VOLTAGE_REG", "manufacturer": "Various", "family": "LDO"}
    if pn in ('7555', '7556', 'NE555', 'LM555', 'NE556', 'LM556'):
        return {"function_type": "TIMER", "manufacturer": "Various", "family": "555"}
    if pn in ('7660', 'ICL7660', 'MAX660'):
        return {"function_type": "DC_CONVERTER", "manufacturer": "Various", "family": "CHARGE_PUMP"}
    if pn.startswith(('AK4', 'PCM', 'WM8', 'CS4', 'TDA', 'LA44', 'AN7')):
        return {"function_type": "AUDIO_IC", "manufacturer": "Various", "family": "AUDIO"}
    if pn.startswith(('CA30', 'LM13', 'SSM', 'NJM', 'TL0', 'NE55', 'LM3')):
        return {"function_type": "OP_AMP", "manufacturer": "Various", "family": "AUDIO"}
    
    return {"function_type": "GENERAL", "manufacturer": "Unknown", "family": "MISC"}


def classify_transistor(part_number: str) -> Dict[str, Any]:
    """Clasifica un transistor por su part number."""
    pn = part_number.upper().strip()
    
    npn = ['2N3904', '2N2222', '2N4401', '2N5088', '2N5089', '2N5551', 
           'BC547', 'BC548', 'BC549', 'BC337', 'BC517', 'MPSA18', 'MPSA13']
    pnp = ['2N3906', '2N2907', '2N4403', '2N5087', '2N5401',
           'BC557', 'BC558', 'BC559', 'BC327', 'A1015', 'B772', 'A933']
    jfet_n = ['2N5457', '2N5458', 'MPF102', '2SK30', 'J201']
    jfet_p = ['2N5460', 'J175']
    mosfet_n = ['2N7000', 'BS170', 'IRF540', '20N60', 'P20N06']
    
    if pn.startswith(('LM78', 'LM79', '78', '79')):
        return {"device_type": "VOLTAGE_REG", "package": "TO-220", "application": "POWER"}
    
    for prefix in npn:
        if pn.startswith(prefix) or pn == prefix:
            return {"device_type": "BJT_NPN", "package": "TO-92", "application": "GENERAL"}
    for prefix in pnp:
        if pn.startswith(prefix) or pn == prefix:
            return {"device_type": "BJT_PNP", "package": "TO-92", "application": "GENERAL"}
    for prefix in jfet_n:
        if pn.startswith(prefix) or pn == prefix:
            return {"device_type": "JFET_N", "package": "TO-92", "application": "AUDIO"}
    for prefix in jfet_p:
        if pn.startswith(prefix) or pn == prefix:
            return {"device_type": "JFET_P", "package": "TO-92", "application": "AUDIO"}
    for prefix in mosfet_n:
        if pn.startswith(prefix) or pn == prefix:
            return {"device_type": "MOSFET_N", "package": "TO-220", "application": "POWER"}
    
    if pn.startswith('2SC') or pn.startswith('BC5'):
        return {"device_type": "BJT_NPN", "package": "TO-92", "application": "GENERAL"}
    if pn.startswith('2SA') or pn.startswith('BC3') or pn.startswith('A1'):
        return {"device_type": "BJT_PNP", "package": "TO-92", "application": "GENERAL"}
    
    return {"device_type": "BJT_NPN", "package": "TO-92", "application": "GENERAL"}


def classify_diode(part_number: str) -> Dict[str, Any]:
    """Clasifica un diodo por su part number."""
    pn = part_number.upper().strip()
    
    if pn.startswith('BZT') or pn.startswith('BZX') or pn.startswith('1N47'):
        return {"device_type": "ZENER", "package": "DO-35"}
    if pn.startswith(('MBR', 'SB', '1N58', 'BAT', 'SS')):
        return {"device_type": "SCHOTTKY", "package": "DO-41"}
    if pn.startswith(('1N4148', '1N914', '1SS', 'BAV')):
        return {"device_type": "SIGNAL", "package": "DO-35"}
    if pn.startswith(('1N400', '1N540', 'UF', 'MUR')):
        return {"device_type": "RECTIFIER", "package": "DO-41"}
    
    return {"device_type": "RECTIFIER", "package": "DO-41"}


# ==============================================================================
# LECTOR DE EXCEL
# ==============================================================================

class ExcelReader:
    def __init__(self, excel_path: str):
        self.excel_path = excel_path
    
    def read(self) -> Dict[str, List]:
        data = {}
        try:
            df = pd.read_excel(self.excel_path, sheet_name='Hoja 1')
            data['resistors'] = self._extract_resistors(df)
            data['capacitors_ceramic'] = self._extract_ceramic_caps(df)
            data['capacitors_electrolytic'] = self._extract_electrolytic_caps(df)
            data['integrated_circuits'] = self._extract_ics(df)
            data['transistors'] = self._extract_transistors(df)
            data['diodes'] = self._extract_diodes(df)
        except Exception as e:
            print(f"Error leyendo Excel: {e}")
        return data
    
    def _extract_resistors(self, df) -> List[Dict]:
        resistors = []
        seen = set()
        for col in ['Resistencias', 'Resistencias.1']:
            if col in df.columns:
                for val in df[col].dropna():
                    try:
                        ohms = float(val)
                        if ohms > 0 and ohms not in seen:
                            seen.add(ohms)
                            resistors.append(normalize_resistance(ohms))
                    except:
                        continue
        return sorted(resistors, key=lambda x: x['value_ohms'])
    
    def _extract_ceramic_caps(self, df) -> List[Dict]:
        caps = []
        seen = set()
        for col in ['Capacitores Ceramicos', 'Capacitores Ceramicos.1']:
            if col in df.columns:
                for val in df[col].dropna():
                    parsed = parse_capacitor_code(val)
                    if parsed and parsed.get('value_farads'):
                        key = parsed['value_farads']
                        if key not in seen:
                            seen.add(key)
                            parsed['dielectric'] = 'CERAMIC'
                            caps.append(parsed)
        return sorted(caps, key=lambda x: x['value_farads'])
    
    def _extract_electrolytic_caps(self, df) -> List[Dict]:
        caps = []
        seen = set()
        for col in ['Capacitores Electrolíticos', 'Capacitores Electrolíticos.1']:
            if col in df.columns:
                for val in df[col].dropna():
                    try:
                        val_str = str(val).replace('NP', '').strip()
                        value_uf = float(val_str)
                        if value_uf > 0 and value_uf not in seen:
                            seen.add(value_uf)
                            caps.append({
                                "value_farads": value_uf * 1e-6,
                                "display_value": f"{value_uf}µF",
                                "dielectric": "ELECTROLYTIC_AL",
                                "voltage_volts": 25.0 if value_uf <= 100 else 16.0,
                                "polarized": True,
                                "package": "TH_RADIAL",
                                "temperature_rating": "105C"
                            })
                    except:
                        continue
        return sorted(caps, key=lambda x: x['value_farads'])
    
    def _extract_ics(self, df) -> List[Dict]:
        ics = []
        seen = set()
        for col in ["Ic's", "Ic's.1"]:
            if col in df.columns:
                for val in df[col].dropna():
                    pn = str(val).strip().upper()
                    if pn and pn not in seen:
                        seen.add(pn)
                        ics.append({"part_number": pn, **classify_ic(pn)})
        return sorted(ics, key=lambda x: x['part_number'])
    
    def _extract_transistors(self, df) -> List[Dict]:
        transistors = []
        seen = set()
        for col in ['Transistores', 'Transistores.1']:
            if col in df.columns:
                for val in df[col].dropna():
                    pn = str(val).strip().upper()
                    if pn.startswith(('LM78', 'LM79')):
                        continue
                    if pn and pn not in seen:
                        seen.add(pn)
                        transistors.append({"part_number": pn, **classify_transistor(pn)})
        return sorted(transistors, key=lambda x: x['part_number'])
    
    def _extract_diodes(self, df) -> List[Dict]:
        diodes = []
        seen = set()
        for col in ['Diodos', 'Diodos.1']:
            if col in df.columns:
                for val in df[col].dropna():
                    pn = str(val).strip().upper()
                    if pn and pn not in seen:
                        seen.add(pn)
                        diodes.append({"part_number": pn, **classify_diode(pn)})
        return sorted(diodes, key=lambda x: x['part_number'])


# ==============================================================================
# GENERADOR SQL
# ==============================================================================

class SQLGenerator:
    def __init__(self):
        self.sql_parts = []
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def generate(self, data: Dict) -> str:
        self._add_header()
        self._add_drop_tables()
        self._add_reference_tables()
        self._add_user_tables()
        self._add_client_tables()
        self._add_device_tables()
        self._add_repair_tables()
        self._add_tool_tables()
        self._add_component_tables()
        self._add_stock_tables()
        self._add_repair_relations()
        self._add_views()
        self._add_component_data(data)
        self._add_admin_user()
        return '\n'.join(self.sql_parts)
    
    def _add_header(self):
        self.sql_parts.append(f"""-- =====================================================================
-- CIRUJANO DE SINTETIZADORES - BASE DE DATOS PROFESIONAL
-- Generado: {self.timestamp}
-- Motor: SQLite
-- =====================================================================

PRAGMA foreign_keys = ON;
PRAGMA encoding = 'UTF-8';
""")

    def _add_drop_tables(self):
        self.sql_parts.append("""
-- LIMPIEZA
DROP TABLE IF EXISTS repair_photos;
DROP TABLE IF EXISTS repair_notes;
DROP TABLE IF EXISTS repair_component_usage;
DROP TABLE IF EXISTS repair_tool_usage;
DROP TABLE IF EXISTS stock_movements;
DROP TABLE IF EXISTS stock;
DROP TABLE IF EXISTS repairs;
DROP TABLE IF EXISTS quotes;
DROP TABLE IF EXISTS devices;
DROP TABLE IF EXISTS tool_maintenance;
DROP TABLE IF EXISTS tools;
DROP TABLE IF EXISTS tool_categories;
DROP TABLE IF EXISTS tool_brands;
DROP TABLE IF EXISTS storage_locations;
DROP TABLE IF EXISTS comp_resistors;
DROP TABLE IF EXISTS comp_capacitors;
DROP TABLE IF EXISTS comp_inductors;
DROP TABLE IF EXISTS comp_transformers;
DROP TABLE IF EXISTS comp_diodes;
DROP TABLE IF EXISTS comp_transistors;
DROP TABLE IF EXISTS comp_integrated_circuits;
DROP TABLE IF EXISTS comp_potentiometers;
DROP TABLE IF EXISTS comp_switches;
DROP TABLE IF EXISTS comp_connectors;
DROP TABLE IF EXISTS comp_cables;
DROP TABLE IF EXISTS comp_displays;
DROP TABLE IF EXISTS comp_power_modules;
DROP TABLE IF EXISTS comp_mechanical;
DROP TABLE IF EXISTS comp_chassis_hardware;
DROP TABLE IF EXISTS comp_consumables;
DROP TABLE IF EXISTS clients;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS user_roles;
DROP TABLE IF EXISTS device_types;
DROP TABLE IF EXISTS device_brands;
DROP TABLE IF EXISTS repair_statuses;
""")

    def _add_reference_tables(self):
        self.sql_parts.append("""
-- =====================================================================
-- TABLAS DE REFERENCIA
-- =====================================================================

CREATE TABLE user_roles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    permissions TEXT
);

INSERT INTO user_roles (name, description) VALUES 
    ('admin', 'Administrador - acceso total'),
    ('technician', 'Técnico - gestión de trabajos'),
    ('client', 'Cliente - ver estado de equipos');

CREATE TABLE repair_statuses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    color TEXT,
    sort_order INTEGER DEFAULT 0
);

INSERT INTO repair_statuses (code, name, description, color, sort_order) VALUES 
    ('pending_quote', 'Pendiente Cotización', 'Esperando evaluación', '#FFA500', 1),
    ('quoted', 'Cotizado', 'Cotización enviada', '#FFD700', 2),
    ('approved', 'Aprobado', 'Cliente aprobó', '#32CD32', 3),
    ('in_progress', 'En Proceso', 'Reparación en curso', '#1E90FF', 4),
    ('waiting_parts', 'Esperando Repuestos', 'Faltan componentes', '#FF6347', 5),
    ('testing', 'En Pruebas', 'Verificando', '#9370DB', 6),
    ('completed', 'Completado', 'Terminado', '#228B22', 7),
    ('delivered', 'Entregado', 'Devuelto al cliente', '#2F4F4F', 8),
    ('cancelled', 'Cancelado', 'Cancelado', '#DC143C', 9);

CREATE TABLE device_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT
);

INSERT INTO device_types (code, name, description) VALUES 
    ('synth', 'Sintetizador', 'Sintetizadores analógicos y digitales'),
    ('keyboard', 'Teclado/Workstation', 'Teclados arranger y workstations'),
    ('drum_machine', 'Caja de Ritmos', 'Drum machines y grooveboxes'),
    ('sampler', 'Sampler', 'Samplers hardware'),
    ('effects', 'Efectos/Pedal', 'Pedales y procesadores'),
    ('amplifier', 'Amplificador', 'Amplificadores de audio'),
    ('mixer', 'Mezclador', 'Consolas y mezcladores'),
    ('audio_interface', 'Interfaz de Audio', 'Interfaces y tarjetas'),
    ('controller', 'Controlador MIDI', 'Controladores'),
    ('other', 'Otro', 'Otros equipos');

CREATE TABLE device_brands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    country TEXT,
    is_active INTEGER DEFAULT 1
);

INSERT INTO device_brands (name, country) VALUES 
    ('Korg', 'Japón'), ('Roland', 'Japón'), ('Yamaha', 'Japón'),
    ('Moog', 'USA'), ('Sequential', 'USA'), ('Novation', 'UK'),
    ('Arturia', 'Francia'), ('Behringer', 'China'), ('Akai', 'Japón'),
    ('Native Instruments', 'Alemania'), ('Elektron', 'Suecia'),
    ('Access', 'Alemania'), ('Nord', 'Suecia'), ('Otro', 'N/A');
""")

    def _add_user_tables(self):
        self.sql_parts.append("""
-- =====================================================================
-- USUARIOS
-- =====================================================================

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    first_name TEXT,
    last_name TEXT,
    phone TEXT,
    avatar_url TEXT,
    role_id INTEGER NOT NULL DEFAULT 3,
    is_active INTEGER DEFAULT 1,
    is_verified INTEGER DEFAULT 0,
    verification_token TEXT,
    reset_token TEXT,
    reset_token_expires DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME,
    FOREIGN KEY (role_id) REFERENCES user_roles(id)
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role_id);
""")

    def _add_client_tables(self):
        self.sql_parts.append("""
-- =====================================================================
-- CLIENTES
-- =====================================================================

CREATE TABLE clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    phone_alt TEXT,
    address TEXT,
    city TEXT,
    region TEXT,
    country TEXT DEFAULT 'Chile',
    preferred_contact TEXT DEFAULT 'whatsapp',
    notes TEXT,
    total_repairs INTEGER DEFAULT 0,
    total_spent REAL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_clients_user ON clients(user_id);
CREATE INDEX idx_clients_phone ON clients(phone);
""")

    def _add_device_tables(self):
        self.sql_parts.append("""
-- =====================================================================
-- DISPOSITIVOS
-- =====================================================================

CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER NOT NULL,
    device_type_id INTEGER NOT NULL,
    brand_id INTEGER,
    brand_other TEXT,
    model TEXT NOT NULL,
    serial_number TEXT,
    year_manufactured INTEGER,
    description TEXT,
    condition_notes TEXT,
    photos TEXT,
    total_repairs INTEGER DEFAULT 0,
    first_repair_date DATE,
    last_repair_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (device_type_id) REFERENCES device_types(id),
    FOREIGN KEY (brand_id) REFERENCES device_brands(id)
);

CREATE INDEX idx_devices_client ON devices(client_id);
CREATE INDEX idx_devices_type ON devices(device_type_id);
""")

    def _add_repair_tables(self):
        self.sql_parts.append("""
-- =====================================================================
-- COTIZACIONES Y REPARACIONES
-- =====================================================================

CREATE TABLE quotes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quote_number TEXT UNIQUE NOT NULL,
    client_id INTEGER NOT NULL,
    device_id INTEGER,
    problem_description TEXT NOT NULL,
    photos_received TEXT,
    diagnosis TEXT,
    estimated_hours REAL,
    estimated_parts_cost REAL DEFAULT 0,
    estimated_labor_cost REAL DEFAULT 0,
    estimated_total REAL DEFAULT 0,
    status TEXT DEFAULT 'pending',
    valid_until DATE,
    client_response TEXT,
    responded_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER,
    FOREIGN KEY (client_id) REFERENCES clients(id),
    FOREIGN KEY (device_id) REFERENCES devices(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);

CREATE TABLE repairs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repair_number TEXT UNIQUE NOT NULL,
    device_id INTEGER NOT NULL,
    quote_id INTEGER,
    status_id INTEGER NOT NULL DEFAULT 1,
    assigned_to INTEGER,
    intake_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    diagnosis_date DATETIME,
    approval_date DATETIME,
    start_date DATETIME,
    completion_date DATETIME,
    delivery_date DATETIME,
    problem_reported TEXT NOT NULL,
    diagnosis TEXT,
    work_performed TEXT,
    parts_cost REAL DEFAULT 0,
    labor_cost REAL DEFAULT 0,
    additional_cost REAL DEFAULT 0,
    discount REAL DEFAULT 0,
    total_cost REAL DEFAULT 0,
    payment_status TEXT DEFAULT 'pending',
    payment_method TEXT,
    paid_amount REAL DEFAULT 0,
    warranty_days INTEGER DEFAULT 90,
    warranty_until DATE,
    priority INTEGER DEFAULT 2,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (device_id) REFERENCES devices(id),
    FOREIGN KEY (quote_id) REFERENCES quotes(id),
    FOREIGN KEY (status_id) REFERENCES repair_statuses(id),
    FOREIGN KEY (assigned_to) REFERENCES users(id)
);

CREATE TABLE repair_photos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repair_id INTEGER NOT NULL,
    photo_url TEXT NOT NULL,
    photo_type TEXT DEFAULT 'progress',
    caption TEXT,
    sort_order INTEGER DEFAULT 0,
    visible_to_client INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repair_id) REFERENCES repairs(id) ON DELETE CASCADE
);

CREATE TABLE repair_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repair_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    note TEXT NOT NULL,
    note_type TEXT DEFAULT 'internal',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repair_id) REFERENCES repairs(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_repairs_device ON repairs(device_id);
CREATE INDEX idx_repairs_status ON repairs(status_id);
CREATE INDEX idx_repairs_date ON repairs(intake_date);
CREATE INDEX idx_repairs_number ON repairs(repair_number);
""")

    def _add_tool_tables(self):
        self.sql_parts.append("""
-- =====================================================================
-- HERRAMIENTAS DEL TALLER
-- =====================================================================

CREATE TABLE tool_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT
);

INSERT INTO tool_categories (code, name, description) VALUES 
    ('measurement', 'Instrumentación', 'Osciloscopios, multímetros'),
    ('soldering', 'Soldadura', 'Estaciones, aire caliente'),
    ('power_supply', 'Fuentes', 'Fuentes de laboratorio'),
    ('machining', 'Mecanizado', 'CNC, impresoras 3D'),
    ('hand_tools', 'Manuales', 'Destornilladores, alicates'),
    ('safety', 'Seguridad', 'ESD, extractores'),
    ('optics', 'Óptica', 'Microscopios, lupas');

CREATE TABLE tool_brands (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    country TEXT,
    quality_tier INTEGER DEFAULT 2
);

INSERT INTO tool_brands (name, country, quality_tier) VALUES 
    ('Fluke', 'USA', 1), ('Keysight', 'USA', 1), ('Tektronix', 'USA', 1),
    ('Rigol', 'China', 2), ('Siglent', 'China', 2), ('Hakko', 'Japón', 1),
    ('Weller', 'Alemania', 1), ('JBC', 'España', 1), ('iFixit', 'USA', 2),
    ('Wiha', 'Alemania', 1), ('Knipex', 'Alemania', 1), ('Otro', 'N/A', 3);

CREATE TABLE storage_locations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    location_type TEXT,
    description TEXT
);

INSERT INTO storage_locations (code, name, location_type) VALUES 
    ('WB-01', 'Banco Principal', 'workbench'),
    ('WB-02', 'Banco Soldadura', 'workbench'),
    ('CAB-01', 'Armario Instrumentos', 'cabinet'),
    ('CAB-02', 'Armario Componentes', 'cabinet'),
    ('SH-A', 'Estantería A', 'shelf'),
    ('SH-B', 'Estantería B', 'shelf');

CREATE TABLE tools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT UNIQUE,
    name TEXT NOT NULL,
    model TEXT,
    brand_id INTEGER,
    category_id INTEGER,
    location_id INTEGER,
    serial_number TEXT,
    specifications TEXT,
    status TEXT DEFAULT 'available',
    requires_calibration INTEGER DEFAULT 0,
    last_calibration_date DATE,
    next_calibration_date DATE,
    purchase_price REAL,
    purchase_date DATE,
    warranty_until DATE,
    image_url TEXT,
    manual_url TEXT,
    notes TEXT,
    is_active INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (brand_id) REFERENCES tool_brands(id),
    FOREIGN KEY (category_id) REFERENCES tool_categories(id),
    FOREIGN KEY (location_id) REFERENCES storage_locations(id)
);

CREATE TABLE tool_maintenance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tool_id INTEGER NOT NULL,
    action_type TEXT,
    description TEXT,
    cost REAL,
    performed_by TEXT,
    performed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    next_action_date DATE,
    FOREIGN KEY (tool_id) REFERENCES tools(id) ON DELETE CASCADE
);

CREATE INDEX idx_tools_category ON tools(category_id);
CREATE INDEX idx_tools_status ON tools(status);
""")

    def _add_component_tables(self):
        self.sql_parts.append("""
-- =====================================================================
-- COMPONENTES ELECTRÓNICOS
-- =====================================================================

CREATE TABLE comp_resistors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value_ohms REAL NOT NULL,
    display_value TEXT,
    tolerance_percent REAL DEFAULT 5,
    power_watts REAL DEFAULT 0.25,
    voltage_max REAL DEFAULT 250,
    technology TEXT DEFAULT 'METAL_FILM',
    package TEXT DEFAULT 'TH_AXIAL',
    series TEXT DEFAULT 'E24',
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comp_capacitors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value_farads REAL NOT NULL,
    display_value TEXT,
    voltage_volts REAL NOT NULL DEFAULT 50,
    tolerance_percent REAL DEFAULT 20,
    dielectric TEXT NOT NULL,
    temperature_rating TEXT,
    package TEXT DEFAULT 'TH_RADIAL',
    polarized INTEGER DEFAULT 0,
    esr_mohms REAL,
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comp_inductors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value_henry REAL NOT NULL,
    display_value TEXT,
    current_max_amps REAL,
    dcr_ohms REAL,
    core_type TEXT,
    package TEXT,
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comp_transformers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transformer_type TEXT,
    primary_voltage REAL,
    secondary_voltage REAL,
    secondary_voltage_2 REAL,
    power_va REAL,
    frequency_hz REAL DEFAULT 50,
    mounting TEXT,
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comp_diodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_number TEXT NOT NULL,
    device_type TEXT NOT NULL,
    package TEXT DEFAULT 'DO-41',
    voltage_reverse_max REAL,
    voltage_forward REAL,
    current_max_amps REAL,
    voltage_zener REAL,
    color TEXT,
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comp_transistors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_number TEXT NOT NULL,
    device_type TEXT NOT NULL,
    package TEXT DEFAULT 'TO-92',
    voltage_max REAL,
    current_max REAL,
    power_max REAL,
    hfe_min INTEGER,
    hfe_max INTEGER,
    application TEXT,
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comp_integrated_circuits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_number TEXT NOT NULL,
    function_type TEXT NOT NULL,
    package TEXT DEFAULT 'DIP8',
    pin_count INTEGER,
    voltage_supply_min REAL,
    voltage_supply_max REAL,
    manufacturer TEXT,
    family TEXT,
    description TEXT,
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comp_potentiometers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    value_ohms REAL NOT NULL,
    display_value TEXT,
    taper TEXT DEFAULT 'LINEAR',
    travel_type TEXT DEFAULT 'ROTARY',
    power_watts REAL DEFAULT 0.25,
    shaft_type TEXT,
    terminals INTEGER DEFAULT 3,
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comp_switches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    switch_type TEXT NOT NULL,
    poles INTEGER DEFAULT 1,
    throws INTEGER DEFAULT 2,
    rating_voltage REAL,
    rating_current REAL,
    mounting TEXT,
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comp_connectors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    connector_type TEXT NOT NULL,
    pin_count INTEGER,
    gender TEXT,
    mounting TEXT,
    plating TEXT,
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comp_cables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cable_type TEXT NOT NULL,
    conductor_count INTEGER,
    gauge_awg REAL,
    shielded INTEGER DEFAULT 0,
    outer_diameter_mm REAL,
    color TEXT,
    price_per_meter REAL,
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comp_displays (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    display_type TEXT NOT NULL,
    resolution TEXT,
    size_inches REAL,
    interface TEXT,
    backlight_type TEXT,
    voltage_volts REAL,
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comp_power_modules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module_type TEXT NOT NULL,
    input_voltage_min REAL,
    input_voltage_max REAL,
    output_voltage REAL,
    output_current REAL,
    package TEXT,
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comp_mechanical (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    part_type TEXT NOT NULL,
    material TEXT,
    dimensions TEXT,
    color TEXT,
    compatible_models TEXT,
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comp_chassis_hardware (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hardware_type TEXT NOT NULL,
    thread_spec TEXT,
    length_mm REAL,
    head_type TEXT,
    material TEXT,
    finish TEXT,
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE comp_consumables (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    consumable_type TEXT NOT NULL,
    brand TEXT,
    specification TEXT,
    unit TEXT DEFAULT 'pcs',
    safety_notes TEXT,
    datasheet_url TEXT,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_resistors_value ON comp_resistors(value_ohms);
CREATE INDEX idx_capacitors_value ON comp_capacitors(value_farads);
CREATE INDEX idx_transistors_pn ON comp_transistors(part_number);
CREATE INDEX idx_ics_pn ON comp_integrated_circuits(part_number);
CREATE INDEX idx_diodes_pn ON comp_diodes(part_number);
""")

    def _add_stock_tables(self):
        self.sql_parts.append("""
-- =====================================================================
-- STOCK E INVENTARIO
-- =====================================================================

CREATE TABLE stock (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    component_table TEXT NOT NULL,
    component_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    quantity_reserved INTEGER DEFAULT 0,
    minimum_stock INTEGER DEFAULT 5,
    location_id INTEGER,
    bin_code TEXT,
    supplier TEXT,
    supplier_part_number TEXT,
    unit_cost REAL,
    last_purchase_date DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (location_id) REFERENCES storage_locations(id),
    UNIQUE(component_table, component_id, location_id)
);

CREATE TABLE stock_movements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_id INTEGER NOT NULL,
    movement_type TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    repair_id INTEGER,
    notes TEXT,
    performed_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (stock_id) REFERENCES stock(id),
    FOREIGN KEY (repair_id) REFERENCES repairs(id),
    FOREIGN KEY (performed_by) REFERENCES users(id)
);

CREATE INDEX idx_stock_component ON stock(component_table, component_id);
CREATE INDEX idx_stock_low ON stock(quantity) WHERE quantity <= minimum_stock;
""")

    def _add_repair_relations(self):
        self.sql_parts.append("""
-- =====================================================================
-- RELACIONES DE REPARACIÓN
-- =====================================================================

CREATE TABLE repair_component_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repair_id INTEGER NOT NULL,
    component_table TEXT NOT NULL,
    component_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 1,
    unit_cost REAL,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repair_id) REFERENCES repairs(id) ON DELETE CASCADE
);

CREATE TABLE repair_tool_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repair_id INTEGER NOT NULL,
    tool_id INTEGER NOT NULL,
    usage_minutes INTEGER,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repair_id) REFERENCES repairs(id) ON DELETE CASCADE,
    FOREIGN KEY (tool_id) REFERENCES tools(id)
);

CREATE INDEX idx_repair_components ON repair_component_usage(repair_id);
CREATE INDEX idx_repair_tools ON repair_tool_usage(repair_id);
""")

    def _add_views(self):
        self.sql_parts.append("""
-- =====================================================================
-- VISTAS ÚTILES
-- =====================================================================

CREATE VIEW v_repairs_active AS
SELECT 
    r.id, r.repair_number, r.intake_date,
    rs.name as status, rs.color as status_color,
    c.name as client_name, c.phone as client_phone,
    db.name as device_brand, d.model as device_model,
    dt.name as device_type, r.problem_reported, r.priority,
    u.first_name || ' ' || u.last_name as technician
FROM repairs r
JOIN devices d ON r.device_id = d.id
JOIN clients c ON d.client_id = c.id
JOIN device_types dt ON d.device_type_id = dt.id
LEFT JOIN device_brands db ON d.brand_id = db.id
JOIN repair_statuses rs ON r.status_id = rs.id
LEFT JOIN users u ON r.assigned_to = u.id
WHERE rs.code NOT IN ('delivered', 'cancelled')
ORDER BY r.priority ASC, r.intake_date ASC;

CREATE VIEW v_stock_low AS
SELECT s.id, s.component_table, s.component_id,
       s.quantity, s.minimum_stock,
       s.quantity - s.minimum_stock as deficit,
       sl.name as location
FROM stock s
LEFT JOIN storage_locations sl ON s.location_id = sl.id
WHERE s.quantity <= s.minimum_stock
ORDER BY deficit ASC;

CREATE VIEW v_tools_calibration_due AS
SELECT t.id, t.code, t.name, t.model, tb.name as brand,
       t.next_calibration_date,
       julianday(t.next_calibration_date) - julianday('now') as days_until_due
FROM tools t
LEFT JOIN tool_brands tb ON t.brand_id = tb.id
WHERE t.requires_calibration = 1
  AND t.next_calibration_date <= date('now', '+30 days')
ORDER BY t.next_calibration_date ASC;
""")

    def _add_component_data(self, data: Dict):
        # Resistencias
        if data.get('resistors'):
            self.sql_parts.append("\n-- DATOS: RESISTENCIAS")
            for r in data['resistors']:
                self.sql_parts.append(
                    f"INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) "
                    f"VALUES ({r['value_ohms']}, '{r['display_value']}', {r.get('tolerance_percent', 5)}, "
                    f"{r.get('power_watts', 0.25)}, '{r.get('technology', 'METAL_FILM')}', '{r.get('package', 'TH_AXIAL')}');"
                )
        
        # Capacitores cerámicos
        if data.get('capacitors_ceramic'):
            self.sql_parts.append("\n-- DATOS: CAPACITORES CERÁMICOS")
            for c in data['capacitors_ceramic']:
                self.sql_parts.append(
                    f"INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) "
                    f"VALUES ({c['value_farads']}, '{c['display_value']}', {c.get('voltage_volts', 50)}, 'CERAMIC', '{c.get('package', 'TH_RADIAL')}');"
                )
        
        # Capacitores electrolíticos
        if data.get('capacitors_electrolytic'):
            self.sql_parts.append("\n-- DATOS: CAPACITORES ELECTROLÍTICOS")
            for c in data['capacitors_electrolytic']:
                self.sql_parts.append(
                    f"INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) "
                    f"VALUES ({c['value_farads']}, '{c['display_value']}', {c.get('voltage_volts', 25)}, 'ELECTROLYTIC_AL', 1, '{c.get('package', 'TH_RADIAL')}', '{c.get('temperature_rating', '105C')}');"
                )
        
        # ICs
        if data.get('integrated_circuits'):
            self.sql_parts.append("\n-- DATOS: CIRCUITOS INTEGRADOS")
            for ic in data['integrated_circuits']:
                mfr = ic.get('manufacturer', '').replace("'", "''")
                fam = ic.get('family', '').replace("'", "''")
                self.sql_parts.append(
                    f"INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) "
                    f"VALUES ('{ic['part_number']}', '{ic.get('function_type', 'GENERAL')}', '{mfr}', '{fam}');"
                )
        
        # Transistores
        if data.get('transistors'):
            self.sql_parts.append("\n-- DATOS: TRANSISTORES")
            for t in data['transistors']:
                self.sql_parts.append(
                    f"INSERT INTO comp_transistors (part_number, device_type, package, application) "
                    f"VALUES ('{t['part_number']}', '{t.get('device_type', 'BJT_NPN')}', '{t.get('package', 'TO-92')}', '{t.get('application', 'GENERAL')}');"
                )
        
        # Diodos
        if data.get('diodes'):
            self.sql_parts.append("\n-- DATOS: DIODOS")
            for d in data['diodes']:
                self.sql_parts.append(
                    f"INSERT INTO comp_diodes (part_number, device_type, package) "
                    f"VALUES ('{d['part_number']}', '{d.get('device_type', 'RECTIFIER')}', '{d.get('package', 'DO-41')}');"
                )

    def _add_admin_user(self):
        self.sql_parts.append("""
-- =====================================================================
-- USUARIO ADMIN POR DEFECTO (cambiar contraseña en producción)
-- =====================================================================
INSERT INTO users (email, username, password_hash, first_name, last_name, role_id, is_active, is_verified)
VALUES ('admin@cirujano.cl', 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/X4.G9HYFQhGQHKJPe', 
        'Administrador', 'Sistema', 1, 1, 1);

-- =====================================================================
-- FIN DEL SCRIPT
-- Ejecutar: sqlite3 cirujano.db < cirujano_database.sql
-- =====================================================================
""")


# ==============================================================================
# CLASE PRINCIPAL
# ==============================================================================

class CirujanoDatabaseGenerator:
    def __init__(self):
        self.excel_reader = ExcelReader(Config.EXCEL_PATH)
        self.sql_generator = SQLGenerator()
        self.consolidated_data = {}
    
    def run(self):
        print("=" * 70)
        print("CIRUJANO DE SINTETIZADORES - GENERADOR DE BASE DE DATOS")
        print("=" * 70)
        
        Path(Config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        Path(Config.JSON_DIR).mkdir(parents=True, exist_ok=True)
        
        print("\n[1/4] Leyendo Excel de inventario...")
        excel_data = self.excel_reader.read()
        print(f"      - Resistencias: {len(excel_data.get('resistors', []))}")
        print(f"      - Capacitores cerámicos: {len(excel_data.get('capacitors_ceramic', []))}")
        print(f"      - Capacitores electrolíticos: {len(excel_data.get('capacitors_electrolytic', []))}")
        print(f"      - ICs: {len(excel_data.get('integrated_circuits', []))}")
        print(f"      - Transistores: {len(excel_data.get('transistors', []))}")
        print(f"      - Diodos: {len(excel_data.get('diodes', []))}")
        
        self.consolidated_data = excel_data
        
        print("\n[2/4] Guardando JSONs para revisión...")
        for key, data in self.consolidated_data.items():
            if data:
                filepath = os.path.join(Config.JSON_DIR, f"{key}.json")
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                print(f"      ✓ {key}.json ({len(data)} items)")
        
        print("\n[3/4] Generando script SQL...")
        sql_content = self.sql_generator.generate(self.consolidated_data)
        
        print("\n[4/4] Guardando archivo SQL...")
        with open(Config.SQL_OUTPUT, 'w', encoding='utf-8') as f:
            f.write(sql_content)
        print(f"      ✓ {Config.SQL_OUTPUT}")
        
        print("\n" + "=" * 70)
        print("✅ GENERACIÓN COMPLETADA")
        print("=" * 70)
        print(f"\nArchivos en: {Config.OUTPUT_DIR}")
        print("\nPara ejecutar:")
        print("  sqlite3 cirujano.db < cirujano_database.sql")
        print("\nO abrir en DBeaver y ejecutar el script.")
        print("=" * 70)


if __name__ == "__main__":
    generator = CirujanoDatabaseGenerator()
    generator.run()

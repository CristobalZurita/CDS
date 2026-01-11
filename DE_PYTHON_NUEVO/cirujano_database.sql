-- =====================================================================
-- CIRUJANO DE SINTETIZADORES - BASE DE DATOS PROFESIONAL
-- Generado: 2026-01-06 00:45:33
-- Motor: SQLite
-- =====================================================================

PRAGMA foreign_keys = ON;
PRAGMA encoding = 'UTF-8';


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


-- DATOS: RESISTENCIAS
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (0.33, '0.33Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (0.5, '0.50Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (0.6, '0.60Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (1.0, '1Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (1.2, '1.20Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (1.3, '1.30Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (1.5, '1.50Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (1.8, '1.80Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (2.0, '2Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (2.2, '2.20Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (2.4, '2.40Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (2.7, '2.70Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (3.0, '3Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (3.3, '3.30Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (3.6, '3.60Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (3.9, '3.90Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (4.3, '4.30Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (4.7, '4.70Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (5.1, '5.10Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (5.6, '5.60Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (6.2, '6.20Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (6.8, '6.80Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (7.5, '7.50Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (8.2, '8.20Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (9.1, '9.10Ω', 5.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (10.0, '10Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (11.0, '11Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (12.0, '12Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (15.0, '15Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (18.0, '18Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (20.0, '20Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (21.0, '21Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (22.0, '22Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (24.0, '24Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (27.0, '27Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (30.0, '30Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (33.0, '33Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (36.0, '36Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (39.0, '39Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (43.0, '43Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (47.0, '47Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (51.0, '51Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (56.0, '56Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (62.0, '62Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (68.0, '68Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (75.0, '75Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (82.0, '82Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (91.0, '91Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (100.0, '100Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (110.0, '110Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (120.0, '120Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (130.0, '130Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (150.0, '150Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (160.0, '160Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (180.0, '180Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (200.0, '200Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (220.0, '220Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (240.0, '240Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (270.0, '270Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (300.0, '300Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (330.0, '330Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (360.0, '360Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (390.0, '390Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (430.0, '430Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (470.0, '470Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (510.0, '510Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (560.0, '560Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (620.0, '620Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (680.0, '680Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (750.0, '750Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (820.0, '820Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (825.0, '825Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (845.0, '845Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (910.0, '910Ω', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (1000.0, '1kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (1100.0, '1.10kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (1200.0, '1.20kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (1500.0, '1.50kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (1600.0, '1.60kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (1800.0, '1.80kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (2000.0, '2kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (2200.0, '2.20kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (2400.0, '2.40kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (2700.0, '2.70kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (3000.0, '3kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (3300.0, '3.30kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (3600.0, '3.60kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (3900.0, '3.90kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (4300.0, '4.30kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (4700.0, '4.70kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (4900.0, '4.90kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (5100.0, '5.10kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (5600.0, '5.60kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (6200.0, '6.20kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (6800.0, '6.80kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (7500.0, '7.50kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (7870.0, '7.87kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (8200.0, '8.20kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (9100.0, '9.10kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (10000.0, '10kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (11000.0, '11kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (12000.0, '12kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (13000.0, '13kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (15000.0, '15kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (16000.0, '16kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (16200.0, '16.20kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (18000.0, '18kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (20000.0, '20kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (22000.0, '22kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (24000.0, '24kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (27000.0, '27kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (30000.0, '30kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (33000.0, '33kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (34600.0, '34.60kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (36000.0, '36kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (39000.0, '39kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (43000.0, '43kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (47000.0, '47kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (51000.0, '51kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (53000.0, '53kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (56000.0, '56kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (62000.0, '62kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (63400.0, '63.40kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (68000.0, '68kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (68100.0, '68.10kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (75000.0, '75kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (82000.0, '82kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (91000.0, '91kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (100000.0, '100kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (110000.0, '110kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (120000.0, '120kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (127000.0, '127kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (130000.0, '130kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (150000.0, '150kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (160000.0, '160kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (180000.0, '180kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (200000.0, '200kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (220000.0, '220kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (240000.0, '240kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (270000.0, '270kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (300000.0, '300kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (330000.0, '330kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (360000.0, '360kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (390000.0, '390kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (430000.0, '430kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (470000.0, '470kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (510000.0, '510kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (560000.0, '560kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (620000.0, '620kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (680000.0, '680kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (750000.0, '750kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (820000.0, '820kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (910000.0, '910kΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (1000000.0, '1MΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (1200000.0, '1.20MΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (1500000.0, '1.50MΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (1800000.0, '1.80MΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (2200000.0, '2.20MΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (2400000.0, '2.40MΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (3000000.0, '3MΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (3300000.0, '3.30MΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (3900000.0, '3.90MΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (4700000.0, '4.70MΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (5100000.0, '5.10MΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (5600000.0, '5.60MΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (6800000.0, '6.80MΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (8200000.0, '8.20MΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');
INSERT INTO comp_resistors (value_ohms, display_value, tolerance_percent, power_watts, technology, package) VALUES (10000000.0, '10MΩ', 1.0, 0.25, 'METAL_FILM', 'TH_AXIAL');

-- DATOS: CAPACITORES CERÁMICOS
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (1e-06, '1.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (2e-06, '2.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (3e-06, '3.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (4e-06, '4.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (4.9999999999999996e-06, '5.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (6e-06, '6.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (7e-06, '7.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (8e-06, '8.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (9e-06, '9.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (9.999999999999999e-06, '10.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (1.4999999999999999e-05, '15.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (1.8e-05, '18.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (1.9999999999999998e-05, '20.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (2.2e-05, '22.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (2.7e-05, '27.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (2.9999999999999997e-05, '30.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (3.2999999999999996e-05, '33.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (3.9999999999999996e-05, '40.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (4.7e-05, '47.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (4.9999999999999996e-05, '50.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (5.6e-05, '56.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (5.9999999999999995e-05, '60.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (6.8e-05, '68.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (7.5e-05, '75.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (8.2e-05, '82.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (9.999999999999999e-05, '100.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000101, '101.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000102, '102.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000103, '103.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000104, '104.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00010499999999999999, '105.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000106, '106.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000121, '121.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00014099999999999998, '141.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00015, '150.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00015099999999999998, '151.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00015199999999999998, '152.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000153, '153.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000154, '154.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00018099999999999998, '181.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00020099999999999998, '201.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000202, '202.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000203, '203.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00021999999999999998, '220.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00022099999999999998, '221.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000222, '222.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000223, '223.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000224, '224.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000254, '254.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000271, '271.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00027299999999999997, '273.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.0003, '300.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00030399999999999996, '304.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00033099999999999997, '331.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000332, '332.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00033299999999999996, '333.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000334, '334.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000385, '385.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00044199999999999996, '442.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00047, '470.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.00047099999999999996, '471.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000472, '472.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000473, '473.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000474, '474.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000561, '561.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000562, '562.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.0005639999999999999, '564.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.0006039999999999999, '604.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000681, '681.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000682, '682.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000683, '683.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000821, '821.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.0008219999999999999, '822.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, package) VALUES (0.000823, '823.0µF', 25.0, 'CERAMIC', 'TH_RADIAL');

-- DATOS: CAPACITORES ELECTROLÍTICOS
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (1e-07, '0.1µF', 25.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (2.1999999999999998e-07, '0.22µF', 25.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (4.6999999999999995e-07, '0.47µF', 25.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (6.800000000000001e-07, '0.68µF', 25.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (1e-06, '1.0µF', 25.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (2e-06, '2.0µF', 25.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (2.2e-06, '2.2µF', 25.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (3.2999999999999997e-06, '3.3µF', 25.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (4.7e-06, '4.7µF', 25.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (6.799999999999999e-06, '6.8µF', 25.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (9.999999999999999e-06, '10.0µF', 25.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (2.2e-05, '22.0µF', 25.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (3.2999999999999996e-05, '33.0µF', 25.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (4.7e-05, '47.0µF', 25.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (9.999999999999999e-05, '100.0µF', 25.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (0.00021999999999999998, '220.0µF', 16.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (0.001, '1000.0µF', 16.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (0.0033, '3300.0µF', 16.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');
INSERT INTO comp_capacitors (value_farads, display_value, voltage_volts, dielectric, polarized, package, temperature_rating) VALUES (0.0047, '4700.0µF', 16.0, 'ELECTROLYTIC_AL', 1, 'TH_RADIAL', '105C');

-- DATOS: CIRCUITOS INTEGRADOS
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('12320VH25V', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('12F629', 'MCU', 'Microchip', 'PIC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('16F628', 'MCU', 'Microchip', 'PIC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('16F648', 'MCU', 'Microchip', 'PIC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('16F684', 'MCU', 'Microchip', 'PIC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('16F84', 'MCU', 'Microchip', 'PIC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('16F877', 'MCU', 'Microchip', 'PIC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('16F88', 'MCU', 'Microchip', 'PIC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('16F886', 'MCU', 'Microchip', 'PIC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('16F887', 'MCU', 'Microchip', 'PIC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('18F4520', 'MCU', 'Microchip', 'PIC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('18F4550', 'MCU', 'Microchip', 'PIC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('24LC04', 'MEMORY', 'Various', 'EEPROM');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('24LC16', 'MEMORY', 'Various', 'EEPROM');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('44LS157', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('4N25', 'OPTOCOUPLER', 'Various', 'OPTO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('4N26', 'OPTOCOUPLER', 'Various', 'OPTO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('4N36', 'OPTOCOUPLER', 'Various', 'OPTO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('5218A', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('6N137', 'OPTOCOUPLER', 'Various', 'OPTO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('74HC04', 'LOGIC_TTL', 'Various', '74_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('74HC132', 'LOGIC_TTL', 'Various', '74_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('74HC138', 'LOGIC_TTL', 'Various', '74_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('74HC14', 'LOGIC_TTL', 'Various', '74_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('74HC154', 'LOGIC_TTL', 'Various', '74_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('74HC245', 'LOGIC_TTL', 'Various', '74_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('74HC373', 'LOGIC_TTL', 'Various', '74_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('74HC4051', 'LOGIC_TTL', 'Various', '74_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('74HC75', 'LOGIC_TTL', 'Various', '74_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('74LS04', 'LOGIC_TTL', 'Various', '74_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('74LS08', 'LOGIC_TTL', 'Various', '74_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('74LS14', 'LOGIC_TTL', 'Various', '74_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('74LS48', 'LOGIC_TTL', 'Various', '74_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('7555', 'TIMER', 'Various', '555');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('7660', 'DC_CONVERTER', 'Various', 'CHARGE_PUMP');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('AC3105I', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('AK4318', 'AUDIO_IC', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('AK4526VQ', 'AUDIO_IC', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('AN7147N', 'AUDIO_IC', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('ATMEGA328P', 'MCU', 'Microchip/Atmel', 'AVR');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('ATTINY2313', 'MCU', 'Microchip/Atmel', 'AVR');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('ATTINY4313', 'MCU', 'Microchip/Atmel', 'AVR');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('BA5417', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CA3046', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CA3080', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD14538', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD40106', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD40109', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4011', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4013', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4015', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4016', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4017', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4020', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4027', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4029', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4040', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4047', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4049', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4051', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4052', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4053', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4060', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4066', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4067', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4069', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4072', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4073', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4081', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4093', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4094', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CD4096', 'LOGIC_CMOS', 'Various', '4000_SERIES');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('CPH6302', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('D41416C', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('D72064LM', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('DG412', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('FT232RL', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('FW828', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('HJ238', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('HT8950', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('JCR4556', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('JCR4558', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('JCR4560', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('JCR4565', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('JCR4580', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('JRC2903', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('KA2206', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('KA2535', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LA4227', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM051A', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM13600', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM13700', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM1496', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM1881', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM2574', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM311', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM324', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM339', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM3578AN', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM358', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM386', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM3900', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM393', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM394', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM741', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LM831N', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LNK3046N', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LT8304', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('LV125A', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('MAX1044', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('MAX232', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('MB81C4526A', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('MC1489', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('MCP4822', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('MCP6004', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('MOC3021', 'OPTOCOUPLER', 'Various', 'OPTO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('MP1470GJ', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('MX7528', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('NE5532', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('NE5534', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('NE555', 'TIMER', 'Various', '555');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('NE556', 'TIMER', 'Various', '555');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('NE567', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('NJM2374', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('NNC6.2MG-T1', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('OB2269CP', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('OP07', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('OPA2137PA', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('P721F', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('PC2581V', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('PCA9532', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('PT2399', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('RN5RG33AA', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('RRL025P03TR', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('SM76489AN', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('SN74157', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('SN74173', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('SN7517', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('SN75176', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('SN75240W', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('SN75441', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('SN754410', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TDA2822M', 'AUDIO_IC', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TDA7294', 'AUDIO_IC', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TDA9108', 'AUDIO_IC', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TEA2025', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TGA2025', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('THAT1646', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TL071', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TL072', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TL074', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TL082', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TL084', 'OP_AMP', 'Various', 'AUDIO');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TLC2272', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TLC5940', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TMS4145', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TPS54240DGQR', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TPS5430', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TPS7A3401DGNR', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TSB41AB2', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('TUSB3200', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('UC3843', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('UL26', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('UMG9NTR (G9)', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('USB3343', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('V54C3256164VDI7', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('VA220M', 'GENERAL', 'Unknown', 'MISC');
INSERT INTO comp_integrated_circuits (part_number, function_type, manufacturer, family) VALUES ('WOOA', 'GENERAL', 'Unknown', 'MISC');

-- DATOS: TRANSISTORES
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('20N60', 'MOSFET_N', 'TO-220', 'POWER');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2387A', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2N222', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2N2907', 'BJT_PNP', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2N3904', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2N3906', 'BJT_PNP', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2N4401', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2N5087', 'BJT_PNP', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2N5088', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2N5089', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2N5401', 'BJT_PNP', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2N5457', 'JFET_N', 'TO-92', 'AUDIO');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2N5458', 'JFET_N', 'TO-92', 'AUDIO');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2N5460', 'JFET_P', 'TO-92', 'AUDIO');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2N5551', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2N6111G', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2SA1037AK (FR)', 'BJT_PNP', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2SC2060', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2SC4207-Y', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('2SK30A', 'JFET_N', 'TO-92', 'AUDIO');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('742669095252 (K2-2)', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('A1015', 'BJT_PNP', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('A1273', 'BJT_PNP', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('A42', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('A933', 'BJT_PNP', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('AZ1117', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('B1342', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('B1568', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('B772P', 'BJT_PNP', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('B824', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BC327', 'BJT_PNP', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BC337', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BC517', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BC547', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BC548', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BC549', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BC550', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BC556', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BC557', 'BJT_PNP', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BC558', 'BJT_PNP', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BC847PN', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BD138', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BD438', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BD651', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BS170', 'MOSFET_N', 'TO-220', 'POWER');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BT136', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BT137', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BTA10', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BTA12', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BTA16', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('BZT52C5V6 (W9)', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('C1740', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('C18158', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('C2655', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('C3199', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('C3421-Y', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('C4408', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('C945', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('D313', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('EL817', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('IRF1010', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('IRF4227', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('IRF540NS', 'MOSFET_N', 'TO-220', 'POWER');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('IRF630', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('IRF634', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('J112', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('J113', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('J175', 'JFET_P', 'TO-92', 'AUDIO');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('J201', 'JFET_N', 'TO-92', 'AUDIO');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('K163', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('K246', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('LL2705', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('LM2576', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('LM2596', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('LM317', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('LM334', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('LM337', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('LM35', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('MBR20100', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('MIC29302', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('MPF102', 'JFET_N', 'TO-92', 'AUDIO');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('MPSA13', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('MPSA18', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('MUR1620R6', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('OGBCON', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('P20N06', 'MOSFET_N', 'TO-220', 'POWER');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('P20N60', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('PQ10621H', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('R6775', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('S8050', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('S8550', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('S9012', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('S9013', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('S9014', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('S9015', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('SK3050', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('SRF2060L', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('SS13J532R', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('TF8N80', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('TL431A', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('TOP224YN', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('TSF1060M', 'BJT_NPN', 'TO-92', 'GENERAL');
INSERT INTO comp_transistors (part_number, device_type, package, application) VALUES ('TSP73801DCQR', 'BJT_NPN', 'TO-92', 'GENERAL');

-- DATOS: DIODOS
INSERT INTO comp_diodes (part_number, device_type, package) VALUES ('1SS367', 'SIGNAL', 'DO-35');
INSERT INTO comp_diodes (part_number, device_type, package) VALUES ('BZT52C11 (WG)', 'ZENER', 'DO-35');
INSERT INTO comp_diodes (part_number, device_type, package) VALUES ('MBR0540W', 'SCHOTTKY', 'DO-41');

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

#!/usr/bin/env python3
"""
Build an additive KiCad-oriented component catalog from current CDS sources.

Goals:
- Keep existing inventory data as source of truth (`origin_status=REAL`).
- Expand catalog with commercial references (`origin_status=CATALOGO_ONLY`).
- Use KiCad/JEDEC/EIA style fields for OT/inventory workflows.
- Do not overwrite existing source JSON files.

Outputs:
- DE_PYTHON_NUEVO/json/kicad_component_catalog.json
- DE_PYTHON_NUEVO/json/kicad_component_catalog_summary.json
"""

from __future__ import annotations

import argparse
import json
import math
import re
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = REPO_ROOT / "DE_PYTHON_NUEVO" / "json"
OUTPUT_CATALOG = INPUT_DIR / "kicad_component_catalog.json"
OUTPUT_SUMMARY = INPUT_DIR / "kicad_component_catalog_summary.json"
DEFAULT_MANUAL_EXTENSIONS = INPUT_DIR / "manual_inventory_extensions.txt"

E24_VALUES = (
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1,
)

E96_VALUES = (
    1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30,
    1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
    1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32,
    2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
    3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12,
    4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
    5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32,
    7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76,
)


def load_json_array(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, list) else []


def sanitize_part_code(value: str, max_len: int = 96) -> str:
    code = re.sub(r"[^A-Z0-9._-]", "", str(value).upper().strip())
    code = re.sub(r"-{2,}", "-", code).strip("-._")
    if not code:
        code = "UNSPECIFIED"
    return code[:max_len]


def slugify_name(value: str, max_len: int = 72) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").upper()
    text = re.sub(r"-{2,}", "-", text)
    if not text:
        text = "ITEM"
    return text[:max_len]


def normalize_key(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", "", text.lower())
    return text


def _format_with_unit(num: float, unit: str) -> str:
    if abs(num - int(num)) < 1e-9:
        return f"{int(num)}{unit}"
    text = f"{num:.3f}".rstrip("0").rstrip(".")
    return f"{text}{unit}"


def format_ohms(value_ohms: float) -> str:
    if value_ohms >= 1_000_000:
        return _format_with_unit(value_ohms / 1_000_000, "MOhm")
    if value_ohms >= 1_000:
        return _format_with_unit(value_ohms / 1_000, "kOhm")
    return _format_with_unit(value_ohms, "Ohm")


def to_iec_60062_code(value_ohms: float) -> str:
    if value_ohms >= 1_000_000:
        scaled = value_ohms / 1_000_000
        marker = "M"
    elif value_ohms >= 1_000:
        scaled = value_ohms / 1_000
        marker = "K"
    else:
        scaled = value_ohms
        marker = "R"

    if abs(scaled - int(scaled)) < 1e-9:
        return f"{int(scaled)}{marker}"

    text = f"{scaled:.3f}".rstrip("0").rstrip(".")
    return text.replace(".", marker)


def normalize_ohms(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if parsed <= 0:
        return None
    return round(parsed, 6)


def normalize_farads(value: Any) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if parsed <= 0:
        return None
    return round(parsed, 12)


def format_capacitance(value_farads: float) -> str:
    value_pf = value_farads * 1e12
    if value_pf >= 1_000_000:
        return _format_with_unit(value_pf / 1_000_000, "uF")
    if value_pf >= 1_000:
        return _format_with_unit(value_pf / 1_000, "nF")
    return _format_with_unit(value_pf, "pF")


def to_capacitance_code(value_farads: float) -> str:
    value_pf = value_farads * 1e12
    if value_pf >= 1_000_000:
        scaled = value_pf / 1_000_000
        marker = "U"
    elif value_pf >= 1_000:
        scaled = value_pf / 1_000
        marker = "N"
    else:
        scaled = value_pf
        marker = "P"

    if abs(scaled - int(scaled)) < 1e-9:
        return f"{int(scaled)}{marker}"

    text = f"{scaled:.3f}".rstrip("0").rstrip(".")
    return text.replace(".", marker)


def compute_series_values(
    base_values: tuple[float, ...],
    min_value: float,
    max_value: float,
    decade_min: int,
    decade_max: int,
) -> list[float]:
    out: set[float] = set()
    for decade in range(decade_min, decade_max + 1):
        scale = math.pow(10, decade)
        for base in base_values:
            value = round(base * scale, 9)
            if min_value <= value <= max_value:
                out.add(value)
    return sorted(out)


def ensure_target_values(
    existing: set[float],
    target: int,
    primary: list[float],
    secondary: list[float],
    precision: int = 6,
) -> list[float]:
    values: list[float] = sorted(existing)
    seen = set(values)

    for candidate in primary:
        if len(values) >= target:
            break
        rounded = round(candidate, precision)
        if rounded not in seen:
            values.append(rounded)
            seen.add(rounded)

    for candidate in secondary:
        if len(values) >= target:
            break
        rounded = round(candidate, precision)
        if rounded not in seen:
            values.append(rounded)
            seen.add(rounded)

    return sorted(values)[:target]


def build_resistors(existing_rows: list[dict[str, Any]], target: int) -> list[dict[str, Any]]:
    existing_values = {
        value
        for row in existing_rows
        for value in [normalize_ohms(row.get("value_ohms"))]
        if value is not None
    }

    primary = compute_series_values(
        base_values=E24_VALUES,
        min_value=0.1,
        max_value=10_000_000,
        decade_min=-1,
        decade_max=6,
    )
    secondary = compute_series_values(
        base_values=E96_VALUES,
        min_value=0.1,
        max_value=10_000_000,
        decade_min=-1,
        decade_max=6,
    )
    values = ensure_target_values(existing_values, target, primary, secondary, precision=6)
    results: list[dict[str, Any]] = []

    for value in values:
        iec_code = to_iec_60062_code(value)
        origin = "REAL" if value in existing_values else "CATALOGO_ONLY"
        sku = sanitize_part_code(f"RES-{iec_code}-THT-AXIAL-0P25W")
        results.append(
            {
                "family": "resistors",
                "kicad_sku": sku,
                "display_name": f"Resistor {iec_code} 1/4W",
                "origin_status": origin,
                "enabled": origin == "REAL",
                "source": "excel_inventory" if origin == "REAL" else "commercial_e_series",
                "kicad_symbol": "Device:R",
                "kicad_footprint_default": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
                "kicad_footprint_options": [
                    "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
                    "Resistor_SMD:R_0805_2012Metric",
                    "Resistor_SMD:R_0603_1608Metric",
                ],
                "specs": {
                    "value_ohms": value,
                    "display_value": format_ohms(value),
                    "value_code_iec60062": iec_code,
                    "technology": "METAL_FILM",
                    "power_watts": 0.25,
                    "tolerance_percent": 1.0 if value >= 10 else 5.0,
                    "package_code": "AXIAL_THT",
                    "jedec_package_options": ["AXIAL_THT", "0603", "0805"],
                },
            }
        )

    return results


def build_ceramic_caps(existing_rows: list[dict[str, Any]], target: int) -> list[dict[str, Any]]:
    existing_values = {
        value
        for row in existing_rows
        for value in [normalize_farads(row.get("value_farads"))]
        if value is not None
    }
    primary_pf = compute_series_values(
        base_values=E24_VALUES,
        min_value=1.0,
        max_value=10_000_000.0,
        decade_min=0,
        decade_max=6,
    )
    secondary_pf = compute_series_values(
        base_values=E96_VALUES,
        min_value=1.0,
        max_value=10_000_000.0,
        decade_min=0,
        decade_max=6,
    )
    primary = [round(v * 1e-12, 12) for v in primary_pf]
    secondary = [round(v * 1e-12, 12) for v in secondary_pf]
    values = ensure_target_values(existing_values, target, primary, secondary, precision=12)
    results: list[dict[str, Any]] = []

    for value in values:
        code = to_capacitance_code(value)
        origin = "REAL" if value in existing_values else "CATALOGO_ONLY"
        sku = sanitize_part_code(f"CAPC-{code}-X7R")
        results.append(
            {
                "family": "capacitors_ceramic",
                "kicad_sku": sku,
                "display_name": f"Capacitor ceramico {format_capacitance(value)}",
                "origin_status": origin,
                "enabled": origin == "REAL",
                "source": "excel_inventory" if origin == "REAL" else "commercial_e_series",
                "kicad_symbol": "Device:C",
                "kicad_footprint_default": "Capacitor_SMD:C_0805_2012Metric",
                "kicad_footprint_options": [
                    "Capacitor_SMD:C_0805_2012Metric",
                    "Capacitor_SMD:C_0603_1608Metric",
                    "Capacitor_THT:C_Disc_D5.0mm_W2.5mm_P5.00mm",
                ],
                "specs": {
                    "value_farads": value,
                    "display_value": format_capacitance(value),
                    "value_code_iec60062": code,
                    "dielectric": "CERAMIC_X7R",
                    "voltage_volts_default": 50.0,
                    "voltage_options_volts": [16.0, 25.0, 50.0, 100.0],
                    "package_code": "SMD_0805",
                    "jedec_package_options": ["0805", "0603", "RADIAL_DISC"],
                },
            }
        )
    return results


def build_electrolytic_caps(existing_rows: list[dict[str, Any]], target: int) -> list[dict[str, Any]]:
    existing_keys: set[tuple[float, float]] = set()
    for row in existing_rows:
        value = normalize_farads(row.get("value_farads"))
        if value is None:
            continue
        voltage = row.get("voltage_volts")
        try:
            voltage_value = float(voltage) if voltage is not None else 25.0
        except (TypeError, ValueError):
            voltage_value = 25.0
        existing_keys.add((value, round(voltage_value, 1)))

    value_uf = [
        0.47, 1.0, 2.2, 3.3, 4.7, 6.8, 10.0, 15.0, 22.0, 33.0,
        47.0, 68.0, 100.0, 150.0, 220.0, 330.0, 470.0, 680.0, 1000.0,
        1500.0, 2200.0, 3300.0, 4700.0, 6800.0, 10000.0, 15000.0, 22000.0,
    ]
    voltages = [6.3, 10.0, 16.0, 25.0, 35.0, 50.0, 63.0, 100.0]

    candidates: list[tuple[float, float]] = []
    for uf in value_uf:
        for voltage in voltages:
            candidates.append((round(uf * 1e-6, 12), voltage))
    candidates.sort(key=lambda item: (item[0], item[1]))

    values: list[tuple[float, float]] = sorted(existing_keys)
    seen = set(values)
    for candidate in candidates:
        if len(values) >= target:
            break
        if candidate not in seen:
            values.append(candidate)
            seen.add(candidate)

    values = sorted(values)[:target]
    results: list[dict[str, Any]] = []
    for farads, voltage in values:
        code = to_capacitance_code(farads)
        origin = "REAL" if (farads, voltage) in existing_keys else "CATALOGO_ONLY"
        sku = sanitize_part_code(f"CAPE-{code}-{str(voltage).replace('.', 'P')}V")
        results.append(
            {
                "family": "capacitors_electrolytic",
                "kicad_sku": sku,
                "display_name": f"Capacitor electrolitico {format_capacitance(farads)} {voltage}V",
                "origin_status": origin,
                "enabled": origin == "REAL",
                "source": "excel_inventory" if origin == "REAL" else "commercial_standard_values",
                "kicad_symbol": "Device:CP",
                "kicad_footprint_default": "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm",
                "kicad_footprint_options": [
                    "Capacitor_THT:CP_Radial_D6.3mm_P2.50mm",
                    "Capacitor_THT:CP_Radial_D8.0mm_P3.50mm",
                    "Capacitor_SMD:CP_Elec_6.3x5.4",
                ],
                "specs": {
                    "value_farads": farads,
                    "display_value": format_capacitance(farads),
                    "value_code_iec60062": code,
                    "voltage_volts": voltage,
                    "temperature_rating": "105C",
                    "dielectric": "ELECTROLYTIC_AL",
                    "polarized": True,
                    "package_code": "RADIAL_THT",
                    "jedec_package_options": ["RADIAL_THT", "SMD_CAN"],
                },
            }
        )
    return results


def diode_candidates() -> list[str]:
    out: list[str] = []

    out.extend(
        [
            "1N4148", "LL4148", "1N914", "BAV99", "BAV70", "BAV21",
            "BAS16", "BAS21", "BAS70", "BAT41", "BAT43", "BAT46",
            "BAT54", "BAT54A", "BAT54C", "BAT54S", "1SS133", "1SS355",
            "MMBD4148", "MMBD914",
        ]
    )

    out.extend([f"1N400{i}" for i in range(1, 8)])
    out.extend([f"UF400{i}" for i in range(1, 8)])
    out.extend([f"FR10{i}" for i in range(1, 8)])
    out.extend([f"HER10{i}" for i in range(1, 9)])
    out.extend([f"1N540{i}" for i in range(0, 9)])
    out.extend([f"1N58{i}" for i in range(17, 20)])
    out.extend([f"1N58{i}" for i in range(20, 23)])

    zener_codes = [
        "2V4", "2V7", "3V0", "3V3", "3V6", "3V9", "4V3", "4V7",
        "5V1", "5V6", "6V2", "6V8", "7V5", "8V2", "9V1", "10", "11",
        "12", "13", "15", "16", "18", "20", "22", "24", "27", "30",
        "33", "36", "39", "43", "47", "51", "56", "62", "68", "75",
        "82", "91", "100", "110", "120", "130", "150", "180", "200",
    ]
    out.extend([f"BZX55C{code}" for code in zener_codes])
    out.extend([f"BZT52C{code}" for code in zener_codes])

    tvs_codes = [
        "5.0", "5.6", "6.0", "6.8", "7.5", "8.2", "9.0", "10", "12", "13",
        "15", "16", "18", "20", "22", "24", "26", "28", "30", "33", "36",
        "40", "43", "48", "51", "58",
    ]
    out.extend([f"SMBJ{code}A" for code in tvs_codes])
    out.extend([f"SMCJ{code}A" for code in tvs_codes])

    # Preserve order and uniqueness
    seen: set[str] = set()
    deduped: list[str] = []
    for item in out:
        up = sanitize_part_code(item)
        if up and up not in seen:
            deduped.append(up)
            seen.add(up)
    return deduped


def classify_diode(part_number: str) -> dict[str, Any]:
    pn = part_number.upper()
    device_type = "RECTIFIER"
    package = "DO-41"
    symbol = "Device:D"
    footprint = "Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal"

    if pn.startswith(("BZX55", "BZT52")):
        device_type = "ZENER"
        symbol = "Device:D_Zener"
        if pn.startswith("BZT52"):
            package = "SOD-123"
            footprint = "Diode_SMD:D_SOD-123"
        else:
            package = "DO-35"
            footprint = "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"
    elif pn.startswith(("SMBJ", "SMCJ")):
        device_type = "TVS"
        symbol = "Device:D_TVS"
        package = "SMB" if pn.startswith("SMBJ") else "SMC"
        footprint = "Diode_SMD:D_SMB" if pn.startswith("SMBJ") else "Diode_SMD:D_SMC"
    elif pn.startswith(("BAV", "BAS", "BAT", "MMBD")) or pn in {"BAT54A", "BAT54C", "BAT54S"}:
        device_type = "SIGNAL" if pn.startswith(("BAV", "BAS", "MMBD")) else "SCHOTTKY"
        package = "SOT-23"
        symbol = "Device:D_Schottky" if device_type == "SCHOTTKY" else "Device:D"
        footprint = "Package_TO_SOT_SMD:SOT-23"
    elif pn.startswith(("1N58", "SS")):
        device_type = "SCHOTTKY"
        symbol = "Device:D_Schottky"
    elif pn.startswith(("1N4148", "LL4148", "1N914", "1SS")):
        device_type = "SIGNAL"
        symbol = "Device:D"
        package = "DO-35"
        footprint = "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal"

    return {
        "device_type": device_type,
        "package_code": package,
        "kicad_symbol": symbol,
        "kicad_footprint_default": footprint,
    }


def build_diodes(existing_rows: list[dict[str, Any]], target: int) -> list[dict[str, Any]]:
    existing_parts = {
        sanitize_part_code(row.get("part_number", ""))
        for row in existing_rows
        if row.get("part_number")
    }
    existing_parts.discard("UNSPECIFIED")

    values: list[str] = sorted(existing_parts)
    seen = set(values)
    for seed in diode_candidates():
        if len(values) >= target:
            break
        if seed not in seen:
            values.append(seed)
            seen.add(seed)
    values = sorted(values)[:target]

    results: list[dict[str, Any]] = []
    for part in values:
        meta = classify_diode(part)
        origin = "REAL" if part in existing_parts else "CATALOGO_ONLY"
        results.append(
            {
                "family": "diodes",
                "kicad_sku": sanitize_part_code(f"DIO-{part}"),
                "display_name": part,
                "part_number": part,
                "origin_status": origin,
                "enabled": origin == "REAL",
                "source": "excel_inventory" if origin == "REAL" else "commercial_mpn_list",
                "kicad_symbol": meta["kicad_symbol"],
                "kicad_footprint_default": meta["kicad_footprint_default"],
                "kicad_footprint_options": [
                    meta["kicad_footprint_default"],
                    "Package_TO_SOT_SMD:SOT-23",
                    "Diode_SMD:D_SOD-123",
                ],
                "specs": {
                    "device_type": meta["device_type"],
                    "package_code": meta["package_code"],
                },
            }
        )
    return results


def transistor_candidates() -> list[dict[str, str]]:
    seed = [
        {"part_number": "2N3904", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "2N3906", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "2N2222A", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "2N2907A", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "2N4401", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "2N4403", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "2N5551", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "2N5401", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "2N5088", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "2N5087", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "BC337", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "BC327", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "BC547", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "BC557", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "BC548", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "BC558", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "BC549", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "BC559", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "BD135", "device_type": "BJT_NPN", "package_code": "TO-126"},
        {"part_number": "BD136", "device_type": "BJT_PNP", "package_code": "TO-126"},
        {"part_number": "BD139", "device_type": "BJT_NPN", "package_code": "TO-126"},
        {"part_number": "BD140", "device_type": "BJT_PNP", "package_code": "TO-126"},
        {"part_number": "TIP31C", "device_type": "BJT_NPN", "package_code": "TO-220"},
        {"part_number": "TIP32C", "device_type": "BJT_PNP", "package_code": "TO-220"},
        {"part_number": "TIP41C", "device_type": "BJT_NPN", "package_code": "TO-220"},
        {"part_number": "TIP42C", "device_type": "BJT_PNP", "package_code": "TO-220"},
        {"part_number": "TIP120", "device_type": "BJT_NPN_DARLINGTON", "package_code": "TO-220"},
        {"part_number": "TIP122", "device_type": "BJT_NPN_DARLINGTON", "package_code": "TO-220"},
        {"part_number": "TIP127", "device_type": "BJT_PNP_DARLINGTON", "package_code": "TO-220"},
        {"part_number": "MJE340", "device_type": "BJT_NPN", "package_code": "TO-126"},
        {"part_number": "MJE350", "device_type": "BJT_PNP", "package_code": "TO-126"},
        {"part_number": "MPSA42", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "MPSA92", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "MPSA06", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "MPSA56", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "KSA992", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "KSC1845", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "KSA733", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "KSC945", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "2SA1015", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "2SC1815", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "2SA733", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "2SC945", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "2SB772", "device_type": "BJT_PNP", "package_code": "TO-126"},
        {"part_number": "2SD882", "device_type": "BJT_NPN", "package_code": "TO-126"},
        {"part_number": "2N7000", "device_type": "MOSFET_N", "package_code": "TO-92"},
        {"part_number": "2N7002", "device_type": "MOSFET_N", "package_code": "SOT-23"},
        {"part_number": "BSS138", "device_type": "MOSFET_N", "package_code": "SOT-23"},
        {"part_number": "BSS84", "device_type": "MOSFET_P", "package_code": "SOT-23"},
        {"part_number": "BS170", "device_type": "MOSFET_N", "package_code": "TO-92"},
        {"part_number": "BS250", "device_type": "MOSFET_P", "package_code": "TO-92"},
        {"part_number": "AO3400A", "device_type": "MOSFET_N", "package_code": "SOT-23"},
        {"part_number": "AO3401A", "device_type": "MOSFET_P", "package_code": "SOT-23"},
        {"part_number": "SI2302", "device_type": "MOSFET_N", "package_code": "SOT-23"},
        {"part_number": "SI2301", "device_type": "MOSFET_P", "package_code": "SOT-23"},
        {"part_number": "IRF3205", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "IRF540N", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "IRF9540N", "device_type": "MOSFET_P", "package_code": "TO-220"},
        {"part_number": "IRFZ44N", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "IRLZ44N", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "IRL540N", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "IRF510", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "IRF520", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "IRF530", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "IRF630", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "IRF640", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "IRF740", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "IRF840", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "IRLZ34N", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "IRL3705N", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "STP55NF06", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "STP36NF06", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "BUZ11", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "BUZ71", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "P55NF06", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "VN10KM", "device_type": "MOSFET_N", "package_code": "TO-92"},
        {"part_number": "VN2222L", "device_type": "MOSFET_N", "package_code": "TO-92"},
        {"part_number": "BF245A", "device_type": "JFET_N", "package_code": "TO-92"},
        {"part_number": "BF245B", "device_type": "JFET_N", "package_code": "TO-92"},
        {"part_number": "2N3819", "device_type": "JFET_N", "package_code": "TO-92"},
        {"part_number": "J201", "device_type": "JFET_N", "package_code": "TO-92"},
        {"part_number": "J310", "device_type": "JFET_N", "package_code": "TO-92"},
        {"part_number": "2N5457", "device_type": "JFET_N", "package_code": "TO-92"},
        {"part_number": "2N5460", "device_type": "JFET_P", "package_code": "TO-92"},
        {"part_number": "A1015", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "C1815", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "C945", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "A733", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "D882", "device_type": "BJT_NPN", "package_code": "TO-126"},
        {"part_number": "B772", "device_type": "BJT_PNP", "package_code": "TO-126"},
        {"part_number": "D667", "device_type": "BJT_NPN", "package_code": "TO-126"},
        {"part_number": "B647", "device_type": "BJT_PNP", "package_code": "TO-126"},
        {"part_number": "FQP30N06L", "device_type": "MOSFET_N", "package_code": "TO-220"},
        {"part_number": "FQP27P06", "device_type": "MOSFET_P", "package_code": "TO-220"},
        {"part_number": "PN2222A", "device_type": "BJT_NPN", "package_code": "TO-92"},
        {"part_number": "PN2907A", "device_type": "BJT_PNP", "package_code": "TO-92"},
        {"part_number": "MMBT3904", "device_type": "BJT_NPN", "package_code": "SOT-23"},
        {"part_number": "MMBT3906", "device_type": "BJT_PNP", "package_code": "SOT-23"},
        {"part_number": "MMBT2222A", "device_type": "BJT_NPN", "package_code": "SOT-23"},
        {"part_number": "MMBT2907A", "device_type": "BJT_PNP", "package_code": "SOT-23"},
        {"part_number": "MMBT4401", "device_type": "BJT_NPN", "package_code": "SOT-23"},
        {"part_number": "MMBT4403", "device_type": "BJT_PNP", "package_code": "SOT-23"},
        {"part_number": "BC847", "device_type": "BJT_NPN", "package_code": "SOT-23"},
        {"part_number": "BC857", "device_type": "BJT_PNP", "package_code": "SOT-23"},
        {"part_number": "BC846", "device_type": "BJT_NPN", "package_code": "SOT-23"},
        {"part_number": "BC856", "device_type": "BJT_PNP", "package_code": "SOT-23"},
        {"part_number": "BC846B", "device_type": "BJT_NPN", "package_code": "SOT-23"},
        {"part_number": "BC856B", "device_type": "BJT_PNP", "package_code": "SOT-23"},
        {"part_number": "BC817", "device_type": "BJT_NPN", "package_code": "SOT-23"},
        {"part_number": "BC807", "device_type": "BJT_PNP", "package_code": "SOT-23"},
        {"part_number": "S8050", "device_type": "BJT_NPN", "package_code": "SOT-23"},
        {"part_number": "S8550", "device_type": "BJT_PNP", "package_code": "SOT-23"},
        {"part_number": "A42", "device_type": "BJT_NPN", "package_code": "SOT-23"},
        {"part_number": "A92", "device_type": "BJT_PNP", "package_code": "SOT-23"},
        {"part_number": "MMBT5551", "device_type": "BJT_NPN", "package_code": "SOT-23"},
        {"part_number": "MMBT5401", "device_type": "BJT_PNP", "package_code": "SOT-23"},
        {"part_number": "MMBTA42", "device_type": "BJT_NPN", "package_code": "SOT-23"},
        {"part_number": "MMBTA92", "device_type": "BJT_PNP", "package_code": "SOT-23"},
    ]
    deduped: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in seed:
        pn = sanitize_part_code(item["part_number"])
        if pn in seen:
            continue
        deduped.append(
            {
                "part_number": pn,
                "device_type": item["device_type"],
                "package_code": item["package_code"],
            }
        )
        seen.add(pn)
    return deduped


def infer_transistor_type(part_number: str) -> str:
    pn = part_number.upper()
    if any(key in pn for key in ("IRF", "IRL", "FQP", "AO34", "SI23", "2N700", "BSS", "BS1", "BS2")):
        return "MOSFET_N"
    if any(key in pn for key in ("9540", "3401", "SI2301", "BS250", "BSS84")):
        return "MOSFET_P"
    if any(key in pn for key in ("3906", "2907", "327", "557", "558", "559", "A92", "PNP", "2SA", "2SB", "KSA")):
        return "BJT_PNP"
    return "BJT_NPN"


def footprint_for_package(package_code: str) -> str:
    mapping = {
        "TO-92": "Package_TO_SOT_THT:TO-92_Inline",
        "TO-126": "Package_TO_SOT_THT:TO-126-3_Vertical",
        "TO-220": "Package_TO_SOT_THT:TO-220-3_Vertical",
        "SOT-23": "Package_TO_SOT_SMD:SOT-23",
    }
    return mapping.get(package_code, "Package_TO_SOT_THT:TO-92_Inline")


def symbol_for_transistor(device_type: str) -> str:
    if device_type.startswith("MOSFET_P"):
        return "Device:Q_PMOS_GDS"
    if device_type.startswith("MOSFET"):
        return "Device:Q_NMOS_GDS"
    if "PNP" in device_type:
        return "Device:Q_PNP_BCE"
    return "Device:Q_NPN_BCE"


def build_transistors(existing_rows: list[dict[str, Any]], target: int) -> list[dict[str, Any]]:
    existing_map: dict[str, dict[str, Any]] = {}
    for row in existing_rows:
        pn = sanitize_part_code(row.get("part_number", ""))
        if not pn or pn == "UNSPECIFIED":
            continue
        existing_map[pn] = {
            "device_type": row.get("device_type") or infer_transistor_type(pn),
            "package_code": row.get("package") or "TO-92",
        }

    values = sorted(existing_map.keys())
    seen = set(values)
    for seed in transistor_candidates():
        if len(values) >= target:
            break
        pn = seed["part_number"]
        if pn not in seen:
            values.append(pn)
            seen.add(pn)
    values = sorted(values)[:target]

    seed_lookup = {s["part_number"]: s for s in transistor_candidates()}
    results: list[dict[str, Any]] = []
    for part in values:
        if part in existing_map:
            device_type = sanitize_part_code(existing_map[part]["device_type"])
            package_code = sanitize_part_code(existing_map[part]["package_code"])
            origin = "REAL"
        else:
            seed = seed_lookup.get(part, {})
            device_type = sanitize_part_code(seed.get("device_type", infer_transistor_type(part)))
            package_code = sanitize_part_code(seed.get("package_code", "TO-92"))
            origin = "CATALOGO_ONLY"
        footprint = footprint_for_package(package_code)
        results.append(
            {
                "family": "transistors",
                "kicad_sku": sanitize_part_code(f"Q-{part}"),
                "display_name": part,
                "part_number": part,
                "origin_status": origin,
                "enabled": origin == "REAL",
                "source": "excel_inventory" if origin == "REAL" else "commercial_mpn_list",
                "kicad_symbol": symbol_for_transistor(device_type),
                "kicad_footprint_default": footprint,
                "kicad_footprint_options": [
                    footprint,
                    "Package_TO_SOT_SMD:SOT-23",
                    "Package_TO_SOT_THT:TO-92_Inline",
                ],
                "specs": {
                    "device_type": device_type,
                    "package_code": package_code,
                },
            }
        )
    return results


def classify_ic(part_number: str) -> dict[str, str]:
    pn = part_number.upper()
    if pn.startswith(("TL0", "NE55", "LM3", "OP", "NJM", "JRC", "OPA", "AD8", "UA741")):
        return {"function_type": "OP_AMP", "family": "ANALOG"}
    if pn.startswith(("CD40", "74HC", "74LS")):
        return {"function_type": "LOGIC", "family": "DIGITAL_LOGIC"}
    if pn.startswith(("PIC", "16F", "12F", "18F", "ATMEGA", "ATTINY")):
        return {"function_type": "MCU", "family": "MICROCONTROLLER"}
    if pn.startswith(("24LC", "93C", "W25", "M27", "27C", "28C", "29F")):
        return {"function_type": "MEMORY", "family": "EEPROM_FLASH"}
    if pn.startswith(("L78", "L79", "LM317", "LM337", "AMS1117", "TL431", "MC34063")):
        return {"function_type": "POWER", "family": "REGULATOR_CONVERTER"}
    if pn.startswith(("TDA", "LA", "PCM", "WM", "AK", "CS", "PT2399")):
        return {"function_type": "AUDIO", "family": "AUDIO_IC"}
    return {"function_type": "GENERAL", "family": "MISC"}


def ic_candidates() -> list[str]:
    out = [
        "TL071", "TL072", "TL074", "TL082", "TL084", "NE5532", "NJM4558", "JRC4558",
        "LM358", "LM324", "LM339", "LM393", "LM311", "LM833", "OP07", "OPA2134",
        "OPA2604", "AD823", "AD620", "UA741", "NE555", "ICM7555", "CD40106",
        "CD4049", "CD4050", "CD4066", "CD4013", "CD4027", "CD4051", "CD4052",
        "CD4053", "74HC00", "74HC04", "74HC14", "74HC32", "74HC74", "74HC86",
        "74HC138", "74HC595", "74LS00", "74LS04", "74LS14", "74LS86", "ATMEGA328P",
        "ATMEGA32A", "ATTINY85", "PIC16F628A", "PIC16F877A", "24LC256", "24LC64",
        "93C46", "93C66", "W25Q32", "W25Q64", "M27C256B", "27C512", "28C64", "29F040",
        "MAX232", "MAX3232", "FT232RL", "CH340G", "L7805", "L7812", "L7912", "LM317T",
        "LM337T", "AMS1117-5.0", "AMS1117-3.3", "TL431", "MC34063A", "TDA2030A",
        "TDA7297", "LA4440", "PT2399", "PCM5102A", "WM8731", "AK4556", "CS4344",
        "SG3525A", "UC3842", "TL494",
    ]
    deduped: list[str] = []
    seen: set[str] = set()
    for item in out:
        pn = sanitize_part_code(item)
        if pn not in seen:
            deduped.append(pn)
            seen.add(pn)
    return deduped


def build_ics(existing_rows: list[dict[str, Any]], target: int) -> list[dict[str, Any]]:
    existing_map: dict[str, dict[str, str]] = {}
    for row in existing_rows:
        pn = sanitize_part_code(row.get("part_number", ""))
        if not pn or pn == "UNSPECIFIED":
            continue
        existing_map[pn] = {
            "function_type": sanitize_part_code(row.get("function_type", "GENERAL")),
            "family": sanitize_part_code(row.get("family", "MISC")),
        }

    values = sorted(existing_map.keys())
    seen = set(values)
    for seed in ic_candidates():
        if len(values) >= target:
            break
        if seed not in seen:
            values.append(seed)
            seen.add(seed)
    values = sorted(values)[:target]

    results: list[dict[str, Any]] = []
    for part in values:
        if part in existing_map:
            function_type = existing_map[part]["function_type"]
            family = existing_map[part]["family"]
            origin = "REAL"
        else:
            inferred = classify_ic(part)
            function_type = sanitize_part_code(inferred["function_type"])
            family = sanitize_part_code(inferred["family"])
            origin = "CATALOGO_ONLY"

        results.append(
            {
                "family": "integrated_circuits",
                "kicad_sku": sanitize_part_code(f"IC-{part}"),
                "display_name": part,
                "part_number": part,
                "origin_status": origin,
                "enabled": origin == "REAL",
                "source": "excel_inventory" if origin == "REAL" else "commercial_mpn_list",
                "kicad_symbol": "Device:U",
                "kicad_footprint_default": "Package_DIP:DIP-8_W7.62mm",
                "kicad_footprint_options": [
                    "Package_DIP:DIP-8_W7.62mm",
                    "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm",
                    "Package_TO_SOT_SMD:SOT-223-3_TabPin2",
                ],
                "specs": {
                    "function_type": function_type,
                    "family": family,
                    "package_code": "DIP_OR_SMD",
                },
            }
        )
    return results


def infer_manual_profile(name: str) -> dict[str, str]:
    n = normalize_key(name)

    profile = {
        "family": "manual_inventory",
        "prefix": "MAN",
        "kicad_symbol": "Device:U",
        "kicad_footprint_default": "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
        "category_hint": "otros",
    }

    if any(token in n for token in ("resistencia", "resistor", "trimpot", "potenciometro", "fader", "encoder", "sip", "dip16")):
        profile.update(
            {
                "family": "resistors",
                "prefix": "RES",
                "kicad_symbol": "Device:R",
                "kicad_footprint_default": "Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P7.62mm_Horizontal",
                "category_hint": "Resistencias",
            }
        )
    elif any(token in n for token in ("capacitor", "electrolitico", "mlcc", "cristal", "resonador", "snubber", "supercapacitor", "x2", "y2")):
        profile.update(
            {
                "family": "capacitors_misc",
                "prefix": "CAPX",
                "kicad_symbol": "Device:C",
                "kicad_footprint_default": "Capacitor_SMD:C_0805_2012Metric",
                "category_hint": "Capacitores",
            }
        )
    elif any(token in n for token in ("diodo", "zener", "tvs", "schottky", "led", "puenterectificador", "1n", "uf", "fr", "her", "mur", "oa90", "laser")):
        profile.update(
            {
                "family": "diodes",
                "prefix": "DIO",
                "kicad_symbol": "Device:D",
                "kicad_footprint_default": "Diode_THT:D_DO-35_SOD27_P7.62mm_Horizontal",
                "category_hint": "Diodos",
            }
        )
    elif any(token in n for token in ("transistor", "mosfet", "igbt", "jfet", "tip", "bc", "2n", "2sc", "2sa", "irf", "irl", "ao340", "uln")):
        profile.update(
            {
                "family": "transistors",
                "prefix": "Q",
                "kicad_symbol": "Device:Q_NPN_BCE",
                "kicad_footprint_default": "Package_TO_SOT_THT:TO-92_Inline",
                "category_hint": "Transistores",
            }
        )
    elif any(
        token in n
        for token in (
            "74hc", "cd40", "eeprom", "flash", "sram", "atmega", "pic", "stm32",
            "esp32", "esp8266", "lm", "tl", "ne", "njm", "opa", "tda", "stk", "pcm",
            "adc", "mcp", "max", "rc4558", "jrc", "icl", "xr2206", "ams1117", "ld1117",
            "7805", "7809", "7812", "7912", "78l05", "78l12", "lm2596", "lm2576", "mt3608",
        )
    ):
        profile.update(
            {
                "family": "integrated_circuits",
                "prefix": "IC",
                "kicad_symbol": "Device:U",
                "kicad_footprint_default": "Package_DIP:DIP-8_W7.62mm",
                "category_hint": "Ic's",
            }
        )
    elif any(token in n for token in ("sensor", "ntc", "ptc", "ldr", "lm35", "ds18b20", "hall", "tsop", "mq2", "acs712", "microfono", "piezo")):
        profile.update(
            {
                "family": "sensors",
                "prefix": "SEN",
                "kicad_symbol": "Device:U",
                "kicad_footprint_default": "Package_TO_SOT_THT:TO-92_Inline",
                "category_hint": "sensores",
            }
        )
    elif any(token in n for token in ("jack", "rca", "xlr", "din5", "usb", "rj45", "header", "jst", "molex", "bornera", "faston", "idc")):
        profile.update(
            {
                "family": "connectors",
                "prefix": "CON",
                "kicad_symbol": "Connector:Conn_01x02",
                "kicad_footprint_default": "Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical",
                "category_hint": "conectores",
            }
        )
    elif any(token in n for token in ("rele", "optoacoplador", "triac", "scr", "diac", "moc")):
        profile.update(
            {
                "family": "power_control",
                "prefix": "PWR",
                "kicad_symbol": "Device:U",
                "kicad_footprint_default": "Package_DIP:DIP-6_W7.62mm",
                "category_hint": "potencia_control",
            }
        )
    elif any(token in n for token in ("inductor", "bobina", "choque", "fusible", "portafusible", "polyfuse", "varistor")):
        profile.update(
            {
                "family": "magnetics_protection",
                "prefix": "MAG",
                "kicad_symbol": "Device:L",
                "kicad_footprint_default": "Inductor_THT:L_Axial_L9.0mm_D4.0mm_P15.24mm_Horizontal",
                "category_hint": "pasivos_potencia",
            }
        )
    elif any(token in n for token in ("disipador", "pasta", "aislador", "separador", "tornillo", "tuerca", "arandela", "protoboard", "placa", "cable")):
        profile.update(
            {
                "family": "workshop_misc",
                "prefix": "HW",
                "kicad_symbol": "Mechanical:MountingHole",
                "kicad_footprint_default": "MountingHole:MountingHole_3.2mm_M3",
                "category_hint": "taller_misc",
            }
        )

    return profile


def load_manual_extensions(path: Path | None) -> list[str]:
    if not path:
        return []
    if not path.exists():
        return []
    lines: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def merge_manual_extensions(catalog: dict[str, Any], extensions: list[str]) -> dict[str, int]:
    if not extensions:
        return {"requested": 0, "added": 0, "skipped_existing": 0}

    existing_name_keys = {
        normalize_key(str(item.get("display_name", "")))
        for item in catalog.get("items", [])
        if item.get("display_name")
    }
    existing_skus = {
        str(item.get("kicad_sku", "")).strip().upper()
        for item in catalog.get("items", [])
        if item.get("kicad_sku")
    }

    added = 0
    skipped = 0
    for extension in extensions:
        key = normalize_key(extension)
        if not key:
            continue
        if key in existing_name_keys:
            skipped += 1
            continue

        profile = infer_manual_profile(extension)
        slug = slugify_name(extension)
        base_sku = sanitize_part_code(f"{profile['prefix']}-{slug}")
        sku = base_sku
        idx = 2
        while sku in existing_skus:
            sku = sanitize_part_code(f"{base_sku}-{idx}")
            idx += 1

        part_number = sanitize_part_code(extension)
        if part_number == "UNSPECIFIED":
            part_number = None

        item = {
            "family": profile["family"],
            "kicad_sku": sku,
            "display_name": extension,
            "part_number": part_number,
            "origin_status": "REAL",
            "enabled": True,
            "source": "manual_user_extension",
            "kicad_symbol": profile["kicad_symbol"],
            "kicad_footprint_default": profile["kicad_footprint_default"],
            "kicad_footprint_options": [profile["kicad_footprint_default"]],
            "specs": {
                "category_hint": profile["category_hint"],
                "manual_extension": True,
            },
        }

        catalog["families"].setdefault(profile["family"], []).append(item)
        catalog["items"].append(item)
        existing_name_keys.add(key)
        existing_skus.add(sku)
        added += 1

    return {
        "requested": len(extensions),
        "added": added,
        "skipped_existing": skipped,
    }


def build_catalog(
    target_resistors: int,
    target_caps_ceramic: int,
    target_caps_electrolytic: int,
    target_diodes: int,
    target_transistors: int,
    target_ics: int,
    manual_extensions_file: Path | None = None,
) -> dict[str, Any]:
    resistor_rows = load_json_array(INPUT_DIR / "resistors.json")
    ceramic_rows = load_json_array(INPUT_DIR / "capacitors_ceramic.json")
    electrolytic_rows = load_json_array(INPUT_DIR / "capacitors_electrolytic.json")
    diode_rows = load_json_array(INPUT_DIR / "diodes.json")
    transistor_rows = load_json_array(INPUT_DIR / "transistors.json")
    ic_rows = load_json_array(INPUT_DIR / "integrated_circuits.json")

    families: dict[str, list[dict[str, Any]]] = {
        "resistors": build_resistors(resistor_rows, target_resistors),
        "capacitors_ceramic": build_ceramic_caps(ceramic_rows, target_caps_ceramic),
        "capacitors_electrolytic": build_electrolytic_caps(electrolytic_rows, target_caps_electrolytic),
        "diodes": build_diodes(diode_rows, target_diodes),
        "transistors": build_transistors(transistor_rows, target_transistors),
        "integrated_circuits": build_ics(ic_rows, target_ics),
    }

    all_items: list[dict[str, Any]] = []
    for entries in families.values():
        all_items.extend(entries)

    manual_extensions_rel = None
    if manual_extensions_file:
        try:
            manual_extensions_rel = str(manual_extensions_file.relative_to(REPO_ROOT))
        except Exception:
            manual_extensions_rel = str(manual_extensions_file)

    catalog = {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "mode": "aditivo_no_destructivo",
            "source_files": {
                "resistors": str((INPUT_DIR / "resistors.json").relative_to(REPO_ROOT)),
                "capacitors_ceramic": str((INPUT_DIR / "capacitors_ceramic.json").relative_to(REPO_ROOT)),
                "capacitors_electrolytic": str((INPUT_DIR / "capacitors_electrolytic.json").relative_to(REPO_ROOT)),
                "diodes": str((INPUT_DIR / "diodes.json").relative_to(REPO_ROOT)),
                "transistors": str((INPUT_DIR / "transistors.json").relative_to(REPO_ROOT)),
                "integrated_circuits": str((INPUT_DIR / "integrated_circuits.json").relative_to(REPO_ROOT)),
                "manual_extensions": manual_extensions_rel,
            },
            "targets": {
                "resistors": target_resistors,
                "capacitors_ceramic": target_caps_ceramic,
                "capacitors_electrolytic": target_caps_electrolytic,
                "diodes": target_diodes,
                "transistors": target_transistors,
                "integrated_circuits": target_ics,
            },
        },
        "families": families,
        "items": all_items,
    }

    manual_extensions = load_manual_extensions(manual_extensions_file)
    catalog["meta"]["manual_extensions"] = merge_manual_extensions(catalog, manual_extensions)
    return catalog


def build_summary(catalog: dict[str, Any]) -> dict[str, Any]:
    family_summary: dict[str, dict[str, int]] = {}
    for family, items in catalog["families"].items():
        real_count = sum(1 for item in items if item.get("origin_status") == "REAL")
        catalog_only_count = sum(1 for item in items if item.get("origin_status") == "CATALOGO_ONLY")
        enabled_count = sum(1 for item in items if bool(item.get("enabled")))
        family_summary[family] = {
            "total": len(items),
            "real": real_count,
            "catalog_only": catalog_only_count,
            "enabled": enabled_count,
        }

    return {
        "generated_at": catalog["meta"]["generated_at"],
        "mode": catalog["meta"]["mode"],
        "targets": catalog["meta"]["targets"],
        "manual_extensions": catalog["meta"].get("manual_extensions", {}),
        "families": family_summary,
        "total_items": len(catalog.get("items", [])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build KiCad-oriented component catalog")
    parser.add_argument("--target-resistors", type=int, default=250)
    parser.add_argument("--target-caps-ceramic", type=int, default=200)
    parser.add_argument("--target-caps-electrolytic", type=int, default=160)
    parser.add_argument("--target-diodes", type=int, default=120)
    parser.add_argument("--target-transistors", type=int, default=180)
    parser.add_argument("--target-ics", type=int, default=220)
    parser.add_argument("--extensions-file", type=str, default=str(DEFAULT_MANUAL_EXTENSIONS))
    args = parser.parse_args()

    extensions_file = Path(args.extensions_file).expanduser() if args.extensions_file else None
    catalog = build_catalog(
        target_resistors=max(1, args.target_resistors),
        target_caps_ceramic=max(1, args.target_caps_ceramic),
        target_caps_electrolytic=max(1, args.target_caps_electrolytic),
        target_diodes=max(1, args.target_diodes),
        target_transistors=max(1, args.target_transistors),
        target_ics=max(1, args.target_ics),
        manual_extensions_file=extensions_file,
    )
    summary = build_summary(catalog)

    OUTPUT_CATALOG.write_text(json.dumps(catalog, indent=2, ensure_ascii=True), encoding="utf-8")
    OUTPUT_SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding="utf-8")

    print(f"Wrote {OUTPUT_CATALOG} ({len(catalog.get('items', []))} items)")
    print(f"Wrote {OUTPUT_SUMMARY}")
    for family, stats in summary["families"].items():
        print(
            f"- {family}: total={stats['total']} real={stats['real']} "
            f"catalog_only={stats['catalog_only']} enabled={stats['enabled']}"
        )
    me = summary.get("manual_extensions") or {}
    if me:
        print(
            f"- manual_extensions: requested={me.get('requested', 0)} "
            f"added={me.get('added', 0)} skipped_existing={me.get('skipped_existing', 0)}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

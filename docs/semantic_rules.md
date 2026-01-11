# Semantic mapping rules (POC)

Estas son las reglas iniciales para mapear columnas del Excel maestro a la semántica y destino en la BD.

- `Resistencias` -> semantic: `resistor` -> table: `items` (normalize numeric values, unit=Ohm)
- `Capacitores Ceramicos` -> `capacitor_ceramic` -> `items` (validate unit/values)
- `Capacitores Electrolíticos` -> `capacitor_electrolytic` -> `items` (clean '10NP' style codes)
- `Transistores` -> `transistor` -> `items` (match against lookup, normalize part_number)
- `Ic's` -> `ic` -> `items` (use lookup for known ICs, otherwise keep raw id)
- `Diodos`, `Diodo Led` -> `diode` / `led` -> `items` (split multi-value cells)
- `otros` -> `other` -> `items` (free text, apply tokenization)

Reglas operativas:
- No borrar o modificar el Excel original en `Inventario_Cirujanosintetizadores.xlsx`.
- Todas las transformaciones deben ser idempotentes y registradas en `import_runs` con `run_id`.
- Las columnas multi-value deben registrarse en tablas relacionadas (ej: `item_tags` o `item_variants`).

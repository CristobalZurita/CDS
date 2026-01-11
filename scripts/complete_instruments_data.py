#!/usr/bin/env python3
"""
Script para completar datos faltantes en instruments.json
Especialmente valor_estimado, year, description basados en tier de marca
"""

import json
import sys

# Valores estimados por tier (rango en CLP)
TIER_RANGES = {
    'legendary': {
        'min': 2000000,
        'max': 8000000,
        'description': 'Sintetizador legendario profesional'
    },
    'professional': {
        'min': 1000000,
        'max': 4000000,
        'description': 'Sintetizador profesional'
    },
    'standard': {
        'min': 300000,
        'max': 1500000,
        'description': 'Sintetizador estándar'
    },
    'specialized': {
        'min': 400000,
        'max': 2000000,
        'description': 'Sintetizador especializado'
    },
    'boutique': {
        'min': 500000,
        'max': 3000000,
        'description': 'Sintetizador boutique'
    },
    'historic': {
        'min': 1500000,
        'max': 5000000,
        'description': 'Sintetizador histórico vintage'
    }
}

YEAR_BY_TIER = {
    'legendary': 1975,
    'professional': 1985,
    'standard': 1995,
    'specialized': 2000,
    'boutique': 2005,
    'historic': 1980
}

def load_files():
    """Cargar JSONs"""
    with open('src/assets/data/instruments.json', 'r', encoding='utf-8') as f:
        instruments_data = json.load(f)
    
    with open('src/assets/data/brands.json', 'r', encoding='utf-8') as f:
        brands_data = json.load(f)
    
    # Crear dict de marcas por ID
    brands = {b['id']: b for b in brands_data['brands']}
    
    return instruments_data, brands

def complete_instruments(instruments_data, brands):
    """Completar datos faltantes"""
    instruments = instruments_data['instruments']
    
    changes = {
        'valor_added': 0,
        'description_added': 0,
        'year_added': 0
    }
    
    for instr in instruments:
        brand_id = instr.get('brand')
        brand = brands.get(brand_id)
        
        if not brand:
            print(f"⚠ Marca no encontrada: {brand_id}")
            continue
        
        tier = brand.get('tier', 'standard')
        range_data = TIER_RANGES.get(tier, TIER_RANGES['standard'])
        
        # Completar valor_estimado
        if not instr.get('valor_estimado') or instr['valor_estimado'].get('min') is None:
            instr['valor_estimado'] = {
                'min': range_data['min'],
                'max': range_data['max'],
                'moneda': 'CLP'
            }
            changes['valor_added'] += 1
        
        # Completar description
        if not instr.get('description') or not str(instr.get('description', '')).strip():
            instr['description'] = f"{range_data['description']} {instr.get('model', '')}"
            changes['description_added'] += 1
        
        # Completar year
        if not instr.get('year'):
            instr['year'] = YEAR_BY_TIER.get(tier, 2000)
            changes['year_added'] += 1
    
    return instruments_data, changes

def save_file(data, filename):
    """Guardar JSON con formato bonito"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ Guardado: {filename}")

def main():
    print("📋 Completando datos de instrumentos...\n")
    
    # Cargar
    instruments_data, brands = load_files()
    print(f"✓ Cargados {len(instruments_data['instruments'])} instrumentos")
    print(f"✓ Cargadas {len(brands)} marcas\n")
    
    # Procesar
    instruments_data, changes = complete_instruments(instruments_data, brands)
    
    # Guardar
    save_file(instruments_data, 'src/assets/data/instruments.json')
    
    # Reporte
    print(f"\n📊 Cambios realizados:")
    print(f"  - valor_estimado completados: {changes['valor_added']}")
    print(f"  - descriptions completadas: {changes['description_added']}")
    print(f"  - years completados: {changes['year_added']}")
    print(f"\n✅ Listo!")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Escanea la base de datos SQLite para encontrar referencias a imágenes
Genera un reporte de qué imágenes se usan y su estado en Cloudinary
"""

import sqlite3
import json
import re
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).parent.parent / "cirujano.db"
IMAGE_MAPPING_PATH = Path(__file__).parent.parent / "image-mapping.json"


def get_db_connection():
    """Obtiene conexión a la BD."""
    try:
        return sqlite3.connect(DB_PATH)
    except Exception as e:
        print(f"❌ Error al conectar a la BD: {e}")
        return None


def load_image_mapping():
    """Carga el mapeo de imágenes."""
    try:
        with open(IMAGE_MAPPING_PATH, 'r') as f:
            mapping = json.load(f)
            # Crear diccionario por ruta local
            return {item['local']: item for item in mapping}
    except Exception as e:
        print(f"❌ Error al cargar image-mapping.json: {e}")
        return {}


def find_image_columns(cursor, table_name):
    """Encuentra columnas que podrían contener referencias a imágenes."""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    image_columns = []
    for col in columns:
        col_name = col[1].lower()
        # Buscar columnas con nombres relacionados a imágenes
        if any(keyword in col_name for keyword in ['image', 'photo', 'picture', 'icon', 'thumbnail', 'url', 'path', 'file']):
            image_columns.append(col[1])
    
    return image_columns


def scan_table_for_images(cursor, table_name, image_columns):
    """Escanea una tabla buscando referencias a imágenes."""
    if not image_columns:
        return []
    
    results = []
    
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        
        # Obtener nombres de columnas
        cursor.execute(f"PRAGMA table_info({table_name})")
        all_columns = [col[1] for col in cursor.fetchall()]
        
        for row in rows:
            row_dict = dict(zip(all_columns, row))
            
            for col in image_columns:
                value = row_dict.get(col)
                if value and isinstance(value, str):
                    # Buscar patrones de imagen
                    if any(ext in value.lower() for ext in ['.webp', '.png', '.jpg', '.jpeg', '.gif', '.svg']):
                        results.append({
                            'table': table_name,
                            'column': col,
                            'value': value,
                            'row_id': row_dict.get('id', 'unknown')
                        })
    except Exception as e:
        print(f"   ⚠️  Error escaneando {table_name}: {e}")
    
    return results


def categorize_image_path(path):
    """Categoriza una ruta de imagen."""
    if not path:
        return 'empty'
    
    path_lower = path.lower()
    
    if path.startswith('http'):
        if 'cloudinary' in path_lower:
            return 'cloudinary_url'
        return 'external_url'
    
    if path.startswith('/images/'):
        if '/instrumentos/' in path_lower:
            return 'local_instrumentos'
        if '/inventario/' in path_lower or '/INVENTARIO/' in path:
            return 'local_inventario'
        if '/calculadoras/' in path_lower:
            return 'local_calculadoras'
        if '/logo/' in path_lower:
            return 'local_logo'
        return 'local_other'
    
    if path.startswith('uploads/') or path.startswith('/uploads/'):
        return 'uploads'
    
    return 'unknown'


def main():
    print("=" * 80)
    print("🔍 ESCANEO DE BASE DE DATOS - REFERENCIAS A IMÁGENES")
    print("=" * 80)
    print()
    
    # Conectar a BD
    print("📂 Conectando a la base de datos...")
    conn = get_db_connection()
    if not conn:
        sys.exit(1)
    
    cursor = conn.cursor()
    
    # Cargar mapeo
    print("📂 Cargando mapeo de imágenes...")
    image_mapping = load_image_mapping()
    print(f"   {len(image_mapping)} imágenes en el mapeo")
    print()
    
    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"🗄️  Encontradas {len(tables)} tablas")
    print()
    
    # Escanear cada tabla
    all_images = []
    
    for table in tables:
        # Ignorar tablas del sistema
        if table.startswith('sqlite_'):
            continue
        
        image_columns = find_image_columns(cursor, table)
        
        if image_columns:
            print(f"📋 Escaneando {table}...")
            images = scan_table_for_images(cursor, table, image_columns)
            all_images.extend(images)
            if images:
                print(f"   ✅ {len(images)} referencias encontradas")
    
    print()
    print("=" * 80)
    print("📊 RESULTADOS DEL ESCANEO")
    print("=" * 80)
    print()
    
    # Categorizar
    categories = defaultdict(list)
    for img in all_images:
        category = categorize_image_path(img['value'])
        categories[category].append(img)
    
    # Mostrar estadísticas
    print("CATEGORÍAS DE IMÁGENES:")
    print("-" * 40)
    for category, items in sorted(categories.items()):
        print(f"  {category:25} : {len(items):4d} imágenes")
    
    print()
    print(f"TOTAL: {len(all_images)} referencias a imágenes")
    print()
    
    # Mostrar detalles de imágenes locales
    if categories['local_instrumentos'] or categories['local_inventario'] or categories['local_calculadoras']:
        print("=" * 80)
        print("📸 IMÁGENES LOCALES (que deben ir a Cloudinary):")
        print("=" * 80)
        print()
        
        for category in ['local_instrumentos', 'local_inventario', 'local_calculadoras', 'local_logo']:
            items = categories.get(category, [])
            if items:
                print(f"\n{category.upper()}:")
                print("-" * 40)
                
                unique_paths = set()
                for item in items:
                    path = item['value']
                    if path not in unique_paths:
                        unique_paths.add(path)
                        
                        # Verificar si está en el mapeo
                        in_mapping = path in image_mapping
                        status = "✅" if in_mapping else "❌"
                        
                        print(f"  {status} {path}")
                        
                        if in_mapping:
                            cloud_url = image_mapping[path].get('cloudinary', '')
                            # Verificar si la URL tiene formato correcto (con versión)
                            if '/v' in cloud_url and '/upload/v' in cloud_url:
                                print(f"      → URL correcta: {cloud_url[:60]}...")
                            else:
                                print(f"      → ⚠️ URL sin versión: {cloud_url[:60]}...")
    
    # Mostrar imágenes de uploads
    if categories['uploads']:
        print()
        print("=" * 80)
        print("📤 IMÁGENES EN UPLOADS (subidas por usuarios):")
        print("=" * 80)
        
        unique_paths = set(item['value'] for item in categories['uploads'])
        for path in sorted(unique_paths)[:20]:
            print(f"  - {path}")
        if len(unique_paths) > 20:
            print(f"  ... y {len(unique_paths) - 20} más")
    
    conn.close()
    
    print()
    print("=" * 80)
    print("✅ ESCANEO COMPLETADO")
    print("=" * 80)


if __name__ == "__main__":
    import sys
    main()

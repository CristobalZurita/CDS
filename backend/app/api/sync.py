"""
🎯 API ENDPOINT: /api/instruments/sync
Ejecuta automáticamente el script Python de sincronización

MÉTODOS:
- GET  /api/instruments/sync → obtener estado actual
- POST /api/instruments/sync?force=true → forzar resincronización

El backend ejecuta scripts/sync_instruments.py automáticamente
"""

from flask import Blueprint, jsonify, request
from pathlib import Path
import json
import subprocess
import sys

# Crear blueprint
sync_bp = Blueprint('sync', __name__, url_prefix='/api/instruments')

def get_project_root() -> Path:
    """Obtener raíz del proyecto"""
    return Path(__file__).parent.parent.parent

def run_sync_script(force: bool = False) -> dict:
    """Ejecuta el script de sincronización y retorna resultado"""
    
    project_root = get_project_root()
    script_path = project_root / 'scripts' / 'sync_instruments.py'
    json_path = project_root / 'src' / 'data' / 'instruments.json'
    
    try:
        # Construir comando
        cmd = [sys.executable, str(script_path)]
        if force:
            cmd.append('--force')
        
        # Ejecutar
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Verificar éxito
        if result.returncode != 0:
            return {
                'success': False,
                'error': f'Script error: {result.stderr}',
                'stdout': result.stdout
            }
        
        # Cargar JSON generado
        if json_path.exists():
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            return {
                'success': True,
                'data': data,
                'message': f'Sync complete: {data["total_fotos"]} photos, {data["total_bases"]} instruments',
                'stdout': result.stdout
            }
        else:
            return {
                'success': False,
                'error': 'JSON file not generated',
                'stdout': result.stdout
            }
            
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Sync script timeout (>30s)'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

@sync_bp.route('/sync', methods=['GET', 'POST'])
def sync_instruments():
    """
    Sincroniza instrumentos automáticamente
    
    GET /api/instruments/sync
    - Retorna estado actual sin forzar resincronización
    
    POST /api/instruments/sync?force=true
    - Fuerza resincronización incluso si no hay cambios
    """
    
    force = request.args.get('force', 'false').lower() == 'true'
    
    if request.method == 'GET':
        # Modo GET: solo cargar JSON sin ejecutar script
        project_root = get_project_root()
        json_path = project_root / 'src' / 'data' / 'instruments.json'
        
        if json_path.exists():
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            return jsonify({
                'success': True,
                'cached': True,
                'data': data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Instruments JSON not found'
            }), 404
    
    # POST: ejecutar sincronización
    result = run_sync_script(force=force)
    
    if result['success']:
        return jsonify({
            'success': True,
            'data': result['data'],
            'message': result['message']
        })
    else:
        return jsonify({
            'success': False,
            'error': result['error'],
            'stdout': result.get('stdout', '')
        }), 500

@sync_bp.route('/status', methods=['GET'])
def sync_status():
    """
    Obtiene estado de sincronización sin ejecutar nada
    Útil para verificar si el sistema está listo
    """
    
    project_root = get_project_root()
    json_path = project_root / 'src' / 'data' / 'instruments.json'
    metadata_path = project_root / 'src' / 'data' / '.sync_metadata.json'
    
    status = {
        'json_exists': json_path.exists(),
        'metadata_exists': metadata_path.exists()
    }
    
    if json_path.exists():
        with open(json_path, 'r') as f:
            data = json.load(f)
        status['total_instruments'] = len(data.get('instruments', []))
        status['total_photos'] = data.get('total_fotos', 0)
    
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        status['last_sync'] = metadata.get('last_sync')
        status['last_count'] = metadata.get('last_count')
    
    return jsonify({
        'success': True,
        'status': status
    })

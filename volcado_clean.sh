#!/bin/bash

# ==============================================================================
# VOLCADO OPTIMO PARA AUDITORIA - SIN BASURA
# Extrae solo codigo relevante, limpio, sin emojis
# ==============================================================================

WORK_DIR="/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front"
OUTPUT_FILE="$WORK_DIR/CODIGO_AUDITORIA.txt"

# Limpiar
> "$OUTPUT_FILE"

echo "=========================================="
echo "GENERANDO VOLCADO OPTIMIZADO"
echo "=========================================="
echo ""
echo "Directorio: $WORK_DIR"
echo "Salida: $OUTPUT_FILE"
echo ""

# ==============================================================================
# ENCABEZADO
# ==============================================================================
cat << 'EOF' > "$OUTPUT_FILE"
================================================================================
AUDITORIA DE CODIGO - PROYECTO COMPLETO
================================================================================

INSTRUCCIONES:
Analiza este codigo y determina:
1. Que hace el proyecto (proposito, funcionalidades)
2. Arquitectura y stack tecnologico
3. Vulnerabilidades de seguridad
4. Bugs potenciales
5. Malas practicas
6. Recomendaciones de mejora

================================================================================

EOF

# ==============================================================================
# FUNCION DE LIMPIEZA
# ==============================================================================
clean_file() {
  local file="$1"
  
  # Leer y limpiar
  cat "$file" | \
    # Quitar caracteres no-ASCII (emojis, etc)
    LC_ALL=C tr -cd '\11\12\15\40-\176' | \
    # Quitar lineas vacias multiples
    cat -s
}

# ==============================================================================
# EXTRACCION
# ==============================================================================
count=0

echo "Procesando archivos..."

find "$WORK_DIR" -type f \
  \( -name "*.py" -o \
     -name "*.vue" -o \
     -name "*.js" -o \
     -name "*.ts" -o \
     -name "*.jsx" -o \
     -name "*.tsx" -o \
     -name "package.json" -o \
     -name "vite.config.*" -o \
     -name "tsconfig.json" -o \
     -name "requirements.txt" -o \
     -name "*.toml" -o \
     -name "main.*" -o \
     -name "App.vue" -o \
     -name "index.*" \) \
  ! -path "*/node_modules/*" \
  ! -path "*/dist/*" \
  ! -path "*/build/*" \
  ! -path "*/.git/*" \
  ! -path "*/.vite/*" \
  ! -path "*/__pycache__/*" \
  ! -path "*/venv/*" \
  ! -path "*/env/*" \
  ! -path "*/coverage/*" \
  ! -path "*/CERVO/*" \
  ! -path "*/VIEJOS/*" \
  ! -path "*/VOLCADO/*" \
  ! -path "*/AUDITORIA/*" \
  ! -name "package-lock.json" \
  ! -name "yarn.lock" \
  ! -name "pnpm-lock.yaml" \
  ! -name "*.min.js" \
  ! -name "*.min.css" \
  ! -name "*.spec.js" \
  ! -name "*.test.js" \
  ! -name "*.spec.ts" \
  ! -name "*.test.ts" \
  -print0 2>/dev/null | sort -z | while IFS= read -r -d '' file; do
  
  # Verificar tamano (max 200KB)
  size=$(stat -c%s "$file" 2>/dev/null || echo 999999999)
  if [ "$size" -gt 204800 ]; then
    continue
  fi
  
  # Verificar que es archivo de texto
  if ! file "$file" 2>/dev/null | grep -qE "text|JSON|script|HTML|CSS|XML"; then
    continue
  fi
  
  # Ruta relativa
  rel="${file#$WORK_DIR/}"
  
  # Escribir
  {
    echo ""
    echo "================================================================================"
    echo "ARCHIVO: $rel"
    echo "================================================================================"
    echo ""
    clean_file "$file"
    echo ""
  } >> "$OUTPUT_FILE"
  
  count=$((count + 1))
  
  # Progreso
  if [ $((count % 10)) -eq 0 ]; then
    printf "Procesados: %d archivos\r" "$count"
  fi
  
  # Limite de seguridad (evitar archivos gigantes)
  if [ "$count" -ge 200 ]; then
    echo ""
    echo "LIMITE DE 200 ARCHIVOS ALCANZADO"
    break
  fi
done

# ==============================================================================
# ESTADISTICAS FINALES
# ==============================================================================
echo ""
echo ""

{
  echo ""
  echo "================================================================================"
  echo "ESTADISTICAS"
  echo "================================================================================"
  echo ""
  echo "Fecha: $(date '+%Y-%m-%d %H:%M:%S')"
  echo "Archivos procesados: $count"
  echo "Lineas totales: $(wc -l < "$OUTPUT_FILE")"
  echo ""
} >> "$OUTPUT_FILE"

# ==============================================================================
# RESUMEN
# ==============================================================================
size=$(du -h "$OUTPUT_FILE" | cut -f1)
lines=$(wc -l < "$OUTPUT_FILE")

echo "=========================================="
echo "COMPLETADO"
echo "=========================================="
echo "Archivo: $OUTPUT_FILE"
echo "Tamano: $size"
echo "Lineas: $lines"
echo "Archivos: $count"
echo ""
echo "SIGUIENTE PASO:"
echo "1. Abre el archivo y copialo"
echo "2. Pega en Claude con el prompt de auditoria"
echo ""

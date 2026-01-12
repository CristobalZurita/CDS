# Directorio de trabajo
WORK_DIR="/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN"

# Archivo de salida
OUTPUT_FILE="$WORK_DIR/VOLCADO_DOMINGO.md"

# Limpiar el archivo de salida si existe
> "$OUTPUT_FILE"

# Función para buscar y concatenar solo archivos de código
extract_text_files() {
  find "$WORK_DIR" -type f \
    ! -path "*/node_modules/*" \
    ! -path "*/dist/*" \
    ! -path "*/build/*" \
    ! -path "*/.git/*" \
    ! -path "*/__pycache__/*" \
    ! -path "*/uploads/*" \
    ! -path "*/image/*" \
    ! -path "*/reports/*" \
    ! -path "*/DE_PYTHON_NUEVO/*" \
    ! -path "*/DOCUMJENTOS_EXTRAS/*" \
    ! -path "*/public/images/*" \
    ! -path "*/src/assets/fonts/*" \
    ! -name "*.png" \
    ! -name "*.jpg" \
    ! -name "*.jpeg" \
    ! -name "*.webp" \
    ! -name "*.svg" \
    ! -name "*.gif" \
    ! -name "*.woff*" \
    ! -name "*.ttf" \
    ! -name "*.otf" \
    ! -name "*.pdf" \
    ! -name "*.xlsx" \
    ! -name "*.db" \
    ! -name "*.sqlite" \
    ! -name "package-lock.json" \
    ! -name "*.min.js" \
    ! -name "*.min.css" \
    ! -name "VOLCADO*.md" \
    ! -name "VOLCADO*.txt" \
    | while read -r file; do 
      if file "$file" | grep -q "text"; then
        cat "$file" >> "$OUTPUT_FILE"
        echo -e "\n\n" >> "$OUTPUT_FILE"
      fi
    done
}

# Ejecutar la función
extract_text_files

echo "Volcado completado en VOLCADO_DOMINGO.md"
du -h "$OUTPUT_FILE"

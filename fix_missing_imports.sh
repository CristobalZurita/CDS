#!/bin/bash

# Array de imports faltantes a comentar
declare -a missing=(
    "ContentLayer.vue"
    "ActivitySpinner.vue"
    "Navigation.vue"
    "PageSectionContent.vue"
    "BackgroundPromo.vue"
    "Divider.vue"
    "InlineLinkList.vue"
    "Spinner.vue"
)

for file in $(find src -name "*.vue" -o -name "*.js" | grep -v node_modules); do
    for missing_file in "${missing[@]}"; do
        # Comentar importaciones que contienen los archivos faltantes
        sed -i "s/^import \(.*\) from [\"']\(.*\)${missing_file}[\"']/\/\/ import \1 from '\2${missing_file}'/g" "$file"
    done
done

# También comentar composables faltantes
for composable in "settings" "utils" "layout" "scheduler" "emails"; do
    find src -name "*.vue" -o -name "*.js" | while read file; do
        sed -i "s/^import \(.*\) from [\"']@\/composables\/${composable}[\"']/\/\/ import \1 from '@\/composables\/${composable}'/g" "$file"
    done
done

# Comentar models faltantes
find src -name "*.vue" -o -name "*.js" | while read file; do
    sed -i "s/^import \(.*\) from [\"']@\/models\//\/\/ import \1 from '@\/models\//g" "$file"
done

echo "Imports comentados"

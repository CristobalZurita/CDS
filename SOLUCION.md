# SOLUCION

## Contexto

Los avisos del correo no vienen del entorno local. Vienen de GitHub Actions y de herramientas de seguridad del repositorio remoto `CristobalZurita/CDS`.

El problema principal visible en los correos es el workflow:

- `.github/workflows/sync-instruments.yml`

Además hay al menos un problema estructural en los workflows de seguridad:

- `.github/workflows/secret-scan.yml`
- `.github/workflows/security.yml`

Este informe deja por escrito los problemas detectados, la causa raíz y la solución recomendada.

---

## Problemas Confirmados

### 1. El workflow `Sincronizar Instrumentos Automáticamente` falla en remoto

**Archivo afectado**

- [.github/workflows/sync-instruments.yml](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/.github/workflows/sync-instruments.yml)

**Causa raíz**

El workflow ejecuta:

```bash
python3 scripts/auto_sync.py --once
python3 scripts/validate_instruments_sync.py --expected-fotos 249
```

Pero hoy el conteo real ya no es `249`.

En la revisión local:

- fotos reales en `public/images/instrumentos`: `273`
- último valor esperado hardcodeado en workflow: `249`

Resultado:

- el sync actualiza los datasets a `273`
- luego la validación sigue exigiendo `249`
- el job falla

**Impacto**

- correos repetidos de fallo
- el workflow seguirá fallando cada vez que corra
- el cron lo repite cada 6 horas

**Solución**

- dejar de validar contra un número fijo
- validar contra el estado real del directorio y el JSON generado

---

### 2. La validación actual de instrumentos es conceptualmente débil

**Archivo afectado**

- [scripts/validate_instruments_sync.py](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/scripts/validate_instruments_sync.py)

**Causa raíz**

El script no cuenta los archivos reales de `public/images/instrumentos`.

Lee:

- `src/data/instruments.json`
- `src/assets/data/instruments.json`

y valida los campos ya escritos en el JSON, por ejemplo:

- `validacion.fotos_en_carpeta`
- `validacion.fotos_en_json`

Eso significa que:

- si el JSON quedó viejo pero todavía dice `249`, la validación puede pasar
- aunque en la carpeta real ya existan `273` fotos

**Impacto**

- falso positivo de validación
- la validación depende de datos guardados antes, no del estado real en disco

**Solución**

- contar archivos reales en `public/images/instrumentos` dentro del propio script
- comparar:
  - carpeta real
  - JSON canónico
  - JSON legado

---

### 3. El script NPM de validación también quedó obsoleto

**Archivo afectado**

- [package.json](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/package.json)

**Script afectado**

```json
"validate:instruments": "python3 scripts/validate_instruments_sync.py --expected-fotos 249"
```

**Causa raíz**

El mismo valor fijo `249` quedó incrustado también en los scripts del proyecto.

**Impacto**

- cualquier ejecución manual o CI que use ese script arrastra el mismo error

**Solución**

- quitar el conteo fijo del script
- o actualizarlo automáticamente desde el estado real

---

### 4. El workflow de secret scan básico está mal escrito y puede fallar siempre

**Archivo afectado**

- [.github/workflows/secret-scan.yml](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/.github/workflows/secret-scan.yml)

**Bloque problemático**

```bash
for PATTERN in "SECRET_KEY" "JWT_SECRET" "JWT_REFRESH_SECRET" "AWS_SECRET_ACCESS_KEY" "PRIVATE_KEY"; do
  if git grep -n -- "${PATTERN}" || true; then
    FOUND=1
  fi
done
```

**Causa raíz**

`|| true` hace que la condición del `if` termine siendo verdadera incluso cuando `git grep` no encuentra nada.

En otras palabras:

- `FOUND` termina en `1`
- el job puede fallar aunque no exista un secreto real expuesto

**Impacto**

- ruido en CI
- falsos positivos de seguridad
- correos innecesarios

**Solución**

Cambiar la lógica por algo que sólo marque `FOUND=1` cuando `git grep` encuentre resultados reales.

---

### 5. Los correos se repiten porque el workflow tiene cron

**Archivo afectado**

- [.github/workflows/sync-instruments.yml](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/.github/workflows/sync-instruments.yml)

**Configuración actual**

```yml
schedule:
  - cron: '0 */6 * * *'
```

**Causa raíz**

Aunque no estés trabajando localmente, GitHub vuelve a correr el workflow periódicamente.

Si sigue mal configurado:

- seguirá fallando
- seguirá enviando correos

**Impacto**

- spam operativo
- falsa sensación de inestabilidad local

**Solución**

- corregir primero la validación
- o desactivar temporalmente el `schedule` hasta arreglar el flujo

---

## Problemas Probables / Relevantes

### 6. El correo de `Security Scanning` puede venir de varios puntos frágiles

**Archivo afectado**

- [.github/workflows/security.yml](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/.github/workflows/security.yml)

**Puntos de riesgo**

1. Usa referencias flotantes:
   - `@main`
   - `@master`

2. Usa `actions/upload-artifact@v3`
   - versión vieja
   - riesgo de deprecación o comportamiento inestable

3. El job `code-quality` depende de:
   - `SONAR_TOKEN`
   - configuración correcta de SonarCloud

4. El repositorio trackea una base de datos binaria:
   - [backend/cirujano.db](/mnt/CZ_BODEGA/010_VSCODE/007_PROYECTOS_WEB/cirujano-front_CLEAN/backend/cirujano.db)

**Impacto**

- más superficie para falsos positivos
- posible ruido de scanners por contenido binario o histórico

**Solución**

- fijar versiones estables de actions
- revisar si `SONAR_TOKEN` y el proyecto Sonar están realmente configurados
- reducir superficie escaneada donde corresponda
- evaluar sacar la DB trackeada del repo en una fase controlada

---

### 7. El incidente de GitGuardian requiere revisar el fingerprint exacto

**Señal observada**

- correo de `GitGuardian Team`

**Estado**

No se puede identificar el hallazgo exacto sólo desde el repo local sin abrir el detalle del incidente en GitHub/GitGuardian.

**Fuentes probables**

- históricos del repositorio
- binarios trackeados
- cadenas de prueba que parecen secretos
- ejemplos/documentación con nombres tipo `JWT_SECRET`, `PRIVATE_KEY`, etc.

**Observación importante**

En el repo actual sí aparecen cadenas como:

- `JWT_SECRET`
- `JWT_REFRESH_SECRET`
- `PRIVATE_KEY`

pero muchas de ellas están en:

- tests
- ejemplos
- documentación
- workflows defectuosos

No necesariamente son credenciales reales.

**Solución**

- abrir el detalle del incidente en GitGuardian
- identificar el archivo y commit exacto
- corregir el origen real y no por intuición

---

## Resumen Ejecutivo

### Problema principal

El spam de correos de `Sincronizar Instrumentos Automáticamente` no se debe al entorno local, sino a que el flujo remoto quedó desalineado:

- hay `273` fotos reales
- el workflow todavía exige `249`

### Problema secundario importante

El `secret-scan.yml` básico está mal implementado y puede marcar fallo aunque no exista un secreto real expuesto.

### Problema de fondo

Los workflows mezclan:

- validaciones con números fijos
- escaneos demasiado sensibles
- referencias flotantes
- posibles fuentes de ruido como la DB trackeada

---

## Prioridad de Solución

### Alta

1. Arreglar `sync-instruments.yml`
2. Arreglar `validate_instruments_sync.py`
3. Arreglar `package.json` en `validate:instruments`
4. Arreglar `secret-scan.yml`

### Media

5. Revisar `security.yml`
6. Revisar el incidente exacto de GitGuardian

### Baja pero recomendable

7. Revisar estrategia de versionado de `backend/cirujano.db`

---

## Estado Final del Diagnóstico

### Confirmado

- el aviso no es local
- el workflow de sync está roto por conteo fijo viejo
- la validación de instrumentos no valida el disco real
- el secret scan básico está mal escrito

### Pendiente de confirmar con detalle externo

- qué paso exacto falló en `Security Scanning`
- qué fingerprint exacto disparó GitGuardian


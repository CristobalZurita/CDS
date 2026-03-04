# Security History Remediation

Estado al momento de esta preparación:

- `REDACTED` sigue confirmado en historia (`git log --all -S'REDACTED' --oneline --source --all`) en `refs/heads/CZ_NUEVA_SANITIZED`.
- `backend/cirujano.db` sigue trackeado y en historia.
- `backend/cirujano.log.1` sigue trackeado y en historia.
- `REDACTED` aún aparece en archivos trackeados actuales como `TEXTO_SUGERENCIA-md` y `DOCUMJENTOS_EXTRAS/PLAN_TOTAL_1000_PORCIENTO.md`.

## Archivos preparados

- `reports/replace-secrets.txt`
  - Contiene solo el valor confirmado para reemplazo histórico: `REDACTED==>REDACTED`

## Preflight obligatorio

1. Trabajar sobre una clonación limpia o una rama donde todo lo necesario ya esté committeado.
2. Confirmar que no necesitas preservar el historial SHA actual.
3. Confirmar que vas a forzar `push` de todas las ramas afectadas.
4. Avisar a cualquier entorno que consuma SHAs antiguos, tags o PRs abiertos.

## Verificación previa

```bash
git grep -n "REDACTED" -- TEXTO_SUGERENCIA-md DOCUMJENTOS_EXTRAS/PLAN_TOTAL_1000_PORCIENTO.md backend/scripts/seed_admin.py
git log --all --oneline -- backend/cirujano.db
git log --all --oneline -- backend/cirujano.log.1
git log --all -S'REDACTED' --oneline --source --all
```

## Reescritura de historia

Instalar `git-filter-repo` si aún no existe:

```bash
python3 -m pip install git-filter-repo
```

Reescribir historia removiendo la base SQLite y el log trackeado, y redactando `REDACTED`:

```bash
git filter-repo \
  --replace-text reports/replace-secrets.txt \
  --path backend/cirujano.db \
  --path backend/cirujano.log.1 \
  --invert-paths \
  --force
```

## Verificación posterior

Estos comandos deben quedar sin resultados para los secretos/artefactos purgados:

```bash
git log --all -S'REDACTED' --oneline --source --all
git log --all --oneline -- backend/cirujano.db
git log --all --oneline -- backend/cirujano.log.1
git grep -n "REDACTED" $(git rev-list --all)
```

## Push forzado

Solo después de verificar:

```bash
git push origin --force --all
git push origin --force --tags
```

## Pendientes manuales antes o después del rewrite

- `TEXTO_SUGERENCIA-md` sigue conteniendo `REDACTED` en el árbol actual. Si no se limpia en una commit normal, el scanner seguirá marcándolo aunque la historia vieja sea purgada.
- `DOCUMJENTOS_EXTRAS/PLAN_TOTAL_1000_PORCIENTO.md` también conserva `REDACTED` como texto actual.
- Ignorar `backend/cirujano.db` y `backend/cirujano.log.1` no los saca del índice ni de la historia: el rewrite sigue siendo necesario si quieres eliminar el rastro histórico.

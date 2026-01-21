# CDS_PLAN_MITIGAR_05 - Revision total (SQLi/inputs)

## Alcance de revision
- Backend: backend/app, backend/scripts, backend/tests
- Busqueda de SQL manual (`execute`/`cur.execute`) y posibles interpolaciones peligrosas.

## Hallazgos directos
### Uso de SQL manual
- backend/app/api/v1/endpoints/imports.py usa `cur.execute` con placeholders `?` (parametrizado).
- backend/scripts/create_admin.py usa `cur.execute` con placeholders `?` (parametrizado).
- backend/tests/* usa `cur.execute` para fixtures/tests (contexto de prueba).
- backend/app/api/v1/endpoints/inventory.py usa `db.execute(delete(...))` (SQLAlchemy seguro).

### No se detecto (por busqueda simple)
- No se encontraron `execute(f"...{input}...")` en backend/app.
- No se encontraron interpolaciones SQL via f-string en backend/app.

## Riesgos residuales
- SQL manual sigue siendo un vector potencial si se agrega sin placeholders.
- Inputs de texto libre deben validarse con Pydantic (longitud/formato).
- El control principal depende de ORM/parametrizacion; falta un checklist formal por endpoint.

## Acciones recomendadas
1) Formalizar politica anti-inyeccion (prohibir SQL por interpolacion).
2) Agregar validaciones Pydantic a todos los campos de texto libre (min/max/regex).
3) Crear pruebas de payloads maliciosos (SQLi/XSS) y registrar respuestas 400/403.
4) Documentar evidencia: logs de pruebas y respuestas JSON.

## Comandos de verificacion rapida
```bash
grep -R "execute(.*f"" -n backend/app backend/scripts backend/tests
grep -R "\.execute(" -n backend/app backend/scripts backend/tests
```
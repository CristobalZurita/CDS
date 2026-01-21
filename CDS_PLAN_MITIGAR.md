# CDS_PLAN_MITIGAR

## 1) Hallazgos actuales (desde auditorias)
- Riesgo potencial de inyeccion si existiera SQL manual sin parametros.
- Validaciones de texto libre no estan explicitamente documentadas en todos los endpoints.
- Falta evidencia de pruebas anti-inyeccion (SQLi/XSS) en ejecucion.
- Documentacion dispersa puede ocultar vulnerabilidades reales.

## 2) Reglas obligatorias (anti malas practicas)
1) Prohibido SQL con interpolacion de strings.
2) Solo ORM o queries parametrizadas (SQLAlchemy).
3) Todo input de texto libre debe tener validacion Pydantic (longitud, formato).
4) Sanitizar HTML solo para XSS, no como defensa SQL.
5) Logs de intentos invalidos para auditoria.

## 3) Plan de correccion
### Paso A: Auditoria tecnica completa
- Buscar SQL manual (`execute(f"...{input}...")`).
- Listar endpoints que reciben texto libre sin schema estricto.
- Verificar que todos los endpoints usan ORM/parametros.

### Paso B: Correcciones aditivas
- Agregar schemas Pydantic estrictos en inputs de texto libre.
- Reemplazar SQL manual por ORM/parametros.
- Agregar validaciones de longitud, regex y tipos.

### Paso C: Pruebas de seguridad
- Crear checklist de payloads maliciosos (SQLi/XSS).
- Documentar respuestas esperadas (400/403).
- Guardar evidencias (logs/outputs).

## 4) Evidencia requerida
- Reporte de auditoria tecnica (con rutas y endpoints).
- Resultados de pruebas de inyeccion (capturas o logs).
- Confirmacion de ORM/parametrizacion en todos los servicios.

## 5) Resultado esperado
- 0 endpoints vulnerables a SQLi/XSS por entradas de texto libre.
- Validaciones documentadas y reproducibles.
- Evidencia tecnica de mitigacion lista para terceros.
# CDS AUDIT REPORT — 2026-03-05 20:19

## RESUMEN
Total checks: 6
Pasaron: 3
Fallaron: 3

## CRÍTICOS — ROTO
  API_PUBLIC | /docs | HTTP 404 | FAIL
  AUTH | login | HTTP 401 | FAIL — {"detail":"Email o contraseña incorrectos"}
  API_SCAN | openapi | HTTP 0 | ERROR: 'paths'

## OK
  FRONTEND | / | HTTP 200 | OK
  API_PUBLIC | /health | HTTP 200 | OK
  API_PUBLIC | /health | HTTP 200 | OK

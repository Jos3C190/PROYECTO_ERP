---
name: security-remediation
description: Instrucciones para que el Agente de IA analice reportes de seguridad automatizada (OWASP ZAP y Trivy) y aplique parches defensivos (Blue Team) en el código del ERP.
---

# Habilidad: Remedición de Seguridad (Blue Team)

Usa esta habilidad cuando se hayan generado reportes de escaneo de seguridad en la carpeta `./reports/` (`security-report.json` o `trivy-report.json`) y debas auditar o remediar hallazgos.

## Protocolo de Trabajo para el Agente:

1. **Lectura de Reportes (`JSON`):**
   - Leer `reports/security-report.json` o `reports/security-deep-report.json` (Vulnerabilidades dinámicas DAST de OWASP ZAP Baseline y OpenAPI Scan).
   - Leer `reports/trivy-report.json` (Vulnerabilidades estáticas SCA de dependencias).
   - Revisar fallos en las pruebas de seguridad del backend (`backend/tests/integration/api/test_security_bounds.py`).

2. **Clasificación por Severidad:**
   - Priorizar hallazgos de severidad **HIGH** y **CRITICAL**.
   - Identificar si la falla es de cabeceras HTTP, bypass de permisos RBAC, firmas JWT forjadas, inyecciones en DTOs Pydantic o dependencias vulnerables.

3. **Aplicación de Parches Defensivos:**
   - **Falta de cabecera de seguridad:** Actualizar `backend/app/middlewares/security_headers.py`.
   - **Permiso RBAC no verificado:** Agregar `Depends(require_permission(...))` en el router de `backend/app/api/v1/routers/`.
   - **Sanitización DTO:** Reforzar campos en `backend/app/api/v1/schemas/` con validadores Pydantic.
   - **Dependencia vulnerable:** Actualizar versión en `backend/pyproject.toml` (`uv lock`) o `frontend/package.json` (`pnpm update`).

4. **Verificación del Parche:**
   - Ejecutar `docker compose exec backend pytest tests/integration/api/test_security_bounds.py` para validar los límites de seguridad.
   - Ejecutar `make test` para asegurar que el sistema mantiene retrocompatibilidad.
   - Re-ejecutar `.\scripts\security-scan.ps1 -Deep` (o `make security-scan-deep`) para verificar que el reporte queda totalmente limpio.

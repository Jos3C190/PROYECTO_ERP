param (
    [switch]$Deep
)

# ==============================================================================
# Script de Auditoria de Seguridad Automatizada (Red Team) - Windows PowerShell
# ==============================================================================

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " ERP System - Iniciando Auditoria de Seguridad (Red Team Scan)" -ForegroundColor Cyan
if ($Deep) {
    Write-Host " MODO PROFUNDO ACTIVO (DAST OpenAPI + Fuzzing + Tests Backend)" -ForegroundColor Red
}
Write-Host "======================================================================" -ForegroundColor Cyan

# Crear carpeta de reportes si no existe
New-Item -ItemType Directory -Force -Path "reports" | Out-Null

Write-Host "--> 1. Ejecutando pruebas adversariales de seguridad en Backend (Pytest)..." -ForegroundColor Yellow
docker compose exec -T backend pytest tests/integration/api/test_security_bounds.py -v

if ($Deep) {
    Write-Host "--> 2. Iniciando escaneo DAST Activo Profundo (OWASP ZAP OpenAPI Scan)..." -ForegroundColor Yellow
    docker compose --profile security-deep run --rm security-zap-deep
} else {
    Write-Host "--> 2. Iniciando escaneo DAST Baseline con OWASP ZAP..." -ForegroundColor Yellow
    docker compose --profile security run --rm security-zap
}

Write-Host "--> 3. Iniciando escaneo de vulnerabilidades en dependencias con Trivy..." -ForegroundColor Yellow
docker compose --profile security run --rm security-trivy

Write-Host "======================================================================" -ForegroundColor Green
Write-Host " Escaneo completado con exito." -ForegroundColor Green
Write-Host " Reportes generados en:" -ForegroundColor Green
if ($Deep) {
    Write-Host "    - .\reports\security-deep-report.json  (DAST OpenAPI Active Scan)" -ForegroundColor Green
    Write-Host "    - .\reports\security-deep-report.html  (DAST visual profundo)" -ForegroundColor Green
} else {
    Write-Host "    - .\reports\security-report.json       (DAST Baseline)" -ForegroundColor Green
    Write-Host "    - .\reports\security-report.html       (DAST visual)" -ForegroundColor Green
}
Write-Host "    - .\reports\trivy-report.json           (SCA - Codigo y Dependencias)" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Green

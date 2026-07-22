#!/usr/bin/env bash
# ==============================================================================
# Script de Auditoría de Seguridad Automatizada (Red Team)
# Ejecuta OWASP ZAP (DAST) y Trivy (SCA) generando reportes JSON en ./reports
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$ROOT_DIR"

MODE="${1:-baseline}"

echo "======================================================================"
echo " 🔒 ERP System — Iniciando Auditoría de Seguridad (Red Team Scan)"
if [ "$MODE" == "deep" ]; then
    echo " 🔥 MODO PROFUNDO ACTIVO (DAST OpenAPI + Fuzzing + Tests Backend)"
fi
echo "======================================================================"

# Crear carpeta de reportes si no existe
mkdir -p reports

echo "--> 1. Ejecutando pruebas adversariales de seguridad en Backend (Pytest)..."
docker compose exec -T backend pytest tests/integration/api/test_security_bounds.py -v || true

if [ "$MODE" == "deep" ]; then
    echo "--> 2. Iniciando escaneo DAST Activo Profundo (OWASP ZAP OpenAPI Scan)..."
    docker compose --profile security-deep run --rm security-zap-deep || true
else
    echo "--> 2. Iniciando escaneo DAST Baseline con OWASP ZAP..."
    docker compose --profile security run --rm security-zap || true
fi

echo "--> 3. Iniciando escaneo de vulnerabilidades de código con Trivy..."
docker compose --profile security run --rm security-trivy || true

echo "======================================================================"
echo " ✅ Escaneo completado."
echo " 📊 Reportes generados en:"
if [ "$MODE" == "deep" ]; then
    echo "    - ./reports/security-deep-report.json  (DAST OpenAPI Active Scan)"
    echo "    - ./reports/security-deep-report.html  (DAST visual profundo)"
else
    echo "    - ./reports/security-report.json       (DAST Baseline)"
    echo "    - ./reports/security-report.html       (DAST visual)"
fi
echo "    - ./reports/trivy-report.json           (SCA - Código y Dependencias)"
echo "======================================================================"

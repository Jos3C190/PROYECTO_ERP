# Sistema Red Team / Blue Team y Automatización de Seguridad (DevSecOps)

> **Versión:** `v1.0.0` | **Última actualización:** `22/07/2026`  
> **Proyecto:** ERP System  
> **Stack:** OWASP ZAP + Trivy + Pytest Adversarial Bounds + Git Hooks (.githooks)

Este documento detalla la arquitectura de seguridad defensiva (**Blue Team**) y ofensiva (**Red Team**), los contenedores de auditoría automatizada, el sistema de bloqueo de `commit` y `push` mediante Git Hooks y las notificaciones flotantes de Windows.

---

## 1. Visión General de la Arquitectura Red Team / Blue Team

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          RED TEAM (Capa Ofensiva)                           │
│  ┌───────────────────────────┐ ┌──────────────────────┐ ┌─────────────────┐ │
│  │ OWASP ZAP DAST / OpenAPI  │ │ Trivy SCA & Secrets  │ │ Pytest Fuzzing  │ │
│  └─────────────┬─────────────┘ └──────────┬───────────┘ └────────┬────────┘ │
└────────────────│──────────────────────────│──────────────────────│──────────┘
                 │                          │                      │
                 ▼                          ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        REPORTES EN ./reports/*.json                         │
└──────────────────────────────────────────┬──────────────────────────────────┘
                                           │
                                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        BLUE TEAM (Capa Defensiva)                           │
│  ┌───────────────────────────┐ ┌──────────────────────┐ ┌─────────────────┐ │
│  │ Agentes IA Remedición     │ │ RBAC & Security Hdrs │ │ Pydantic v2 DTOs│ │
│  └───────────────────────────┘ └──────────────────────┘ └─────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

El ERP System implementa un ciclo cerrado de seguridad automatizada:
1. **Red Team (Simulaciones de Ataque Real):** Contenedores Docker aislados que ejecutan escaneos DAST activos, inyecciones de código y fuzzing de entradas.
2. **Reportes estructurados:** Generación de diagnósticos en `./reports/` (`security-deep-report.json`, `trivy-report.json`).
3. **Blue Team (Remediación Defensiva):** Habilidad de Agentes de IA (`.agents/skills/security-remediation/SKILL.md`) que lee los reportes JSON y aplica parches de código en FastAPI/SvelteKit.

---

## 2. Contenedores y Herramientas de Auditoría Real

Los escáneres de seguridad están containerizados en el perfil opcional `security` y `security-deep` de `compose.yaml`, evitando instalar herramientas pesadas en la máquina host.

### 2.1 OWASP ZAP (DAST - Dynamic Application Security Testing)
- **Imagen Docker:** `ghcr.io/zaproxy/zaproxy:stable`
- **Servicio `security-zap` (Baseline):** Ejecuta `zap-baseline.py` contra `http://backend:8000`. Detecta fallas pasivas de cabeceras HTTP, cookies inseguras y fugas de información.
- **Servicio `security-zap-deep` (Active OpenAPI Scan):** Ejecuta `zap-api-scan.py -t http://backend:8000/openapi.json -f openapi`. Lanza **118 reglas de ataque activo** probando inyecciones SQL en PostgreSQL, Remote Command Execution (RCE), Path Traversal (LFI), XSS reflejado/persistente, Server-Side Template Injection (SSTI), XXE y desinteligencia de firmas JWT.

### 2.2 Trivy Scanner (SCA - Software Composition Analysis)
- **Imagen Docker:** `aquasec/trivy:latest`
- **Servicio `security-trivy`:** Analiza estáticamente el código fuente y el árbol de dependencias de Python (`pyproject.toml`, `uv.lock`) y Node.js (`package.json`, `pnpm-lock.yaml`).
- **Capacidades:** Detecta CVEs conocidos en paquetes de terceros y realiza escaneo de secretos (API keys o credenciales hardcodeadas).

### 2.3 Pytest Adversarial Bounds (`test_security_bounds.py`)
- **Ubicación:** [`backend/tests/integration/api/test_security_bounds.py`](file:///d:/josec/Documents/Ciclo%20X/TRANSACCIONES%20COMERCIALES%20POR%20MEDIOS%20ELECTR%C3%93NICOS%20SECCI%C3%93N%20A/PROYECTO_ERP/backend/tests/integration/api/test_security_bounds.py)
- **Propósito:** Valida el comportamiento ante tampering de firmas JWT (`alg: none`, claves erróneas), desestimación de peticiones no autenticadas (401), fuzzing con NUL bytes (`\x00`), payloads SQLi y scripts `<script>` en credenciales.

---

## 3. Bloqueo Automatizado de Git Hooks (`pre-commit` y `pre-push`)

Para impedir que se suba código inseguro o con vulnerabilidades a los entornos de desarrollo o producción, se utiliza el sistema de **Git Hooks** versionado en la carpeta [`.githooks/`](file:///d:/josec/Documents/Ciclo%20X/TRANSACCIONES%20COMERCIALES%20POR%20MEDIOS%20ELECTR%C3%93NICOS%20SECCI%C3%93N%20A/PROYECTO_ERP/.githooks).

### 3.1 Hook `pre-commit` (Pruebas Rápida de Límites de Seguridad)
- **Ubicación:** `.githooks/pre-commit`
- **Disparador:** Se ejecuta automáticamente cada vez que el desarrollador hace `git commit` (en la terminal o mediante la interfaz de VS Code/Cursor/GitHub Desktop).
- **Acción:** Ejecuta la suite pytest de seguridad (`test_security_bounds.py`) en ~3 segundos.
- **Resultado:**
  - **Si aprueba:** Continúa con el commit y emite una notificación flotante en Windows.
  - **Si falla:** **Cancela y aborta el commit inmediatamente**, indicando el test que se quebró.

### 3.2 Hook `pre-push` (Auditoría Profunda Red Team)
- **Ubicación:** `.githooks/pre-push`
- **Disparador:** Se ejecuta automáticamente al hacer `git push` o presionar *Sync Changes*.
- **Acción:** Lanza el escaneo DAST Activo Profundo (OWASP ZAP OpenAPI) + Trivy SCA (~1 a 2 minutos).
- **Resultado:**
  - **Si aprueba:** Subida exitosa al repositorio remoto y notificación flotante en Windows.
  - **Si falla:** Aborta el `push`, bloqueando la subida y generando el reporte interactivo en `reports/security-deep-report.html`.

### 3.3 Activación 100% Automática sin Pasos Manuales
Git por defecto no rastrea `.git/hooks/`. Para resolver esto, el script [`scripts/setup.sh`](file:///d:/josec/Documents/Ciclo%20X/TRANSACCIONES%20COMERCIALES%20POR%20MEDIOS%20ELECTR%C3%93NICOS%20SECCI%C3%93N%20A/PROYECTO_ERP/scripts/setup.sh) ejecuta automáticamente:

```bash
git config core.hooksPath .githooks
```

De este modo, cuando cualquier desarrollador clona el proyecto y levanta el entorno por primera vez, Git vincula los hooks de seguridad automáticamente.

---

## 4. Notificaciones Flotantes de Windows (Toast Notifications)

El script de ayuda [`scripts/notify.ps1`](file:///d:/josec/Documents/Ciclo%20X/TRANSACCIONES%20COMERCIALES%20POR%20MEDIOS%20ELECTR%C3%93NICOS%20SECCI%C3%93N%20A/PROYECTO_ERP/scripts/notify.ps1) interactúa con la API nativa de notificaciones de Windows (`System.Windows.Forms.NotifyIcon`).

Al completar un `commit` o `push` con éxito, aparece un globo informativo flotante en la esquina inferior derecha de la pantalla:

> 🔒 **ERP Security - Pre-Commit / Pre-Push**  
> *Auditoría de seguridad aprobada con éxito: 0 vulnerabilidades críticas.*

---

## 5. Comandos de Ejecución Manual

Los desarrolladores y auditores pueden lanzar los escaneos de seguridad en cualquier momento:

### En Windows PowerShell:
```powershell
# Escaneo de seguridad estándar (Baseline DAST + Trivy)
.\scripts\security-scan.ps1

# Escaneo profundo de seguridad (OWASP ZAP OpenAPI Active Scan + Pytest Fuzzing + Trivy)
.\scripts\security-scan.ps1 -Deep
```

### En Linux / macOS / WSL / Make:
```bash
# Escaneo estándar
make security-scan

# Escaneo profundo
make security-scan-deep
```

---

## 6. Remediación Asistida por Agentes de IA (Blue Team Protocol)

Cuando un escaneo detecta vulnerabilidades, los agentes de IA invocan la habilidad [`.agents/skills/security-remediation/SKILL.md`](file:///d:/josec/Documents/Ciclo%20X/TRANSACCIONES%20COMERCIALES%20POR%20MEDIOS%20ELECTR%C3%93NICOS%20SECCI%C3%93N%20A/PROYECTO_ERP/.agents/skills/security-remediation/SKILL.md):

1. Leen `reports/security-deep-report.json` o `reports/trivy-report.json`.
2. Identifican la causa raíz (Falta de permiso RBAC, header HTTP ausente, Pydantic DTO permisivo, paquete desactualizado).
3. Aplican la solución defensiva en el código fuente.
4. Vuelven a ejecutar `.\scripts\security-scan.ps1 -Deep` para validar que el reporte queda totalmente en cero antes de cerrar la tarea.

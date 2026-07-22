---
name: feature-development
description: Protocolo de ingeniería senior para análisis, planificación, desarrollo, seguridad, testing y validación de funcionalidades en el ERP System.
---

# Protocolo de Ingeniería Senior — Desarrollo de Funcionalidades

Usa este protocolo cuando desarrolles o modifiques una funcionalidad en este proyecto ERP (FastAPI + SvelteKit 5 + PostgreSQL).

## Rol y Mentalidad
Actúas como un **ingeniero de software senior** responsable de mantener un sistema ERP en producción. No entregas parches rápidos: entregas soluciones sostenibles, seguras y mantenibles. Sigue estrictamente el ciclo:

**PENSAR → ANALIZAR → PLANIFICAR → EJECUTAR → TESTEAR → VALIDAR**

---

### 1. Pensar y Analizar (Antes de tocar código)
- **Entender el objetivo real:** Comprender la necesidad del negocio, no solo la instrucción literal.
- **Exploración del sistema:** Revisar el código existente relacionado (Domain, Application, Infrastructure, API Routers, SvelteKit Components, Types, Stores y Tests).
- **Identificar dependencias e impactos:** Determinar qué roles, pantallas, reportes, permisos RBAC o tablas en PostgreSQL se ven afectados.
- **Respetar la arquitectura del proyecto:**
  - Backend: Arquitectura Hexagonal en `backend/app/` (`domain/` -> `application/` -> `infrastructure/` -> `api/v1/`).
  - Frontend: SvelteKit 5 con **Runes** (`$state`, `$derived`, `$effect`, `$props`) y tokens **Geist** (Modo Claro/Oscuro).
- **Evitar duplicación (DRY):** Reutilizar servicios, modelos o componentes existentes.
- **Análisis de riesgos ("¿Qué se puede romper?"):** Evaluar regresiones en contratos de API (DTOs Pydantic v2), permisos RBAC, migraciones Alembic y datos existentes.

---

### 2. Planificar
- **Pasos incrementales:** Dividir tareas grandes en sub-problemas pequeños y verificables.
- **Definir estrategia de pruebas:** Determinar cómo probar cada capa (`pytest` en backend, `vitest` en frontend, prueba manual visual).
- **Trade-offs explícitos:** Si la tarea requiere cambios estructurales o de esquema en PostgreSQL, exponer los pros/contras antes de ejecutar.

---

### 3. Ejecutar — Buenas Prácticas Obligatorias

#### Código Limpio & Separación de Capas
- Nombres descriptivos y funciones pequeñas con responsabilidad única (SRP).
- Aplicar SOLID y DRY sin abstracciones prematuras.
- **Backend:** Separación estricta (Domain -> Application -> Infrastructure -> API). Jamás retornar modelos ORM de SQLAlchemy en los endpoints (usar DTOs Pydantic v2).
- **Frontend:** Separación entre componentes presentacionales y contenedores. Exclusividad de Svelte 5 Runes (prohibido `$: ...` o `export let`).

#### Validaciones, Seguridad y RBAC
- **Validar siempre en Backend:** Sanitizar inputs con Pydantic v2, verificar tipos y valores nulos/vacíos.
- **Autorización RBAC:** Proteger endpoints con `Depends(require_permission("recurso:accion"))`.
- **Bitácora de Auditoría:** Registrar automáticamente operaciones de escritura en `audit_logs`.
- **Seguridad:** Cero secretos hardcodeados en código (`.env`), hashing de contraseñas con Argon2id, tokens JWT en cookies HTTP-Only.
- **Errores estructurados:** Mensajes entendibles sin exponer detalles sensibles (stack traces o queries SQL).

#### Experiencia de Usuario (Admin vs Empleado)
- Diferenciar necesidades de un Administrador (control total, auditoría, gestión) vs Empleado/Usuario final (simplicidad, rapidez).
- **Estados visuales obligatorios:** Loading (`.skeleton` shimmer), Empty State (icono + mensaje + acción), Error (banner `border-danger/30`), Success (badge + check).
- Respetar estándares de localización El Salvador (`es-SV`, zona horaria `America/El_Salvador`, moneda USD `$1,250.00`).

---

### 4. Testear
- Escribir o actualizar tests automatizados en backend (`pytest`) y frontend (`vitest`).
- Verificar que no existan regresiones en flujos dependientes.
- Probar casos límite (datos vacíos, valores nulos, permisos insuficientes, errores de red).
- Garantizar que las respuestas JSON mantengan retrocompatibilidad con los clientes frontend.

---

### 5. Validar y Cerrar
- Auto-revisión de código (PR mental): legibilidad, consistencia, nombres, sin código muerto ni `console.log` o `print` de depuración.
- Resumen final: qué se implementó, qué se probó y qué pasos adicionales se requieren (migraciones Alembic con `alembic upgrade head`, siembra con `make seed`, etc.).

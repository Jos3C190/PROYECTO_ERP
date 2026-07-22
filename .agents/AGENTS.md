# Reglas de Proyecto y Guía para Agentes de IA

> **Versión:** `v1.0.0` | **Última actualización:** `22/07/2026`  
> **Proyecto:** ERP System (Boilerplate Empresarial)  
> **Stack:** FastAPI + SvelteKit 5 (Runes) + PostgreSQL 16 + Docker

Este archivo contiene las instrucciones y reglas de arquitectura obligatorias para cualquier Agente de IA (Antigravity, Cursor, Windsurf, Claude Code, GitHub Copilot) que trabaje en este repositorio.

---

## 1. Identidad y Principios Fundamentales

- **Pensamiento sistémico:** Diseña pensando en la mantenibilidad de todo el monorepo.
- **Arquitectura limpia:** Respeta estrictamente la separación entre backend (capas hexagonal) y frontend (componentes y rutas de SvelteKit 5).
- **Simplicidad ante todo:** Evita sobre-ingeniería. Escribe el código más simple que resuelva el problema de forma robusta.

---

## 2. Reglas del Backend (FastAPI + Python 3.12 + PostgreSQL)

### 2.1 Capas de Arquitectura (Hexagonal)
1. **`app/domain/`**: Entidades y puertos (interfaces abstractas). Código Python puro sin dependencias de FastAPI, SQLAlchemy o Pydantic.
2. **`app/application/`**: Casos de uso asíncronos (`execute(...)`). Lógica de negocio pura. Depende de los puertos del dominio.
3. **`app/infrastructure/`**: Implementación concreta de repositorios (SQLAlchemy 2.0 async), modelos de BD (`Base`), clientes de correo o servicios externos.
4. **`app/api/v1/`**: Routers de FastAPI, esquemas Pydantic v2 (DTOs) e inyección de dependencias con `Depends()`.

### 2.2 Reglas Inviolables de Backend
- ❌ **Jamás retornar modelos ORM de SQLAlchemy directamente en los endpoints.** Utiliza siempre DTOs Pydantic v2 (`response_model`).
- ❌ **Jamás ejecutar consultas bloqueantes síncronas.** Toda llamada a la base de datos debe usar `AsyncSession` y `await`.
- 🛡️ **Autorización RBAC:** Proteger cada endpoint que modifique o lea datos sensibles inyectando `Depends(require_permission("recurso:accion"))`.
- 📝 **Bitácora de Auditoría:** Toda acción de escritura (crear, editar, eliminar) debe registrar evento inmutable en `audit_logs`.

---

## 3. Reglas del Frontend (SvelteKit 5 + TypeScript + TailwindCSS)

### 3.1 Exclusividad de Svelte 5 Runes
- ✅ **Utilizar ÚNICAMENTE la sintaxis de Runes de Svelte 5:**
  - Estático/Estado: `let data = $state(...)`
  - Derivado: `let count = $derived(...)`
  - Efecto: `$effect(() => { ... })`
  - Props: `let { prop1, prop2 } = $props()`
- ❌ **Prohibido usar sintaxis obsoleta de Svelte 4:** No usar `$: ...`, ni `export let prop`.

### 3.2 Sistema de Diseño (Geist / Vercel)
- **Variables CSS:** Usar las clases semánticas de Tailwind basadas en CSS variables (ej. `bg-surface`, `bg-surface-muted`, `text-foreground`, `text-foreground-muted`, `border-border`).
- **Soporte de Tema:** Todos los componentes deben verse perfectos tanto en **Modo Claro (Light)** como en **Modo Oscuro (Dark)**.
- **Estados Visuales Obligatorios:**
  - **Loading:** Usar clase `.skeleton` con efecto shimmer manteniendo la misma estructura del contenedor.
  - **Empty State:** Icono atenuado en círculo + mensaje explicativo + botón de acción.
  - **Error State:** Banner con borde tenue `border-danger/30 bg-danger/10` y mensaje legible.

---

## 4. Estándares de Localización (El Salvador - es-SV)

- **Zona horaria:** `America/El_Salvador` (UTC-6)
- **Moneda:** USD (`$`) formateada con separador de miles y dos decimales (`$1,250.00`).
- **Formato de fecha:** `DD/MM/YYYY` (ej. `22/07/2026`).
- **Idioma de interfaz:** Español latinoamericano (`es-SV`).

---

## 5. Seguridad y Calidad de Código

- ❌ **Cero Secretos Hardcodeados:** Nunca incluir contraseñas, claves JWT o API keys en el código fuente. Usar variables de entorno (`.env`).
- ❌ **Cero `console.log` o `print` de depuración:** Eliminar todo log de pruebas antes de guardar.
- 🔒 **Contraseñas:** Hashing con Argon2id.
- 🧪 **Testing:** Todo código nuevo en backend debe incluir su prueba con `pytest`, y en frontend con `vitest`.

---

## 6. Protocolo de Ingeniería Senior (Ciclo Obligatorio)

Todo trabajo en este repositorio debe seguir el ciclo de 5 pasos:

1. **PENSAR Y ANALIZAR:** Entender la necesidad de negocio real (no solo la instrucción literal). Explorar código existente, dependencias, impactos colaterales ("¿Qué se puede romper?") y respetar la arquitectura (Hexagonal en backend, Svelte 5 Runes + Geist en frontend).
2. **PLANIFICAR:** Formular un plan claro dividiendo tareas complejas en pasos incrementales y verificables antes de escribir código.
3. **EJECUTAR:** Aplicar SOLID, DRY, SRP y separación estricta de capas. Validar todo en el backend, aplicar RBAC (`require_permission`), registrar auditoría (`audit_logs`) y cuidar la UX (Admin vs Usuario, estados Loading/Empty/Error).
4. **TESTEAR:** Probar happy path y casos borde (datos vacíos, fallos de red, permisos insuficientes) con tests en `pytest` y `vitest`.
5. **VALIDAR Y CERRAR:** Realizar auto-revisión de código (PR mental), remover todo log/print de pruebas y detallar cambios y pasos adicionales si los hay.

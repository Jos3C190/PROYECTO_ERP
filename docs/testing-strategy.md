# Estrategia de Pruebas y QA (Testing Strategy)

> **Versión:** `v1.0.0` | **Última actualización:** `22/07/2026`  

Este documento define la arquitectura y los estándares de calidad para las pruebas automatizadas en **ERP System**. El objetivo principal es asegurar la estabilidad del sistema, prevenir regresiones y proteger la lógica de dominio antes de cada despliegue a producción.

---

## 1. Pirámide de Pruebas

```
                   /\
                  /  \     E2E Tests (Playwright / Cypress) - Flujos críticos
                 /----\    
                /      \   Integration Tests - Endpoints FastAPI + Postgres
               /--------\  
              /          \ Unit Tests - Casos de Uso, Entidades, Componentes UI
             --------------
```

| Nivel | Herramienta | Enfoque principal | Cobertura Meta |
|---|---|---|---|
| **Backend Unit & Use Case** | `pytest` + `pytest-asyncio` | Lógica de negocio pura en `application/` y reglas de `domain/`. | 85%+ |
| **Backend Integration** | `pytest` + `httpx` + `AsyncSession` | Routers FastAPI, permisos RBAC y consultas SQLAlchemy en PostgreSQL. | 80%+ |
| **Frontend Unit & Component** | `vitest` + `@testing-library/svelte` | Utilidades, formateadores, Svelte 5 runes y componentes UI. | 75%+ |
| **End-to-End (E2E)** | `Playwright` *(planeado)* | Login, navegación entre módulos y flujo completo de permisos. | Flujos clave |

---

## 2. Testing Backend (FastAPI + Pytest)

### 2.1 Estructura de Directorios

```
backend/tests/
├── conftest.py              # Fixtures compartidas (DB session, cliente async, tokens)
├── unit/
│   ├── domain/              # Pruebas de reglas de dominio puras
│   └── application/         # Pruebas de casos de uso (con mocks de repositorios)
├── integration/
│   ├── api/                 # Pruebas de endpoints REST y RBAC
│   └── repositories/        # Pruebas de consultas en la base de datos de test
└── fixtures/
    └── mock_data.py         # Generadores de objetos de prueba
```

### 2.2 Fixtures Clave en `conftest.py`

Las pruebas se ejecutan contra una base de datos PostgreSQL en contenedor o aislada usando sesiones transaccionales que hacen rollback automático al finalizar cada test:

```python
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.api.v1.deps import get_db

@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    """Cliente HTTP asíncrono configurado con la sesión de prueba."""
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def admin_auth_headers(async_client: AsyncClient):
    """Genera token JWT con rol superadmin y retorna headers HTTP."""
    token = create_test_jwt(role="superadmin", permissions=["*"])
    return {"Authorization": f"Bearer {token}"}
```

### 2.3 Ejemplo: Test de Endpoint y Permisos RBAC

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_department_success(async_client: AsyncClient, admin_auth_headers: dict):
    payload = {"name": "Tecnología de Información", "code": "TIC"}
    response = await async_client.post("/api/v1/departments", json=payload, headers=admin_auth_headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Tecnología de Información"
    assert "id" in data

@pytest.mark.asyncio
async def test_create_department_unauthorized_without_permission(async_client: AsyncClient):
    # Sin headers de autorización -> 401 Unauthorized
    response = await async_client.post("/api/v1/departments", json={"name": "Ventas", "code": "VEN"})
    assert response.status_code == 401
```

### 2.4 Comandos de Ejecución Backend

```bash
# Vía Make (recomendado):
make test-backend

# Vía ejecutor directo en Docker:
docker compose exec backend pytest -v --cov=app --cov-report=term-missing

# Ejecutar un archivo o test específico:
docker compose exec backend pytest tests/integration/api/test_users.py -k "test_login"
```

---

## 3. Testing Frontend (SvelteKit 5 + Vitest)

### 3.1 Estructura de Directorios

En este proyecto, los tests del frontend se ubican principalmente en la carpeta raíz `frontend/tests/unit/` (y Vitest también permite co-ubicar tests dentro de `src/`):

```
frontend/
├── vite.config.ts               # Configuración de Vitest (environment: happy-dom)
├── tests/
│   └── unit/
│       ├── setup.ts             # Configuración de entorno de pruebas (@testing-library/svelte)
│       ├── Button.test.ts       # Test unitario de componentes
│       └── client.test.ts       # Test de cliente API
└── src/
    └── lib/                     # Admite tests co-ubicados (*.test.ts)
```

### 3.2 Configuración de Vitest (`vite.config.ts`)

La configuración real del proyecto vive dentro de [frontend/vite.config.ts](file:///d:/josec/Documents/Ciclo%20X/TRANSACCIONES%20COMERCIALES%20POR%20MEDIOS%20ELECTR%C3%93NICOS%20SECCI%C3%93N%20A/PROYECTO_ERP/frontend/vite.config.ts) utilizando el plugin `svelteTesting` y el entorno `happy-dom`:

```typescript
import { sveltekit } from '@sveltejs/kit/vite';
import { svelteTesting } from '@testing-library/svelte/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [sveltekit(), svelteTesting()],
  test: {
    include: ['src/**/*.test.{ts,js}', 'tests/unit/**/*.test.{ts,js}'],
    environment: 'happy-dom',
    setupFiles: ['./tests/unit/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html'],
      include: ['src/lib/**/*.{ts,svelte}']
    }
  }
});
```

### 3.3 Ejemplo: Test de Componente con Svelte 5 Runes

```typescript
import { render, screen } from '@testing-library/svelte';
import { describe, it, expect } from 'vitest';
import Badge from '$lib/components/ui/Badge.svelte';

describe('Badge Component', () => {
  it('renders correct text and variant class', () => {
    render(Badge, { props: { variant: 'success', children: 'Activo' } });
    
    const badgeElement = screen.getByText('Activo');
    expect(badgeElement).toBeInTheDocument();
    expect(badgeElement.classList).toContain('bg-success/10');
  });
});
```

### 3.4 Comandos de Ejecución Frontend

```bash
# Vía Make:
make test-frontend

# Vía pnpm dentro del directorio frontend:
pnpm test

# Ver informe de cobertura:
pnpm test --coverage
```

---

## 4. Reglas y Buenas Prácticas de Testing

1. **Aislamiento Total:** Ningún test debe depender del estado dejado por un test anterior. Cada test limpia o hace rollback de sus datos.
2. **Nombres Descriptivos:** Nombrar los tests indicando el escenario y el resultado esperado:
   - ✅ `test_create_user_should_fail_when_email_already_exists()`
   - ❌ `test_user_error()`
3. **No Testear Implementaciones Internas:** Probar los contratos de entrada/salida (entradas HTTP, código de respuesta, payloads JSON), no variables internas privadas.
4. **Cero Tolerancia a Flaky Tests:** Si un test falla intermitentemente por temas de tiempo o concurrencia asíncrona, debe ser arreglado de inmediato utilizando `await` explícito.
5. **Comprobación en CI:** Ningún Pull Request o Commit se fusiona a `main` si los comandos `make test` no pasan en su totalidad.

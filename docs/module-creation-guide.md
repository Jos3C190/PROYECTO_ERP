# Guía de Creación de Nuevos Módulos ERP

> **Versión:** `v1.0.0` | **Última actualización:** `22/07/2026`  

Esta guía detalla el procedimiento paso a paso para extender el ERP agregando un nuevo módulo funcional (ejemplo: `Proveedores`, `Productos`, `Cotizaciones de Compra`), garantizando la adherencia a la arquitectura hexagonal en el backend y el patrón de componentes en SvelteKit 5.

---

## 1. Arquitectura del Módulo

Un módulo completo requiere sincronización entre el Backend (API, Aplicación, Dominio, Infraestructura) y el Frontend (Tipos, API Client, Componentes, Rutas y Navegación).

```
┌────────────────────────────────────────────────────────────────────────┐
│ FRONTEND (SvelteKit 5)                                                 │
│  src/lib/types/      ──► src/lib/api/      ──► src/routes/(app)/     │
│  (Interfaces TS)         (Fetch Client)        (+page.svelte & UI)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ HTTP REST (JSON + JWT)
┌───────────────────────────────────▼────────────────────────────────────┐
│ BACKEND (FastAPI Hexagonal)                                            │
│  api/v1/routers/     ──► application/      ──► domain/                 │
│  (Endpoints & DTOs)      (Casos de Uso)        (Entidades & Puertos)   │
│                                                     ▲                  │
│                          infrastructure/           │                   │
│                          (Modelos & Repos) ────────┘                   │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Paso a Paso: Backend (FastAPI)

Tomaremos como ejemplo la creación del módulo **Proveedores (`vendors`)**.

### Paso 2.1: Definir la Entidad y Puertos en el Dominio

1. Crear la entidad en [backend/app/domain/entities/vendor.py](file:///d:/josec/Documents/Ciclo%20X/TRANSACCIONES%20COMERCIALES%20POR%20MEDIOS%20ELECTR%C3%93NICOS%20SECCI%C3%93N%20A/PROYECTO_ERP/backend/app/domain/entities):
   ```python
   from dataclasses import dataclass
   from datetime import datetime
   from typing import Optional
   from uuid import UUID

   @dataclass
   class Vendor:
       id: UUID
       name: str
       tax_id: str  # NIT / NRC
       email: Optional[str]
       phone: Optional[str]
       is_active: bool
       created_at: datetime
       updated_at: datetime
   ```

2. Definir la interfaz del repositorio (Puerto) en `app/domain/ports/vendor_repository.py`:
   ```python
   from abc import ABC, abstractmethod
   from typing import List, Optional
   from uuid import UUID
   from app.domain.entities.vendor import Vendor

   class VendorRepositoryPort(ABC):
       @abstractmethod
       async def get_by_id(self, vendor_id: UUID) -> Optional[Vendor]: ...

       @abstractmethod
       async def list_all(self, limit: int = 100, offset: int = 0) -> List[Vendor]: ...

       @abstractmethod
       async def create(self, vendor: Vendor) -> Vendor: ...
   ```

---

### Paso 2.2: Definir el Modelo ORM y la Migración

1. Crear el modelo SQLAlchemy en `app/infrastructure/db/models/vendor.py`:
   ```python
   import uuid
   from datetime import datetime
   from sqlalchemy import String, Boolean, DateTime
   from sqlalchemy.orm import Mapped, mapped_column
   from app.infrastructure.db.base import Base

   class VendorModel(Base):
       __tablename__ = "vendors"

       id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
       name: Mapped[str] = mapped_column(String(150), nullable=False)
       tax_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
       email: Mapped[str | None] = mapped_column(String(255), nullable=True)
       phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
       is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
       created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
       updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
   ```

2. Importar el modelo en `app/infrastructure/db/models/__init__.py` para que Alembic lo detecte.
3. Generar y aplicar la migración:
   ```bash
   docker compose exec backend alembic revision --autogenerate -m "create vendors table"
   docker compose exec backend alembic upgrade head
   ```

---

### Paso 2.3: Implementar el Repositorio

Crear la implementación concreta en `app/infrastructure/repositories/vendor_repository.py`:
```python
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.ports.vendor_repository import VendorRepositoryPort
from app.domain.entities.vendor import Vendor
from app.infrastructure.db.models.vendor import VendorModel

class PostgresVendorRepository(VendorRepositoryPort):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, vendor_id: UUID) -> Optional[Vendor]:
        stmt = select(VendorModel).where(VendorModel.id == vendor_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def list_all(self, limit: int = 100, offset: int = 0) -> List[Vendor]:
        stmt = select(VendorModel).limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, model: VendorModel) -> Vendor:
        return Vendor(
            id=model.id,
            name=model.name,
            tax_id=model.tax_id,
            email=model.email,
            phone=model.phone,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
```

---

### Paso 2.4: Crear los Casos de Uso (Application Layer)

Crear casos de uso específicos en `app/application/use_cases/vendors/`:
- `list_vendors.py`
- `create_vendor.py`

Ejemplo de `create_vendor.py`:
```python
from app.domain.ports.vendor_repository import VendorRepositoryPort
from app.domain.entities.vendor import Vendor
from app.core.exceptions import ConflictException

class CreateVendorUseCase:
    def __init__(self, repo: VendorRepositoryPort):
        self._repo = repo

    async def execute(self, name: str, tax_id: str, email: str | None, phone: str | None) -> Vendor:
        # Business validation logic
        existing = await self._repo.get_by_tax_id(tax_id)
        if existing:
            raise ConflictException(f"El proveedor con NIT/NRC {tax_id} ya existe")
        
        vendor = Vendor(
            id=uuid4(),
            name=name,
            tax_id=tax_id,
            email=email,
            phone=phone,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        return await self._repo.create(vendor)
```

---

### Paso 2.5: Definir Esquemas DTO (Pydantic v2) y Router FastAPI

1. Definir Pydantic schemas en `app/api/v1/schemas/vendor.py`:
   ```python
   from pydantic import BaseModel, EmailStr, ConfigDict
   from uuid import UUID
   from datetime import datetime

   class VendorCreate(BaseModel):
       name: str
       tax_id: str
       email: EmailStr | None = None
       phone: str | None = None

   class VendorResponse(BaseModel):
       model_config = ConfigDict(from_attributes=True)

       id: UUID
       name: str
       tax_id: str
       email: str | None
       phone: str | None
       is_active: bool
       created_at: datetime
   ```

2. Crear Router en `app/api/v1/routers/vendors.py` asegurando verificación de permisos RBAC:
   ```python
   from fastapi import APIRouter, Depends, status
   from app.api.v1.deps import get_current_user, require_permission, get_db
   from app.api.v1.schemas.vendor import VendorCreate, VendorResponse
   from app.infrastructure.repositories.vendor_repository import PostgresVendorRepository
   from app.application.use_cases.vendors.create_vendor import CreateVendorUseCase

   router = APIRouter(prefix="/vendors", tags=["Vendors"])

   @router.post("", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
   async def create_vendor(
       payload: VendorCreate,
       current_user = Depends(require_permission("vendors:create")),
       session = Depends(get_db)
   ):
       repo = PostgresVendorRepository(session)
       use_case = CreateVendorUseCase(repo)
       return await use_case.execute(payload.name, payload.tax_id, payload.email, payload.phone)
   ```

3. Registrar el router en [backend/app/api/v1/api.py](file:///d:/josec/Documents/Ciclo%20X/TRANSACCIONES%20COMERCIALES%20POR%20MEDIOS%20ELECTR%C3%93NICOS%20SECCI%C3%93N%20A/PROYECTO_ERP/backend/app/api/v1/api.py):
   ```python
   api_router.include_router(vendors.router)
   ```

4. Registrar permisos en `app/core/permissions.py` y correr `make seed` para actualizar la base de datos con los nuevos permisos (`vendors:read`, `vendors:create`, `vendors:update`, `vendors:delete`).

---

## 3. Paso a Paso: Frontend (SvelteKit 5)

### Paso 3.1: Interfaces TypeScript

Crear los tipos en `frontend/src/lib/types/vendor.ts`:
```typescript
export interface Vendor {
  id: string;
  name: string;
  tax_id: string;
  email?: string;
  phone?: string;
  is_active: boolean;
  created_at: string;
}

export interface CreateVendorDTO {
  name: string;
  tax_id: string;
  email?: string;
  phone?: string;
}
```

### Paso 3.2: API Client Service

Crear el servicio en `frontend/src/lib/api/vendors.ts`:
```typescript
import { fetchClient } from './client';
import type { Vendor, CreateVendorDTO } from '$lib/types/vendor';

export const vendorsApi = {
  list: () => fetchClient<Vendor[]>('/vendors'),
  create: (data: CreateVendorDTO) => fetchClient<Vendor>('/vendors', {
    method: 'POST',
    body: JSON.stringify(data),
  }),
};
```

### Paso 3.3: Componentes y Vistas con Svelte 5 Runes

Crear la vista principal en `src/routes/(app)/compras/proveedores/+page.svelte`:
```svelte
<script lang="ts">
  import { onMount } from 'svelte';
  import { vendorsApi } from '$lib/api/vendors';
  import type { Vendor } from '$lib/types/vendor';
  import Badge from '$lib/components/ui/Badge.svelte';

  // Svelte 5 Runes para reactividad
  let vendors = $state<Vendor[]>([]);
  let isLoading = $state(true);
  let error = $state<string | null>(null);

  onMount(async () => {
    try {
      vendors = await vendorsApi.list();
    } catch (e: any) {
      error = e.message || 'Error al cargar proveedores';
    } finally {
      isLoading = false;
    }
  });
</script>

<div class="space-y-6">
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-bold text-foreground">Proveedores</h1>
      <p class="text-sm text-foreground-muted">Gestión de catálogo de proveedores de compra</p>
    </div>
  </div>

  {#if isLoading}
    <div class="skeleton h-48 w-full rounded-lg"></div>
  {:else if error}
    <div class="rounded-lg border border-danger/30 bg-danger/10 p-4 text-sm text-danger" role="alert">
      {error}
    </div>
  {:else if vendors.length === 0}
    <div class="flex flex-col items-center justify-center p-12 text-center border border-border rounded-lg">
      <p class="text-foreground-muted mb-4">No hay proveedores registrados.</p>
    </div>
  {:else}
    <div class="border border-border rounded-lg overflow-hidden">
      <table class="w-full text-left text-sm">
        <thead class="bg-surface-muted text-xs uppercase text-foreground-muted">
          <tr>
            <th class="px-4 py-3">Nombre</th>
            <th class="px-4 py-3">NIT / NRC</th>
            <th class="px-4 py-3">Contacto</th>
            <th class="px-4 py-3">Estado</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border">
          {#each vendors as vendor}
            <tr class="hover:bg-surface-hover">
              <td class="px-4 py-3 font-medium text-foreground">{vendor.name}</td>
              <td class="px-4 py-3 font-mono text-xs">{vendor.tax_id}</td>
              <td class="px-4 py-3 text-foreground-muted">{vendor.email || vendor.phone || '-'}</td>
              <td class="px-4 py-3">
                <Badge variant={vendor.is_active ? 'success' : 'neutral'}>
                  {vendor.is_active ? 'Activo' : 'Inactivo'}
                </Badge>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>
```

---

### Paso 3.4: Registrar en el Sidebar y Navegación RBAC

Actualizar [frontend/src/lib/navigation.ts](file:///d:/josec/Documents/Ciclo%20X/TRANSACCIONES%20COMERCIALES%20POR%20MEDIOS%20ELECTR%C3%93NICOS%20SECCI%C3%93N%20A/PROYECTO_ERP/frontend/src/lib/navigation.ts):
```typescript
{
  title: 'Proveedores',
  href: '/compras/proveedores',
  icon: 'Building2',
  permission: 'vendors:read',
}
```

---

## 4. Checklist de Validación del Módulo

- [ ] **Migraciones:** Alembic aplica y revierte sin errores (`alembic upgrade head` / `alembic downgrade -1`).
- [ ] **RBAC:** Endpoints responden `403 Forbidden` si el usuario no tiene el permiso `vendors:read` / `vendors:create`.
- [ ] **Bitácora:** Toda creación/edición/eliminación genera entrada inmutable en `audit_logs`.
- [ ] **UX/UI:** La pantalla respeta el tema claro/oscuro (variables Geist) y maneja estados Loading, Empty y Error.
- [ ] **Tests:** Cobertura de backend (`pytest`) y frontend (`vitest`) agregada.

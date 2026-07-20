<script lang="ts">
  import { theme } from '$lib/stores/theme.svelte';
  import ThemeToggle from '$lib/components/ui/ThemeToggle.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const features = [
    'Stack FastAPI + SvelteKit 5 + PostgreSQL 16',
    'Arquitectura limpia por capas (Clean / Hexagonal)',
    'Migraciones versionadas con Alembic (async)',
    'Cabeceras de seguridad OWASP, CORS restrictivo, logging estructurado',
    'Modo claro/oscuro sin parpadeo (FOUC) y persistente',
    'Test suite lista (pytest + vitest) — verde por defecto'
  ];

  const upcoming = [
    'Autenticación con JWT + refresh token con rotación',
    'RBAC dinámico administrable desde la UI',
    'CRUD de usuarios, empleados, roles y permisos',
    'Bitácora inmutable (append-only) con diff antes/después',
    'Sidebar con mockups de los 17 módulos futuros',
    'Dashboard con KPIs y actividad reciente real'
  ];
</script>

<svelte:head>
  <title>ERP System — Fase 0 (Cimientos)</title>
</svelte:head>

<main class="min-h-screen bg-surface-muted">
  <header class="border-b border-border bg-surface">
    <div class="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
      <div class="flex items-center gap-3">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <span class="font-bold">E</span>
        </div>
        <div>
          <p class="text-sm font-semibold leading-tight text-foreground">ERP System</p>
          <p class="text-xs text-foreground-muted">Fase 0 · Cimientos</p>
        </div>
      </div>
      <ThemeToggle />
    </div>
  </header>

  <section class="mx-auto max-w-6xl px-6 py-12">
    <div class="mb-10">
      <h1 class="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
        Bienvenido al ERP System
      </h1>
      <p class="mt-3 max-w-2xl text-base text-foreground-muted">
        Boilerplate empresarial modular. Esta entrega corresponde a la <strong>Fase 0</strong>:
        los cimientos de producción (contenedores, DB, migraciones, seguridad, tests y modo
        claro/oscuro). Los módulos de negocio llegan en las fases 1 a 6.
      </p>
    </div>

    <div class="grid gap-6 md:grid-cols-2">
      <Card title="Incluido en Fase 0">
        <ul class="space-y-2 text-sm text-foreground">
          {#each features as f}
            <li class="flex items-start gap-2">
              <span class="mt-1 inline-block h-1.5 w-1.5 flex-none rounded-full bg-success" aria-hidden="true"></span>
              <span>{f}</span>
            </li>
          {/each}
        </ul>
      </Card>

      <Card title="Próximamente (Fases 1–6)">
        <ul class="space-y-2 text-sm text-foreground-muted">
          {#each upcoming as u}
            <li class="flex items-start gap-2">
              <span class="mt-1 inline-block h-1.5 w-1.5 flex-none rounded-full bg-warning" aria-hidden="true"></span>
              <span>{u}</span>
            </li>
          {/each}
        </ul>
      </Card>
    </div>

    <div class="mt-10 flex flex-wrap gap-3">
      <Button onclick={() => window.open('http://localhost:8000/docs', '_blank')}>
        Ver API docs (Swagger)
      </Button>
      <Button variant="secondary" onclick={() => theme.toggle()}>
        Cambiar tema (actual: {theme.current})
      </Button>
    </div>
  </section>
</main>
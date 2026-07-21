<script lang="ts">
  import { session } from '$lib/stores/session.svelte';
  import { permissions } from '$lib/stores/permissions.svelte';
  import { api } from '$lib/api/client';
  import ThemeToggle from '$lib/components/ui/ThemeToggle.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let loading = $state(false);
  let error = $state<string | null>(null);

  async function handleLogout() {
    loading = true;
    try {
      await api.auth.logout();
    } catch {
      // ignore — clearing local state anyway
    } finally {
      session.clear();
      permissions.clear();
      loading = false;
      window.location.href = '/login';
    }
  }
</script>

<svelte:head>
  <title>Dashboard — ERP System</title>
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
          <p class="text-xs text-foreground-muted">Dashboard · Fase 1</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <span class="text-sm text-foreground-muted">
          {session.user?.username ?? '...'}
        </span>
        <ThemeToggle />
        <Button variant="secondary" size="sm" onclick={handleLogout} disabled={loading}>
          {loading ? '...' : 'Cerrar sesión'}
        </Button>
      </div>
    </div>
  </header>

  <section class="mx-auto max-w-6xl px-6 py-12">
    <h1 class="text-2xl font-bold tracking-tight text-foreground">
      Bienvenido, {session.user?.email ?? ''}
    </h1>
    <p class="mt-2 text-sm text-foreground-muted">
      Sesión iniciada correctamente. El dashboard completo arrives en Fase 5.
    </p>

    <div class="mt-8 grid gap-6 md:grid-cols-3">
      <Card title="Usuario">
        <dl class="space-y-2 text-sm">
          <div><dt class="inline text-foreground-muted">ID: </dt><dd class="inline font-mono text-foreground">{session.user?.id?.slice(0, 8)}...</dd></div>
          <div><dt class="inline text-foreground-muted">Rol: </dt><dd class="inline text-foreground">{session.user?.is_superuser ? 'Super Admin' : 'Usuario'}</dd></div>
          <div><dt class="inline text-foreground-muted">Estado: </dt><dd class="inline text-foreground">{session.user?.is_active ? 'Activo' : 'Inactivo'}</dd></div>
        </dl>
      </Card>
      <Card title="Sesión">
        <p class="text-sm text-foreground-muted">
          El token de acceso se renueva automáticamente vía refresh token (rotación con detección de reuso).
        </p>
      </Card>
      <Card title="Módulos">
        <ul class="space-y-2 text-sm">
          <li>
            <a href="/users" class="text-primary hover:underline">Gestión de usuarios →</a>
            <span class="block text-xs text-foreground-muted">Listar, activar, desactivar, desbloquear</span>
          </li>
          <li>
            <a href="/roles" class="text-primary hover:underline">Roles y permisos →</a>
            <span class="block text-xs text-foreground-muted">Ver roles, matriz de permisos</span>
          </li>
          <li>
            <a href="/employees" class="text-primary hover:underline">Empleados →</a>
            <span class="block text-xs text-foreground-muted">Listar, buscar, filtrar por departamento</span>
          </li>
          <li>
            <a href="/departments" class="text-primary hover:underline">Departamentos →</a>
            <span class="block text-xs text-foreground-muted">Jerarquía de departamentos</span>
          </li>
          <li>
            <a href="/audit-log" class="text-primary hover:underline">Bitácora →</a>
            <span class="block text-xs text-foreground-muted">Registro inmutable de eventos</span>
          </li>
        </ul>
      </Card>
    </div>
  </section>
</main>
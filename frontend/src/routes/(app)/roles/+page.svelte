<script lang="ts">
  import { session } from '$lib/stores/session.svelte';
  import { permissions } from '$lib/stores/permissions.svelte';
  import { api, HttpError, type RoleWithPermissions } from '$lib/api/client';
  import ThemeToggle from '$lib/components/ui/ThemeToggle.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let roles = $state<RoleWithPermissions[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);

  async function loadRoles() {
    loading = true;
    error = null;
    try {
      roles = await api.roles.list();
    } catch (err) {
      if (err instanceof HttpError) error = err.message;
      else error = 'Error al cargar roles.';
    } finally {
      loading = false;
    }
  }

  async function handleLogout() {
    try { await api.auth.logout(); } catch { /* ignore */ }
    session.clear();
    permissions.clear();
    window.location.href = '/login';
  }

  $effect(() => { loadRoles(); });
</script>

<svelte:head><title>Roles — ERP System</title></svelte:head>

<main class="min-h-screen bg-surface-muted">
  <header class="border-b border-border bg-surface">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
      <div class="flex items-center gap-3">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <span class="font-bold">E</span>
        </div>
        <div>
          <p class="text-sm font-semibold leading-tight text-foreground">ERP System</p>
          <p class="text-xs text-foreground-muted">Gestión de roles</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a href="/dashboard" class="text-sm text-foreground-muted hover:text-foreground">Dashboard</a>
        <a href="/users" class="text-sm text-foreground-muted hover:text-foreground">Usuarios</a>
        <span class="text-sm text-foreground-muted">{session.user?.username}</span>
        <ThemeToggle />
        <Button variant="secondary" size="sm" onclick={handleLogout}>Cerrar sesión</Button>
      </div>
    </div>
  </header>

  <section class="mx-auto max-w-7xl px-6 py-8">
    <div class="mb-6">
      <h1 class="text-2xl font-bold tracking-tight text-foreground">Roles y permisos</h1>
      <p class="mt-1 text-sm text-foreground-muted">
        {roles.length} rol(es) · {permissions.isSuperuser ? 'Super Admin (todos los permisos)' : `${permissions.permissions.length} permiso(s) asignado(s)`}
      </p>
    </div>

    {#if error}
      <div class="mb-4 rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger" role="alert">
        {error}
      </div>
    {/if}

    {#if loading}
      <Card><p class="py-8 text-center text-sm text-foreground-muted">Cargando roles...</p></Card>
    {:else}
      <div class="grid gap-6 md:grid-cols-2">
        {#each roles as role (role.id)}
          <Card>
            <div class="mb-3 flex items-center justify-between">
              <div>
                <h3 class="text-base font-semibold text-foreground">{role.name}</h3>
                <p class="text-xs text-foreground-muted">{role.description ?? 'Sin descripción'}</p>
              </div>
              {#if role.is_system}
                <span class="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                  <span class="h-1.5 w-1.5 rounded-full bg-primary"></span> Sistema
                </span>
              {/if}
            </div>
            <div class="flex flex-wrap gap-1.5">
              {#each role.permissions as perm (perm.code)}
                <span class="rounded-md bg-surface-muted px-2 py-1 text-xs font-mono text-foreground-muted">
                  {perm.code}
                </span>
              {:else}
                <span class="text-xs text-foreground-muted">Sin permisos asignados</span>
              {/each}
            </div>
          </Card>
        {/each}
      </div>
    {/if}
  </section>
</main>
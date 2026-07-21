<script lang="ts">
  import { session } from '$lib/stores/session.svelte';
  import { permissions } from '$lib/stores/permissions.svelte';
  import { api, HttpError, type DepartmentOut } from '$lib/api/client';
  import ThemeToggle from '$lib/components/ui/ThemeToggle.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let departments = $state<DepartmentOut[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);

  async function loadDepartments() {
    loading = true;
    error = null;
    try {
      departments = await api.departments.list();
    } catch (err) {
      if (err instanceof HttpError) error = err.message;
      else error = 'Error al cargar departamentos.';
    } finally {
      loading = false;
    }
  }

  function parentName(id: string | null): string {
    if (!id) return '—';
    return departments.find((d) => d.id === id)?.name ?? '—';
  }

  async function handleLogout() {
    try { await api.auth.logout(); } catch { /* ignore */ }
    session.clear();
    permissions.clear();
    window.location.href = '/login';
  }

  $effect(() => { loadDepartments(); });
</script>

<svelte:head><title>Departamentos — ERP System</title></svelte:head>

<main class="min-h-screen bg-surface-muted">
  <header class="border-b border-border bg-surface">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
      <div class="flex items-center gap-3">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <span class="font-bold">E</span>
        </div>
        <div>
          <p class="text-sm font-semibold leading-tight text-foreground">ERP System</p>
          <p class="text-xs text-foreground-muted">Departamentos</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a href="/dashboard" class="text-sm text-foreground-muted hover:text-foreground">Dashboard</a>
        <a href="/employees" class="text-sm text-foreground-muted hover:text-foreground">Empleados</a>
        <span class="text-sm text-foreground-muted">{session.user?.username}</span>
        <ThemeToggle />
        <Button variant="secondary" size="sm" onclick={handleLogout}>Cerrar sesión</Button>
      </div>
    </div>
  </header>

  <section class="mx-auto max-w-7xl px-6 py-8">
    <div class="mb-6">
      <h1 class="text-2xl font-bold tracking-tight text-foreground">Departamentos</h1>
      <p class="mt-1 text-sm text-foreground-muted">{departments.length} departamento(s)</p>
    </div>

    {#if error}
      <div class="mb-4 rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger" role="alert">{error}</div>
    {/if}

    {#if loading}
      <Card><p class="py-8 text-center text-sm text-foreground-muted">Cargando departamentos...</p></Card>
    {:else if departments.length === 0}
      <Card><p class="py-8 text-center text-sm text-foreground-muted">No hay departamentos. Cree uno para empezar.</p></Card>
    {:else}
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {#each departments as dept (dept.id)}
          <Card>
            <h3 class="text-base font-semibold text-foreground">{dept.name}</h3>
            <p class="mt-1 text-sm text-foreground-muted">{dept.description ?? 'Sin descripción'}</p>
            <div class="mt-3 border-t border-border pt-3">
              <p class="text-xs text-foreground-muted">
                Padre: <span class="font-medium text-foreground">{parentName(dept.parent_department_id)}</span>
              </p>
            </div>
          </Card>
        {/each}
      </div>
    {/if}
  </section>
</main>
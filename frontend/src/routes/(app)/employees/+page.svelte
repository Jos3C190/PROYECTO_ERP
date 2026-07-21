<script lang="ts">
  import { session } from '$lib/stores/session.svelte';
  import { permissions } from '$lib/stores/permissions.svelte';
  import { api, HttpError, type EmployeeOut, type DepartmentOut, type Page } from '$lib/api/client';
  import ThemeToggle from '$lib/components/ui/ThemeToggle.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let employees = $state<EmployeeOut[]>([]);
  let meta = $state<{ page: number; size: number; total: number; pages: number } | null>(null);
  let departments = $state<DepartmentOut[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);
  let search = $state('');
  let page = $state(1);
  let size = $state(10);
  let searchTimer: ReturnType<typeof setTimeout> | null = null;

  async function loadData() {
    loading = true;
    error = null;
    try {
      const [empResult, deptResult] = await Promise.all([
        api.employees.list({ page, size, search: search || undefined }),
        api.departments.list()
      ]);
      employees = empResult.items;
      meta = empResult.meta;
      departments = deptResult;
    } catch (err) {
      if (err instanceof HttpError) error = err.message;
      else error = 'Error al cargar datos.';
    } finally {
      loading = false;
    }
  }

  function onSearchInput() {
    if (searchTimer) clearTimeout(searchTimer);
    searchTimer = setTimeout(() => { page = 1; loadData(); }, 300);
  }

  function goToPage(p: number) {
    if (p < 1 || (meta && p > meta.pages)) return;
    page = p;
    loadData();
  }

  function deptName(id: string | null): string {
    if (!id) return '—';
    return departments.find((d) => d.id === id)?.name ?? '—';
  }

  function statusBadge(s: string): string {
    const map: Record<string, string> = {
      activo: 'bg-success/10 text-success',
      inactivo: 'bg-foreground-muted/10 text-foreground-muted',
      vacaciones: 'bg-warning/10 text-warning',
      baja: 'bg-danger/10 text-danger'
    };
    return map[s] ?? 'bg-foreground-muted/10 text-foreground-muted';
  }

  async function handleLogout() {
    try { await api.auth.logout(); } catch { /* ignore */ }
    session.clear();
    permissions.clear();
    window.location.href = '/login';
  }

  $effect(() => { loadData(); });
</script>

<svelte:head><title>Empleados — ERP System</title></svelte:head>

<main class="min-h-screen bg-surface-muted">
  <header class="border-b border-border bg-surface">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
      <div class="flex items-center gap-3">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <span class="font-bold">E</span>
        </div>
        <div>
          <p class="text-sm font-semibold leading-tight text-foreground">ERP System</p>
          <p class="text-xs text-foreground-muted">Gestión de empleados</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a href="/dashboard" class="text-sm text-foreground-muted hover:text-foreground">Dashboard</a>
        <a href="/users" class="text-sm text-foreground-muted hover:text-foreground">Usuarios</a>
        <a href="/departments" class="text-sm text-foreground-muted hover:text-foreground">Departamentos</a>
        <span class="text-sm text-foreground-muted">{session.user?.username}</span>
        <ThemeToggle />
        <Button variant="secondary" size="sm" onclick={handleLogout}>Cerrar sesión</Button>
      </div>
    </div>
  </header>

  <section class="mx-auto max-w-7xl px-6 py-8">
    <div class="mb-6 flex items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-foreground">Empleados</h1>
        <p class="mt-1 text-sm text-foreground-muted">
          {meta ? `${meta.total} empleado(s)` : 'Cargando...'}
        </p>
      </div>
      <input
        type="text"
        placeholder="Buscar por nombre o código..."
        bind:value={search}
        oninput={onSearchInput}
        class="w-64 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-foreground placeholder:text-foreground-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
      />
    </div>

    {#if error}
      <div class="mb-4 rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger" role="alert">
        {error}
      </div>
    {/if}

    <Card class="overflow-hidden p-0">
      {#if loading}
        <div class="flex items-center justify-center py-16">
          <p class="text-sm text-foreground-muted">Cargando empleados...</p>
        </div>
      {:else if employees.length === 0}
        <div class="flex flex-col items-center justify-center py-16">
          <p class="text-sm text-foreground-muted">No se encontraron empleados.</p>
        </div>
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="border-b border-border bg-surface-muted">
              <tr>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Código</th>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Nombre</th>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Departamento</th>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Cargo</th>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Estado</th>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Contratación</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border">
              {#each employees as emp (emp.id)}
                <tr class="hover:bg-surface-muted">
                  <td class="px-4 py-3 font-mono text-foreground">{emp.employee_code}</td>
                  <td class="px-4 py-3 font-medium text-foreground">{emp.first_name} {emp.last_name}</td>
                  <td class="px-4 py-3 text-foreground-muted">{deptName(emp.department_id)}</td>
                  <td class="px-4 py-3 text-foreground-muted">{emp.position ?? '—'}</td>
                  <td class="px-4 py-3">
                    <span class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium {statusBadge(emp.status)}">
                      <span class="h-1.5 w-1.5 rounded-full bg-current"></span> {emp.status}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-foreground-muted">
                    {emp.hire_date ? new Date(emp.hire_date).toLocaleDateString('es-ES') : '—'}
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </Card>

    {#if meta && meta.pages > 1}
      <div class="mt-4 flex items-center justify-between">
        <p class="text-xs text-foreground-muted">Página {meta.page} de {meta.pages}</p>
        <div class="flex gap-2">
          <Button variant="secondary" size="sm" onclick={() => goToPage(meta!.page - 1)} disabled={meta!.page <= 1}>Anterior</Button>
          <Button variant="secondary" size="sm" onclick={() => goToPage(meta!.page + 1)} disabled={meta!.page >= meta!.pages}>Siguiente</Button>
        </div>
      </div>
    {/if}
  </section>
</main>
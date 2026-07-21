<script lang="ts">
  import { session } from '$lib/stores/session.svelte';
  import { permissions } from '$lib/stores/permissions.svelte';
  import { api, HttpError, type AuditLogOut, type AuditLogPage } from '$lib/api/client';
  import ThemeToggle from '$lib/components/ui/ThemeToggle.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let logs = $state<AuditLogOut[]>([]);
  let nextCursor = $state<string | null>(null);
  let hasMore = $state(false);
  let loading = $state(false);
  let error = $state<string | null>(null);
  let actionFilter = $state('');
  let statusFilter = $state('');
  let expandedRow = $state<string | null>(null);

  async function loadLogs(cursor?: string) {
    loading = true;
    error = null;
    try {
      const result: AuditLogPage = await api.audit.list({
        limit: 25,
        cursor: cursor || undefined,
        action: actionFilter || undefined,
        status: statusFilter || undefined
      });
      if (cursor) {
        logs = [...logs, ...result.items];
      } else {
        logs = result.items;
      }
      nextCursor = result.next_cursor;
      hasMore = result.has_more;
    } catch (err) {
      if (err instanceof HttpError) error = err.message;
      else error = 'Error al cargar bitácora.';
    } finally {
      loading = false;
    }
  }

  function applyFilters() {
    logs = [];
    nextCursor = null;
    loadLogs();
  }

  function loadMore() {
    if (nextCursor) loadLogs(nextCursor);
  }

  function toggleRow(id: string) {
    expandedRow = expandedRow === id ? null : id;
  }

  function formatState(state: Record<string, unknown> | null): string {
    if (!state) return '—';
    return JSON.stringify(state, null, 2);
  }

  function actionBadge(action: string): string {
    if (action.includes('SUCCESS')) return 'bg-success/10 text-success';
    if (action.includes('FAILED')) return 'bg-danger/10 text-danger';
    return 'bg-primary/10 text-primary';
  }

  async function handleLogout() {
    try { await api.auth.logout(); } catch { /* ignore */ }
    session.clear();
    permissions.clear();
    window.location.href = '/login';
  }

  $effect(() => { loadLogs(); });
</script>

<svelte:head><title>Bitácora — ERP System</title></svelte:head>

<main class="min-h-screen bg-surface-muted">
  <header class="border-b border-border bg-surface">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
      <div class="flex items-center gap-3">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <span class="font-bold">E</span>
        </div>
        <div>
          <p class="text-sm font-semibold leading-tight text-foreground">ERP System</p>
          <p class="text-xs text-foreground-muted">Bitácora del sistema</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a href="/dashboard" class="text-sm text-foreground-muted hover:text-foreground">Dashboard</a>
        <span class="text-sm text-foreground-muted">{session.user?.username}</span>
        <ThemeToggle />
        <Button variant="secondary" size="sm" onclick={handleLogout}>Cerrar sesión</Button>
      </div>
    </div>
  </header>

  <section class="mx-auto max-w-7xl px-6 py-8">
    <div class="mb-6">
      <h1 class="text-2xl font-bold tracking-tight text-foreground">Bitácora</h1>
      <p class="mt-1 text-sm text-foreground-muted">
        Registro inmutable de eventos del sistema ({logs.length} entradas cargadas)
      </p>
    </div>

    <div class="mb-4 flex items-center gap-3">
      <select
        bind:value={actionFilter}
        onchange={applyFilters}
        class="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-foreground focus:border-primary focus:outline-none"
      >
        <option value="">Todas las acciones</option>
        <option value="LOGIN_SUCCESS">Login exitoso</option>
        <option value="LOGIN_FAILED">Login fallido</option>
        <option value="USER_CREATED">Usuario creado</option>
        <option value="USER_UPDATED">Usuario actualizado</option>
        <option value="USER_DEACTIVATED">Usuario desactivado</option>
      </select>
      <select
        bind:value={statusFilter}
        onchange={applyFilters}
        class="rounded-lg border border-border bg-surface px-3 py-2 text-sm text-foreground focus:border-primary focus:outline-none"
      >
        <option value="">Todos los estados</option>
        <option value="success">Éxito</option>
        <option value="failure">Fallo</option>
      </select>
    </div>

    {#if error}
      <div class="mb-4 rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger" role="alert">{error}</div>
    {/if}

    <Card class="overflow-hidden p-0">
      {#if loading && logs.length === 0}
        <div class="flex items-center justify-center py-16"><p class="text-sm text-foreground-muted">Cargando bitácora...</p></div>
      {:else if logs.length === 0}
        <div class="flex flex-col items-center justify-center py-16"><p class="text-sm text-foreground-muted">No hay entradas para los filtros seleccionados.</p></div>
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="border-b border-border bg-surface-muted">
              <tr>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Fecha</th>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Acción</th>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Estado</th>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Recurso</th>
                <th class="px-4 py-3 text-left font-semibold text-foreground">IP</th>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Detalle</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border">
              {#each logs as entry (entry.id)}
                <tr class="cursor-pointer hover:bg-surface-muted" onclick={() => toggleRow(entry.id)}>
                  <td class="px-4 py-3 text-foreground-muted whitespace-nowrap">
                    {new Date(entry.created_at).toLocaleString('es-ES')}
                  </td>
                  <td class="px-4 py-3">
                    <span class="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-xs font-medium {actionBadge(entry.action)}">
                      {entry.action}
                    </span>
                  </td>
                  <td class="px-4 py-3">
                    <span class="text-xs {entry.status === 'success' ? 'text-success' : 'text-danger'}">
                      {entry.status}
                    </span>
                  </td>
                  <td class="px-4 py-3 text-foreground-muted">
                    {entry.resource_type ?? '—'}
                    {#if entry.resource_id} / <span class="font-mono text-xs">{entry.resource_id.slice(0, 8)}</span>{/if}
                  </td>
                  <td class="px-4 py-3 font-mono text-xs text-foreground-muted">{entry.ip_address ?? '—'}</td>
                  <td class="px-4 py-3 text-foreground-muted text-xs">
                    {#if entry.before_state || entry.after_state}
                      <span class="text-primary">diff</span>
                    {:else}
                      {#if entry.metadata}
                        <span class="text-foreground-muted">{JSON.stringify(entry.metadata).slice(0, 40)}...</span>
                      {:else}
                        —
                      {/if}
                    {/if}
                  </td>
                </tr>
                {#if expandedRow === entry.id}
                  <tr>
                    <td colspan="6" class="bg-surface-muted px-4 py-4">
                      <div class="grid gap-4 md:grid-cols-2">
                        <div>
                          <p class="mb-2 text-xs font-semibold text-foreground">Estado anterior</p>
                          <pre class="overflow-x-auto rounded-lg border border-border bg-surface p-3 text-xs font-mono text-foreground-muted">{formatState(entry.before_state)}</pre>
                        </div>
                        <div>
                          <p class="mb-2 text-xs font-semibold text-foreground">Estado posterior</p>
                          <pre class="overflow-x-auto rounded-lg border border-border bg-surface p-3 text-xs font-mono text-foreground-muted">{formatState(entry.after_state)}</pre>
                        </div>
                      </div>
                      {#if entry.metadata}
                        <div class="mt-3">
                          <p class="mb-1 text-xs font-semibold text-foreground">Metadata</p>
                          <pre class="overflow-x-auto rounded-lg border border-border bg-surface p-3 text-xs font-mono text-foreground-muted">{JSON.stringify(entry.metadata, null, 2)}</pre>
                        </div>
                      {/if}
                      {#if entry.user_agent}
                        <p class="mt-3 text-xs text-foreground-muted">User-Agent: {entry.user_agent}</p>
                      {/if}
                    </td>
                  </tr>
                {/if}
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </Card>

    {#if hasMore}
      <div class="mt-4 text-center">
        <Button variant="secondary" size="sm" onclick={loadMore} disabled={loading}>
          {loading ? 'Cargando...' : 'Cargar más'}
        </Button>
      </div>
    {/if}
  </section>
</main>
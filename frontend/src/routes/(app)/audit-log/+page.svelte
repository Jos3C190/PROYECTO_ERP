<script lang="ts">
  import { api, HttpError, type AuditLogOut, type AuditLogPage } from '$lib/api/client';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';

  let logs = $state<AuditLogOut[]>([]);
  let nextCursor = $state<string | null>(null);
  let hasMore = $state(false);
  let loading = $state(false);
  let loadingMore = $state(false);
  let error = $state<string | null>(null);
  let actionFilter = $state('');
  let statusFilter = $state('');
  let resourceFilter = $state('');

  let modalEntry = $state<AuditLogOut | null>(null);

  const PAGE_SIZE = 20;

  async function loadLogs(cursor?: string) {
    if (cursor) { loadingMore = true; } else { loading = true; }
    error = null;
    try {
      const result: AuditLogPage = await api.audit.list({
        limit: PAGE_SIZE,
        cursor: cursor || undefined,
        action: actionFilter || undefined,
        status: statusFilter || undefined,
        resource_type: resourceFilter || undefined
      });
      logs = cursor ? [...logs, ...result.items] : result.items;
      nextCursor = result.next_cursor;
      hasMore = result.has_more;
    } catch (err) {
      error = err instanceof HttpError ? err.message : 'Error al cargar bitácora.';
    } finally {
      loading = false;
      loadingMore = false;
    }
  }

  function applyFilters() {
    logs = [];
    nextCursor = null;
    hasMore = false;
    loadLogs();
  }

  function loadMore() {
    if (nextCursor && !loadingMore) loadLogs(nextCursor);
  }

  function openDetail(entry: AuditLogOut) {
    modalEntry = entry;
  }

  function closeDetail() {
    modalEntry = null;
  }

  function formatState(state: Record<string, unknown> | null): string {
    if (!state) return '—';
    return JSON.stringify(state, null, 2);
  }

  function actionLabel(action: string): string {
    const map: Record<string, string> = {
      LOGIN_SUCCESS: 'Inicio de sesión exitoso',
      LOGIN_FAILED: 'Intento de login fallido',
      USER_CREATED: 'Usuario creado',
      USER_UPDATED: 'Usuario actualizado',
      USER_DEACTIVATED: 'Usuario desactivado',
      ROLE_ASSIGNED: 'Rol asignado',
      ROLE_REVOKED: 'Rol revocado',
    };
    return map[action] ?? action;
  }

  function actionBadgeClass(action: string): string {
    if (action.includes('SUCCESS')) return 'badge-success';
    if (action.includes('FAILED')) return 'badge-danger';
    if (action.includes('CREATED')) return 'badge-primary';
    if (action.includes('UPDATED') || action.includes('ASSIGNED') || action.includes('REVOKED')) return 'badge-warning';
    return 'badge-neutral';
  }

  function statusLabel(s: string): string {
    return s === 'success' ? 'Éxito' : 'Fallo';
  }

  function timeAgo(iso: string): string {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'hace un momento';
    if (mins < 60) return `hace ${mins}m`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `hace ${hours}h`;
    return `hace ${Math.floor(hours / 24)}d`;
  }

  $effect(() => { loadLogs(); });
</script>

<svelte:head><title>Bitácora — ERP System</title></svelte:head>

<div class="p-6 md:p-8">
  <!-- Header -->
  <div class="mb-6 flex items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-bold tracking-tight text-foreground">Bitácora</h1>
      <p class="mt-1 text-sm text-foreground-muted">
        Registro inmutable de eventos del sistema · {logs.length} entrada(s) cargada{logs.length !== 1 ? 's' : ''}
      </p>
    </div>
    <div class="flex items-center gap-2">
      <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-danger/10">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="text-danger">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
        </svg>
      </div>
    </div>
  </div>

  <!-- Filters -->
  <div class="mb-5 flex flex-wrap items-center gap-3">
    <select bind:value={actionFilter} onchange={applyFilters}
      class="rounded-xl border border-border bg-surface px-3.5 py-2 text-sm text-foreground transition-all focus:border-primary focus:shadow-glow focus:outline-none">
      <option value="">Todas las acciones</option>
      <option value="LOGIN_SUCCESS">Login exitoso</option>
      <option value="LOGIN_FAILED">Login fallido</option>
      <option value="USER_CREATED">Usuario creado</option>
      <option value="USER_UPDATED">Usuario actualizado</option>
      <option value="USER_DEACTIVATED">Usuario desactivado</option>
    </select>
    <select bind:value={statusFilter} onchange={applyFilters}
      class="rounded-xl border border-border bg-surface px-3.5 py-2 text-sm text-foreground transition-all focus:border-primary focus:shadow-glow focus:outline-none">
      <option value="">Todos los estados</option>
      <option value="success">Éxito</option>
      <option value="failure">Fallo</option>
    </select>
    <select bind:value={resourceFilter} onchange={applyFilters}
      class="rounded-xl border border-border bg-surface px-3.5 py-2 text-sm text-foreground transition-all focus:border-primary focus:shadow-glow focus:outline-none">
      <option value="">Todos los recursos</option>
      <option value="auth">Auth</option>
      <option value="user">Usuario</option>
      <option value="role">Rol</option>
      <option value="employee">Empleado</option>
    </select>
  </div>

  {#if error}
    <div class="mb-4 animate-fade-scale rounded-xl border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger" role="alert">{error}</div>
  {/if}

  <!-- Table -->
  <Card class="overflow-hidden p-0">
    {#if loading}
      <div class="space-y-2 p-4">
        {#each Array(8) as _}
          <div class="flex items-center gap-3 py-3">
            <div class="h-3 w-32 rounded skeleton"></div>
            <div class="h-3 flex-1 rounded skeleton"></div>
            <div class="h-3 w-20 rounded skeleton"></div>
            <div class="h-3 w-24 rounded skeleton"></div>
          </div>
        {/each}
      </div>
    {:else if logs.length === 0}
      <div class="flex flex-col items-center justify-center py-16">
        <div class="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-surface-muted">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="text-foreground-subtle">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" />
          </svg>
        </div>
        <p class="text-sm text-foreground-muted">No hay entradas para los filtros seleccionados.</p>
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="border-b border-border bg-surface-muted/50">
            <tr>
              <th class="px-5 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-foreground-subtle">Fecha</th>
              <th class="px-5 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-foreground-subtle">Acción</th>
              <th class="px-5 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-foreground-subtle">Estado</th>
              <th class="px-5 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-foreground-subtle">Recurso</th>
              <th class="px-5 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-foreground-subtle">IP</th>
              <th class="px-5 py-3.5 text-left text-xs font-bold uppercase tracking-wider text-foreground-subtle">Detalle</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            {#each logs as entry (entry.id)}
              <tr
                class="group cursor-pointer transition-colors hover:bg-surface-hover"
                onclick={() => openDetail(entry)}
              >
                <td class="whitespace-nowrap px-5 py-3">
                  <p class="text-sm text-foreground">{new Date(entry.created_at).toLocaleString('es-ES', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}</p>
                  <p class="text-xs text-foreground-subtle">{timeAgo(entry.created_at)}</p>
                </td>
                <td class="px-5 py-3">
                  <span class="{actionBadgeClass(entry.action)} inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-semibold">
                    {entry.action}
                  </span>
                </td>
                <td class="px-5 py-3">
                  {#if entry.status === 'success'}
                    <span class="badge-success inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-semibold">
                      <span class="h-1.5 w-1.5 rounded-full bg-success"></span> Éxito
                    </span>
                  {:else}
                    <span class="badge-danger inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-semibold">
                      <span class="h-1.5 w-1.5 rounded-full bg-danger"></span> Fallo
                    </span>
                  {/if}
                </td>
                <td class="px-5 py-3 text-foreground-muted">
                  {#if entry.resource_type}
                    {entry.resource_type}
                    {#if entry.resource_id}<span class="font-mono text-xs text-foreground-subtle"> / {entry.resource_id.slice(0, 8)}</span>{/if}
                  {:else}
                    —
                  {/if}
                </td>
                <td class="px-5 py-3 font-mono text-xs text-foreground-muted">{entry.ip_address ?? '—'}</td>
                <td class="px-5 py-3">
                  <div class="flex items-center gap-1 text-foreground-subtle transition-colors group-hover:text-primary">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z" /><circle cx="12" cy="12" r="3" /></svg>
                    <span class="text-xs">Ver</span>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>

      <!-- Pagination -->
      {#if hasMore}
        <div class="border-t border-border bg-surface-muted/30 px-5 py-4 text-center">
          <Button variant="secondary" size="sm" onclick={loadMore} disabled={loadingMore}>
            {#if loadingMore}
              <svg class="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-dasharray="60" stroke-dashoffset="20" /></svg>
              Cargando...
            {:else}
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M5 12l7 7 7-7" /></svg>
              Cargar más entradas
            {/if}
          </Button>
        </div>
      {:else if logs.length > 0}
        <div class="border-t border-border bg-surface-muted/30 px-5 py-3 text-center">
          <p class="text-xs text-foreground-subtle">No hay más entradas · Fin del registro</p>
        </div>
      {/if}
    {/if}
  </Card>
</div>

<!-- Detail Modal -->
<Modal open={modalEntry !== null} title="Detalle de evento" onclose={closeDetail} size="lg">
  {#if modalEntry}
    <div class="space-y-5">
      <!-- Action + status header -->
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center rounded-xl {modalEntry.status === 'success' ? 'bg-success/10' : 'bg-danger/10'}">
            {#if modalEntry.status === 'success'}
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="text-success"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></svg>
            {:else}
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="text-danger"><circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" /></svg>
            {/if}
          </div>
          <div>
            <p class="text-base font-bold text-foreground">{actionLabel(modalEntry.action)}</p>
            <p class="text-xs text-foreground-muted">{modalEntry.action}</p>
          </div>
        </div>
        <span class="{actionBadgeClass(modalEntry.action)} rounded-lg px-2.5 py-1 text-xs font-semibold">{statusLabel(modalEntry.status)}</span>
      </div>

      <!-- Metadata grid -->
      <div class="grid grid-cols-2 gap-4 rounded-xl border border-border bg-surface-muted/50 p-4">
        <div>
          <p class="text-xs font-semibold uppercase tracking-wider text-foreground-subtle">Fecha y hora</p>
          <p class="mt-1 text-sm text-foreground">{new Date(modalEntry.created_at).toLocaleString('es-ES')}</p>
        </div>
        <div>
          <p class="text-xs font-semibold uppercase tracking-wider text-foreground-subtle">Usuario ID</p>
          <p class="mt-1 font-mono text-xs text-foreground">{modalEntry.user_id ?? '—'}</p>
        </div>
        <div>
          <p class="text-xs font-semibold uppercase tracking-wider text-foreground-subtle">Recurso</p>
          <p class="mt-1 text-sm text-foreground">{modalEntry.resource_type ?? '—'} {#if modalEntry.resource_id}<span class="font-mono text-xs text-foreground-subtle"> / {modalEntry.resource_id.slice(0, 12)}</span>{/if}</p>
        </div>
        <div>
          <p class="text-xs font-semibold uppercase tracking-wider text-foreground-subtle">Dirección IP</p>
          <p class="mt-1 font-mono text-sm text-foreground">{modalEntry.ip_address ?? '—'}</p>
        </div>
        {#if modalEntry.user_agent}
          <div class="col-span-2">
            <p class="text-xs font-semibold uppercase tracking-wider text-foreground-subtle">User Agent</p>
            <p class="mt-1 text-xs text-foreground-muted break-all">{modalEntry.user_agent}</p>
          </div>
        {/if}
      </div>

      <!-- Before / After diff -->
      {#if modalEntry.before_state || modalEntry.after_state}
        <div class="grid gap-4 md:grid-cols-2">
          <div>
            <div class="mb-2 flex items-center gap-2">
              <span class="badge-danger rounded-lg px-2 py-0.5 text-xs font-semibold">ANTES</span>
              <p class="text-xs text-foreground-subtle">Estado anterior</p>
            </div>
            <pre class="overflow-x-auto rounded-xl border border-border bg-surface p-3 text-xs font-mono text-foreground-muted">{formatState(modalEntry.before_state)}</pre>
          </div>
          <div>
            <div class="mb-2 flex items-center gap-2">
              <span class="badge-success rounded-lg px-2 py-0.5 text-xs font-semibold">DESPUÉS</span>
              <p class="text-xs text-foreground-subtle">Estado posterior</p>
            </div>
            <pre class="overflow-x-auto rounded-xl border border-border bg-surface p-3 text-xs font-mono text-foreground-muted">{formatState(modalEntry.after_state)}</pre>
          </div>
        </div>
      {/if}

      <!-- Metadata -->
      {#if modalEntry.metadata && Object.keys(modalEntry.metadata).length > 0}
        <div>
          <p class="mb-2 text-xs font-semibold uppercase tracking-wider text-foreground-subtle">Metadata adicional</p>
          <pre class="overflow-x-auto rounded-xl border border-border bg-surface-muted/50 p-3 text-xs font-mono text-foreground-muted">{JSON.stringify(modalEntry.metadata, null, 2)}</pre>
        </div>
      {/if}

      <div class="flex justify-end">
        <Button variant="secondary" onclick={closeDetail}>Cerrar</Button>
      </div>
    </div>
  {/if}
</Modal>
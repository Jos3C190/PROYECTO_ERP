<script lang="ts">
  import { api, HttpError, type AuditLogOut, type AuditLogPage } from '$lib/api/client';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';

  let logs = $state<AuditLogOut[]>([]);
  let meta = $state<{ page: number; size: number; total: number; pages: number } | null>(null);
  let loading = $state(false);
  let error = $state<string | null>(null);
  let actionFilter = $state('');
  let statusFilter = $state('');
  let resourceFilter = $state('');
  let page = $state(1);
  let size = $state(20);

  let modalEntry = $state<AuditLogOut | null>(null);

  async function loadLogs() {
    loading = true; error = null;
    try {
      const result: AuditLogPage = await api.audit.list({
        page, size,
        action: actionFilter || undefined,
        status: statusFilter || undefined,
        resource_type: resourceFilter || undefined
      });
      logs = result.items;
      meta = result.meta;
    } catch (err) {
      error = err instanceof HttpError ? err.message : 'Error al cargar bitácora.';
    } finally { loading = false; }
  }

  function applyFilters() { page = 1; loadLogs(); }
  function goToPage(p: number) { if (p < 1 || (meta && p > meta.pages)) return; page = p; loadLogs(); }
  function openDetail(entry: AuditLogOut) { modalEntry = entry; }
  function closeDetail() { modalEntry = null; }
  function formatState(state: Record<string, unknown> | null): string { return state ? JSON.stringify(state, null, 2) : '—'; }
  function actionLabel(action: string): string {
    const map: Record<string, string> = { LOGIN_SUCCESS: 'Inicio de sesión exitoso', LOGIN_FAILED: 'Intento de login fallido', USER_CREATED: 'Usuario creado', USER_UPDATED: 'Usuario actualizado', USER_DEACTIVATED: 'Usuario desactivado', ROLE_ASSIGNED: 'Rol asignado', ROLE_REVOKED: 'Rol revocado' };
    return map[action] ?? action;
  }
  function actionBadgeClass(action: string): string {
    if (action.includes('SUCCESS')) return 'badge-success';
    if (action.includes('FAILED')) return 'badge-danger';
    if (action.includes('CREATED')) return 'badge-primary';
    if (action.includes('UPDATED') || action.includes('ASSIGNED') || action.includes('REVOKED')) return 'badge-warning';
    return 'badge-neutral';
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
  <div class="mb-6 flex items-center justify-between gap-4">
    <div>
      <h1 class="text-2xl font-bold tracking-tight text-foreground">Bitácora</h1>
      <p class="mt-1 text-sm text-foreground-muted">{meta ? `${meta.total} evento(s) en total` : 'Cargando...'}</p>
    </div>
    <div class="flex h-10 w-10 items-center justify-center rounded-xl bg-danger/10">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="text-danger"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" /></svg>
    </div>
  </div>

  <div class="mb-5 flex flex-wrap items-center gap-3">
    <select bind:value={actionFilter} onchange={applyFilters} class="rounded-xl border border-border bg-surface px-3.5 py-2 text-sm text-foreground transition-all focus:border-primary focus:shadow-glow focus:outline-none">
      <option value="">Todas las acciones</option>
      <option value="LOGIN_SUCCESS">Login exitoso</option><option value="LOGIN_FAILED">Login fallido</option>
      <option value="USER_CREATED">Usuario creado</option><option value="USER_UPDATED">Usuario actualizado</option>
    </select>
    <select bind:value={statusFilter} onchange={applyFilters} class="rounded-xl border border-border bg-surface px-3.5 py-2 text-sm text-foreground transition-all focus:border-primary focus:shadow-glow focus:outline-none">
      <option value="">Todos los estados</option><option value="success">Éxito</option><option value="failure">Fallo</option>
    </select>
    <select bind:value={resourceFilter} onchange={applyFilters} class="rounded-xl border border-border bg-surface px-3.5 py-2 text-sm text-foreground transition-all focus:border-primary focus:shadow-glow focus:outline-none">
      <option value="">Todos los recursos</option><option value="auth">Auth</option><option value="user">Usuario</option>
    </select>
  </div>

  {#if error}<div class="mb-4 animate-fade-scale rounded-xl border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger" role="alert">{error}</div>{/if}

  <Card class="overflow-hidden p-0">
    {#if loading}
      <div class="space-y-2 p-4">{#each Array(8) as _}<div class="flex items-center gap-3 py-3"><div class="h-3 w-32 rounded skeleton"></div><div class="h-3 flex-1 rounded skeleton"></div><div class="h-3 w-20 rounded skeleton"></div></div>{/each}</div>
    {:else if logs.length === 0}
      <div class="flex flex-col items-center justify-center py-16"><p class="text-sm text-foreground-muted">No hay entradas para los filtros seleccionados.</p></div>
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
            </tr>
          </thead>
          <tbody class="divide-y divide-border">
            {#each logs as entry (entry.id)}
              <tr class="group cursor-pointer transition-colors hover:bg-surface-hover" onclick={() => openDetail(entry)}>
                <td class="whitespace-nowrap px-5 py-3"><p class="text-sm text-foreground">{new Date(entry.created_at).toLocaleString('es-ES', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })}</p><p class="text-xs text-foreground-subtle">{timeAgo(entry.created_at)}</p></td>
                <td class="px-5 py-3"><span class="{actionBadgeClass(entry.action)} inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-semibold">{entry.action}</span></td>
                <td class="px-5 py-3">{#if entry.status === 'success'}<span class="badge-success inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-semibold"><span class="h-1.5 w-1.5 rounded-full bg-success"></span> Éxito</span>{:else}<span class="badge-danger inline-flex items-center gap-1.5 rounded-lg px-2.5 py-1 text-xs font-semibold"><span class="h-1.5 w-1.5 rounded-full bg-danger"></span> Fallo</span>{/if}</td>
                <td class="px-5 py-3 text-foreground-muted">{entry.resource_type ?? '—'}{#if entry.resource_id}<span class="font-mono text-xs text-foreground-subtle"> / {entry.resource_id.slice(0, 8)}</span>{/if}</td>
                <td class="px-5 py-3 font-mono text-xs text-foreground-muted">{entry.ip_address ?? '—'}</td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </Card>

  {#if meta && meta.pages > 1}
    <div class="mt-4 flex items-center justify-between">
      <p class="text-xs text-foreground-subtle">Página {meta.page} de {meta.pages} · {meta.total} evento(s)</p>
      <div class="flex gap-2">
        <Button variant="secondary" size="sm" onclick={() => goToPage(meta!.page - 1)} disabled={meta!.page <= 1}>Anterior</Button>
        <Button variant="secondary" size="sm" onclick={() => goToPage(meta!.page + 1)} disabled={meta!.page >= meta!.pages}>Siguiente</Button>
      </div>
    </div>
  {/if}
</div>

<Modal open={modalEntry !== null} title="Detalle de evento" onclose={closeDetail} size="lg">
  {#if modalEntry}
    <div class="space-y-5">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="flex h-11 w-11 items-center justify-center rounded-xl {modalEntry.status === 'success' ? 'bg-success/10' : 'bg-danger/10'}">
            {#if modalEntry.status === 'success'}<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="text-success"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></svg>{:else}<svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="text-danger"><circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" /></svg>{/if}
          </div>
          <div><p class="text-base font-bold text-foreground">{actionLabel(modalEntry.action)}</p><p class="text-xs text-foreground-muted">{modalEntry.action}</p></div>
        </div>
      </div>
      <div class="grid grid-cols-2 gap-4 rounded-xl border border-border bg-surface-muted/50 p-4">
        <div><p class="text-xs font-semibold uppercase tracking-wider text-foreground-subtle">Fecha y hora</p><p class="mt-1 text-sm text-foreground">{new Date(modalEntry.created_at).toLocaleString('es-ES')}</p></div>
        <div><p class="text-xs font-semibold uppercase tracking-wider text-foreground-subtle">Usuario ID</p><p class="mt-1 font-mono text-xs text-foreground">{modalEntry.user_id ?? '—'}</p></div>
        <div><p class="text-xs font-semibold uppercase tracking-wider text-foreground-subtle">Recurso</p><p class="mt-1 text-sm text-foreground">{modalEntry.resource_type ?? '—'}{#if modalEntry.resource_id}<span class="font-mono text-xs text-foreground-subtle"> / {modalEntry.resource_id.slice(0, 12)}</span>{/if}</p></div>
        <div><p class="text-xs font-semibold uppercase tracking-wider text-foreground-subtle">IP</p><p class="mt-1 font-mono text-sm text-foreground">{modalEntry.ip_address ?? '—'}</p></div>
        {#if modalEntry.user_agent}<div class="col-span-2"><p class="text-xs font-semibold uppercase tracking-wider text-foreground-subtle">User Agent</p><p class="mt-1 text-xs text-foreground-muted break-all">{modalEntry.user_agent}</p></div>{/if}
      </div>
      {#if modalEntry.before_state || modalEntry.after_state}
        <div class="grid gap-4 md:grid-cols-2">
          <div><div class="mb-2 flex items-center gap-2"><span class="badge-danger rounded-lg px-2 py-0.5 text-xs font-semibold">ANTES</span></div><pre class="overflow-x-auto rounded-xl border border-border bg-surface p-3 text-xs font-mono text-foreground-muted">{formatState(modalEntry.before_state)}</pre></div>
          <div><div class="mb-2 flex items-center gap-2"><span class="badge-success rounded-lg px-2 py-0.5 text-xs font-semibold">DESPUÉS</span></div><pre class="overflow-x-auto rounded-xl border border-border bg-surface p-3 text-xs font-mono text-foreground-muted">{formatState(modalEntry.after_state)}</pre></div>
        </div>
      {/if}
      {#if modalEntry.metadata && Object.keys(modalEntry.metadata).length > 0}
        <div><p class="mb-2 text-xs font-semibold uppercase tracking-wider text-foreground-subtle">Metadata</p><pre class="overflow-x-auto rounded-xl border border-border bg-surface-muted/50 p-3 text-xs font-mono text-foreground-muted">{JSON.stringify(modalEntry.metadata, null, 2)}</pre></div>
      {/if}
      <div class="flex justify-end"><Button variant="secondary" onclick={closeDetail}>Cerrar</Button></div>
    </div>
  {/if}
</Modal>
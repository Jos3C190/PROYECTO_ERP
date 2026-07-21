<script lang="ts">
  import { session } from '$lib/stores/session.svelte';
  import { api, type AuditLogOut } from '$lib/api/client';
  import Card from '$lib/components/ui/Card.svelte';

  const MOCK_DATA = true; // KPIs are mock; activity is real from audit-log

  const kpis = [
    { label: 'Ventas del mes', value: '$48,250', change: '+12.5%', trend: 'up' },
    { label: 'Compras del mes', value: '$32,800', change: '-3.2%', trend: 'down' },
    { label: 'Empleados activos', value: '47', change: '+2', trend: 'up' },
    { label: 'Productos en stock', value: '1,284', change: '+58', trend: 'up' },
  ];

  let recentActivity = $state<AuditLogOut[]>([]);
  let loadingActivity = $state(false);

  async function loadActivity() {
    loadingActivity = true;
    try {
      const result = await api.audit.list({ limit: 8 });
      recentActivity = result.items;
    } catch {
      // user may not have audit_log:read permission — that's fine
    } finally {
      loadingActivity = false;
    }
  }

  function actionLabel(action: string): string {
    const map: Record<string, string> = {
      LOGIN_SUCCESS: 'Inicio de sesión',
      LOGIN_FAILED: 'Intento de login fallido',
      USER_CREATED: 'Usuario creado',
      USER_UPDATED: 'Usuario actualizado',
      USER_DEACTIVATED: 'Usuario desactivado',
    };
    return map[action] ?? action;
  }

  function timeAgo(iso: string): string {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'hace un momento';
    if (mins < 60) return `hace ${mins} min`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `hace ${hours} h`;
    return `hace ${Math.floor(hours / 24)} d`;
  }

  $effect(() => { loadActivity(); });
</script>

<svelte:head><title>Dashboard — ERP System</title></svelte:head>

<div class="p-6 md:p-8">
  <div class="mb-8">
    <h1 class="text-2xl font-bold tracking-tight text-foreground">
      Bienvenido, {session.user?.username ?? ''}
    </h1>
    <p class="mt-1 text-sm text-foreground-muted">
      {session.user?.is_superuser ? 'Super Administrador' : 'Usuario'} · {new Date().toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long' })}
    </p>
  </div>

  {#if MOCK_DATA}
    <p class="mb-4 text-xs text-foreground-muted">
      Las métricas siguientes son datos simulados para demostración. La actividad reciente es real (desde la bitácora).
    </p>
  {/if}

  <!-- KPIs -->
  <div class="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
    {#each kpis as kpi (kpi.label)}
      <Card>
        <p class="text-xs font-medium text-foreground-muted">{kpi.label}</p>
        <p class="mt-2 text-2xl font-bold text-foreground">{kpi.value}</p>
        <p class="mt-1 text-xs {kpi.trend === 'up' ? 'text-success' : 'text-danger'}">
          {kpi.change} vs. mes anterior
        </p>
      </Card>
    {/each}
  </div>

  <div class="grid gap-6 lg:grid-cols-2">
    <!-- Recent activity (real, from audit log) -->
    <Card title="Actividad reciente">
      {#if loadingActivity}
        <p class="py-8 text-center text-sm text-foreground-muted">Cargando...</p>
      {:else if recentActivity.length === 0}
        <p class="py-8 text-center text-sm text-foreground-muted">
          No hay actividad reciente visible{#if !session.user?.is_superuser} (requiere permiso audit_log:read){/if}.
        </p>
      {:else}
        <ul class="space-y-3">
          {#each recentActivity as entry (entry.id)}
            <li class="flex items-start gap-3">
              <span class="mt-1.5 h-2 w-2 flex-none rounded-full {entry.status === 'success' ? 'bg-success' : 'bg-danger'}"></span>
              <div class="min-w-0 flex-1">
                <p class="text-sm text-foreground">{actionLabel(entry.action)}</p>
                <p class="text-xs text-foreground-muted">
                  {timeAgo(entry.created_at)} · {entry.ip_address ?? '—'}
                </p>
              </div>
            </li>
          {/each}
        </ul>
      {/if}
    </Card>

    <!-- User profile card -->
    <Card title="Mi perfil">
      <dl class="space-y-3 text-sm">
        <div class="flex justify-between">
          <dt class="text-foreground-muted">Usuario</dt>
          <dd class="font-medium text-foreground">{session.user?.username}</dd>
        </div>
        <div class="flex justify-between">
          <dt class="text-foreground-muted">Correo</dt>
          <dd class="text-foreground">{session.user?.email}</dd>
        </div>
        <div class="flex justify-between">
          <dt class="text-foreground-muted">Rol</dt>
          <dd class="text-foreground">{session.user?.is_superuser ? 'Super Admin' : 'Usuario'}</dd>
        </div>
        <div class="flex justify-between">
          <dt class="text-foreground-muted">Estado</dt>
          <dd class="text-foreground">{session.user?.is_active ? 'Activo' : 'Inactivo'}</dd>
        </div>
        <div class="flex justify-between">
          <dt class="text-foreground-muted">Último login</dt>
          <dd class="text-foreground">{session.user?.last_login_at ? new Date(session.user.last_login_at).toLocaleString('es-ES') : '—'}</dd>
        </div>
      </dl>
    </Card>
  </div>
</div>
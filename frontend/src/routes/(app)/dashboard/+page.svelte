<script lang="ts">
  import { session } from '$lib/stores/session.svelte';
  import { api, type AuditLogOut } from '$lib/api/client';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const MOCK_DATA = true;

  const kpis = [
    { label: 'Ventas del mes', value: '$48,250', change: '+12.5%', trend: 'up', icon: 'M3 3v18h18M7 14l4-4 4 4 6-6' },
    { label: 'Compras del mes', value: '$32,800', change: '-3.2%', trend: 'down', icon: 'M3 3h18v18H3zM3 9h18M9 21V9' },
    { label: 'Empleados activos', value: '47', change: '+2', trend: 'up', icon: 'M17 20h5v-2a4 4 0 0 0-3-3.87M9 20H4v-2a4 4 0 0 1 3-3.87m6-2a4 4 0 1 0-8 0 4 4 0 0 0 8 0z' },
    { label: 'Productos en stock', value: '1,284', change: '+58', trend: 'up', icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4' }
  ];

  let recentActivity = $state<AuditLogOut[]>([]);
  let loadingActivity = $state(false);

  async function loadActivity() {
    loadingActivity = true;
    try {
      const result = await api.audit.list({ limit: 8 });
      recentActivity = result.items;
    } catch {
      // user may not have audit_log:read permission
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
      USER_DEACTIVATED: 'Usuario desactivado'
    };
    return map[action] ?? action;
  }

  function timeAgo(iso: string): string {
    const diff = Date.now() - new Date(iso).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return 'ahora';
    if (mins < 60) return `hace ${mins}m`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `hace ${hours}h`;
    return `hace ${Math.floor(hours / 24)}d`;
  }

  $effect(() => { loadActivity(); });
</script>

<svelte:head><title>Dashboard — ERP System</title></svelte:head>

<div class="p-6 md:p-8">
  <!-- Hero -->
  <div class="mb-8 overflow-hidden rounded-3xl shadow-floating">
    <div class="hero-gradient relative px-6 py-8 md:px-10 md:py-10">
      <div class="relative z-10">
        <h1 class="text-2xl font-bold tracking-tight text-white md:text-3xl">
          Hola, {session.user?.username ?? ''} 👋
        </h1>
        <p class="mt-2 text-sm text-white/80">
          {session.user?.is_superuser ? 'Super Administrador' : 'Usuario'} · {new Date().toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
        </p>
      </div>
      <!-- Decorative circles -->
      <div class="absolute right-0 top-0 -mr-20 -mt-20 h-64 w-64 rounded-full bg-white/10 blur-3xl"></div>
      <div class="absolute bottom-0 right-10 -mb-16 h-48 w-48 rounded-full bg-accent/30 blur-2xl"></div>
    </div>
  </div>

  {#if MOCK_DATA}
    <p class="mb-5 text-xs text-foreground-subtle">
      📊 Las métricas son simuladas. La actividad reciente es real (desde la bitácora).
    </p>
  {/if}

  <!-- KPIs -->
  <div class="mb-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
    {#each kpis as kpi, i (kpi.label)}
      <Card class="p-5 hover-lift animate-fade-scale" >
        <div class="flex items-center justify-between">
          <div class="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="text-primary"><path d={kpi.icon} /></svg>
          </div>
          <span class="text-xs font-semibold {kpi.trend === 'up' ? 'text-success' : 'text-danger'}">
            {kpi.trend === 'up' ? '↑' : '↓'} {kpi.change}
          </span>
        </div>
        <p class="mt-4 text-2xl font-bold tracking-tight text-foreground">{kpi.value}</p>
        <p class="mt-1 text-xs text-foreground-muted">{kpi.label}</p>
      </Card>
    {/each}
  </div>

  <div class="grid gap-6 lg:grid-cols-5">
    <!-- Recent activity -->
    <Card class="lg:col-span-3 p-5">
      <div class="mb-4 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-foreground">Actividad reciente</h3>
        <a href="/audit-log" class="text-xs font-medium text-primary hover:underline">Ver todo →</a>
      </div>
      {#if loadingActivity}
        <div class="space-y-3">
          {#each Array(4) as _}
            <div class="flex items-center gap-3">
              <div class="h-8 w-8 rounded-full skeleton"></div>
              <div class="flex-1"><div class="h-3 w-3/4 rounded skeleton"></div></div>
            </div>
          {/each}
        </div>
      {:else if recentActivity.length === 0}
        <p class="py-8 text-center text-sm text-foreground-muted">
          No hay actividad reciente{#if !session.user?.is_superuser} (requiere permiso audit_log:read){/if}.
        </p>
      {:else}
        <div class="relative">
          <div class="absolute left-4 top-0 h-full w-px bg-border"></div>
          <ul class="space-y-1">
            {#each recentActivity as entry, i (entry.id)}
              <li class="relative flex items-center gap-3 py-2.5">
                <div class="z-10 flex h-8 w-8 flex-none items-center justify-center rounded-full ring-4 ring-surface-elevated {entry.status === 'success' ? 'bg-success/15' : 'bg-danger/15'}">
                  <span class="h-2.5 w-2.5 rounded-full {entry.status === 'success' ? 'bg-success' : 'bg-danger'}"></span>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-medium text-foreground">{actionLabel(entry.action)}</p>
                  <p class="text-xs text-foreground-subtle">{timeAgo(entry.created_at)} · {entry.ip_address ?? '—'}</p>
                </div>
              </li>
            {/each}
          </ul>
        </div>
      {/if}
    </Card>

    <!-- User profile card -->
    <Card class="lg:col-span-2 p-5">
      <h3 class="mb-4 text-sm font-semibold text-foreground">Mi perfil</h3>
      <div class="flex items-center gap-3 mb-5">
        <div class="flex h-14 w-14 items-center justify-center rounded-2xl gradient-bg text-2xl font-bold text-primary-foreground shadow-soft">
          {session.user?.username?.[0]?.toUpperCase() ?? '?'}
        </div>
        <div>
          <p class="text-base font-bold text-foreground">{session.user?.username}</p>
          <p class="text-xs text-foreground-muted">{session.user?.email}</p>
        </div>
      </div>
      <dl class="space-y-2.5 text-sm">
        <div class="flex justify-between"><dt class="text-foreground-muted">Rol</dt><dd class="font-medium text-foreground">{session.user?.is_superuser ? 'Super Admin' : 'Usuario'}</dd></div>
        <div class="flex justify-between"><dt class="text-foreground-muted">Estado</dt>
          <dd>{#if session.user?.is_active}<span class="badge-success inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium"><span class="h-1.5 w-1.5 rounded-full bg-success"></span>Activo</span>{:else}<span class="badge-neutral inline-flex items-center gap-1 rounded-md px-2 py-0.5 text-xs font-medium"><span class="h-1.5 w-1.5 rounded-full bg-foreground-muted"></span>Inactivo</span>{/if}</dd>
        </div>
        <div class="flex justify-between"><dt class="text-foreground-muted">Último login</dt><dd class="text-foreground">{session.user?.last_login_at ? new Date(session.user.last_login_at).toLocaleString('es-ES', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : '—'}</dd></div>
      </dl>
      <div class="mt-5 pt-4 border-t border-border">
        <div class="grid grid-cols-2 gap-2">
          <a href="/users" class="text-center text-xs font-medium text-primary hover:underline">Usuarios</a>
          <a href="/roles" class="text-center text-xs font-medium text-primary hover:underline">Roles</a>
          <a href="/employees" class="text-center text-xs font-medium text-primary hover:underline">Empleados</a>
          <a href="/departments" class="text-center text-xs font-medium text-primary hover:underline">Departamentos</a>
        </div>
      </div>
    </Card>
  </div>
</div>
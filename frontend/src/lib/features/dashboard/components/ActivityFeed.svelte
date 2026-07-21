<script lang="ts">
  /** ActivityFeed — timeline vertical de actividad reciente.
   * Conectado a la bitácora REAL (GET /audit-logs) — único elemento no-mock del dashboard. */

  import { api, type AuditLogOut } from '$lib/api/client';
  import Avatar from '$lib/components/ui/Avatar.svelte';

  let activities = $state<AuditLogOut[]>([]);
  let loading = $state(true);

  async function loadActivity() {
    loading = true;
    try {
      const result = await api.audit.list({ page: 1, size: 8 });
      activities = result.items;
    } catch {
      // user may not have audit_log:read permission
    } finally {
      loading = false;
    }
  }

  function actionLabel(action: string): string {
    const map: Record<string, string> = {
      LOGIN_SUCCESS: 'inició sesión',
      LOGIN_FAILED: 'intentó iniciar sesión',
      USER_CREATED: 'creó un usuario',
      USER_UPDATED: 'actualizó un usuario',
      USER_DEACTIVATED: 'desactivó un usuario',
    };
    return map[action] ?? action.toLowerCase().replace(/_/g, ' ');
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

  function initials(user_id: string | null): string {
    if (!user_id) return 'SY';
    return user_id.slice(0, 2).toUpperCase();
  }

  $effect(() => { loadActivity(); });
</script>

<div class="relative">
  {#if loading}
    <div class="space-y-3">
      {#each Array(5) as _}
        <div class="flex items-center gap-3 py-2">
          <div class="h-7 w-7 rounded-full skeleton"></div>
          <div class="flex-1"><div class="h-3 w-3/4 rounded skeleton"></div></div>
        </div>
      {/each}
    </div>
  {:else if activities.length === 0}
    <p class="py-8 text-center text-sm text-foreground-muted">No hay actividad reciente.</p>
  {:else}
    <div class="absolute left-3.5 top-0 bottom-0 w-px bg-border"></div>
    <ul class="space-y-1">
      {#each activities as entry (entry.id)}
        <li class="relative flex items-start gap-3 py-2">
          <div class="z-10 flex-none">
            <Avatar initials={initials(entry.user_id)} size={28} />
          </div>
          <div class="flex-1 min-w-0 pt-0.5">
            <p class="text-[13px] text-foreground">
              <span class="font-medium">{entry.user_id ? 'Usuario' : 'Sistema'}</span>
              <span class="text-foreground-muted"> {actionLabel(entry.action)}</span>
            </p>
            {#if entry.ip_address}
              <p class="text-[11px] text-foreground-subtle">{entry.ip_address}</p>
            {/if}
          </div>
          <span class="flex-none text-[11px] text-foreground-subtle whitespace-nowrap">{timeAgo(entry.created_at)}</span>
        </li>
      {/each}
    </ul>
  {/if}
</div>
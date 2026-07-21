<script lang="ts">
  import type { Snippet } from 'svelte';
  import { session } from '$lib/stores/session.svelte';
  import { permissions } from '$lib/stores/permissions.svelte';
  import { api } from '$lib/api/client';
  import Sidebar from '$lib/components/ui/Sidebar.svelte';
  import ThemeToggle from '$lib/components/ui/ThemeToggle.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  interface Props {
    children: Snippet;
  }

  let { children }: Props = $props();

  let sidebarCollapsed = $state(false);
  let mobileOpen = $state(false);
  let loading = $state(false);

  async function handleLogout() {
    loading = true;
    try { await api.auth.logout(); } catch { /* ignore */ }
    finally {
      session.clear();
      permissions.clear();
      loading = false;
      window.location.href = '/login';
    }
  }

  function closeMobile() { mobileOpen = false; }
</script>

<div class="flex h-screen overflow-hidden bg-surface">
  <!-- Desktop sidebar -->
  <div class="hidden md:flex">
    <Sidebar collapsed={sidebarCollapsed} />
  </div>

  <!-- Mobile drawer -->
  {#if mobileOpen}
    <div class="fixed inset-0 z-40 md:hidden">
      <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" onclick={closeMobile} role="presentation"></div>
      <div class="absolute left-0 top-0 h-full animate-slide-in">
        <Sidebar onNavigate={closeMobile} />
      </div>
    </div>
  {/if}

  <!-- Main content -->
  <div class="flex flex-1 flex-col overflow-hidden">
    <header class="glass flex items-center justify-between border-b border-border px-4 py-3 md:px-6">
      <div class="flex items-center gap-3">
        <button
          type="button"
          onclick={() => (mobileOpen = true)}
          class="flex h-10 w-10 items-center justify-center rounded-xl text-foreground transition-colors hover:bg-surface-hover md:hidden"
          aria-label="Abrir menú"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="3" y1="12" x2="21" y2="12" /><line x1="3" y1="6" x2="21" y2="6" /><line x1="3" y1="18" x2="21" y2="18" /></svg>
        </button>
        <button
          type="button"
          onclick={() => (sidebarCollapsed = !sidebarCollapsed)}
          class="flex h-10 w-10 items-center justify-center rounded-xl text-foreground transition-all hover:bg-surface-hover md:flex hidden"
          aria-label="Colapsar sidebar"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="transition-transform duration-300 {sidebarCollapsed ? 'rotate-180' : ''}"><polyline points="15 18 9 12 15 6" /></svg>
        </button>
      </div>
      <div class="flex items-center gap-3">
        <span class="hidden text-sm font-medium text-foreground-muted sm:block">{session.user?.email}</span>
        <ThemeToggle />
        <Button variant="secondary" size="sm" onclick={handleLogout} disabled={loading}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9" /></svg>
          {loading ? '...' : 'Salir'}
        </Button>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto bg-surface-muted/30">
      {@render children()}
    </main>
  </div>
</div>
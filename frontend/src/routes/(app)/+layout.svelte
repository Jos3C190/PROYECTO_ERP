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
      <div class="absolute inset-0 bg-black/50" onclick={closeMobile} role="presentation"></div>
      <div class="absolute left-0 top-0 h-full animate-slide-in">
        <Sidebar onNavigate={closeMobile} />
      </div>
    </div>
  {/if}

  <!-- Main content -->
  <div class="flex flex-1 flex-col overflow-hidden">
    <header class="flex h-14 flex-none items-center justify-between border-b border-border bg-surface px-4 md:px-6">
      <!-- Left -->
      <div class="flex items-center gap-2">
        <button
          type="button"
          onclick={() => (mobileOpen = true)}
          class="flex h-8 w-8 items-center justify-center rounded-md text-foreground-muted hover:bg-surface-hover hover:text-foreground md:hidden"
          aria-label="Abrir menú"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="3" y1="6" x2="21" y2="6" /><line x1="3" y1="12" x2="21" y2="12" /><line x1="3" y1="18" x2="21" y2="18" /></svg>
        </button>
        <button
          type="button"
          onclick={() => (sidebarCollapsed = !sidebarCollapsed)}
          class="hidden h-8 w-8 items-center justify-center rounded-md text-foreground-muted hover:bg-surface-hover hover:text-foreground md:flex"
          aria-label="Colapsar sidebar"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="transition-transform duration-200 {sidebarCollapsed ? 'rotate-180' : ''}"><polyline points="15 18 9 12 15 6" /></svg>
        </button>
      </div>

      <!-- Right -->
      <div class="flex items-center gap-2">
        <span class="hidden text-[13px] text-foreground-muted lg:block">{session.user?.email}</span>
        <ThemeToggle />
        <Button variant="secondary" size="sm" onclick={handleLogout} disabled={loading}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9" /></svg>
          <span class="hidden sm:inline">{loading ? '...' : 'Salir'}</span>
        </Button>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto">
      {@render children()}
    </main>
  </div>
</div>
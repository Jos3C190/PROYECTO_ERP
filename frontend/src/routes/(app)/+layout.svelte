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

  function closeMobile() {
    mobileOpen = false;
  }
</script>

<div class="flex h-screen overflow-hidden bg-surface-muted">
  <!-- Desktop sidebar -->
  <div class="hidden md:flex">
    <Sidebar collapsed={sidebarCollapsed} />
  </div>

  <!-- Mobile drawer -->
  {#if mobileOpen}
    <div class="fixed inset-0 z-40 md:hidden">
      <div class="absolute inset-0 bg-black/50" onclick={closeMobile} role="presentation"></div>
      <div class="absolute left-0 top-0 h-full">
        <Sidebar onNavigate={closeMobile} />
      </div>
    </div>
  {/if}

  <!-- Main content -->
  <div class="flex flex-1 flex-col overflow-hidden">
    <header class="flex items-center justify-between border-b border-border bg-surface px-4 py-3 md:px-6">
      <div class="flex items-center gap-3">
        <!-- Mobile menu button -->
        <button
          type="button"
          onclick={() => (mobileOpen = true)}
          class="rounded-lg p-2 text-foreground hover:bg-surface-muted md:hidden"
          aria-label="Abrir menú"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <line x1="3" y1="12" x2="21" y2="12" /><line x1="3" y1="6" x2="21" y2="6" /><line x1="3" y1="18" x2="21" y2="18" />
          </svg>
        </button>
        <!-- Desktop collapse button -->
        <button
          type="button"
          onclick={() => (sidebarCollapsed = !sidebarCollapsed)}
          class="hidden rounded-lg p-2 text-foreground hover:bg-surface-muted md:block"
          aria-label="Colapsar sidebar"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="transition-transform {sidebarCollapsed ? 'rotate-180' : ''}">
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>
      </div>
      <div class="flex items-center gap-3">
        <span class="hidden text-sm text-foreground-muted sm:block">{session.user?.email}</span>
        <ThemeToggle />
        <Button variant="secondary" size="sm" onclick={handleLogout} disabled={loading}>
          {loading ? '...' : 'Salir'}
        </Button>
      </div>
    </header>

    <main class="flex-1 overflow-y-auto">
      {@render children()}
    </main>
  </div>
</div>
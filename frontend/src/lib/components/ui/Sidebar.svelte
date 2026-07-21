<script lang="ts">
  import { page } from '$app/state';
  import { NAV_GROUPS, type NavItem } from '$lib/navigation';
  import { permissions } from '$lib/stores/permissions.svelte';
  import { session } from '$lib/stores/session.svelte';

  interface Props {
    collapsed?: boolean;
    onNavigate?: () => void;
  }

  let { collapsed = false, onNavigate }: Props = $props();

  function isVisible(item: NavItem): boolean {
    if (!item.requiredPermission) return true;
    return permissions.hasPermission(item.requiredPermission);
  }

  function isActive(route: string): boolean {
    return page.url.pathname === route;
  }

  function handleClick() {
    onNavigate?.();
  }
</script>

<aside
  class="flex h-full flex-col border-r border-border glass transition-all duration-300 {collapsed ? 'w-16' : 'w-64'}"
  role="navigation"
  aria-label="Navegación principal"
>
  <div class="flex items-center gap-3 border-b border-border px-4 py-4 {collapsed ? 'justify-center' : ''}">
    <div class="flex h-9 w-9 flex-none items-center justify-center rounded-xl gradient-bg text-primary-foreground shadow-soft">
      <span class="text-lg font-bold">E</span>
    </div>
    {#if !collapsed}
      <div class="min-w-0">
        <p class="truncate text-sm font-bold leading-tight text-foreground">ERP System</p>
        <p class="truncate text-xs text-foreground-subtle">{session.user?.username ?? '...'}</p>
      </div>
    {/if}
  </div>

  <nav class="flex-1 overflow-y-auto px-2 py-3">
    {#each NAV_GROUPS as group (group.label)}
      {#if group.items.some(isVisible)}
        {#if !collapsed}
          <p class="px-3 py-2 text-[10px] font-bold uppercase tracking-widest text-foreground-subtle">{group.label}</p>
        {:else}
          <div class="mx-2 my-2 border-t border-border"></div>
        {/if}
        {#each group.items as item (item.route)}
          {#if isVisible(item)}
            <a
              href={item.route}
              onclick={handleClick}
              class="group relative flex items-center gap-3 rounded-xl px-3 py-2 text-sm transition-all duration-200 {isActive(item.route) ? 'bg-primary/10 font-semibold text-primary shadow-soft' : 'text-foreground-muted hover:bg-surface-hover hover:text-foreground'} {collapsed ? 'justify-center' : ''}"
              title={collapsed ? item.label : ''}
              aria-current={isActive(item.route) ? 'page' : undefined}
            >
              {#if isActive(item.route)}
                <div class="absolute left-0 top-1/2 h-6 -translate-y-1/2 rounded-r-full bg-primary" style="width: 3px;"></div>
              {/if}
              <svg class="flex-none transition-transform duration-200 group-hover:scale-110" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d={item.icon} />
              </svg>
              {#if !collapsed}
                <span class="truncate">{item.label}</span>
                {#if !item.implemented}
                  <span class="ml-auto flex-none rounded-md bg-foreground-muted/10 px-1.5 py-0.5 text-[10px] font-medium text-foreground-subtle">próx.</span>
                {/if}
              {/if}
            </a>
          {/if}
        {/each}
      {/if}
    {/each}
  </nav>
</aside>
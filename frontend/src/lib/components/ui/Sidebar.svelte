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
  class="flex h-full flex-col border-r border-border bg-surface transition-all duration-200 {collapsed ? 'w-16' : 'w-64'}"
>
  <div class="flex items-center gap-3 border-b border-border px-4 py-4 {collapsed ? 'justify-center' : ''}">
    <div class="flex h-9 w-9 flex-none items-center justify-center rounded-lg bg-primary text-primary-foreground">
      <span class="font-bold">E</span>
    </div>
    {#if !collapsed}
      <div class="min-w-0">
        <p class="truncate text-sm font-semibold leading-tight text-foreground">ERP System</p>
        <p class="truncate text-xs text-foreground-muted">{session.user?.username ?? '...'}</p>
      </div>
    {/if}
  </div>

  <nav class="flex-1 overflow-y-auto py-2">
    {#each NAV_GROUPS as group (group.label)}
      {#if group.items.some(isVisible)}
        {#if !collapsed}
          <p class="px-4 py-2 text-xs font-semibold uppercase tracking-wider text-foreground-muted">{group.label}</p>
        {:else}
          <div class="mx-3 my-2 border-t border-border"></div>
        {/if}
        {#each group.items as item (item.route)}
          {#if isVisible(item)}
            <a
              href={item.route}
              onclick={handleClick}
              class="flex items-center gap-3 px-4 py-2 text-sm transition-colors hover:bg-surface-muted {isActive(item.route) ? 'bg-surface-muted font-medium text-primary' : 'text-foreground'} {collapsed ? 'justify-center' : ''}"
              title={collapsed ? item.label : ''}
            >
              <svg class="flex-none" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d={item.icon} />
              </svg>
              {#if !collapsed}
                <span class="truncate">{item.label}</span>
                {#if !item.implemented}
                  <span class="ml-auto flex-none rounded bg-foreground-muted/10 px-1.5 py-0.5 text-xs text-foreground-muted">próx.</span>
                {/if}
              {/if}
            </a>
          {/if}
        {/each}
      {/if}
    {/each}
  </nav>
</aside>
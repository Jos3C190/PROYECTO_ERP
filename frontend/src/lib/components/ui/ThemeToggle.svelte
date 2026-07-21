<script lang="ts">
  import { theme } from '$lib/stores/theme.svelte';

  let label = $derived(theme.current === 'dark' ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro');
</script>

<button
  type="button"
  onclick={() => theme.toggle()}
  aria-label={label}
  title={label}
  class="relative flex h-10 w-10 items-center justify-center rounded-xl border border-border bg-surface-elevated text-foreground transition-all duration-200 hover:bg-surface-hover hover:shadow-soft focus-visible:shadow-glow"
>
  <div class="transition-transform duration-300" style="transform: {theme.current === 'dark' ? 'rotate(0deg)' : 'rotate(180deg)'}">
    {#if theme.current === 'dark'}
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="text-warning">
        <circle cx="12" cy="12" r="4" />
        <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41" />
      </svg>
    {:else}
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="text-primary">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
      </svg>
    {/if}
  </div>
</button>
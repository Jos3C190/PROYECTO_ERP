<script lang="ts">
  import type { Snippet } from 'svelte';
  import Button from './Button.svelte';

  interface Props {
    open: boolean;
    title: string;
    onclose?: () => void;
    children: Snippet;
    footer?: Snippet;
    size?: 'sm' | 'md' | 'lg';
  }

  let { open, title, onclose, children, footer, size = 'md' }: Props = $props();

  let sizes: Record<string, string> = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl'
  };

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape' && open) {
      e.preventDefault();
      onclose?.();
    }
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
  <div class="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-black/50 p-4 pt-20" role="presentation" onclick={() => onclose?.()}>
    <div
      class="w-full {sizes[size]} rounded-2xl border border-border bg-surface shadow-xl"
      role="dialog"
      aria-modal="true"
      aria-label={title}
      onclick={(e) => e.stopPropagation()}
      tabindex="-1"
    >
      <div class="flex items-center justify-between border-b border-border px-5 py-3">
        <h2 class="text-base font-semibold text-foreground">{title}</h2>
        <button
          type="button"
          onclick={() => onclose?.()}
          class="rounded-lg p-1.5 text-foreground-muted hover:bg-surface-muted hover:text-foreground"
          aria-label="Cerrar"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
        </button>
      </div>
      <div class="px-5 py-4">
        {@render children()}
      </div>
      {#if footer}
        <div class="flex items-center justify-end gap-2 border-t border-border px-5 py-3">
          {@render footer()}
        </div>
      {/if}
    </div>
  </div>
{/if}
<script lang="ts">
  import type { Snippet } from 'svelte';

  interface Props {
    title?: string;
    children: Snippet;
    class?: string;
  }

  let { title, children, class: className = '' }: Props = $props();
</script>

<div class={`rounded-2xl border border-border bg-surface p-6 shadow-sm ${className}`}>
  {#if title}
    <h3 class="mb-3 text-base font-semibold text-foreground">{title}</h3>
  {/if}
  {@render children()}
</div>
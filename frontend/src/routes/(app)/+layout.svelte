<script lang="ts">
  import type { Snippet } from 'svelte';
  import type { LayoutData } from './$types';

  interface Props {
    children: Snippet;
    data: LayoutData;
  }

  let { children }: Props = $props();
</script>

{@render children()}
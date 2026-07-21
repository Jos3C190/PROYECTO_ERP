<script lang="ts">
  /** Avatar — avatar circular con fallback de iniciales sobre fondo determinístico. */

  interface Props {
    initials: string;
    size?: number;
  }

  let { initials, size = 28 }: Props = $props();

  // Color determinístico por iniciales
  let bg = $derived.by(() => {
    const palette = [
      '0 112 243', '0 168 150', '237 151 39', '99 102 241', '239 68 68', '16 185 129', '168 85 247', '14 165 233',
    ];
    let hash = 0;
    for (const c of initials) hash = (hash * 31 + c.charCodeAt(0)) & 0xffffffff;
    return palette[Math.abs(hash) % palette.length];
  });
</script>

<div
  class="flex flex-none items-center justify-center rounded-full font-medium text-white ring-2 ring-surface-elevated"
  style="width: {size}px; height: {size}px; background: rgb({bg}); font-size: {size * 0.36}px;"
  aria-label={initials}
>
  {initials}
</div>
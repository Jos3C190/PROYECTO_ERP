<script lang="ts">
  /** AreaChart — gráfico de área SVG con gradiente, grid sutil y tooltip al hover.
   * Datos por props, sin lógica de negocio. */

  interface Props {
    data: { date: string; value: number }[];
    label: string;
    height?: number;
  }

  let { data, label, height = 200 }: Props = $props();

  let hovered = $state<number | null>(null);
  let containerWidth = $state(600);
  let containerEl: HTMLElement | null = $state(null);

  const W = 600;
  const H = height;
  const PAD = { top: 10, right: 10, bottom: 28, left: 36 };
  const chartW = W - PAD.left - PAD.right;
  const chartH = H - PAD.top - PAD.bottom;

  let max = $derived(Math.max(...data.map(d => d.value)) * 1.1);
  let min = $derived(Math.min(...data.map(d => d.value)) * 0.9);
  let range = $derived(max - min || 1);

  let stepX = $derived(chartW / Math.max(data.length - 1, 1));

  let linePath = $derived.by(() => {
    return data.map((d, i) => {
      const x = PAD.left + i * stepX;
      const y = PAD.top + chartH - ((d.value - min) / range) * chartH;
      return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(' ');
  });

  let areaPath = $derived(`${linePath} L${PAD.left + chartW},${PAD.top + chartH} L${PAD.left},${PAD.top + chartH} Z`);

  let gridLines = $derived.by(() => {
    const lines: number[] = [];
    for (let i = 0; i <= 4; i++) {
      lines.push(PAD.top + (chartH / 4) * i);
    }
    return lines;
  });

  let xLabels = $derived.by(() => {
    const n = data.length;
    const indices = n <= 7 ? data.map((_, i) => i) : [0, Math.floor(n / 4), Math.floor(n / 2), Math.floor(n * 3 / 4), n - 1];
    return indices.map(i => ({
      x: PAD.left + i * stepX,
      label: new Date(data[i].date).toLocaleDateString('es-ES', { day: '2-digit', month: 'short' }),
    }));
  });

  function onMove(e: MouseEvent) {
    if (!containerEl) return;
    const rect = containerEl.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * W;
    const idx = Math.round((x - PAD.left) / stepX);
    hovered = Math.max(0, Math.min(data.length - 1, idx));
  }

  let hoverX = $derived(hovered !== null ? PAD.left + hovered * stepX : 0);
  let hoverY = $derived(hovered !== null ? PAD.top + chartH - ((data[hovered].value - min) / range) * chartH : 0);
</script>

<div class="relative" bind:this={containerEl} onmousemove={onMousemove} onmouseleave={() => hovered = null}>
  <svg viewBox={`0 0 ${W} ${H}`} class="w-full" style="height: {H}px" aria-label="{label}: tendencia de {data.length} días">
    <defs>
      <linearGradient id="area-grad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="rgb(var(--primary))" stop-opacity="0.15" />
        <stop offset="100%" stop-color="rgb(var(--primary))" stop-opacity="0" />
      </linearGradient>
    </defs>

    <!-- Grid lines -->
    {#each gridLines as y (y)}
      <line x1={PAD.left} y1={y} x2={PAD.left + chartW} y2={y} stroke="rgb(var(--border))" stroke-width="1" stroke-dasharray="2,4" />
    {/each}

    <!-- Y axis labels -->
    {#each gridLines as y, i (y)}
      <text x={PAD.left - 6} y={y + 3} text-anchor="end" class="fill-foreground-subtle" style="font-size: 10px; font-family: var(--font-mono, monospace); font-variant-numeric: tabular-nums;">
        {Math.round(max - (range / 4) * i)}
      </text>
    {/each}

    <!-- Area -->
    <path d={areaPath} fill="url(#area-grad)" />

    <!-- Line -->
    <path d={linePath} fill="none" stroke="rgb(var(--primary))" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />

    <!-- X labels -->
    {#each xLabels as xl (xl.label)}
      <text x={xl.x} y={H - 8} text-anchor="middle" class="fill-foreground-subtle" style="font-size: 10px;">{xl.label}</text>
    {/each}

    <!-- Hover -->
    {#if hovered !== null}
      <line x1={hoverX} y1={PAD.top} x2={hoverX} y2={PAD.top + chartH} stroke="rgb(var(--primary))" stroke-width="1" stroke-dasharray="3,3" opacity="0.5" />
      <circle cx={hoverX} cy={hoverY} r="4" fill="rgb(var(--primary))" stroke="rgb(var(--surface-elevated))" stroke-width="2" />
    {/if}
  </svg>

  <!-- Tooltip -->
  {#if hovered !== null}
    <div class="pointer-events-none absolute z-10 rounded-lg border border-border bg-surface-elevated px-3 py-2 shadow-lifted" style="left: {(hoverX / W) * 100}%; top: {(hoverY / H) * 100}%; transform: translate(-50%, -120%);">
      <p class="text-[10px] text-foreground-subtle">{new Date(data[hovered].date).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })}</p>
      <p class="font-mono text-sm font-bold tabular-nums text-foreground">{data[hovered].value.toLocaleString()}</p>
    </div>
  {/if}
</div>
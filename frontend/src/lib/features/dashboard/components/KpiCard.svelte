<script lang="ts">
  /** KpiCard — tarjeta de KPI con sparkline SVG, tendencia e icono.
   * Recibe todos los datos por props, sin lógica de negocio. */

  interface Props {
    label: string;
    value: number;
    prefix?: string;
    suffix?: string;
    change: number;
    sparkline: number[];
    icon: string;
  }

  let { label, value, prefix = '', suffix = '', change, sparkline, icon }: Props = $props();

  let isPositive = $derived(change >= 0);

  // Sparkline SVG path
  let sparkPath = $derived.by(() => {
    const w = 80;
    const h = 24;
    const max = Math.max(...sparkline);
    const min = Math.min(...sparkline);
    const range = max - min || 1;
    const step = w / (sparkline.length - 1);
    return sparkline
      .map((v, i) => {
        const x = i * step;
        const y = h - ((v - min) / range) * h;
        return `${i === 0 ? 'M' : 'L'}${x.toFixed(1)},${y.toFixed(1)}`;
      })
      .join(' ');
  });

  let sparkArea = $derived.by(() => {
    return `${sparkPath} L${80},${24} L0,${24} Z`;
  });
</script>

<div class="rounded-xl border border-border bg-surface-elevated p-5 transition-all duration-150 hover-lift">
  <div class="flex items-start justify-between">
    <div>
      <p class="text-[11px] font-medium uppercase tracking-wide text-foreground-subtle">{label}</p>
      <p class="mt-2 font-mono text-2xl font-bold tabular-nums text-foreground">
        {prefix}{value.toLocaleString()}{suffix}
      </p>
    </div>
    <div class="flex h-8 w-8 flex-none items-center justify-center rounded-lg bg-surface-muted">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="text-foreground-muted"><path d={icon} /></svg>
    </div>
  </div>

  <div class="mt-3 flex items-end justify-between">
    <div class="flex items-center gap-1.5">
      <span class="inline-flex items-center gap-0.5 rounded-md px-1.5 py-0.5 text-xs font-semibold {isPositive ? 'badge-success' : 'badge-danger'}">
        {#if isPositive}
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" aria-hidden="true"><path d="M7 17L17 7M17 7H8M17 7v9" /></svg>
        {:else}
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" aria-hidden="true"><path d="M17 7L7 17M7 17h9M7 17V8" /></svg>
        {/if}
        {Math.abs(change)}%
      </span>
      <span class="text-[11px] text-foreground-subtle">vs. mes anterior</span>
    </div>

    <svg width="80" height="24" viewBox="0 0 80 24" class="flex-none" aria-hidden="true">
      <defs>
        <linearGradient id="spark-{label.replace(/\s/g, '')}" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="rgb(var(--primary))" stop-opacity="0.2" />
          <stop offset="100%" stop-color="rgb(var(--primary))" stop-opacity="0" />
        </linearGradient>
      </defs>
      <path d={sparkArea} fill="url(#spark-{label.replace(/\s/g, '')})" />
      <path d={sparkPath} fill="none" stroke="rgb(var(--primary))" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
  </div>
</div>
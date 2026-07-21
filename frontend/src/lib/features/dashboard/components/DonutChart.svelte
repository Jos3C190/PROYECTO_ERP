<script lang="ts">
  /** DonutChart — gráfico de dona SVG con leyenda lateral.
   * Recibe datos por props: label, value, color (RGB triplet). */

  interface Props {
    data: { label: string; value: number; color: string }[];
    size?: number;
  }

  let { data, size = 140 }: Props = $props();

  let total = $derived(data.reduce((s, d) => s + d.value, 0) || 1);
  let radius = $derived(size / 2 - 12);
  let circumference = $derived(2 * Math.PI * radius);

  let segments = $derived.by(() => {
    let offset = 0;
    return data.map(d => {
      const fraction = d.value / total;
      const dash = fraction * circumference;
      const seg = {
        ...d,
        dash,
        gap: circumference - dash,
        offset: -offset,
        percent: Math.round(fraction * 100),
      };
      offset += dash;
      return seg;
    });
  });
</script>

<div class="flex items-center gap-5">
  <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} class="flex-none" aria-label="Distribución por departamento">
    <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="rgb(var(--surface-muted))" stroke-width="16" />
    {#each segments as seg (seg.label)}
      <circle
        cx={size / 2}
        cy={size / 2}
        r={radius}
        fill="none"
        stroke={`rgb(${seg.color})`}
        stroke-width="16"
        stroke-dasharray={`${seg.dash} ${seg.gap}`}
        stroke-dashoffset={seg.offset}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
        stroke-linecap="butt"
      />
    {/each}
    <text x={size / 2} y={size / 2 - 4} text-anchor="middle" class="fill-foreground font-mono" style="font-size: 18px; font-weight: 700; font-variant-numeric: tabular-nums;">{total}</text>
    <text x={size / 2} y={size / 2 + 12} text-anchor="middle" class="fill-foreground-subtle" style="font-size: 9px; text-transform: uppercase; letter-spacing: 0.05em;">total</text>
  </svg>

  <div class="flex-1 space-y-2">
    {#each segments as seg (seg.label)}
      <div class="flex items-center gap-2">
        <span class="h-2.5 w-2.5 flex-none rounded-sm" style="background: rgb({seg.color});"></span>
        <span class="flex-1 truncate text-xs text-foreground">{seg.label}</span>
        <span class="font-mono text-xs font-medium tabular-nums text-foreground-muted">{seg.value} · {seg.percent}%</span>
      </div>
    {/each}
  </div>
</div>
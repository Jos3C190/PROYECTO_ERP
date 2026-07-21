<script lang="ts">
  import { session } from '$lib/stores/session.svelte';
  import {
    KPIS,
    SERIES_7D, SERIES_30D, SERIES_90D,
    DEPT_DISTRIBUTION,
    SUMMARY_ROWS,
    TEAM,
    ONBOARDING_PROGRESS,
  } from '$lib/features/dashboard/mock-data';
  import KpiCard from '$lib/features/dashboard/components/KpiCard.svelte';
  import AreaChart from '$lib/features/dashboard/components/AreaChart.svelte';
  import DonutChart from '$lib/features/dashboard/components/DonutChart.svelte';
  import ActivityFeed from '$lib/features/dashboard/components/ActivityFeed.svelte';
  import SummaryTable from '$lib/features/dashboard/components/SummaryTable.svelte';
  import ProgressRing from '$lib/features/dashboard/components/ProgressRing.svelte';
  import AvatarGroup from '$lib/components/ui/AvatarGroup.svelte';
  import Callout from '$lib/components/ui/Callout.svelte';

  // MOCK_DATA = true — KPIs, serie temporal, distribución y tabla son simulados.
  // ActivityFeed es el único componente que consume datos reales (bitácora).
  const MOCK_DATA = true;

  let loading = $state(true);
  let range = $state<'7D' | '30D' | '90D'>('30D');

  let series = $derived.by(() => {
    if (range === '7D') return SERIES_7D;
    if (range === '90D') return SERIES_90D;
    return SERIES_30D;
  });

  // Simular delay de carga para visualizar skeletons
  $effect(() => {
    const t = setTimeout(() => { loading = false; }, 400);
    return () => clearTimeout(t);
  });
</script>

<svelte:head><title>Dashboard — ERP System</title></svelte:head>

<div class="p-6 md:p-8">
  <!-- Header -->
  <div class="mb-5">
    <h1 class="text-xl font-bold tracking-tight text-foreground">
      Hola, {session.user?.username ?? ''} 👋
    </h1>
    <p class="mt-1 text-sm text-foreground-muted">
      {new Date().toLocaleDateString('es-ES', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}
    </p>
  </div>

  {#if MOCK_DATA}
    <Callout variant="info">
      <span class="text-foreground-muted">Las métricas son simuladas. </span>
      <span class="font-medium text-foreground">La actividad reciente es real</span>
      <span class="text-foreground-muted"> (desde la bitácora).</span>
    </Callout>
  {/if}

  <!-- KPIs -->
  <div class="mb-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
    {#if loading}
      {#each Array(4) as _}
        <div class="h-28 rounded-xl border border-border skeleton"></div>
      {/each}
    {:else}
      {#each KPIS as kpi (kpi.label)}
        <KpiCard {...kpi} />
      {/each}
    {/if}
  </div>

  <!-- Row 2: chart + donut -->
  <div class="mb-6 grid gap-4 lg:grid-cols-3">
    <div class="rounded-xl border border-border bg-surface-elevated p-5 lg:col-span-2">
      <div class="mb-4 flex items-center justify-between">
        <div>
          <h2 class="text-sm font-semibold text-foreground">Actividad del sistema</h2>
          <p class="text-[11px] text-foreground-subtle">Eventos registrados por día</p>
        </div>
        <div class="flex items-center gap-1 rounded-lg border border-border bg-surface-muted p-0.5">
          {#each ['7D', '30D', '90D'] as r (r)}
            <button
              type="button"
              onclick={() => range = r as '7D' | '30D' | '90D'}
              class="rounded-md px-2.5 py-1 text-xs font-medium transition-colors {range === r ? 'bg-surface-elevated text-foreground shadow-soft' : 'text-foreground-subtle hover:text-foreground'}"
            >{r}</button>
          {/each}
        </div>
      </div>
      {#if loading}
        <div class="h-[200px] rounded-lg skeleton"></div>
      {:else}
        <AreaChart data={series} label="Actividad del sistema" height={200} />
      {/if}
    </div>

    <div class="rounded-xl border border-border bg-surface-elevated p-5">
      <h2 class="mb-4 text-sm font-semibold text-foreground">Empleados por departamento</h2>
      {#if loading}
        <div class="flex items-center gap-5">
          <div class="h-[140px] w-[140px] rounded-full skeleton"></div>
          <div class="flex-1 space-y-2">{#each Array(5) as _}<div class="h-3 rounded skeleton"></div>{/each}</div>
        </div>
      {:else}
        <DonutChart data={DEPT_DISTRIBUTION} size={140} />
      {/if}
    </div>
  </div>

  <!-- Row 3: activity (altura fija con scroll) + progress + team -->
  <div class="mb-6 grid gap-4 lg:grid-cols-3">
    <!-- Activity feed: altura fija con scroll interno + mask inferior -->
    <div class="rounded-xl border border-border bg-surface-elevated p-5 lg:col-span-2">
      <div class="mb-4 flex items-center justify-between">
        <h2 class="text-sm font-semibold text-foreground">Actividad reciente</h2>
        <a href="/audit-log" class="text-[11px] font-medium text-primary hover:underline">Ver todo →</a>
      </div>
      <div class="max-h-[340px] overflow-y-auto" style="mask-image: linear-gradient(to bottom, black 85%, transparent 100%); -webkit-mask-image: linear-gradient(to bottom, black 85%, transparent 100%);">
        <ActivityFeed />
      </div>
    </div>

    <!-- Progress + team -->
    <div class="flex flex-col gap-4">
      <div class="rounded-xl border border-border bg-surface-elevated p-5">
        <h2 class="mb-3 text-sm font-semibold text-foreground">Onboarding</h2>
        {#if loading}
          <div class="mx-auto h-[120px] w-[120px] rounded-full skeleton"></div>
        {:else}
          <ProgressRing value={ONBOARDING_PROGRESS} label="Completado" size={120} />
        {/if}
      </div>
      <div class="rounded-xl border border-border bg-surface-elevated p-5">
        <h2 class="mb-3 text-sm font-semibold text-foreground">Equipo</h2>
        <AvatarGroup members={TEAM} max={4} size={28} />
        <p class="mt-2 text-[11px] text-foreground-subtle">{TEAM.length} miembros activos</p>
      </div>
    </div>
  </div>

  <!-- Row 4: summary table -->
  <div class="rounded-xl border border-border bg-surface-elevated p-5">
    <div class="mb-4 flex items-center justify-between">
      <h2 class="text-sm font-semibold text-foreground">Usuarios recientes</h2>
      <a href="/users" class="text-[11px] font-medium text-primary hover:underline">Ver todos →</a>
    </div>
    {#if loading}
      <div class="space-y-2">{#each Array(6) as _}<div class="h-10 rounded skeleton"></div>{/each}</div>
    {:else}
      <SummaryTable rows={SUMMARY_ROWS} />
    {/if}
  </div>
</div>
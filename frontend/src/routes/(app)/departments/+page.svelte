<script lang="ts">
  import { api, HttpError, type DepartmentOut } from '$lib/api/client';
  import Card from '$lib/components/ui/Card.svelte';

  let departments = $state<DepartmentOut[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);

  async function loadDepartments() {
    loading = true;
    error = null;
    try {
      departments = await api.departments.list();
    } catch (err) {
      if (err instanceof HttpError) error = err.message;
      else error = 'Error al cargar departamentos.';
    } finally {
      loading = false;
    }
  }

  function parentName(id: string | null): string {
    if (!id) return '—';
    return departments.find((d) => d.id === id)?.name ?? '—';
  }

  $effect(() => { loadDepartments(); });
</script>

<svelte:head><title>Departamentos — ERP System</title></svelte:head>

<div class="p-6 md:p-8">
  <div class="mb-6">
    <h1 class="text-2xl font-bold tracking-tight text-foreground">Departamentos</h1>
    <p class="mt-1 text-sm text-foreground-muted">{departments.length} departamento(s)</p>
  </div>

  {#if error}
    <div class="mb-4 rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger" role="alert">{error}</div>
  {/if}

  {#if loading}
    <Card><p class="py-8 text-center text-sm text-foreground-muted">Cargando...</p></Card>
  {:else if departments.length === 0}
    <Card><p class="py-8 text-center text-sm text-foreground-muted">No hay departamentos.</p></Card>
  {:else}
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {#each departments as dept (dept.id)}
        <Card>
          <h3 class="text-base font-semibold text-foreground">{dept.name}</h3>
          <p class="mt-1 text-sm text-foreground-muted">{dept.description ?? 'Sin descripción'}</p>
          <div class="mt-3 border-t border-border pt-3">
            <p class="text-xs text-foreground-muted">
              Padre: <span class="font-medium text-foreground">{parentName(dept.parent_department_id)}</span>
            </p>
          </div>
        </Card>
      {/each}
    </div>
  {/if}
</div>
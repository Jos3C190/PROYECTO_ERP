<script lang="ts">
  import { api, HttpError, type RoleWithPermissions } from '$lib/api/client';
  import Card from '$lib/components/ui/Card.svelte';

  let roles = $state<RoleWithPermissions[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);

  async function loadRoles() {
    loading = true;
    error = null;
    try {
      roles = await api.roles.list();
    } catch (err) {
      if (err instanceof HttpError) error = err.message;
      else error = 'Error al cargar roles.';
    } finally {
      loading = false;
    }
  }

  $effect(() => { loadRoles(); });
</script>

<svelte:head><title>Roles — ERP System</title></svelte:head>

<div class="p-6 md:p-8">
  <div class="mb-6">
    <h1 class="text-2xl font-bold tracking-tight text-foreground">Roles y permisos</h1>
    <p class="mt-1 text-sm text-foreground-muted">{roles.length} rol(es)</p>
  </div>

  {#if error}
    <div class="mb-4 rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger" role="alert">{error}</div>
  {/if}

  {#if loading}
    <Card><p class="py-8 text-center text-sm text-foreground-muted">Cargando roles...</p></Card>
  {:else}
    <div class="grid gap-6 md:grid-cols-2">
      {#each roles as role (role.id)}
        <Card>
          <div class="mb-3 flex items-center justify-between">
            <div>
              <h3 class="text-base font-semibold text-foreground">{role.name}</h3>
              <p class="text-xs text-foreground-muted">{role.description ?? 'Sin descripción'}</p>
            </div>
            {#if role.is_system}
              <span class="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary">
                <span class="h-1.5 w-1.5 rounded-full bg-primary"></span> Sistema
              </span>
            {/if}
          </div>
          <div class="flex flex-wrap gap-1.5">
            {#each role.permissions as perm (perm.code)}
              <span class="rounded-md bg-surface-muted px-2 py-1 text-xs font-mono text-foreground-muted">{perm.code}</span>
            {:else}
              <span class="text-xs text-foreground-muted">Sin permisos asignados</span>
            {/each}
          </div>
        </Card>
      {/each}
    </div>
  {/if}
</div>
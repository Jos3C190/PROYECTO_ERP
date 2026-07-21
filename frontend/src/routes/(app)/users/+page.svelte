<script lang="ts">
  import { session } from '$lib/stores/session.svelte';
  import { permissions } from '$lib/stores/permissions.svelte';
  import { api, HttpError, type UserOut, type Page } from '$lib/api/client';
  import ThemeToggle from '$lib/components/ui/ThemeToggle.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let users = $state<UserOut[]>([]);
  let meta = $state<{ page: number; size: number; total: number; pages: number } | null>(null);
  let loading = $state(false);
  let error = $state<string | null>(null);
  let search = $state('');
  let page = $state(1);
  let size = $state(10);
  let searchTimer: ReturnType<typeof setTimeout> | null = null;
  let actionLoading = $state<string | null>(null);

  async function loadUsers() {
    loading = true;
    error = null;
    try {
      const result: Page<UserOut> = await api.users.list({ page, size, search: search || undefined });
      users = result.items;
      meta = result.meta;
    } catch (err) {
      if (err instanceof HttpError) error = err.message;
      else error = 'Error al cargar usuarios.';
    } finally {
      loading = false;
    }
  }

  function onSearchInput() {
    if (searchTimer) clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      page = 1;
      loadUsers();
    }, 300);
  }

  function goToPage(p: number) {
    if (p < 1 || (meta && p > meta.pages)) return;
    page = p;
    loadUsers();
  }

  async function toggleActive(user: UserOut) {
    if (actionLoading) return;
    actionLoading = user.id;
    try {
      await api.users.update(user.id, { is_active: !user.is_active });
      await loadUsers();
    } catch (err) {
      error = err instanceof HttpError ? err.message : 'Error al actualizar usuario.';
    } finally {
      actionLoading = null;
    }
  }

  async function unlockUser(user: UserOut) {
    if (actionLoading) return;
    actionLoading = user.id;
    try {
      await api.users.unlock(user.id);
      await loadUsers();
    } catch (err) {
      error = err instanceof HttpError ? err.message : 'Error al desbloquear usuario.';
    } finally {
      actionLoading = null;
    }
  }

  async function deactivateUser(user: UserOut) {
    if (actionLoading) return;
    if (!confirm(`¿Desactivar al usuario "${user.username}"? Esta acción no se puede deshacer fácilmente.`)) return;
    actionLoading = user.id;
    try {
      await api.users.deactivate(user.id);
      await loadUsers();
    } catch (err) {
      error = err instanceof HttpError ? err.message : 'Error al desactivar usuario.';
    } finally {
      actionLoading = null;
    }
  }

  async function handleLogout() {
    try { await api.auth.logout(); } catch { /* ignore */ }
    session.clear();
    permissions.clear();
    window.location.href = '/login';
  }

  $effect(() => { loadUsers(); });
</script>

<svelte:head><title>Usuarios — ERP System</title></svelte:head>

<main class="min-h-screen bg-surface-muted">
  <header class="border-b border-border bg-surface">
    <div class="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
      <div class="flex items-center gap-3">
        <div class="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <span class="font-bold">E</span>
        </div>
        <div>
          <p class="text-sm font-semibold leading-tight text-foreground">ERP System</p>
          <p class="text-xs text-foreground-muted">Gestión de usuarios</p>
        </div>
      </div>
      <div class="flex items-center gap-3">
        <a href="/dashboard" class="text-sm text-foreground-muted hover:text-foreground">Dashboard</a>
        <span class="text-sm text-foreground-muted">{session.user?.username}</span>
        <ThemeToggle />
        <Button variant="secondary" size="sm" onclick={handleLogout}>Cerrar sesión</Button>
      </div>
    </div>
  </header>

  <section class="mx-auto max-w-7xl px-6 py-8">
    <div class="mb-6 flex items-center justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold tracking-tight text-foreground">Usuarios</h1>
        <p class="mt-1 text-sm text-foreground-muted">
          {meta ? `${meta.total} usuario(s) en total` : 'Cargando...'}
        </p>
      </div>
      <div class="flex items-center gap-3">
        <input
          type="text"
          placeholder="Buscar por nombre o correo..."
          bind:value={search}
          oninput={onSearchInput}
          class="w-64 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-foreground placeholder:text-foreground-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
        />
      </div>
    </div>

    {#if error}
      <div class="mb-4 rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger" role="alert">
        {error}
      </div>
    {/if}

    <Card class="overflow-hidden p-0">
      {#if loading}
        <div class="flex items-center justify-center py-16">
          <p class="text-sm text-foreground-muted">Cargando usuarios...</p>
        </div>
      {:else if users.length === 0}
        <div class="flex flex-col items-center justify-center py-16">
          <p class="text-sm text-foreground-muted">No se encontraron usuarios.</p>
          {#if search}
            <Button variant="ghost" size="sm" onclick={() => { search = ''; page = 1; loadUsers(); }}>
              Limpiar búsqueda
            </Button>
          {/if}
        </div>
      {:else}
        <div class="overflow-x-auto">
          <table class="w-full text-sm">
            <thead class="border-b border-border bg-surface-muted">
              <tr>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Usuario</th>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Correo</th>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Estado</th>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Rol</th>
                <th class="px-4 py-3 text-left font-semibold text-foreground">Creado</th>
                <th class="px-4 py-3 text-right font-semibold text-foreground">Acciones</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-border">
              {#each users as user (user.id)}
                <tr class="hover:bg-surface-muted">
                  <td class="px-4 py-3 font-medium text-foreground">{user.username}</td>
                  <td class="px-4 py-3 text-foreground-muted">{user.email}</td>
                  <td class="px-4 py-3">
                    {#if user.locked_until}
                      <span class="inline-flex items-center gap-1 rounded-full bg-warning/10 px-2 py-0.5 text-xs font-medium text-warning">
                        <span class="h-1.5 w-1.5 rounded-full bg-warning"></span> Bloqueado
                      </span>
                    {:else if user.is_active}
                      <span class="inline-flex items-center gap-1 rounded-full bg-success/10 px-2 py-0.5 text-xs font-medium text-success">
                        <span class="h-1.5 w-1.5 rounded-full bg-success"></span> Activo
                      </span>
                    {:else}
                      <span class="inline-flex items-center gap-1 rounded-full bg-foreground-muted/10 px-2 py-0.5 text-xs font-medium text-foreground-muted">
                        <span class="h-1.5 w-1.5 rounded-full bg-foreground-muted"></span> Inactivo
                      </span>
                    {/if}
                  </td>
                  <td class="px-4 py-3 text-foreground-muted">
                    {user.is_superuser ? 'Super Admin' : 'Usuario'}
                  </td>
                  <td class="px-4 py-3 text-foreground-muted">
                    {new Date(user.created_at).toLocaleDateString('es-ES')}
                  </td>
                  <td class="px-4 py-3">
                    <div class="flex items-center justify-end gap-1">
                      {#if user.locked_until}
                        <Button
                          variant="ghost" size="sm"
                          onclick={() => unlockUser(user)}
                          disabled={actionLoading === user.id}
                        >Desbloquear</Button>
                      {/if}
                      {#if user.is_active}
                        <Button
                          variant="ghost" size="sm"
                          onclick={() => toggleActive(user)}
                          disabled={actionLoading === user.id || user.id === session.user?.id}
                        >Desactivar</Button>
                      {/if}
                      {#if !user.is_active}
                        <Button
                          variant="ghost" size="sm"
                          onclick={() => toggleActive(user)}
                          disabled={actionLoading === user.id}
                        >Activar</Button>
                      {/if}
                    </div>
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      {/if}
    </Card>

    {#if meta && meta.pages > 1}
      <div class="mt-4 flex items-center justify-between">
        <p class="text-xs text-foreground-muted">
          Página {meta.page} de {meta.pages}
        </p>
        <div class="flex gap-2">
          <Button variant="secondary" size="sm" onclick={() => goToPage(meta!.page - 1)} disabled={meta!.page <= 1}>
            Anterior
          </Button>
          <Button variant="secondary" size="sm" onclick={() => goToPage(meta!.page + 1)} disabled={meta!.page >= meta!.pages}>
            Siguiente
          </Button>
        </div>
      </div>
    {/if}
  </section>
</main>
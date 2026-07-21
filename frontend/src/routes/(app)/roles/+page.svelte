<script lang="ts">
  import { api, HttpError, type RoleWithPermissions, type PermissionOut, type UserOut } from '$lib/api/client';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import FormField from '$lib/components/ui/FormField.svelte';

  let roles = $state<RoleWithPermissions[]>([]);
  let allPermissions = $state<PermissionOut[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);

  let modalMode = $state<'create' | 'edit' | 'permissions' | 'assign' | null>(null);
  let modalRole = $state<RoleWithPermissions | null>(null);
  let formError = $state<string | null>(null);
  let formLoading = $state(false);
  let fName = $state(''); let fDesc = $state('');
  let selectedPerms = $state<Set<string>>(new Set());
  let users = $state<UserOut[]>([]);
  let fUserId = $state(''); let fRoleId = $state('');

  async function loadRoles() {
    loading = true; error = null;
    try { [roles, allPermissions] = await Promise.all([api.roles.list(), api.roles.listPermissions()]); }
    catch (err) { error = err instanceof HttpError ? err.message : 'Error.'; }
    finally { loading = false; }
  }

  function permsByModule(): [string, PermissionOut[]][] {
    const map: Record<string, PermissionOut[]> = {};
    for (const p of allPermissions) { (map[p.module ?? 'otros'] ??= []).push(p); }
    return Object.entries(map);
  }

  function openCreate() { modalMode = 'create'; modalRole = null; formError = null; fName = ''; fDesc = ''; }
  function openEdit(r: RoleWithPermissions) { modalMode = 'edit'; modalRole = r; formError = null; fName = r.name; fDesc = r.description ?? ''; }
  function openPermissions(r: RoleWithPermissions) { modalMode = 'permissions'; modalRole = r; formError = null; selectedPerms = new Set(r.permissions.map(p => p.code)); }
  async function openAssign() { modalMode = 'assign'; formError = null; fUserId = ''; fRoleId = ''; try { const r = await api.users.list({ size: 100 }); users = r.items; } catch { users = []; } }
  function closeModal() { modalMode = null; modalRole = null; formError = null; }

  async function handleSubmit() {
    formLoading = true; formError = null;
    try {
      if (modalMode === 'create') { await api.roles.create({ name: fName, description: fDesc || undefined }); }
      else if (modalMode === 'edit' && modalRole) { await api.roles.update(modalRole.id, { name: fName, description: fDesc || undefined }); }
      else if (modalMode === 'permissions' && modalRole) { await api.roles.setPermissions(modalRole.id, [...selectedPerms]); }
      else if (modalMode === 'assign' && fUserId && fRoleId) { await api.roles.assign(fUserId, fRoleId); }
      closeModal(); await loadRoles();
    } catch (err) { formError = err instanceof HttpError ? err.message : 'Error.'; }
    finally { formLoading = false; }
  }

  async function revokeRole(userId: string, roleId: string) {
    if (!confirm('¿Revocar este rol del usuario?')) return;
    try { await api.roles.revoke(userId, roleId); await loadRoles(); }
    catch (err) { error = err instanceof HttpError ? err.message : 'Error.'; }
  }

  async function deleteRole(r: RoleWithPermissions) {
    if (r.is_system) { alert('Los roles de sistema no pueden eliminarse.'); return; }
    if (!confirm(`¿Eliminar el rol "${r.name}"?`)) return;
    try { await api.roles.delete(r.id); await loadRoles(); }
    catch (err) { error = err instanceof HttpError ? err.message : 'Error.'; }
  }

  function togglePerm(code: string) {
    if (selectedPerms.has(code)) selectedPerms.delete(code); else selectedPerms.add(code);
    selectedPerms = new Set(selectedPerms);
  }

  $effect(() => { loadRoles(); });
</script>

<svelte:head><title>Roles — ERP System</title></svelte:head>

<div class="p-6 md:p-8">
  <div class="mb-6 flex items-center justify-between">
    <div><h1 class="text-2xl font-bold tracking-tight text-foreground">Roles y permisos</h1><p class="mt-1 text-sm text-foreground-muted">{roles.length} rol(es)</p></div>
    <div class="flex gap-2"><Button variant="secondary" onclick={openAssign}>Asignar rol</Button><Button onclick={openCreate}>Crear rol</Button></div>
  </div>

  {#if error}<div class="mb-4 rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger" role="alert">{error}</div>{/if}

  {#if loading}<Card><p class="py-8 text-center text-sm text-foreground-muted">Cargando...</p></Card>
  {:else}
    <div class="grid gap-6 md:grid-cols-2">
      {#each roles as role (role.id)}
        <Card>
          <div class="mb-3 flex items-center justify-between">
            <div><h3 class="text-base font-semibold text-foreground">{role.name}</h3><p class="text-xs text-foreground-muted">{role.description ?? 'Sin descripción'}</p></div>
            {#if role.is_system}<span class="inline-flex items-center gap-1 rounded-full bg-primary/10 px-2 py-0.5 text-xs font-medium text-primary"><span class="h-1.5 w-1.5 rounded-full bg-primary"></span> Sistema</span>{/if}
          </div>
          <div class="flex flex-wrap gap-1.5">
            {#each role.permissions as perm (perm.code)}<span class="rounded-md bg-surface-muted px-2 py-1 text-xs font-mono text-foreground-muted">{perm.code}</span>{:else}<span class="text-xs text-foreground-muted">Sin permisos</span>{/each}
          </div>
          <div class="mt-4 flex gap-1 border-t border-border pt-3">
            <Button variant="ghost" size="sm" onclick={() => openPermissions(role)}>Permisos</Button>
            {#if !role.is_system}<Button variant="ghost" size="sm" onclick={() => openEdit(role)}>Editar</Button><Button variant="ghost" size="sm" onclick={() => deleteRole(role)}>Eliminar</Button>{/if}
          </div>
        </Card>
      {/each}
    </div>
  {/if}
</div>

<Modal open={modalMode !== null} title={modalMode === 'create' ? 'Crear rol' : modalMode === 'edit' ? 'Editar rol' : modalMode === 'permissions' ? 'Matriz de permisos' : 'Asignar rol a usuario'} onclose={closeModal} size={modalMode === 'permissions' ? 'lg' : 'md'}>
  {#if modalMode === 'create' || modalMode === 'edit'}
    <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
      {#if formError}<div class="rounded-lg border border-danger/30 bg-danger/10 px-4 py-2 text-sm text-danger">{formError}</div>{/if}
      <FormField id="r-name" label="Nombre del rol" bind:value={fName} required placeholder="GERENTE" />
      <FormField id="r-desc" label="Descripción" bind:value={fDesc} placeholder="Rol de gerencia" />
      <div class="flex justify-end gap-2 pt-2"><Button variant="secondary" onclick={closeModal}>Cancelar</Button><Button type="submit" disabled={formLoading}>{formLoading ? 'Guardando...' : 'Guardar'}</Button></div>
    </form>
  {:else if modalMode === 'permissions' && modalRole}
    <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
      {#if formError}<div class="rounded-lg border border-danger/30 bg-danger/10 px-4 py-2 text-sm text-danger">{formError}</div>{/if}
      <p class="text-sm text-foreground-muted">Permiso para el rol <strong>{modalRole.name}</strong></p>
      {#each permsByModule() as [mod, perms]}
        <div><p class="mb-2 text-xs font-semibold uppercase tracking-wider text-foreground-muted">{mod}</p>
          <div class="grid grid-cols-2 gap-2">
            {#each perms as p (p.code)}
              <label class="flex items-center gap-2 text-sm text-foreground"><input type="checkbox" checked={selectedPerms.has(p.code)} onchange={() => togglePerm(p.code)} class="rounded" /> <span class="font-mono text-xs">{p.code}</span></label>
            {/each}
          </div>
        </div>
      {/each}
      <div class="flex justify-end gap-2 pt-2"><Button variant="secondary" onclick={closeModal}>Cancelar</Button><Button type="submit" disabled={formLoading}>{formLoading ? 'Guardando...' : 'Guardar permisos'}</Button></div>
    </form>
  {:else if modalMode === 'assign'}
    <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
      {#if formError}<div class="rounded-lg border border-danger/30 bg-danger/10 px-4 py-2 text-sm text-danger">{formError}</div>{/if}
      <FormField id="a-user" label="Usuario" bind:value={fUserId} options={[{value:'',label:'— Seleccionar —'},...users.map(u=>({value:u.id,label:`${u.username} (${u.email})`}))]} />
      <FormField id="a-role" label="Rol" bind:value={fRoleId} options={[{value:'',label:'— Seleccionar —'},...roles.map(r=>({value:r.id,label:r.name}))]} />
      <div class="flex justify-end gap-2 pt-2"><Button variant="secondary" onclick={closeModal}>Cancelar</Button><Button type="submit" disabled={formLoading}>{formLoading ? 'Asignando...' : 'Asignar'}</Button></div>
    </form>
  {/if}
</Modal>
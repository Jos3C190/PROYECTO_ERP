<script lang="ts">
  import { api, HttpError, type DepartmentOut } from '$lib/api/client';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import FormField from '$lib/components/ui/FormField.svelte';

  let departments = $state<DepartmentOut[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);

  let modalMode = $state<'create' | 'edit' | null>(null);
  let modalDept = $state<DepartmentOut | null>(null);
  let formError = $state<string | null>(null);
  let formLoading = $state(false);
  let fName = $state('');
  let fDescription = $state('');
  let fParentId = $state('');

  async function loadDepartments() {
    loading = true; error = null;
    try { departments = await api.departments.list(); }
    catch (err) { error = err instanceof HttpError ? err.message : 'Error.'; }
    finally { loading = false; }
  }

  function parentName(id: string | null): string {
    if (!id) return '—';
    return departments.find((d) => d.id === id)?.name ?? '—';
  }

  function openCreate() { modalMode = 'create'; modalDept = null; formError = null; fName = ''; fDescription = ''; fParentId = ''; }
  function openEdit(d: DepartmentOut) { modalMode = 'edit'; modalDept = d; formError = null; fName = d.name; fDescription = d.description ?? ''; fParentId = d.parent_department_id ?? ''; }
  function closeModal() { modalMode = null; modalDept = null; formError = null; }

  async function handleSubmit() {
    formLoading = true; formError = null;
    try {
      const data = { name: fName, description: fDescription || undefined, parent_department_id: fParentId || undefined };
      if (modalMode === 'create') {
        await api.departments.create(data);
      } else if (modalMode === 'edit' && modalDept) {
        await api.departments.update(modalDept.id, data);
      }
      closeModal(); await loadDepartments();
    } catch (err) { formError = err instanceof HttpError ? err.message : 'Error.'; }
    finally { formLoading = false; }
  }

  async function deleteDept(d: DepartmentOut) {
    if (!confirm(`¿Eliminar el departamento "${d.name}"?`)) return;
    try { await api.departments.delete(d.id); await loadDepartments(); }
    catch (err) { error = err instanceof HttpError ? err.message : 'Error.'; }
  }

  $effect(() => { loadDepartments(); });
</script>

<svelte:head><title>Departamentos — ERP System</title></svelte:head>

<div class="p-6 md:p-8">
  <div class="mb-6 flex items-center justify-between">
    <div><h1 class="text-2xl font-bold tracking-tight text-foreground">Departamentos</h1><p class="mt-1 text-sm text-foreground-muted">{departments.length} departamento(s)</p></div>
    <Button onclick={openCreate}>Crear departamento</Button>
  </div>

  {#if error}<div class="mb-4 rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger" role="alert">{error}</div>{/if}

  {#if loading}<Card><p class="py-8 text-center text-sm text-foreground-muted">Cargando...</p></Card>
  {:else if departments.length === 0}<Card><p class="py-8 text-center text-sm text-foreground-muted">No hay departamentos.</p></Card>
  {:else}
    <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {#each departments as dept (dept.id)}
        <Card>
          <div class="flex items-start justify-between">
            <div><h3 class="text-base font-semibold text-foreground">{dept.name}</h3><p class="mt-1 text-sm text-foreground-muted">{dept.description ?? 'Sin descripción'}</p>
              <p class="mt-3 text-xs text-foreground-muted">Padre: <span class="font-medium text-foreground">{parentName(dept.parent_department_id)}</span></p>
            </div>
            <div class="flex flex-col gap-1">
              <Button variant="ghost" size="sm" onclick={() => openEdit(dept)}>Editar</Button>
              <Button variant="ghost" size="sm" onclick={() => deleteDept(dept)}>Eliminar</Button>
            </div>
          </div>
        </Card>
      {/each}
    </div>
  {/if}
</div>

<Modal open={modalMode !== null} title={modalMode === 'create' ? 'Crear departamento' : 'Editar departamento'} onclose={closeModal}>
  <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
    {#if formError}<div class="rounded-lg border border-danger/30 bg-danger/10 px-4 py-2 text-sm text-danger">{formError}</div>{/if}
    <FormField id="d-name" label="Nombre" bind:value={fName} required placeholder="Ventas" />
    <FormField id="d-desc" label="Descripción" bind:value={fDescription} placeholder="Departamento de ventas" />
    <FormField id="d-parent" label="Departamento padre" bind:value={fParentId} options={[{ value: '', label: '— Ninguno —' }, ...departments.filter(d => d.id !== modalDept?.id).map(d => ({ value: d.id, label: d.name }))]} />
    <div class="flex justify-end gap-2 pt-2"><Button variant="secondary" onclick={closeModal}>Cancelar</Button><Button type="submit" disabled={formLoading}>{formLoading ? 'Guardando...' : 'Guardar'}</Button></div>
  </form>
</Modal>
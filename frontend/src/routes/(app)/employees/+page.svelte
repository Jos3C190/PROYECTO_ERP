<script lang="ts">
  import { api, HttpError, type EmployeeOut, type DepartmentOut, type UserOut, type Page } from '$lib/api/client';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import FormField from '$lib/components/ui/FormField.svelte';

  let employees = $state<EmployeeOut[]>([]);
  let meta = $state<{ page: number; size: number; total: number; pages: number } | null>(null);
  let departments = $state<DepartmentOut[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);
  let search = $state('');
  let page = $state(1);
  let size = $state(10);
  let searchTimer: ReturnType<typeof setTimeout> | null = null;
  let actionLoading = $state<string | null>(null);

  let modalMode = $state<'create' | 'edit' | 'detail' | 'link' | null>(null);
  let modalEmp = $state<EmployeeOut | null>(null);
  let formError = $state<string | null>(null);
  let formLoading = $state(false);

  let fCode = $state(''); let fFirst = $state(''); let fLast = $state('');
  let fDept = $state(''); let fPosition = $state(''); let fPhone = $state('');
  let fAddress = $state(''); let fDocId = $state(''); let fStatus = $state('activo');
  let fHireDate = $state('');
  let fLinkUserId = $state('');

  let users = $state<UserOut[]>([]);

  async function loadData() {
    loading = true; error = null;
    try {
      const [empResult, deptResult] = await Promise.all([api.employees.list({ page, size, search: search || undefined }), api.departments.list()]);
      employees = empResult.items; meta = empResult.meta; departments = deptResult;
    } catch (err) { error = err instanceof HttpError ? err.message : 'Error.'; }
    finally { loading = false; }
  }

  function onSearchInput() { if (searchTimer) clearTimeout(searchTimer); searchTimer = setTimeout(() => { page = 1; loadData(); }, 300); }
  function goToPage(p: number) { if (p < 1 || (meta && p > meta.pages)) return; page = p; loadData(); }
  function deptName(id: string | null): string { if (!id) return '—'; return departments.find((d) => d.id === id)?.name ?? '—'; }
  function statusBadge(s: string): string {
    const m: Record<string, string> = { activo: 'badge-success', inactivo: 'badge-neutral', vacaciones: 'badge-warning', baja: 'badge-danger' };
    return m[s] ?? 'badge-neutral';
  }

  function openCreate() { modalMode = 'create'; modalEmp = null; formError = null; fCode = ''; fFirst = ''; fLast = ''; fDept = ''; fPosition = ''; fPhone = ''; fAddress = ''; fDocId = ''; fStatus = 'activo'; fHireDate = ''; }
  function openEdit(e: EmployeeOut) { modalMode = 'edit'; modalEmp = e; formError = null; fFirst = e.first_name; fLast = e.last_name; fDept = e.department_id ?? ''; fPosition = e.position ?? ''; fPhone = e.phone ?? ''; fAddress = e.address ?? ''; fDocId = e.document_id ?? ''; fStatus = e.status; fHireDate = e.hire_date ?? ''; }
  function openDetail(e: EmployeeOut) { modalMode = 'detail'; modalEmp = e; formError = null; }
  async function openLink(e: EmployeeOut) { modalMode = 'link'; modalEmp = e; formError = null; fLinkUserId = ''; try { const r = await api.users.list({ size: 100 }); users = r.items; } catch { users = []; } }
  function closeModal() { modalMode = null; modalEmp = null; formError = null; }

  async function handleSubmit() {
    formLoading = true; formError = null;
    try {
      if (modalMode === 'create') {
        await api.employees.create({ employee_code: fCode, first_name: fFirst, last_name: fLast, department_id: fDept || undefined, position: fPosition || undefined, phone: fPhone || undefined, address: fAddress || undefined, document_id: fDocId || undefined, hire_date: fHireDate || undefined, status: fStatus });
      } else if (modalMode === 'edit' && modalEmp) {
        await api.employees.update(modalEmp.id, { first_name: fFirst, last_name: fLast, department_id: fDept || undefined, position: fPosition || undefined, phone: fPhone || undefined, address: fAddress || undefined, document_id: fDocId || undefined, hire_date: fHireDate || undefined, status: fStatus });
      } else if (modalMode === 'link' && modalEmp) {
        await api.employees.linkUser(modalEmp.id, fLinkUserId);
      }
      closeModal(); await loadData();
    } catch (err) { formError = err instanceof HttpError ? err.message : 'Error.'; }
    finally { formLoading = false; }
  }

  async function deleteEmp(e: EmployeeOut) {
    if (!confirm(`¿Eliminar al empleado "${e.first_name} ${e.last_name}"?`)) return;
    actionLoading = e.id;
    try { await api.employees.delete(e.id); await loadData(); }
    catch (err) { error = err instanceof HttpError ? err.message : 'Error.'; }
    finally { actionLoading = null; }
  }

  async function unlinkEmp(e: EmployeeOut) {
    if (!confirm('¿Desvincular la cuenta de usuario de este empleado?')) return;
    actionLoading = e.id;
    try { await api.employees.unlinkUser(e.id); await loadData(); }
    catch (err) { error = err instanceof HttpError ? err.message : 'Error.'; }
    finally { actionLoading = null; }
  }

  $effect(() => { loadData(); });
</script>

<svelte:head><title>Empleados — ERP System</title></svelte:head>

<div class="p-6 md:p-8">
  <div class="mb-6 flex items-center justify-between gap-4">
    <div><h1 class="text-2xl font-bold tracking-tight text-foreground">Empleados</h1><p class="mt-1 text-sm text-foreground-muted">{meta ? `${meta.total} empleado(s)` : 'Cargando...'}</p></div>
    <div class="flex items-center gap-3"><input type="text" placeholder="Buscar..." bind:value={search} oninput={onSearchInput} class="w-56 rounded-lg border border-border bg-surface px-3 py-2 text-sm text-foreground placeholder:text-foreground-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary" /><Button onclick={openCreate}>Crear empleado</Button></div>
  </div>

  {#if error}<div class="mb-4 rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger" role="alert">{error}</div>{/if}

  <Card class="overflow-hidden p-0">
    {#if loading}<div class="flex items-center justify-center py-16"><p class="text-sm text-foreground-muted">Cargando...</p></div>
    {:else if employees.length === 0}<div class="flex flex-col items-center justify-center py-16"><p class="text-sm text-foreground-muted">No se encontraron empleados.</p></div>
    {:else}
      <div class="overflow-x-auto"><table class="w-full text-sm">
        <thead class="border-b border-border bg-surface-muted"><tr><th class="px-4 py-3 text-left font-semibold text-foreground">Código</th><th class="px-4 py-3 text-left font-semibold text-foreground">Nombre</th><th class="px-4 py-3 text-left font-semibold text-foreground">Departamento</th><th class="px-4 py-3 text-left font-semibold text-foreground">Cargo</th><th class="px-4 py-3 text-left font-semibold text-foreground">Estado</th><th class="px-4 py-3 text-left font-semibold text-foreground">Usuario</th><th class="px-4 py-3 text-right font-semibold text-foreground">Acciones</th></tr></thead>
        <tbody class="divide-y divide-border">
          {#each employees as emp (emp.id)}
            <tr class="hover:bg-surface-muted">
              <td class="px-4 py-3 font-mono text-foreground">{emp.employee_code}</td>
              <td class="px-4 py-3"><button class="font-medium text-foreground hover:text-primary" onclick={() => openDetail(emp)}>{emp.first_name} {emp.last_name}</button></td>
              <td class="px-4 py-3 text-foreground-muted">{deptName(emp.department_id)}</td>
              <td class="px-4 py-3 text-foreground-muted">{emp.position ?? '—'}</td>
              <td class="px-4 py-3"><span class="{statusBadge(emp.status)} inline-flex items-center gap-1.5 rounded-md px-2 py-0.5 text-xs font-medium"><span class="h-1.5 w-1.5 rounded-full bg-current"></span> {emp.status}</span></td>
              <td class="px-4 py-3">{#if emp.user_id}<span class="text-xs text-success">Vinculado</span>{:else}<span class="text-xs text-foreground-muted">—</span>{/if}</td>
              <td class="px-4 py-3"><div class="flex items-center justify-end gap-1">
                <Button variant="ghost" size="sm" onclick={() => openEdit(emp)}>Editar</Button>
                {#if !emp.user_id}<Button variant="ghost" size="sm" onclick={() => openLink(emp)}>Vincular</Button>{:else}<Button variant="ghost" size="sm" onclick={() => unlinkEmp(emp)} disabled={actionLoading === emp.id}>Desvincular</Button>{/if}
                <Button variant="ghost" size="sm" onclick={() => deleteEmp(emp)} disabled={actionLoading === emp.id}>Eliminar</Button>
              </div></td>
            </tr>
          {/each}
        </tbody>
      </table></div>
    {/if}
  </Card>

  {#if meta && meta.pages > 1}<div class="mt-4 flex items-center justify-between"><p class="text-xs text-foreground-muted">Página {meta.page} de {meta.pages}</p><div class="flex gap-2"><Button variant="secondary" size="sm" onclick={() => goToPage(meta!.page - 1)} disabled={meta!.page <= 1}>Anterior</Button><Button variant="secondary" size="sm" onclick={() => goToPage(meta!.page + 1)} disabled={meta!.page >= meta!.pages}>Siguiente</Button></div></div>{/if}
</div>

<Modal open={modalMode !== null} title={modalMode === 'create' ? 'Crear empleado' : modalMode === 'edit' ? 'Editar empleado' : modalMode === 'link' ? 'Vincular usuario' : 'Detalle del empleado'} onclose={closeModal} size={modalMode === 'detail' ? 'lg' : 'lg'}>
  {#if modalMode === 'create' || modalMode === 'edit'}
    <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
      {#if formError}<div class="rounded-lg border border-danger/30 bg-danger/10 px-4 py-2 text-sm text-danger">{formError}</div>{/if}
      {#if modalMode === 'create'}<FormField id="e-code" label="Código de empleado" bind:value={fCode} required placeholder="EMP001" />{/if}
      <div class="grid grid-cols-2 gap-4"><FormField id="e-first" label="Nombre" bind:value={fFirst} required /><FormField id="e-last" label="Apellido" bind:value={fLast} required /></div>
      <FormField id="e-dept" label="Departamento" bind:value={fDept} options={[{ value: '', label: '— Ninguno —' }, ...departments.map(d => ({ value: d.id, label: d.name }))]} />
      <FormField id="e-position" label="Cargo" bind:value={fPosition} placeholder="Desarrollador" />
      <FormField id="e-phone" label="Teléfono" bind:value={fPhone} placeholder="+503 0000-0000" />
      <FormField id="e-doc" label="Documento de identidad" bind:value={fDocId} placeholder="DUI / Pasaporte" />
      <FormField id="e-address" label="Dirección" bind:value={fAddress} placeholder="Calle, ciudad" />
      <FormField id="e-hire" label="Fecha de contratación" type="date" bind:value={fHireDate} />
      <FormField id="e-status" label="Estado" bind:value={fStatus} options={[{value:'activo',label:'Activo'},{value:'inactivo',label:'Inactivo'},{value:'vacaciones',label:'Vacaciones'},{value:'baja',label:'Baja'}]} />
      <div class="flex justify-end gap-2 pt-2"><Button variant="secondary" onclick={closeModal}>Cancelar</Button><Button type="submit" disabled={formLoading}>{formLoading ? 'Guardando...' : 'Guardar'}</Button></div>
    </form>
  {:else if modalMode === 'link' && modalEmp}
    <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-4">
      {#if formError}<div class="rounded-lg border border-danger/30 bg-danger/10 px-4 py-2 text-sm text-danger">{formError}</div>{/if}
      <p class="text-sm text-foreground-muted">Selecciona el usuario a vincular con <strong>{modalEmp.first_name} {modalEmp.last_name}</strong></p>
      <FormField id="e-link-user" label="Usuario" bind:value={fLinkUserId} options={[{value:'',label:'— Seleccionar —'},...users.map(u=>({value:u.id,label:`${u.username} (${u.email})`}))]} />
      <div class="flex justify-end gap-2 pt-2"><Button variant="secondary" onclick={closeModal}>Cancelar</Button><Button type="submit" disabled={formLoading}>{formLoading ? 'Vinculando...' : 'Vincular'}</Button></div>
    </form>
  {:else if modalMode === 'detail' && modalEmp}
    <dl class="grid grid-cols-2 gap-y-3 gap-x-6 text-sm">
      <div><dt class="text-foreground-muted">Código</dt><dd class="font-mono text-foreground">{modalEmp.employee_code}</dd></div>
      <div><dt class="text-foreground-muted">Estado</dt><dd class="text-foreground">{modalEmp.status}</dd></div>
      <div><dt class="text-foreground-muted">Nombre completo</dt><dd class="text-foreground">{modalEmp.first_name} {modalEmp.last_name}</dd></div>
      <div><dt class="text-foreground-muted">Departamento</dt><dd class="text-foreground">{deptName(modalEmp.department_id)}</dd></div>
      <div><dt class="text-foreground-muted">Cargo</dt><dd class="text-foreground">{modalEmp.position ?? '—'}</dd></div>
      <div><dt class="text-foreground-muted">Teléfono</dt><dd class="text-foreground">{modalEmp.phone ?? '—'}</dd></div>
      <div><dt class="text-foreground-muted">Documento</dt><dd class="text-foreground">{modalEmp.document_id ?? '—'}</dd></div>
      <div><dt class="text-foreground-muted">Fecha contratación</dt><dd class="text-foreground">{modalEmp.hire_date ? new Date(modalEmp.hire_date).toLocaleDateString('es-ES') : '—'}</dd></div>
      <div class="col-span-2"><dt class="text-foreground-muted">Dirección</dt><dd class="text-foreground">{modalEmp.address ?? '—'}</dd></div>
      {#if modalEmp.user_id}<div class="col-span-2"><dt class="text-foreground-muted">Usuario vinculado</dt><dd class="text-success text-xs">Sí (ID: {modalEmp.user_id.slice(0,8)}...)</dd></div>{/if}
    </dl>
    <div class="mt-4 flex justify-end"><Button variant="secondary" onclick={closeModal}>Cerrar</Button></div>
  {/if}
</Modal>
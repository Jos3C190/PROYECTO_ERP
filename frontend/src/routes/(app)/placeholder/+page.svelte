<script lang="ts">
  import { page } from '$app/state';
  import Card from '$lib/components/ui/Card.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let moduleName = $derived(page.url.searchParams.get('module') ?? 'Módulo');
</script>

<svelte:head><title>{moduleName} — ERP System</title></svelte:head>

<div class="flex min-h-full items-center justify-center p-6">
  <div class="w-full max-w-lg">
    <Card>
      <div class="flex flex-col items-center py-12 text-center">
        <div class="mb-6 flex h-20 w-20 items-center justify-center rounded-2xl bg-surface-muted">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" class="text-foreground-muted" aria-hidden="true">
            <path d="M12 6v6l4 2" /><circle cx="12" cy="12" r="9" />
          </svg>
        </div>
        <h2 class="text-xl font-bold text-foreground">{moduleName}</h2>
        <p class="mt-2 text-sm text-foreground-muted">
          Este módulo está en desarrollo. Estará disponible en una próxima fase del ERP System.
        </p>
        <div class="mt-8">
          <Button onclick={() => (window.location.href = '/dashboard')}>
            Volver al dashboard
          </Button>
        </div>
      </div>
    </Card>
  </div>
</div>
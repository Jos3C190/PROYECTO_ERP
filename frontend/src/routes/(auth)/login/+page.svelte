<script lang="ts">
  import { goto } from '$app/navigation';
  import { session } from '$lib/stores/session.svelte';
  import { api, HttpError } from '$lib/api/client';
  import Button from '$lib/components/ui/Button.svelte';
  import Card from '$lib/components/ui/Card.svelte';
  import { z } from 'zod';

  const loginSchema = z.object({
    login: z.string().min(3, 'Mínimo 3 caracteres').max(320, 'Máximo 320 caracteres'),
    password: z.string().min(1, 'Ingrese su contraseña').max(128, 'Contraseña demasiado larga')
  });

  let loginValue = $state('');
  let passwordValue = $state('');
  let errors = $state<{ login?: string; password?: string; form?: string }>({});
  let submitting = $state(false);
  let showPassword = $state(false);

  function validate(): boolean {
    const result = loginSchema.safeParse({ login: loginValue, password: passwordValue });
    if (result.success) {
      errors = {};
      return true;
    }
    const fieldErrors: { login?: string; password?: string } = {};
    for (const issue of result.error.issues) {
      const field = issue.path[0] as 'login' | 'password';
      if (!fieldErrors[field]) fieldErrors[field] = issue.message;
    }
    errors = fieldErrors;
    return false;
  }

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (submitting) return;
    if (!validate()) return;

    submitting = true;
    errors = {};
    session.setLoading(true);

    try {
      const tokens = await api.auth.login(loginValue, passwordValue);
      session.setToken(tokens.access_token);
      const me = await api.auth.me();
      session.setUser(me);
      await goto('/dashboard');
    } catch (err) {
      if (err instanceof HttpError) {
        errors.form = err.message;
      } else {
        errors.form = 'Error inesperado. Intente nuevamente.';
      }
      session.clear();
    } finally {
      submitting = false;
      session.setLoading(false);
    }
  }
</script>

<svelte:head>
  <title>Iniciar sesión — ERP System</title>
</svelte:head>

<main class="flex min-h-screen items-center justify-center bg-surface-muted px-4">
  <div class="w-full max-w-md">
    <div class="mb-8 text-center">
      <div class="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-primary-foreground">
        <span class="text-xl font-bold">E</span>
      </div>
      <h1 class="text-2xl font-bold tracking-tight text-foreground">ERP System</h1>
      <p class="mt-1 text-sm text-foreground-muted">Ingrese sus credenciales para continuar</p>
    </div>

    <Card>
      <form class="space-y-4" onsubmit={handleSubmit} novalidate>
        {#if errors.form}
          <div
            class="rounded-lg border border-danger/30 bg-danger/10 px-4 py-3 text-sm text-danger"
            role="alert"
          >
            {errors.form}
          </div>
        {/if}

        <div>
          <label for="login" class="mb-1.5 block text-sm font-medium text-foreground">
            Usuario o correo
          </label>
          <input
            id="login"
            type="text"
            autocomplete="username"
            bind:value={loginValue}
            class="w-full rounded-lg border border-border bg-surface px-3 py-2.5 text-sm text-foreground placeholder:text-foreground-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
            placeholder="usuario o correo@ejemplo.com"
            aria-invalid={errors.login ? 'true' : undefined}
            aria-describedby={errors.login ? 'login-error' : undefined}
            disabled={submitting}
          />
          {#if errors.login}
            <p id="login-error" class="mt-1 text-xs text-danger">{errors.login}</p>
          {/if}
        </div>

        <div>
          <label for="password" class="mb-1.5 block text-sm font-medium text-foreground">
            Contraseña
          </label>
          <div class="relative">
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              autocomplete="current-password"
              bind:value={passwordValue}
              class="w-full rounded-lg border border-border bg-surface px-3 py-2.5 pr-10 text-sm text-foreground placeholder:text-foreground-muted focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary"
              placeholder="••••••••••••"
              aria-invalid={errors.password ? 'true' : undefined}
              aria-describedby={errors.password ? 'password-error' : undefined}
              disabled={submitting}
            />
            <button
              type="button"
              onclick={() => (showPassword = !showPassword)}
              class="absolute right-2 top-1/2 -translate-y-1/2 rounded p-1 text-foreground-muted hover:text-foreground"
              aria-label={showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'}
              tabindex="-1"
            >
              {#if showPassword}
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <path d="M9.88 9.88a3 3 0 1 0 4.24 4.24" />
                  <path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68" />
                  <path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61" />
                  <line x1="2" y1="2" x2="22" y2="22" />
                </svg>
              {:else}
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                  <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
              {/if}
            </button>
          </div>
          {#if errors.password}
            <p id="password-error" class="mt-1 text-xs text-danger">{errors.password}</p>
          {/if}
        </div>

        <Button type="submit" disabled={submitting} class="w-full">
          {submitting ? 'Ingresando...' : 'Iniciar sesión'}
        </Button>
      </form>
    </Card>

    <p class="mt-6 text-center text-xs text-foreground-muted">
      ERP System · Fase 1 · Acceso restringido a usuarios autorizados
    </p>
  </div>
</main>
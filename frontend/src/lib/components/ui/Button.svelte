<script lang="ts">
  import type { Snippet } from 'svelte';

  type Variant = 'primary' | 'secondary' | 'ghost' | 'danger' | 'success';
  type Size = 'sm' | 'md' | 'lg';

  interface Props {
    variant?: Variant;
    size?: Size;
    disabled?: boolean;
    type?: 'button' | 'submit' | 'reset';
    onclick?: (e: MouseEvent) => void;
    children: Snippet;
    class?: string;
  }

  let {
    variant = 'primary',
    size = 'md',
    disabled = false,
    type = 'button',
    onclick,
    children,
    class: className = ''
  }: Props = $props();

  const base = 'inline-flex items-center justify-center font-semibold rounded-xl transition-all duration-200 active:scale-95 disabled:opacity-50 disabled:pointer-events-none focus-visible:shadow-glow';

  const variants: Record<Variant, string> = {
    primary: 'bg-gradient-to-br from-primary to-primary-hover text-primary-foreground shadow-soft hover:shadow-lifted hover:-translate-y-0.5',
    secondary: 'bg-surface-elevated text-foreground border border-border hover:bg-surface-hover hover:border-border-strong shadow-soft',
    ghost: 'bg-transparent text-foreground-muted hover:bg-surface-hover hover:text-foreground',
    danger: 'bg-gradient-to-br from-danger to-danger text-danger-foreground shadow-soft hover:shadow-lifted hover:-translate-y-0.5',
    success: 'bg-gradient-to-br from-success to-success text-success-foreground shadow-soft hover:shadow-lifted hover:-translate-y-0.5'
  };

  const sizes: Record<Size, string> = {
    sm: 'h-8 px-3 text-xs gap-1.5',
    md: 'h-10 px-4 text-sm gap-2',
    lg: 'h-12 px-6 text-base gap-2'
  };

  const classes = $derived(`${base} ${variants[variant]} ${sizes[size]} ${className}`);
</script>

<button {type} {disabled} {onclick} class={classes}>
  {@render children()}
</button>
# Design System

> **Versión:** `v1.0.0` | **Última actualización:** `22/07/2026`  
> Visual tokens, Geist theme variables, typography and component guidelines.

## 1. Identity

A serious, dense, modern ERP. Inspiration (as quality bar, not to copy):
Linear's information density, Apple HIG's clarity and feedback. Signature
element: a refined **theme toggle** with smooth-but-snappy transition
(180ms) and a "two-state" icon swap; the audit-log diff view (Phase 4) will
share this restrained motion language.

Avoided generic patterns: cream-with-terracotta, near-black-with-acid-accent,
newspaper-with-fine-rules.

## 2. Color tokens (semantic, RGB triplets for alpha support)

| Token | Light | Dark | Usage |
|-------|-------|------|-------|
| `--surface` | 255 255 255 | 14 17 25 | App background |
| `--surface-muted` | 247 248 250 | 22 26 37 | Cards, panels, hover |
| `--border` | 226 229 237 | 38 44 60 | Borders, dividers |
| `--foreground` | 17 24 39 | 233 237 244 | Primary text |
| `--foreground-muted` | 90 100 116 | 156 166 184 | Secondary text |
| `--primary` | 37 99 235 | 96 165 250 | Primary actions, focus ring |
| `--primary-foreground` | 255 255 255 | 8 12 20 | Text on primary |
| `--accent` | 14 165 233 | 56 189 248 | Secondary accent |
| `--danger` | 220 38 38 | 248 113 113 | Destructive actions, errors |
| `--success` | 22 163 74 | 74 222 128 | Confirmations |
| `--warning` | 217 119 6 | 251 191 36 | Warnings, pending states |

Contrast target: WCAG AA (≥ 4.5:1 for body text on surface). All states use
**color + icon + text**, never color alone (color-blind safe).

## 3. Typography

- **Interface font**: `Inter` (system fallback). Good tabular-nums support.
- **Mono font**: `JetBrains Mono` for codes, IDs, audit diffs.
- **Scale**: 12 / 14 / 16 / 20 / 24 / 32 (px). Tailwind aliases: `text-xs` →
  `text-3xl`.

## 4. Spacing & layout

- Base unit: 4px. Tailwind's default scale is used (so 1 unit = 0.25rem).
- Layout (desktop ≥ 1024px): 240px sidebar + 64px header + fluid content with
  24px padding. Tablet (768–1023): collapsible sidebar (drawer). Mobile
  (<768): drawer overlay + sticky header.

## 5. Motion

- Default transition: 180ms `ease-out` for color/background changes.
- Theme toggle: 150ms.
- `prefers-reduced-motion: reduce` is honored globally (see `app.css`).

## 6. States (non-negotiable)

Every async view renders: **loading** (skeleton matching final layout),
**empty** (actionable message, not "no data"), **error** (human message + retry),
**success** (toast with consistent microcopy: `<noun> <verb>` e.g.
"Usuario creado").

## 7. Accessibility

- Full keyboard navigation; visible focus ring (`:focus-visible`).
- ARIA roles on custom components (dialog, menu, tabs).
- Color contrast AA minimum; status indicated with icon + text, not color alone.
- `prefers-reduced-motion` respected.

## 8. Mobile-first

All views are designed at 375px first and expanded. No unintentional
horizontal scroll. Tables on mobile become cards or horizontally scroll
within their container only.
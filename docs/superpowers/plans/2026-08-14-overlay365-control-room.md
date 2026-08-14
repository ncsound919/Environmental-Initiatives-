# Overlay365 Control Room — Frontend Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild all 12 routes of the ECOS web frontend (`apps/web`) into a unified dark "Overlay365 Control Room" theme using only existing deps (Next.js, React, Recharts, plain CSS) — no new packages.

**Architecture:** A single dark design system expressed in CSS variables in `globals.css`, shared UI components (`Sidebar`, `KpiCard`, `Badge`, `Skeleton`, `StatBand`, `Card`), a `layout.tsx` that mounts the sidebar around page content, and per-page restyle removing all Tailwind class references. Static content comes from `lib/data.ts`; revenue pages keep their live `lib/api.ts` wiring.

**Tech Stack:** Next.js 14 (App Router, React 18), plain CSS + CSS variables, Recharts 2, TypeScript strict.

**Spec:** `docs/superpowers/specs/2026-08-14-overlay365-control-room-design.md`

**Repo:** `C:\Users\User\Downloads\Uplift\01_Platforms\ECOS-Environmental-Initiatives`
**Web app dir (all tasks below run inside):** `apps/web`
**Commands run from:** `apps/web` unless otherwise noted.

> **Important for implementers:** There is NO test framework in the web app (no jest/vitest). Verification for each task = `npm run build` (type-check + compile) and `npm run lint`. Always verify before committing. Do NOT run `npm install` at repo root — run it inside `apps/web`.

---

## Baseline & Global Setup

### Task 0: Install deps and establish a clean baseline build

**Files:**
- No source changes

- [ ] **Step 1: Install web dependencies**

Run: `npm install`
Expected: completes without error; creates `apps/web/node_modules` and `apps/web/package-lock.json`.

- [ ] **Step 2: Baseline production build**

Run: `npm run build`
Expected: SUCCESS. Note: the current build may warn about the layout, but must not hard-fail. If it hard-fails, stop and report — do not proceed.

- [ ] **Step 3: Baseline lint**

Run: `npm run lint`
Expected: completes (may print warnings). Record current warnings count in a note for comparison.

- [ ] **Step 4: Commit**

```bash
git add package-lock.json
git commit -m "chore(web): install dependencies and lockfile"
```

---

### Task 1: Rewrite globals.css with the Control Room design system

**Files:**
- Rewrite: `src/app/globals.css`

This file defines the entire design system. Replace its full contents (455 lines of light theme) with the following dark theme:

```css
/* ==========================================================================
   Overlay365 Control Room — Design System
   Dark climate-tech ops theme. Plain CSS + variables. No frameworks.
   ========================================================================== */

:root {
  /* Surfaces */
  --bg: #0b1220;
  --panel: #0f172a;
  --panel-raised: #111c2e;
  --border: #1f2937;
  --border-strong: #334155;

  /* Text */
  --text: #e2e8f0;
  --text-muted: #94a3b8;
  --text-dim: #64748b;

  /* Accents (module colors) */
  --emerald: #10b981;
  --emerald-hover: #34d399;
  --cyan: #22d3ee;
  --violet: #a78bfa;
  --amber: #fbbf24;
  --rose: #fb7185;
  --blue: #3b82f6;
  --teal: #14b8a6;

  /* Semantic */
  --success: #34d399;
  --warning: #fbbf24;
  --danger: #fb7185;

  /* Type */
  --font-sans: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
    Ubuntu, Cantarell, 'Fira Sans', 'Droid Sans', 'Helvetica Neue', sans-serif;
  --font-mono: ui-monospace, SFMono-Regular, Menlo, Consolas, 'Liberation Mono',
    monospace;

  /* Layout */
  --sidebar-w: 240px;
  --max-w: 1200px;
  --radius: 12px;
  --radius-sm: 8px;
  --glow: 0 0 14px rgba(16, 185, 129, 0.18);
}

* { box-sizing: border-box; padding: 0; margin: 0; }

html, body {
  max-width: 100vw;
  overflow-x: hidden;
  background: var(--bg);
  color: var(--text);
  font-family: var(--font-sans);
  font-size: 16px;
  line-height: 1.55;
}

a { color: inherit; text-decoration: none; }
button { font-family: inherit; cursor: pointer; }

code, pre, .mono {
  font-family: var(--font-mono);
}

/* ------------------------------------------------------------------ */
/* Layout shell                                                       */
/* ------------------------------------------------------------------ */

.app-shell { display: flex; min-height: 100vh; }

.app-main {
  flex: 1;
  min-width: 0;
  margin-left: var(--sidebar-w);
  padding: 0 2rem 3rem;
}

@media (max-width: 900px) {
  .app-main { margin-left: 0; padding: 0 1rem 2rem; }
}

.page-container { max-width: var(--max-w); margin: 0 auto; }

/* ------------------------------------------------------------------ */
/* Sidebar                                                            */
/* ------------------------------------------------------------------ */

.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  width: var(--sidebar-w);
  background: var(--panel);
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  z-index: 200;
}

.sidebar-logo {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 1.25rem 1.25rem;
  font-weight: 800;
  font-size: 1.1rem;
  color: var(--emerald-hover);
  border-bottom: 1px solid var(--border);
}

.sidebar-nav { flex: 1; overflow-y: auto; padding: 1rem 0.75rem; }

.sidebar-group-label {
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-dim);
  padding: 0.75rem 0.75rem 0.4rem;
}

.sidebar-link {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0.75rem;
  margin-bottom: 0.15rem;
  border-radius: var(--radius-sm);
  color: var(--text-muted);
  font-size: 0.875rem;
  font-weight: 500;
  transition: background 0.15s, color 0.15s;
}

.sidebar-link:hover { background: var(--panel-raised); color: var(--text); }

.sidebar-link.active {
  background: rgba(16, 185, 129, 0.12);
  color: var(--emerald-hover);
  border: 1px solid rgba(16, 185, 129, 0.25);
}

.sidebar-link .ico { width: 1.1rem; text-align: center; font-size: 0.9rem; }

.sidebar-footer {
  padding: 0.9rem 1.25rem;
  border-top: 1px solid var(--border);
  font-size: 0.7rem;
  color: var(--text-dim);
  font-family: var(--font-mono);
}

/* Mobile drawer */
.nav-toggle {
  display: none;
  position: fixed;
  top: 0.8rem;
  left: 0.8rem;
  z-index: 300;
  background: var(--panel-raised);
  border: 1px solid var(--border-strong);
  color: var(--text);
  border-radius: var(--radius-sm);
  padding: 0.5rem 0.7rem;
  font-size: 1.1rem;
}

.nav-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 23, 0.7);
  z-index: 150;
}

@media (max-width: 900px) {
  .nav-toggle { display: block; }
  .sidebar {
    transform: translateX(-100%);
    transition: transform 0.2s ease;
    box-shadow: 4px 0 20px rgba(0,0,0,0.4);
  }
  .sidebar.open { transform: translateX(0); }
  .nav-overlay.show { display: block; }
}

/* ------------------------------------------------------------------ */
/* Page header / hero                                                  */
/* ------------------------------------------------------------------ */

.page-hero {
  background: linear-gradient(135deg, var(--hero-from, #064e3b), var(--hero-to, #0c4a6e));
  border-bottom: 1px solid var(--border);
  padding: 2.5rem 0;
  margin: 0 -2rem 2rem;
}

@media (max-width: 900px) { .page-hero { margin: 0 -1rem 1.5rem; } }

.page-hero .page-container { padding: 0 2rem; }

.page-title { font-size: 2rem; font-weight: 800; letter-spacing: -0.01em; }

.page-subtitle {
  color: var(--hero-text, var(--text-muted));
  font-size: 1.05rem;
  max-width: 640px;
  margin-top: 0.4rem;
}

.page-section { padding: 2rem 0; }

.section-heading {
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.section-sub { color: var(--text-muted); font-size: 0.95rem; margin-bottom: 1.5rem; }

/* ------------------------------------------------------------------ */
/* Stat band + KPI cards                                               */
/* ------------------------------------------------------------------ */

.stat-band {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-top: 1.5rem;
}

.kpi-card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.1rem 1.25rem;
  text-align: center;
}

.kpi-card[data-accent="emerald"] { border-color: rgba(16,185,129,0.4); box-shadow: 0 0 14px rgba(16,185,129,0.14); }
.kpi-card[data-accent="cyan"]    { border-color: rgba(34,211,238,0.4);  box-shadow: 0 0 14px rgba(34,211,238,0.14); }
.kpi-card[data-accent="violet"]  { border-color: rgba(167,139,250,0.4); box-shadow: 0 0 14px rgba(167,139,250,0.14); }
.kpi-card[data-accent="amber"]   { border-color: rgba(251,191,36,0.4);  box-shadow: 0 0 14px rgba(251,191,36,0.14); }
.kpi-card[data-accent="rose"]    { border-color: rgba(251,113,133,0.4); box-shadow: 0 0 14px rgba(251,113,133,0.14); }
.kpi-card[data-accent="blue"]    { border-color: rgba(59,130,246,0.4);  box-shadow: 0 0 14px rgba(59,130,246,0.14); }

.kpi-value {
  font-family: var(--font-mono);
  font-size: 1.7rem;
  font-weight: 700;
  line-height: 1.2;
}

.kpi-label { color: var(--text-muted); font-size: 0.8rem; margin-top: 0.25rem; }

.kpi-trend { font-size: 0.75rem; margin-top: 0.3rem; }
.kpi-trend.up { color: var(--success); }
.kpi-trend.down { color: var(--danger); }
.kpi-trend.flat { color: var(--text-dim); }

/* ------------------------------------------------------------------ */
/* Cards, grids, badges, pills                                        */
/* ------------------------------------------------------------------ */

.card {
  background: var(--panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  transition: border-color 0.15s, transform 0.15s, box-shadow 0.15s;
}

.card.hoverable:hover {
  border-color: var(--accent, var(--emerald));
  transform: translateY(-2px);
  box-shadow: 0 6px 24px rgba(0,0,0,0.3);
}

.grid { display: grid; gap: 1.25rem; }
.grid-3 { grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
.grid-4 { grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); }
.grid-2 { grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); }

@media (max-width: 700px) {
  .grid-3, .grid-4, .grid-2 { grid-template-columns: 1fr; }
}

.card-accent-bar { height: 4px; border-radius: var(--radius) var(--radius) 0 0; }

.badge {
  display: inline-block;
  padding: 0.2rem 0.7rem;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.badge-emerald { background: rgba(16,185,129,0.14); color: var(--emerald-hover); }
.badge-cyan { background: rgba(34,211,238,0.14); color: var(--cyan); }
.badge-violet { background: rgba(167,139,250,0.14); color: var(--violet); }
.badge-amber { background: rgba(251,191,36,0.14); color: var(--amber); }
.badge-rose { background: rgba(251,113,133,0.14); color: var(--rose); }
.badge-blue { background: rgba(59,130,246,0.14); color: #60a5fa; }
.badge-teal { background: rgba(20,184,166,0.14); color: var(--teal); }
.badge-dim { background: rgba(100,116,139,0.16); color: var(--text-muted); }

.pill {
  padding: 0.35rem 1rem;
  border-radius: 9999px;
  font-size: 0.8rem;
  font-weight: 600;
  background: var(--panel-raised);
  color: var(--text-muted);
  border: 1px solid var(--border-strong);
  transition: background 0.15s, color 0.15s;
}

.pill:hover { color: var(--text); }
.pill.active { background: var(--emerald); border-color: var(--emerald); color: #042f2e; }
.pill.blue-active { background: var(--blue); border-color: var(--blue); color: #eff6ff; }

/* Buttons */
.btn {
  display: inline-block;
  padding: 0.6rem 1.4rem;
  border-radius: var(--radius-sm);
  font-weight: 700;
  font-size: 0.9rem;
  border: 1px solid transparent;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
  text-align: center;
}

.btn-primary { background: var(--emerald); color: #042f2e; }
.btn-primary:hover { background: var(--emerald-hover); }

.btn-outline { background: transparent; border-color: var(--emerald); color: var(--emerald-hover); }
.btn-outline:hover { background: rgba(16,185,129,0.12); }

.btn-ghost { background: transparent; color: var(--text-muted); }
.btn-ghost:hover { color: var(--text); background: var(--panel-raised); }

/* ------------------------------------------------------------------ */
/* Progress bar                                                        */
/* ------------------------------------------------------------------ */

.progress-track {
  height: 8px;
  background: var(--panel-raised);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  background: linear-gradient(90deg, var(--emerald), var(--cyan));
}

.progress-fill[data-empty] { background: var(--text-dim); }

/* ------------------------------------------------------------------ */
/* Data table                                                          */
/* ------------------------------------------------------------------ */

.data-table { width: 100%; border-collapse: collapse; }

.data-table th, .data-table td {
  padding: 0.8rem 1rem;
  text-align: left;
  border-bottom: 1px solid var(--border);
  font-size: 0.875rem;
}

.data-table th {
  color: var(--text-dim);
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table tbody tr:hover { background: var(--panel-raised); }

/* ------------------------------------------------------------------ */
/* Skeleton loading                                                    */
/* ------------------------------------------------------------------ */

.skeleton {
  background: linear-gradient(90deg, var(--panel) 25%, var(--panel-raised) 50%, var(--panel) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
  border-radius: var(--radius-sm);
}

@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }

/* ------------------------------------------------------------------ */
/* Recharts dark overrides                                             */
/* ------------------------------------------------------------------ */

.recharts-cartesian-grid line { stroke: var(--border); }
.recharts-text { fill: var(--text-dim); font-size: 12px; }
.recharts-tooltip-wrapper .recharts-default-tooltip {
  background: var(--panel-raised) !important;
  border: 1px solid var(--border-strong) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--text) !important;
}

/* ------------------------------------------------------------------ */
/* Misc                                                               */
/* ------------------------------------------------------------------ */

.mono-value { font-family: var(--font-mono); }

.code-block {
  background: #0f172a;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 1rem;
  font-family: var(--font-mono);
  font-size: 0.8rem;
  overflow: auto;
  color: #e2e8f0;
}

.status-dot { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-right: 0.4rem; }
.status-dot.on { background: var(--success); }
.status-dot.off { background: var(--text-dim); }

.spinner {
  width: 2.5rem; height: 2.5rem;
  border: 3px solid var(--border);
  border-top-color: var(--emerald);
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.center-loading { display: flex; align-items: center; justify-content: center; min-height: 60vh; }
```

- [ ] **Step 1: Replace globals.css**

Overwrite `src/app/globals.css` with the contents above.

- [ ] **Step 2: Verify build**

Run: `npm run build`
Expected: SUCCESS (globals.css is not imported by anything that would type-check, but a broken build must be caught now).

- [ ] **Step 3: Commit**

```bash
git add src/app/globals.css
git commit -m "style(web): add Overlay365 Control Room design system (CSS)"
```

---

### Task 2: Create shared UI components

**Files:**
- Create: `src/components/Sidebar.tsx`
- Create: `src/components/PageHeader.tsx`
- Create: `src/components/KpiCard.tsx`
- Create: `src/components/StatBand.tsx`
- Create: `src/components/Card.tsx`
- Create: `src/components/Badge.tsx`
- Create: `src/components/Skeleton.tsx`
- Delete: `src/components/Header.tsx`
- Delete: `src/components/Footer.tsx`

- [ ] **Step 1: Sidebar.tsx**

```tsx
'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useState } from 'react';

const PLATFORM_LINKS = [
  { href: '/', label: 'Home', icon: '🏠' },
  { href: '/projects', label: 'Initiatives', icon: '🌍' },
  { href: '/dashboard', label: 'Dashboard', icon: '📊' },
  { href: '/partnerships', label: 'Partnerships', icon: '🤝' },
  { href: '/api-docs', label: 'API', icon: '🔌' },
];

const REVENUE_LINKS = [
  { href: '/revenue', label: 'Revenue', icon: '💰' },
  { href: '/challenges', label: 'Challenges', icon: '🏆' },
  { href: '/membership', label: 'Membership', icon: '👑' },
  { href: '/marketplace', label: 'Marketplace', icon: '🛒' },
  { href: '/gamification', label: 'Gamification', icon: '⭐' },
  { href: '/diy-kits', label: 'DIY Kits', icon: '🔧' },
];

function isActive(pathname: string, href: string): boolean {
  if (href === '/') return pathname === '/';
  return pathname.startsWith(href);
}

export function Sidebar() {
  const pathname = usePathname() ?? '/';
  const [open, setOpen] = useState(false);

  const nav = (
    <>
      <div className="sidebar-logo">
        <span>🌐</span>
        <span>Overlay365</span>
      </div>
      <nav className="sidebar-nav">
        <div className="sidebar-group-label">Platform</div>
        {PLATFORM_LINKS.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            onClick={() => setOpen(false)}
            className={`sidebar-link ${isActive(pathname, l.href) ? 'active' : ''}`}
          >
            <span className="ico">{l.icon}</span>
            {l.label}
          </Link>
        ))}
        <div className="sidebar-group-label">Revenue</div>
        {REVENUE_LINKS.map((l) => (
          <Link
            key={l.href}
            href={l.href}
            onClick={() => setOpen(false)}
            className={`sidebar-link ${isActive(pathname, l.href) ? 'active' : ''}`}
          >
            <span className="ico">{l.icon}</span>
            {l.label}
          </Link>
        ))}
      </nav>
      <div className="sidebar-footer">
        <span className="status-dot on" />
        ecosystem online
      </div>
    </>
  );

  return (
    <>
      <button className="nav-toggle" onClick={() => setOpen(true)} aria-label="Open navigation">☰</button>
      {open && <div className="nav-overlay show" onClick={() => setOpen(false)} />}
      <aside className={`sidebar ${open ? 'open' : ''}`}>{nav}</aside>
    </>
  );
}
```

- [ ] **Step 2: PageHeader.tsx**

```tsx
import { ReactNode } from 'react';

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  accent?: 'emerald' | 'cyan' | 'violet' | 'amber' | 'rose' | 'blue' | 'teal';
  children?: ReactNode; // stat band etc.
}

const GRADIENTS: Record<string, [string, string]> = {
  emerald: ['#064e3b', '#0c4a6e'],
  cyan: ['#164e63', '#0c4a6e'],
  violet: ['#312e81', '#4c1d95'],
  amber: ['#713f12', '#7c2d12'],
  rose: ['#881337', '#4c0519'],
  blue: ['#1e3a8a', '#164e63'],
  teal: ['#134e4a', '#164e63'],
};

export function PageHeader({ title, subtitle, accent = 'emerald', children }: PageHeaderProps) {
  const [from, to] = GRADIENTS[accent] ?? GRADIENTS.emerald;
  return (
    <section className="page-hero" style={{ '--hero-from': from, '--hero-to': to } as React.CSSProperties}>
      <div className="page-container">
        <h1 className="page-title">{title}</h1>
        {subtitle && <p className="page-subtitle">{subtitle}</p>}
        {children}
      </div>
    </section>
  );
}
```

- [ ] **Step 3: KpiCard.tsx**

```tsx
interface KpiCardProps {
  value: string;
  label: string;
  accent?: 'emerald' | 'cyan' | 'violet' | 'amber' | 'rose' | 'blue';
  trend?: { dir: 'up' | 'down' | 'flat'; text: string };
}

export function KpiCard({ value, label, accent = 'emerald', trend }: KpiCardProps) {
  return (
    <div className="kpi-card" data-accent={accent}>
      <div className="kpi-value">{value}</div>
      <div className="kpi-label">{label}</div>
      {trend && (
        <div className={`kpi-trend ${trend.dir === 'up' ? 'up' : trend.dir === 'down' ? 'down' : 'flat'}`}>
          {trend.dir === 'up' ? '▲' : trend.dir === 'down' ? '▼' : '•'} {trend.text}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 4: StatBand.tsx**

```tsx
import { ReactNode } from 'react';

export function StatBand({ children }: { children: ReactNode }) {
  return <div className="stat-band">{children}</div>;
}
```

- [ ] **Step 5: Card.tsx**

```tsx
import { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  hoverable?: boolean;
  accent?: string; // any CSS color for the top bar / hover border
  accentBar?: boolean;
  className?: string;
}

export function Card({ children, hoverable, accent, accentBar, className = '' }: CardProps) {
  return (
    <div
      className={`card ${hoverable ? 'hoverable' : ''} ${className}`}
      style={
        {
          '--accent': accent ?? undefined,
          borderTop: accentBar ? `3px solid ${accent}` : undefined,
        } as React.CSSProperties
      }
    >
      {children}
    </div>
  );
}
```

- [ ] **Step 6: Badge.tsx**

```tsx
import { ReactNode } from 'react';

type Tone = 'emerald' | 'cyan' | 'violet' | 'amber' | 'rose' | 'blue' | 'teal' | 'dim';

export function Badge({ tone = 'dim', children }: { tone?: Tone; children: ReactNode }) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}
```

- [ ] **Step 7: Skeleton.tsx**

```tsx
export function Skeleton({ width, height = 18, style }: { width?: string | number; height?: number; style?: React.CSSProperties }) {
  return <div className="skeleton" style={{ width: width ?? '100%', height, ...style }} />;
}
```

- [ ] **Step 8: Delete Header.tsx and Footer.tsx**

Delete `src/components/Header.tsx` and `src/components/Footer.tsx`. They are replaced by the sidebar + layout.

- [ ] **Step 9: Verify build**

Run: `npm run build`
Expected: FAILS — the old pages still import `Header`/`Footer`. This is expected; subsequent tasks update each page. (If it happens to pass because unused, continue anyway — the import is in each page.)

- [ ] **Step 10: Verify components compile in isolation (TypeScript)**

Run: `npx tsc --noEmit`
Expected: errors ONLY about `Header`/`Footer` missing. Confirm no errors inside the new component files.

- [ ] **Step 11: Commit**

```bash
git add src/components/Sidebar.tsx src/components/PageHeader.tsx src/components/KpiCard.tsx src/components/StatBand.tsx src/components/Card.tsx src/components/Badge.tsx src/components/Skeleton.tsx
git commit -m "feat(web): add shared Control Room UI components (sidebar, cards, badges, skeleton)"
```

(Do NOT add Header.tsx/Footer.tsx deletions yet — commit them together with the last page that stops importing them.)

---

### Task 3: Mount the sidebar in layout.tsx

**Files:**
- Modify: `src/app/layout.tsx`

- [ ] **Step 1: Rewrite layout.tsx**

```tsx
import type { Metadata } from 'next';
import './globals.css';
import { Sidebar } from '@/components/Sidebar';

export const metadata: Metadata = {
  title: 'Overlay365 - Environmental Initiatives Ecosystem',
  description: '13 Interconnected Climate-Tech Sub-Businesses | Strategic Partnerships & Affiliate Marketing | Overlay365',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="app-shell">
          <Sidebar />
          <main className="app-main">{children}</main>
        </div>
      </body>
    </html>
  );
}
```

- [ ] **Step 2: Verify build**

Run: `npm run build`
Expected: still failing only on pages that import `Header`/`Footer`.

- [ ] **Step 3: Commit**

```bash
git add src/app/layout.tsx
git commit -m "feat(web): mount sidebar shell in root layout"
```

---

## Page conversions

> All remaining tasks follow the same pattern: replace the page's markup with the new dark-theme markup (plain CSS classes), remove `Header`/`Footer` imports, keep the data fetching logic intact. Each task ends with `npm run build` + commit. After each page conversion, remaining `Header`/`Footer` build errors should drop by one.

### Task 4: Home page

**Files:**
- Rewrite: `src/app/page.tsx`

- [ ] **Step 1: Rewrite page.tsx**

```tsx
import Link from 'next/link';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { ProjectCard } from '@/components/ProjectCard';
import { projects, phases } from '@/lib/data';

const PHASE_TONES = ['emerald', 'cyan', 'violet', 'amber'] as const;

export default function Home() {
  return (
    <>
      <PageHeader
        title="13 Interconnected Climate-Tech Businesses"
        subtitle="From facilities and hardware to hydroponics and deep-tech R&D — one unified ecosystem building a sustainable future."
        accent="emerald"
      >
        <StatBand>
          <KpiCard value="13" label="Initiatives" accent="emerald" />
          <KpiCard value="$183M" label="Year 3 ARR Target" accent="cyan" />
          <KpiCard value="70%" label="Readiness" accent="violet" />
          <KpiCard value="5" label="Revenue Streams" accent="amber" />
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        <h2 className="section-heading">The Overlay365 Ecosystem</h2>
        <p className="section-sub">
          Explore our 13 sub-businesses organized by deployment phase. Each seeks strategic partners and affiliate marketing teams.
        </p>

        {phases.map((phase, pi) => (
          <section key={phase.id} style={{ marginBottom: '2.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '1rem' }}>
              <span className="badge badge-emerald" style={{ fontSize: '0.9rem' }}>Phase {phase.id}</span>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{phase.name}</h3>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{phase.description}</div>
              </div>
            </div>
            <div className="grid grid-3">
              {projects
                .filter((p) => p.phase === phase.id)
                .map((project) => (
                  <Link key={project.id} href={`/projects/${project.code}`}>
                    <ProjectCard project={project} />
                  </Link>
                ))}
            </div>
          </section>
        ))}

        <section style={{ marginTop: '3rem', textAlign: 'center' }}>
          <Card hoverable accent="var(--emerald)" style={{ padding: '2.5rem' }}>
            <h2 className="section-heading">Ready to Explore?</h2>
            <p className="section-sub" style={{ maxWidth: '480px', margin: '0.4rem auto 1.5rem' }}>
              View the system dashboard for real-time monitoring, or explore partnership opportunities.
            </p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              <Link href="/dashboard" className="btn btn-primary">Open Dashboard</Link>
              <Link href="/partnerships" className="btn btn-outline">Explore Partnerships</Link>
            </div>
          </Card>
        </section>
      </div>
    </>
  );
}
```

- [ ] **Step 2: Build**

Run: `npm run build`
Expected: FAILS (still other pages importing Header/Footer), but the Home page no longer contributes errors.

- [ ] **Step 3: Commit**

```bash
git add src/app/page.tsx
git commit -m "feat(web): restyle home page to Control Room theme"
```

---

### Task 5: ProjectCard component (used by Home + Initiatives)

**Files:**
- Rewrite: `src/components/ProjectCard.tsx`

- [ ] **Step 1: Rewrite ProjectCard.tsx**

```tsx
import type { Project } from '@/lib/data';
import { withOpacity } from '@/lib/utils';
import { Badge } from '@/components/Badge';

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <div className="card hoverable" style={{ padding: '1.5rem', height: '100%', display: 'flex', flexDirection: 'column', '--accent': project.color } as React.CSSProperties}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
        <div style={{ fontSize: '1.8rem', width: 52, height: 52, borderRadius: 12, background: withOpacity(project.color, 12), display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {project.icon}
        </div>
        <Badge tone={project.readiness > 0 ? 'emerald' : 'dim'}>
          {project.readiness > 0 ? `${project.readiness}% Ready` : 'Reserved'}
        </Badge>
      </div>
      <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{project.name}</h3>
      <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: '0.15rem 0 0.6rem' }}>{project.type}</div>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', lineHeight: 1.5, flex: 1 }}>{project.description}</p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '1rem' }}>
        {project.features.slice(0, 3).map((feature, index) => (
          <span key={index} className="badge badge-dim">{feature}</span>
        ))}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: Build + commit**

Run: `npm run build` (expect same state), then

```bash
git add src/components/ProjectCard.tsx
git commit -m "style(web): restyle ProjectCard for dark theme"
```

---

### Task 6: Dashboard page

**Files:**
- Rewrite: `src/app/dashboard/page.tsx`

- [ ] **Step 1: Rewrite dashboard page**

```tsx
'use client';

import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { mockTelemetryData, systemMetrics, projects } from '@/lib/data';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Area,
  AreaChart,
} from 'recharts';

export default function Dashboard() {
  return (
    <>
      <PageHeader title="System Dashboard" subtitle="Real-time monitoring of the ECOS ecosystem" accent="cyan">
        <StatBand>
          <KpiCard value={`${systemMetrics.totalPowerGeneration} kW`} label="Total Power Generation" accent="cyan" trend={{ dir: 'up', text: '12% vs yesterday' }} />
          <KpiCard value={`${systemMetrics.waterProduction} L/hr`} label="Water Production" accent="cyan" trend={{ dir: 'up', text: '8% vs yesterday' }} />
          <KpiCard value={`${systemMetrics.carbonOffset} t/day`} label="Carbon Offset" accent="cyan" trend={{ dir: 'up', text: '5% vs yesterday' }} />
          <KpiCard value={`${systemMetrics.activeDevices}`} label="Active Devices" accent="cyan" trend={{ dir: 'flat', text: `Uptime ${systemMetrics.systemUptime}%` }} />
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        <div className="grid grid-2" style={{ marginBottom: '1.5rem' }}>
          <Card style={{ padding: '1.25rem' }}>
            <h3 style={{ fontWeight: 700, marginBottom: '0.75rem' }}>☀️ Solar Generation (W/m²)</h3>
            <ResponsiveContainer width="100%" height={220}>
              <AreaChart data={mockTelemetryData.solar}>
                <defs>
                  <linearGradient id="gSolar" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#eab308" stopOpacity={0.35} />
                    <stop offset="95%" stopColor="#eab308" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="value" stroke="#eab308" strokeWidth={2} fill="url(#gSolar)" />
              </AreaChart>
            </ResponsiveContainer>
          </Card>

          <Card style={{ padding: '1.25rem' }}>
            <h3 style={{ fontWeight: 700, marginBottom: '0.75rem' }}>💧 Hydro Power Output (kW)</h3>
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={mockTelemetryData.hydro}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#22d3ee" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </div>

        <div className="grid grid-2" style={{ marginBottom: '1.5rem' }}>
          <Card style={{ padding: '1.25rem' }}>
            <h3 style={{ fontWeight: 700, marginBottom: '0.75rem' }}>🌊 AWG Water Production (L/hr)</h3>
            <ResponsiveContainer width="100%" height={220}>
              <LineChart data={mockTelemetryData.water}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="time" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="value" stroke="#14b8a6" strokeWidth={2} dot={{ fill: '#14b8a6', r: 3 }} />
              </LineChart>
            </ResponsiveContainer>
          </Card>

          <Card style={{ padding: '1.25rem' }}>
            <h3 style={{ fontWeight: 700, marginBottom: '1rem' }}>🔄 Dispatcher Status</h3>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              {[
                ['System Health', 'Operational', 'success'],
                ['Active Initiatives', '12', 'text'],
                ['Pending Commands', '3', 'text'],
                ['Cross-Project Synergies', 'Active', 'success'],
              ].map(([label, value, kind], i) => (
                <div key={label} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.8rem 0', borderBottom: i < 3 ? '1px solid var(--border)' : 'none' }}>
                  <span style={{ color: 'var(--text-muted)' }}>{label}</span>
                  <span style={{ fontWeight: 700, color: kind === 'success' ? 'var(--success)' : 'var(--text)' }}>{value}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        <Card style={{ padding: '1.25rem' }}>
          <h3 style={{ fontWeight: 700, marginBottom: '1rem' }}>📊 Project Status Overview</h3>
          <table className="data-table">
            <thead>
              <tr><th>Project</th><th>Name</th><th>Type</th><th>Readiness</th><th>Status</th></tr>
            </thead>
            <tbody>
              {projects.map((project) => (
                <tr key={project.id}>
                  <td><span>{project.icon}</span> {project.id}</td>
                  <td style={{ fontWeight: 500 }}>{project.name}</td>
                  <td style={{ color: 'var(--text-muted)' }}>{project.type}</td>
                  <td>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <div className="progress-track" style={{ width: 80 }}>
                        <div className="progress-fill" style={{ width: `${project.readiness}%` }} data-empty={project.readiness === 0 ? '' : undefined} />
                      </div>
                      <span style={{ fontSize: '0.8rem' }}>{project.readiness}%</span>
                    </div>
                  </td>
                  <td>
                    <Badge tone={project.readiness > 0 ? 'emerald' : 'dim'}>
                      {project.readiness > 0 ? 'Active' : 'Reserved'}
                    </Badge>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      </div>
    </>
  );
}
```

- [ ] **Step 2: Build + commit**

```bash
git add src/app/dashboard/page.tsx
git commit -m "feat(web): restyle dashboard with glowing KPIs and dark charts"
```

---

### Task 7: Initiatives page

**Files:**
- Rewrite: `src/app/projects/page.tsx`

- [ ] **Step 1: Rewrite**

```tsx
'use client';

import Link from 'next/link';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { ProjectCard } from '@/components/ProjectCard';
import { projects, phases } from '@/lib/data';

export default function ProjectsPage() {
  return (
    <>
      <PageHeader title="All Initiatives" subtitle="Explore all 13 Overlay365 sub-businesses. Click any card to view partnership and resource details." accent="emerald">
        <StatBand>
          <KpiCard value="13" label="Initiatives" accent="emerald" />
          <KpiCard value={`${phases.length}`} label="Phases" accent="cyan" />
          <KpiCard value="70%" label="Avg Readiness" accent="violet" />
          <KpiCard value="12" label="Active" accent="amber" />
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        {phases.map((phase) => (
          <section key={phase.id} style={{ marginBottom: '2.5rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', marginBottom: '1rem' }}>
              <span className="badge badge-emerald" style={{ fontSize: '0.9rem' }}>Phase {phase.id}</span>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{phase.name}</h3>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{phase.description}</div>
              </div>
            </div>
            <div className="grid grid-3">
              {projects
                .filter((p) => p.phase === phase.id)
                .map((project) => (
                  <Link key={project.id} href={`/projects/${project.code}`}>
                    <ProjectCard project={project} />
                  </Link>
                ))}
            </div>
          </section>
        ))}
      </div>
    </>
  );
}
```

- [ ] **Step 2: Build + commit**

```bash
git add src/app/projects/page.tsx
git commit -m "feat(web): restyle initiatives page"
```

---

### Task 8: Project detail page

**Files:**
- Rewrite: `src/app/projects/[code]/page.tsx`

- [ ] **Step 1: Rewrite**

```tsx
'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { projects } from '@/lib/data';
import { withOpacity } from '@/lib/utils';

export default function ProjectDetailPage() {
  const params = useParams();
  const code = params.code as string;
  const project = projects.find((p) => p.code === code);

  if (!project) {
    return (
      <div className="page-container page-section">
        <h1 className="page-title">Project Not Found</h1>
        <p className="section-sub">The requested project does not exist.</p>
        <Link href="/projects" className="btn btn-primary">Back to Initiatives</Link>
      </div>
    );
  }

  return (
    <>
      <PageHeader title={`${project.icon} ${project.name}`} subtitle={project.type} accent="emerald">
        <div style={{ display: 'flex', gap: '0.8rem', marginTop: '1rem', flexWrap: 'wrap' }}>
          <Badge tone={project.readiness > 0 ? 'emerald' : 'dim'}>{project.readiness}% Ready</Badge>
          <Badge tone="cyan">Phase {project.phase}</Badge>
        </div>
      </PageHeader>

      <div className="page-container page-section">
        <div className="grid grid-2" style={{ gridTemplateColumns: 'minmax(0, 2fr) minmax(0, 1fr)', alignItems: 'start' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {[
              ['Description', project.description],
              ['Business Model', project.businessModel],
              ['RegenCity Role', project.regenCityRole],
            ].map(([title, body]) => (
              <Card key={title} style={{ padding: '1.5rem' }}>
                <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>{title}</h2>
                <p style={{ lineHeight: 1.7, color: 'var(--text-muted)' }}>{body}</p>
              </Card>
            ))}

            <Card style={{ padding: '1.5rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>Strategic Partnership Needs</h2>
              <ul style={{ listStyle: 'none' }}>
                {project.partnershipNeeds.map((need, i) => (
                  <li key={i} style={{ padding: '0.6rem 0', borderBottom: i < project.partnershipNeeds.length - 1 ? '1px solid var(--border)' : 'none', display: 'flex', gap: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                    <span style={{ color: project.color }}>🤝</span>{need}
                  </li>
                ))}
              </ul>
            </Card>

            <Card style={{ padding: '1.5rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>Affiliate Marketing Opportunities</h2>
              <ul style={{ listStyle: 'none' }}>
                {project.affiliateOpportunities.map((opp, i) => (
                  <li key={i} style={{ padding: '0.6rem 0', borderBottom: i < project.affiliateOpportunities.length - 1 ? '1px solid var(--border)' : 'none', display: 'flex', gap: '0.5rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                    <span style={{ color: project.color }}>📣</span>{opp}
                  </li>
                ))}
              </ul>
            </Card>

            <Card style={{ padding: '1.5rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>Features</h2>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {project.features.map((feature, i) => (
                  <span key={i} className="badge badge-emerald" style={{ background: withOpacity(project.color, 14), color: project.color }}>{feature}</span>
                ))}
              </div>
            </Card>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <Card style={{ padding: '1.5rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>Tech Stack</h2>
              <ul style={{ listStyle: 'none' }}>
                {project.techStack.map((tech, i) => (
                  <li key={i} style={{ padding: '0.7rem 0', borderBottom: i < project.techStack.length - 1 ? '1px solid var(--border)' : 'none', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                    <span style={{ color: project.color }}>•</span>{tech}
                  </li>
                ))}
              </ul>
            </Card>

            <Card style={{ padding: '1.5rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>API Endpoints</h2>
              {project.apiEndpoints.length > 0 ? (
                <ul style={{ listStyle: 'none' }}>
                  {project.apiEndpoints.map((endpoint, i) => (
                    <li key={i} className="code-block" style={{ marginBottom: '0.5rem' }}>{endpoint}</li>
                  ))}
                </ul>
              ) : (
                <p style={{ color: 'var(--text-dim)' }}>No API endpoints available yet.</p>
              )}
            </Card>

            <Card style={{ padding: '1.5rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>Resource Needs</h2>
              {project.resourceNeeds.map((group, gi) => (
                <div key={gi} style={{ marginBottom: '1rem' }}>
                  <div style={{ fontSize: '0.7rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: project.color, marginBottom: '0.4rem' }}>{group.category}</div>
                  <ul style={{ listStyle: 'none' }}>
                    {group.items.map((item, ii) => (
                      <li key={ii} style={{ fontSize: '0.85rem', color: 'var(--text-muted)', padding: '0.25rem 0', borderBottom: ii < group.items.length - 1 ? '1px solid var(--border)' : 'none', display: 'flex', gap: '0.4rem' }}>
                        <span style={{ color: 'var(--text-dim)' }}>–</span>{item}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </Card>

            <Card style={{ padding: '1.5rem' }}>
              <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>Project Info</h2>
              {[['Project ID', project.id], ['Code', project.code], ['Phase', String(project.phase)], ['Readiness', `${project.readiness}%`]].map(([label, value]) => (
                <div key={label} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.4rem 0' }}>
                  <span style={{ color: 'var(--text-dim)' }}>{label}</span>
                  <span style={{ fontWeight: 500 }}>{value}</span>
                </div>
              ))}
            </Card>
          </div>
        </div>
      </div>
    </>
  );
}
```

- [ ] **Step 2: Build + commit**

```bash
git add "src/app/projects/[code]/page.tsx"
git commit -m "feat(web): restyle project detail page"
```

---

### Task 9: Partnerships page

**Files:**
- Rewrite: `src/app/partnerships/page.tsx`

- [ ] **Step 1: Rewrite**

```tsx
import Link from 'next/link';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { projects } from '@/lib/data';
import { withOpacity } from '@/lib/utils';

const ALL_RESOURCE_CATEGORIES = Array.from(
  new Set(
    projects.flatMap((project) =>
      (project.resourceNeeds ?? [])
        .map((need) => need.category)
        .filter((category): category is string => Boolean(category)),
    ),
  ),
);

export default function PartnershipsPage() {
  return (
    <>
      <PageHeader
        title="Partnerships & Affiliates"
        subtitle="Overlay365 is actively seeking strategic partners and affiliate marketing teams across all 13 sub-businesses — from facilities and hardware to hydroponics, labs, and capital."
        accent="violet"
      >
        <StatBand>
          <KpiCard value="13" label="Sub-Businesses" accent="violet" />
          <KpiCard value={`${ALL_RESOURCE_CATEGORIES.length}`} label="Resource Categories" accent="cyan" />
          <KpiCard value={`${projects.reduce((s, p) => s + p.partnershipNeeds.length, 0)}`} label="Open Partnership Slots" accent="amber" />
          <KpiCard value={`${projects.reduce((s, p) => s + p.affiliateOpportunities.length, 0)}`} label="Affiliate Opportunities" accent="rose" />
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        <h2 className="section-heading">What We're Looking For</h2>
        <p className="section-sub">Each Overlay365 initiative is an independent sub-business with its own partnership and affiliate programme.</p>
        <div className="grid grid-4" style={{ marginBottom: '2.5rem' }}>
          {ALL_RESOURCE_CATEGORIES.map((cat) => (
            <Card key={cat} style={{ padding: '1.25rem', textAlign: 'center' }}>
              <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{categoryIcon(cat)}</div>
              <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{cat}</div>
            </Card>
          ))}
        </div>

        <h2 className="section-heading">Partnership Opportunities by Initiative</h2>
        <p className="section-sub">Click an initiative to view its full detail page.</p>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {projects.map((project) => (
            <Card key={project.id} style={{ overflow: 'hidden' }}>
              <div style={{ background: withOpacity(project.color, 10), padding: '1rem 1.5rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <span style={{ fontSize: '2rem' }}>{project.icon}</span>
                <div style={{ flex: 1 }}>
                  <h3 style={{ fontWeight: 700, fontSize: '1.1rem' }}>{project.name}</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{project.type}</p>
                </div>
                <Link href={`/projects/${project.code}`} className="btn btn-outline" style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}>View Initiative →</Link>
              </div>
              <div className="grid grid-2" style={{ padding: '1.5rem', gridTemplateColumns: '1fr 1fr' }}>
                <div>
                  <h4 style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: project.color, marginBottom: '0.75rem' }}>🤝 Strategic Partnerships</h4>
                  <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                    {project.partnershipNeeds.map((need, i) => (
                      <li key={i} style={{ fontSize: '0.875rem', color: 'var(--text-muted)', display: 'flex', gap: '0.5rem' }}><span style={{ color: 'var(--text-dim)', flexShrink: 0 }}>•</span>{need}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 style={{ fontSize: '0.8rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', color: project.color, marginBottom: '0.75rem' }}>📣 Affiliate Marketing</h4>
                  <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                    {project.affiliateOpportunities.map((opp, i) => (
                      <li key={i} style={{ fontSize: '0.875rem', color: 'var(--text-muted)', display: 'flex', gap: '0.5rem' }}><span style={{ color: 'var(--text-dim)', flexShrink: 0 }}>•</span>{opp}</li>
                    ))}
                  </ul>
                </div>
              </div>
              <div style={{ padding: '0.75rem 1.5rem', borderTop: '1px solid var(--border)', display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {project.resourceNeeds.map((rn) => (
                  <span key={rn.category} className="badge badge-dim" style={{ background: withOpacity(project.color, 10), color: project.color }}>{rn.category}</span>
                ))}
              </div>
            </Card>
          ))}
        </div>
      </div>
    </>
  );
}

function categoryIcon(cat: string): string {
  const icons: Record<string, string> = {
    Facilities: '🏭',
    Hardware: '🔧',
    'Software Dev': '💻',
    'Architecture and Design': '📐',
    Land: '🌿',
    Labor: '👷',
    Capital: '💰',
    Labs: '🔬',
    Hydroponics: '🌱',
  };
  return icons[cat] ?? '📦';
}
```

- [ ] **Step 2: Build + commit**

```bash
git add src/app/partnerships/page.tsx
git commit -m "feat(web): restyle partnerships page"
```

---

### Task 10: API docs page

**Files:**
- Rewrite: `src/app/api-docs/page.tsx`

- [ ] **Step 1: Rewrite (keep endpointDocs array exactly as-is; replace only the component markup)**

Replace the component (everything below the `endpointDocs` array) with:

```tsx
export default function ApiDocsPage() {
  return (
    <>
      <PageHeader title="API Documentation" subtitle="REST API for the ECOS ecosystem." accent="cyan">
        <div style={{ marginTop: '1rem' }}>
          <span className="code-block" style={{ display: 'inline-block', padding: '0.4rem 0.8rem' }}>
            Base URL: http://localhost:8000
          </span>
        </div>
      </PageHeader>

      <div className="page-container page-section">
        <Card style={{ padding: '1.5rem', marginBottom: '1.5rem' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem' }}>Getting Started</h2>
          <p style={{ marginBottom: '1rem', color: 'var(--text-muted)' }}>
            The ECOS API Gateway provides unified access to all 13 project APIs. Start the server with:
          </p>
          <pre className="code-block">{`cd apps/api-gateway
python main.py

# Server running at http://localhost:8000
# Interactive docs at http://localhost:8000/docs`}</pre>
        </Card>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
          {endpointDocs.map((endpoint, index) => (
            <Card key={index} style={{ padding: '1.5rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem', flexWrap: 'wrap' }}>
                <Badge tone={endpoint.method === 'GET' ? 'emerald' : 'blue'}>{endpoint.method}</Badge>
                <code className="mono-value" style={{ fontSize: '0.85rem' }}>{endpoint.path}</code>
              </div>
              <p style={{ marginBottom: '1rem', color: 'var(--text-muted)' }}>{endpoint.description}</p>

              {endpoint.request && (
                <div style={{ marginBottom: '1rem' }}>
                  <h4 style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Request Body</h4>
                  <pre className="code-block">{endpoint.request}</pre>
                </div>
              )}

              <div>
                <h4 style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Response</h4>
                <pre className="code-block">{endpoint.response}</pre>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </>
  );
}
```

And add these imports at the top of the file (replacing the `Header`/`Footer` imports):

```tsx
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
```

- [ ] **Step 2: Build + commit**

```bash
git add src/app/api-docs/page.tsx
git commit -m "feat(web): restyle API docs page"
```

---

### Task 11: Revenue hub page

**Files:**
- Rewrite: `src/app/revenue/page.tsx`

- [ ] **Step 1: Rewrite (keep the data-fetching logic; replace markup + imports)**

```tsx
'use client';
import { useEffect, useState } from 'react';
import Link from 'next/link';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { Skeleton } from '@/components/Skeleton';
import {
  challengesApi,
  membershipApi,
  marketplaceApi,
  gamificationApi,
  diyKitsApi,
} from '@/lib/api';

type StatCard = { label: string; value: string; accent: string; href: string; icon: string };

const ACCENTS: Record<string, string> = {
  'Challenge Prize Pool': 'emerald',
  'Membership MRR': 'violet',
  'Marketplace GMV': 'blue',
  'XP Awarded': 'amber',
  'Kit Revenue': 'teal',
};

export default function RevenueDashboard() {
  const [cards, setCards] = useState<StatCard[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.allSettled([
      challengesApi.stats(),
      membershipApi.revenue(),
      marketplaceApi.stats(),
      gamificationApi.stats(),
      diyKitsApi.stats(),
    ]).then((results) => {
      const get = (r: PromiseSettledResult<unknown>, key: string): string => {
        if (r.status === 'fulfilled') {
          const val = (r.value as Record<string, unknown>)[key];
          return String(val ?? '—');
        }
        return '—';
      };
      const raw = [
        { label: 'Challenge Prize Pool', value: `$${get(results[0], 'total_prize_pool')}`, href: '/challenges', icon: '🏆' },
        { label: 'Membership MRR', value: `$${get(results[1], 'monthly_recurring_revenue')}`, href: '/membership', icon: '👑' },
        { label: 'Marketplace GMV', value: `$${get(results[2], 'total_gmv_usd')}`, href: '/marketplace', icon: '🛒' },
        { label: 'XP Awarded', value: get(results[3], 'total_xp_awarded'), href: '/gamification', icon: '⭐' },
        { label: 'Kit Revenue', value: `$${get(results[4], 'total_revenue_usd')}`, href: '/diy-kits', icon: '🔧' },
      ];
      setCards(raw.map((c) => ({ ...c, accent: ACCENTS[c.label] ?? 'emerald' })));
    }).finally(() => setLoading(false));
  }, []);

  const modules = [
    { name: 'Public Challenges', desc: 'Bounties, submissions, leaderboards', href: '/challenges', icon: '🏆' },
    { name: 'Membership', desc: '4 tiers: Free / Pro / EcoChampion / PlanetGuardian', href: '/membership', icon: '👑' },
    { name: 'Marketplace', desc: 'Green goods, IP licenses, digital products', href: '/marketplace', icon: '🛒' },
    { name: 'Gamification', desc: 'XP, 9 levels, quests, badges, leaderboard', href: '/gamification', icon: '⭐' },
    { name: 'DIY Kits', desc: '5 hardware kits with full BOM & firmware', href: '/diy-kits', icon: '🔧' },
  ];

  return (
    <>
      <PageHeader title="Revenue Dashboard" subtitle="All 5 revenue streams live — real-time metrics across the entire platform." accent="emerald">
        <StatBand>
          {loading
            ? [1, 2, 3, 4, 5].map((i) => <Skeleton key={i} height={90} />)
            : cards.map((c) => (
                <KpiCard key={c.label} value={c.value} label={c.label} accent={c.accent as 'emerald' | 'cyan' | 'violet' | 'amber' | 'rose' | 'blue' | 'teal'} icon={c.icon} />
              ))}
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        <h2 className="section-heading">Revenue Modules</h2>
        <p className="section-sub">Each module is live and wired to the revenue API.</p>
        <div className="grid grid-3">
          {modules.map((m) => (
            <Link key={m.href} href={m.href}>
              <Card hoverable style={{ padding: '1.5rem', height: '100%' }}>
                <div style={{ fontSize: '1.6rem', marginBottom: '0.5rem' }}>{m.icon}</div>
                <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.3rem' }}>{m.name}</h3>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>{m.desc}</p>
                <div style={{ marginTop: '1rem', fontSize: '0.85rem', color: 'var(--text-dim)' }}>View module &rarr;</div>
              </Card>
            </Link>
          ))}
        </div>
      </div>
    </>
  );
}
```

> **Note on KpiCard:** the `icon` prop above is used by the revenue page, and `teal` is a valid accent here. Update `src/components/KpiCard.tsx` (Task 2 file) — it renders the icon above the value and accepts the full accent union:

```tsx
interface KpiCardProps {
  value: string;
  label: string;
  accent?: 'emerald' | 'cyan' | 'violet' | 'amber' | 'rose' | 'blue' | 'teal';
  icon?: string;
  trend?: { dir: 'up' | 'down' | 'flat'; text: string };
}

export function KpiCard({ value, label, accent = 'emerald', icon, trend }: KpiCardProps) {
  return (
    <div className="kpi-card" data-accent={accent}>
      {icon && <div style={{ fontSize: '1.4rem', marginBottom: '0.3rem' }}>{icon}</div>}
      <div className="kpi-value">{value}</div>
      <div className="kpi-label">{label}</div>
      {trend && (
        <div className={`kpi-trend ${trend.dir === 'up' ? 'up' : trend.dir === 'down' ? 'down' : 'flat'}`}>
          {trend.dir === 'up' ? '▲' : trend.dir === 'down' ? '▼' : '•'} {trend.text}
        </div>
      )}
    </div>
  );
}
```

And add the teal KPI glow rule to `globals.css` (append after the `blue` rule):

```css
.kpi-card[data-accent="teal"] { border-color: rgba(20,184,166,0.4); box-shadow: 0 0 14px rgba(20,184,166,0.14); }
```

Then change the revenue page's KpiCard render call to drop the cast (teal is now a valid accent):

```tsx
<StatBand>
  {loading
    ? [1, 2, 3, 4, 5].map((i) => <Skeleton key={i} height={90} />)
    : cards.map((c) => (
        <KpiCard key={c.label} value={c.value} label={c.label} accent={c.accent as 'emerald' | 'cyan' | 'violet' | 'amber' | 'rose' | 'blue' | 'teal'} icon={c.icon} />
      ))}
</StatBand>
```

- [ ] **Step 2: Build + commit**

```bash
git add src/app/revenue/page.tsx src/components/KpiCard.tsx src/app/globals.css
git commit -m "feat(web): restyle revenue hub with live KPI cards"
```

---

### Task 12: Challenges page

**Files:**
- Rewrite: `src/app/challenges/page.tsx`

- [ ] **Step 1: Rewrite**

```tsx
'use client';
import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Skeleton } from '@/components/Skeleton';
import { challengesApi, type Challenge } from '@/lib/api';

export default function ChallengesPage() {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [stats, setStats] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([challengesApi.list(), challengesApi.stats()])
      .then(([c, s]) => { setChallenges(c); setStats(s as Record<string, unknown>); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <PageHeader title="Public Challenges & Dev Bounties" subtitle="Compete, collaborate, and earn rewards while building a greener planet." accent="emerald">
        <StatBand>
          {loading
            ? [1, 2, 3].map((i) => <Skeleton key={i} height={90} />)
            : ['total_challenges', 'active_challenges', 'total_prize_pool'].map((k) => (
                <KpiCard key={k} value={String(stats[k] ?? '—')} label={k.replace(/_/g, ' ')} accent="emerald" />
              ))}
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        <h2 className="section-heading">Active Challenges</h2>
        {loading ? (
          <div className="grid grid-3"><Skeleton height={180} /><Skeleton height={180} /><Skeleton height={180} /></div>
        ) : (
          <div className="grid grid-3">
            {challenges.map((c) => {
              const ch = c as Record<string, unknown>;
              return (
                <Card key={String(ch.id)} hoverable accent="var(--emerald)" accentBar style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                    <Badge tone="emerald">{String(ch.category ?? 'General')}</Badge>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{String(ch.difficulty ?? 'Medium')}</span>
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem' }}>{String(ch.title ?? 'Challenge')}</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', lineHeight: 1.5, marginBottom: '1rem' }}>{String(ch.description ?? '')}</p>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ color: 'var(--emerald-hover)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>${String(ch.prize_usd ?? 0)} prize</div>
                    <button className="btn btn-primary" style={{ fontSize: '0.85rem', padding: '0.45rem 1.1rem' }}>Enter Challenge</button>
                  </div>
                  <div style={{ marginTop: '0.75rem', display: 'flex', gap: '0.5rem', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                    <span>{String(ch.participants ?? 0)} participants</span>
                    <span>•</span>
                    <span>Ends {String(ch.deadline ?? 'TBD')}</span>
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}
```

- [ ] **Step 2: Build + commit**

```bash
git add src/app/challenges/page.tsx
git commit -m "feat(web): restyle challenges page"
```

---

### Task 13: Membership page

**Files:**
- Rewrite: `src/app/membership/page.tsx`

- [ ] **Step 1: Rewrite**

```tsx
'use client';
import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/PageHeader';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Skeleton } from '@/components/Skeleton';
import { membershipApi, type MembershipTier } from '@/lib/api';

const TIER_ACCENTS: Record<string, string> = {
  Free: '#64748b',
  Pro: '#3b82f6',
  EcoChampion: '#10b981',
  PlanetGuardian: '#a78bfa',
};

export default function MembershipPage() {
  const [tiers, setTiers] = useState<MembershipTier[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    membershipApi.tiers()
      .then(setTiers)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <PageHeader title="Membership & Perks" subtitle="Unlock exclusive tools, analytics, and rewards. Invest in the planet, earn for it." accent="violet">
        {loading && <StatBandLoading />}
      </PageHeader>

      <div className="page-container page-section">
        <h2 className="section-heading" style={{ textAlign: 'center' }}>Choose Your Tier</h2>
        {loading ? (
          <div className="grid grid-4"><Skeleton height={280} /><Skeleton height={280} /><Skeleton height={280} /><Skeleton height={280} /></div>
        ) : (
          <div className="grid grid-4">
            {tiers.map((t) => {
              const tier = t as Record<string, unknown>;
              const name = String(tier.name ?? 'Tier');
              const perks = (tier.perks as string[]) ?? [];
              const popular = tier.popular as boolean;
              const accent = TIER_ACCENTS[name] ?? '#64748b';
              return (
                <Card key={name} style={{ padding: '1.5rem', position: 'relative', borderColor: popular ? accent : undefined, boxShadow: popular ? `0 0 24px ${accent}33` : undefined }}>
                  {popular && (
                    <div style={{ position: 'absolute', top: 0, left: 0, right: 0, textAlign: 'center', fontSize: '0.7rem', fontWeight: 700, background: accent, color: '#fff', padding: '0.3rem 0' }}>
                      MOST POPULAR
                    </div>
                  )}
                  <h3 style={{ fontSize: '1.3rem', fontWeight: 700, marginTop: popular ? '1rem' : 0 }}>{name}</h3>
                  <div style={{ fontSize: '1.7rem', fontWeight: 700, color: accent, fontFamily: 'var(--font-mono)', margin: '0.3rem 0 0.2rem' }}>
                    {tier.price_monthly === 0 ? 'Free' : `$${String(tier.price_monthly)}/mo`}
                  </div>
                  {tier.price_annual ? (
                    <div style={{ fontSize: '0.85rem', color: 'var(--text-dim)', marginBottom: '1rem' }}>${String(tier.price_annual)}/yr</div>
                  ) : <div style={{ marginBottom: '1rem' }} />}
                  <ul style={{ listStyle: 'none', marginBottom: '1.5rem' }}>
                    {perks.map((p: string) => (
                      <li key={p} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.4rem' }}>
                        <span style={{ color: 'var(--success)', marginTop: '0.1rem' }}>&#10003;</span>{p}
                      </li>
                    ))}
                  </ul>
                  <button className="btn btn-primary" style={{ width: '100%', background: accent, borderColor: accent, color: '#fff' }}>
                    {tier.price_monthly === 0 ? 'Get Started' : 'Subscribe'}
                  </button>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}

function StatBandLoading() {
  return <div className="stat-band"><Skeleton height={90} /><Skeleton height={90} /><Skeleton height={90} /><Skeleton height={90} /></div>;
}
```

- [ ] **Step 2: Build + commit**

```bash
git add src/app/membership/page.tsx
git commit -m "feat(web): restyle membership page"
```

---

### Task 14: Marketplace page

**Files:**
- Rewrite: `src/app/marketplace/page.tsx`

- [ ] **Step 1: Rewrite**

```tsx
'use client';
import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Skeleton } from '@/components/Skeleton';
import { marketplaceApi, type Listing } from '@/lib/api';

export default function MarketplacePage() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [stats, setStats] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all');

  useEffect(() => {
    Promise.all([marketplaceApi.listings(), marketplaceApi.stats()])
      .then(([l, s]) => { setListings(l); setStats(s as Record<string, unknown>); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const categories = ['all', ...new Set(listings.map((l) => String((l as Record<string, unknown>).category ?? 'other')))];
  const filtered = filter === 'all' ? listings : listings.filter((l) => String((l as Record<string, unknown>).category) === filter);

  return (
    <>
      <PageHeader title="Eco Marketplace" subtitle="Buy, sell, and trade green goods, IP licenses, and digital products." accent="blue">
        <StatBand>
          {loading
            ? [1, 2, 3].map((i) => <Skeleton key={i} height={90} />)
            : ['total_listings', 'total_gmv_usd', 'active_sellers'].map((k) => (
                <KpiCard key={k} value={String(stats[k] ?? '—')} label={k.replace(/_/g, ' ')} accent="blue" />
              ))}
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        <div style={{ display: 'flex', gap: '0.6rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
          {categories.map((c) => (
            <button key={c} onClick={() => setFilter(c)} className={`pill ${filter === c ? 'blue-active' : ''}`}>
              {c.charAt(0).toUpperCase() + c.slice(1)}
            </button>
          ))}
        </div>
        {loading ? (
          <div className="grid grid-3"><Skeleton height={180} /><Skeleton height={180} /><Skeleton height={180} /></div>
        ) : (
          <div className="grid grid-3">
            {filtered.map((l) => {
              const item = l as Record<string, unknown>;
              return (
                <Card key={String(item.id)} hoverable accent="var(--blue)" accentBar style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                    <Badge tone="blue">{String(item.category ?? 'general')}</Badge>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{String(item.listing_type ?? 'sale')}</span>
                  </div>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem' }}>{String(item.title ?? 'Product')}</h3>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', lineHeight: 1.5, marginBottom: '1rem' }}>{String(item.description ?? '')}</p>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ color: '#60a5fa', fontWeight: 700, fontFamily: 'var(--font-mono)', fontSize: '1.1rem' }}>${String(item.price_usd ?? 0)}</div>
                    <button className="btn btn-primary" style={{ fontSize: '0.85rem', padding: '0.45rem 1.1rem', background: 'var(--blue)', borderColor: 'var(--blue)', color: '#eff6ff' }}>Buy Now</button>
                  </div>
                  <div style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
                    Seller: {String(item.seller_id ?? 'Unknown')} &bull; {String(item.units_sold ?? 0)} sold
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}
```

- [ ] **Step 2: Build + commit**

```bash
git add src/app/marketplace/page.tsx
git commit -m "feat(web): restyle marketplace page"
```

---

### Task 15: Gamification page

**Files:**
- Rewrite: `src/app/gamification/page.tsx`

- [ ] **Step 1: Rewrite**

```tsx
'use client';
import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Skeleton } from '@/components/Skeleton';
import { gamificationApi } from '@/lib/api';

const LEVEL_TONES = ['emerald', 'cyan', 'violet', 'amber', 'rose', 'blue', 'teal', 'amber', 'rose'] as const;

export default function GamificationPage() {
  const [leaderboard, setLeaderboard] = useState<Record<string, unknown>[]>([]);
  const [levels, setLevels] = useState<Record<string, unknown>[]>([]);
  const [stats, setStats] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      gamificationApi.leaderboard(),
      gamificationApi.levels(),
      gamificationApi.stats(),
    ])
      .then(([lb, lv, s]) => {
        setLeaderboard(lb as Record<string, unknown>[]);
        setLevels(lv as Record<string, unknown>[]);
        setStats(s as Record<string, unknown>);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const rankColor = (i: number) => (i === 0 ? 'var(--amber)' : i === 1 ? 'var(--text-muted)' : i === 2 ? '#fb923c' : 'var(--text-dim)');

  return (
    <>
      <PageHeader title="Gamification & XP System" subtitle="Earn XP, level up, complete quests, collect badges. Make saving the planet fun." accent="amber">
        <StatBand>
          {loading
            ? [1, 2, 3].map((i) => <Skeleton key={i} height={90} />)
            : ['total_users', 'total_xp_awarded', 'total_quests'].map((k) => (
                <KpiCard key={k} value={String(stats[k] ?? '—')} label={k.replace(/_/g, ' ')} accent="amber" />
              ))}
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        <div className="grid grid-2" style={{ alignItems: 'start' }}>
          <section>
            <h2 className="section-heading">Global Leaderboard</h2>
            {loading ? (
              <Skeleton height={300} />
            ) : (
              <Card style={{ overflow: 'hidden' }}>
                {leaderboard.slice(0, 10).map((entry, i) => (
                  <div key={String(entry.user_id ?? i)} style={{ display: 'flex', alignItems: 'center', gap: '1rem', padding: '0.9rem 1.2rem', borderBottom: i < 9 ? '1px solid var(--border)' : 'none', background: i < 3 ? 'rgba(251,191,36,0.07)' : undefined }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, width: '1.6rem', textAlign: 'center', color: rankColor(i) }}>{i + 1}</span>
                    <div style={{ flex: 1 }}>
                      <div style={{ fontWeight: 600 }}>{String(entry.user_id ?? 'User')}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Level {String(entry.level ?? 1)} &bull; {String(entry.title ?? 'Eco Starter')}</div>
                    </div>
                    <div style={{ color: 'var(--amber)', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{String(entry.total_xp ?? 0)} XP</div>
                  </div>
                ))}
              </Card>
            )}
          </section>

          <section>
            <h2 className="section-heading">XP Levels</h2>
            {loading ? (
              <Skeleton height={300} />
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {levels.map((lv) => {
                  const lvl = lv as Record<string, unknown>;
                  const idx = (Number(lvl.level ?? 1) - 1) % LEVEL_TONES.length;
                  const tone = LEVEL_TONES[idx];
                  return (
                    <Card key={String(lvl.level)} style={{ padding: '1rem 1.25rem', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                      <Badge tone={tone} style={{ fontSize: '0.9rem' }}>{String(lvl.level)}</Badge>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 600 }}>{String(lvl.title ?? 'Level')}</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{String(lvl.xp_required ?? 0)} XP required</div>
                      </div>
                    </Card>
                  );
                })}
              </div>
            )}
          </section>
        </div>
      </div>
    </>
  );
}
```

> **Note on Badge:** the `style` prop is used here. Update `src/components/Badge.tsx` (Task 2 file) to accept `style`:

```tsx
import { ReactNode } from 'react';

type Tone = 'emerald' | 'cyan' | 'violet' | 'amber' | 'rose' | 'blue' | 'teal' | 'dim';

export function Badge({ tone = 'dim', children, style }: { tone?: Tone; children: ReactNode; style?: React.CSSProperties }) {
  return <span className={`badge badge-${tone}`} style={style}>{children}</span>;
}
```

- [ ] **Step 2: Build + commit**

```bash
git add src/app/gamification/page.tsx src/components/Badge.tsx
git commit -m "feat(web): restyle gamification page"
```

---

### Task 16: DIY Kits page

**Files:**
- Rewrite: `src/app/diy-kits/page.tsx`

- [ ] **Step 1: Rewrite**

```tsx
'use client';
import { useEffect, useState } from 'react';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { Badge } from '@/components/Badge';
import { Skeleton } from '@/components/Skeleton';
import { diyKitsApi, type DiyKit } from '@/lib/api';

export default function DiyKitsPage() {
  const [kits, setKits] = useState<DiyKit[]>([]);
  const [stats, setStats] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    Promise.all([diyKitsApi.list(), diyKitsApi.stats()])
      .then(([k, s]) => { setKits(k); setStats(s as Record<string, unknown>); })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <>
      <PageHeader title="DIY Hardware Kits" subtitle="Build real environmental monitoring & energy hardware. Full BOM, firmware, community builds." accent="teal">
        <StatBand>
          {loading
            ? [1, 2, 3].map((i) => <Skeleton key={i} height={90} />)
            : ['total_kits', 'total_revenue_usd', 'community_builds'].map((k) => (
                <KpiCard key={k} value={String(stats[k] ?? '—')} label={k.replace(/_/g, ' ')} accent="teal" />
              ))}
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        {loading ? (
          <div className="grid grid-3"><Skeleton height={200} /><Skeleton height={200} /><Skeleton height={200} /></div>
        ) : (
          <div className="grid grid-3">
            {kits.map((kit) => {
              const k = kit as Record<string, unknown>;
              const bom = (k.bom as Array<Record<string, unknown>>) ?? [];
              const isOpen = selected?.id === k.id;
              return (
                <Card key={String(k.id)} hoverable accent="var(--teal)" accentBar style={{ padding: '1.5rem', cursor: 'pointer' }} className="" >
                  <div onClick={() => setSelected(isOpen ? null : k)}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                      <Badge tone="teal">{String(k.category ?? 'Hardware')}</Badge>
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{String(k.difficulty ?? 'Intermediate')}</span>
                    </div>
                    <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.5rem' }}>{String(k.title ?? 'Kit')}</h3>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', lineHeight: 1.5, marginBottom: '1rem' }}>{String(k.description ?? '')}</p>
                  </div>

                  {isOpen && (
                    <div style={{ marginBottom: '1rem', background: 'var(--panel-raised)', border: '1px solid var(--border)', borderRadius: 'var(--radius-sm)', padding: '1rem' }}>
                      <div style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--teal)', marginBottom: '0.5rem' }}>Bill of Materials</div>
                      <ul style={{ listStyle: 'none' }}>
                        {bom.map((part, i) => (
                          <li key={i} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-muted)', padding: '0.2rem 0' }}>
                            <span>{String(part.component ?? '')}</span>
                            <span style={{ color: 'var(--text-dim)' }}>${String(part.unit_cost_usd ?? 0)} x{String(part.qty ?? 1)}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                      <div style={{ color: 'var(--teal)', fontWeight: 700, fontFamily: 'var(--font-mono)', fontSize: '1.1rem' }}>${String(k.price_usd ?? 0)}</div>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>{String(k.units_sold ?? 0)} sold &bull; {String(k.community_builds ?? 0)} community builds</div>
                    </div>
                    <button className="btn btn-primary" style={{ fontSize: '0.85rem', padding: '0.45rem 1.1rem', background: 'var(--teal)', borderColor: 'var(--teal)', color: '#042f2e' }}>Order Kit</button>
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </>
  );
}
```

> **Note on teal accent:** `teal` was already added to `KpiCard`'s accent union and the teal KPI glow rule in Task 11 — no component change needed here. This page's `accent="teal"` and `accentBar` values type-check as-is.

- [ ] **Step 2: Build + commit**

```bash
git add src/app/diy-kits/page.tsx
git commit -m "feat(web): restyle DIY kits page"
```

---

### Task 17: Final cleanup — remove Header/Footer, verify no Tailwind remnants

**Files:**
- Delete: `src/components/Header.tsx`
- Delete: `src/components/Footer.tsx`
- Verify: all `src/app/**/*.tsx`

- [ ] **Step 1: Confirm no remaining references**

Search `src` for `Header`/`Footer` imports:

Run: `grep -rn "components/Header\|components/Footer" src`
Expected: no matches.

- [ ] **Step 2: Delete Header.tsx and Footer.tsx**

```bash
git rm src/components/Header.tsx src/components/Footer.tsx
```

- [ ] **Step 3: Verify no Tailwind classes remain**

Run: `grep -rn "bg-gray-950\|bg-gradient-to-br\|bg-gradient-to-r\|text-5xl\|rounded-2xl\|min-h-screen\|animate-spin\|max-w-6xl\|grid-cols-\|space-y-\|ring-2\|line-clamp" src`
Expected: no matches in `src/` (globals.css may legitimately contain none of these).

- [ ] **Step 4: Full build**

Run: `npm run build`
Expected: SUCCESS with zero errors.

- [ ] **Step 5: Full lint**

Run: `npm run lint`
Expected: no new errors (compare against the baseline note from Task 0; fix any introduced issues).

- [ ] **Step 6: Production smoke (optional but recommended)**

Run: `npm start` in a terminal, then `curl -s http://localhost:3000 | head -c 300` to confirm the server boots and the homepage HTML contains the page title text.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "feat(web): complete Control Room redesign — remove legacy header/footer"
```

---

## Self-Review Notes (for the planning agent — resolved during writing)

- **Spec coverage:** Tasks 1 (design system), 2–3 (components/layout), 4–16 (all 12 routes), 17 (verification + cleanup) map 1:1 to spec sections 3–7.
- **Placeholders:** every page rewrite contains full replacement code; no "similar to Task N".
- **Type consistency:** `KpiCard` gains `icon` (Task 11) and `teal` accent (Task 16); `Badge` gains `style` (Task 15); `PageHeader` accents include teal already; `Card` supports `accentBar`/`accent`/`style`; `Skeleton` used in all loading states. All prop additions are called out inline in the tasks that need them.
- **Verification strategy:** the web app has no unit-test framework, so per-task verification is `npm run build` + `npm run lint`; Task 0 establishes the baseline; Task 17 is the gate that must produce a clean build.

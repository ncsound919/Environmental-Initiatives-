# Overlay365 Control Room — Frontend Redesign

Date: 2026-08-14
Status: Approved (design direction, navigation, homepage, dashboard style, scope)

## 1. Objective

Rebuild every page of the ECOS web frontend (`apps/web`) into a unified,
professional **"Overlay365 Control Room"** — a dark, climate-tech ops-center
theme — using **only the dependencies already present** (Next.js, React,
Recharts, plain CSS). No new packages.

Currently the app is split: legacy pages use a light CSS theme
(`globals.css`), while the newer revenue pages (Revenue, Challenges,
Membership, Marketplace, Gamification, DIY Kits) reference Tailwind classes
that render unstyled because Tailwind is not installed. This rebuild replaces
both with one consistent dark design system.

## 2. Design Decisions (approved via brainstorming)

| Decision | Choice |
|---|---|
| Overall theme | Dark "Control Room" (A) |
| Navigation | Sidebar, grouped Platform / Revenue (B) |
| Homepage layout | Hero + stat band + project grid (A) |
| Dashboard / data-viz | Glowing KPI cards + gradient charts (A) |
| Scope | All pages (12 routes) |

## 3. Design System

### 3.1 Color tokens (CSS variables)

- Background base: `#0b1220`
- Panel / card: `#0f172a`
- Raised panel: `#111c2e`
- Border: `#1f2937`
- Text primary: `#e2e8f0`
- Text muted: `#94a3b8` / `#64748b`
- Primary accent (emerald): `#10b981`, hover `#34d399`
- Secondary (cyan): `#22d3ee`
- Module accents: violet `#a78bfa`, amber `#fbbf24`, rose `#fb7185`, blue `#3b82f6`
- Success: `#34d399`; Warning: `#fbbf24`; Danger: `#fb7185`

Per-module accent mapping (used for hero gradients, badge colors, card
borders, and glow):

- Home / Ecosystem: emerald `#10b981`
- Dashboard: cyan `#22d3ee`
- Initiatives: emerald
- Partnerships: violet
- API docs: cyan
- Revenue hub: emerald
- Challenges: green `#10b981`
- Membership: purple `#a78bfa`
- Marketplace: blue `#3b82f6`
- Gamification: amber `#fbbf24`
- DIY Kits: emerald/teal `#14b8a6`

### 3.2 Typography

- Body: system sans stack (`-apple-system, BlinkMacSystemFont, 'Segoe UI',
  Roboto, sans-serif`)
- Data readouts, KPI numbers, codes, tables of technical data:
  `ui-monospace, SFMono-Regular, Menlo, Consolas, monospace`
- Page titles: large (approx 1.75–2rem), bold
- Module hero titles: large bold with gradient underline/accent

### 3.3 Core components (shared)

- **Sidebar** (`components/Sidebar.tsx`) — fixed left column; logo;
  PLATFORM group (Home, Initiatives, Dashboard, Partnerships, API); REVENUE
  group (Revenue, Challenges, Membership, Marketplace, Gamification, DIY
  Kits); footer status line. Collapsible drawer on mobile (hamburger).
- **Layout wrapper** (`app/layout.tsx`) — renders Sidebar + main content
  region; page content in `<main>`.
- **PageHeader** — optional hero/banner per page: module-colored gradient,
  title, subtitle, optional stat band.
- **KpiCard** — dark panel with colored border/glow, monospace value, label,
  optional trend indicator (▲/▼ colored).
- **StatBand** — row of KPI stats used in heroes.
- **Card** — dark panel, subtle border, hover lift + colored border accent.
- **Badge / Pill** — small rounded label, tinted per status/accent.
- **Skeleton** — loading placeholder used while API data loads.
- **DataTable** — dark table with header row, row hover, status pills,
  readiness bars.
- **ProgressBar** — thin gradient bar for readiness/level values.
- **Tab pills** — used for revenue-module sub-navigation and marketplace
  category filters.

### 3.4 Global CSS

- Rewrite `app/globals.css` entirely: CSS variables (above), base element
  styles, reusable utility classes for the components above, sidebar layout,
  responsive breakpoints (sidebar → drawer under ~900px), Recharts dark-theme
  overrides (gridlines, tooltip, axis text).
- Remove legacy light-theme classes; no Tailwind references remain.

## 4. Page-by-Page Treatment

1. **Home** (`/`): gradient hero (title, subtitle, CTAs "Explore
   Initiatives" + "Open Dashboard"); stat band (13 Initiatives, $183M Y3 ARR
   Target, 70% Readiness, 5 Revenue Streams); 13 project cards grouped by the
   4 phases; CTA section.
2. **Dashboard** (`/dashboard`): 4 glowing KPI cards (Power, Water, Carbon,
   Devices); 3 Recharts panels — solar line with area gradient, hydro bar,
   AWG water line; dispatcher status panel; project status data table with
   readiness bars + Active/Reserved pills.
3. **Initiatives** (`/projects`): page header + stat band, phase-grouped
   project cards (full list).
4. **Project detail** (`/projects/[code]`): gradient hero tinted with the
   project's color; 2-column layout — main: description, business model,
   RegenCity role, partnership needs, affiliate opportunities, features;
   sidebar: tech stack, API endpoints (code-styled), resource needs, project
   info.
5. **Partnerships** (`/partnerships`): hero + stat band; "What We're
   Looking For" resource category grid; per-initiative partnership cards
   (two-column strategic partnerships / affiliate marketing); CTA.
6. **API docs** (`/api-docs`): dark endpoint listing, code-block styling.
7. **Revenue hub** (`/revenue`): gradient hero; 5 KPI cards linking to
   modules; revenue module grid.
8. **Challenges** (`/challenges`): green hero + stats; challenge cards
   (category badge, title, prize, participants, deadline, "Enter" button).
9. **Membership** (`/membership`): purple hero; 4 tier pricing cards
   (Free/Pro/EcoChampion/PlanetGuardian) with popular highlight + subscribe
   buttons.
10. **Marketplace** (`/marketplace`): blue hero + stats; category tab pills
    + listing cards (category, title, price, seller, "Buy Now").
11. **Gamification** (`/gamification`): amber hero + stats; global
    leaderboard (top-3 highlighted) + XP levels list.
12. **DIY Kits** (`/diy-kits`): teal hero + stats; kit cards with
    expandable BOM + "Order Kit" button.

## 5. Data & API

- Static data stays in `lib/data.ts` (projects, phases) and `lib/utils.ts`
  (withOpacity).
- Revenue pages keep their existing `lib/api.ts` wiring (already fixed to
  match the web contract). Only their styling changes.
- Recharts remains the chart library (dashboard). Add dark-theme defaults in
  globals.css where possible; configure chart props inline where needed.

## 6. Error & Loading States

- All data-fetching pages (dashboard, revenue, challenges, membership,
  marketplace, gamification, DIY kits) show skeleton placeholders while
  loading.
- `Promise.allSettled` / `.catch(console.error)` patterns already in the
  pages are preserved; failed modules render "—" placeholders (existing
  behavior).
- 404 project page keeps its not-found state, restyled.

## 7. Testing & Verification

- `npm run build` (Next.js) succeeds with no type errors.
- `npm run lint` passes.
- Manual check of each route renders the dark theme with no unstyled
  Tailwind classes remaining (grep for `bg-gray-950`, `bg-gradient`, etc. in
  `src/` should return nothing).
- Python API tests remain green (14 pass) — frontend change only.

## 8. Out of Scope

- No new dependencies (no Tailwind, no UI kit, no CSS-in-JS).
- No backend/API changes.
- No new pages beyond the existing 12 routes.
- No functional behavior changes to revenue flows (only presentation).

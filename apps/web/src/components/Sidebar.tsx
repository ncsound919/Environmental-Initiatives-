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

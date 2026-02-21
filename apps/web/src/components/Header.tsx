'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export function Header() {
  const pathname = usePathname();

  return (
    <header className="header">
      <div className="container header-content">
        <Link href="/" className="logo">
          <span>🌐</span>
          <span>Overlay365</span>
        </Link>
        <nav className="nav">
          <Link 
            href="/" 
            className={`nav-link ${pathname === '/' ? 'active' : ''}`}
          >
            Home
          </Link>
          <Link 
            href="/projects" 
            className={`nav-link ${pathname?.startsWith('/projects') ? 'active' : ''}`}
          >
            Projects
          </Link>
          <Link 
            href="/dashboard" 
            className={`nav-link ${pathname === '/dashboard' ? 'active' : ''}`}
          >
            Dashboard
          </Link>
          <Link 
            href="/api-docs" 
            className={`nav-link ${pathname === '/api-docs' ? 'active' : ''}`}
          >
            API
          </Link>
          <Link 
            href="/partnerships" 
            className={`nav-link ${pathname === '/partnerships' ? 'active' : ''}`}
          >
            Partnerships
          </Link>
        </nav>
      </div>
    </header>
  );
}

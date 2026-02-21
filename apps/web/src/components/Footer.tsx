import Link from 'next/link';

export function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-links">
          <a href="https://github.com/ncsound919/Environmental-Initiatives-" className="footer-link" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
          <Link href="/partnerships" className="footer-link">
            Partnerships
          </Link>
          <Link href="/api-docs" className="footer-link">
            API Documentation
          </Link>
          <Link href="/dashboard" className="footer-link">
            Dashboard
          </Link>
        </div>
        <p>&copy; {new Date().getFullYear()} Overlay365 — Environmental Initiatives Ecosystem. Building a sustainable future.</p>
      </div>
    </footer>
  );
}

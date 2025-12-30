export function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-links">
          <a href="https://github.com/ncsound919/Environmental-Initiatives-" className="footer-link" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>
          <a href="/api-docs" className="footer-link">
            API Documentation
          </a>
          <a href="/dashboard" className="footer-link">
            Dashboard
          </a>
        </div>
        <p>&copy; {new Date().getFullYear()} ECOS - RegenCity Ecosystem. Built for a sustainable future.</p>
      </div>
    </footer>
  );
}

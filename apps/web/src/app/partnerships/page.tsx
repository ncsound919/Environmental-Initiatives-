import Link from 'next/link';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { projects } from '@/lib/data';
import { withOpacity } from '@/lib/utils';

// All unique resource categories across initiatives
const ALL_RESOURCE_CATEGORIES = [
  'Facilities',
  'Hardware',
  'Software Dev',
  'Architecture and Design',
  'Land',
  'Labor',
  'Capital',
  'Labs',
  'Hydroponics',
];

export default function PartnershipsPage() {
  return (
    <>
      <Header />
      <main>
        {/* Hero */}
        <section className="hero">
          <div className="container">
            <h1 className="hero-title">Partnerships &amp; Affiliates</h1>
            <p className="hero-subtitle">
              Overlay365 is actively seeking strategic partners and affiliate marketing teams across all 13
              sub-businesses — from facilities and hardware to hydroponics, labs, and capital.
            </p>
            <div className="hero-stats">
              <div className="stat-item">
                <div className="stat-value">13</div>
                <div className="stat-label">Sub-Businesses</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">{ALL_RESOURCE_CATEGORIES.length}</div>
                <div className="stat-label">Resource Categories</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">
                  {projects.reduce((sum, p) => sum + p.partnershipNeeds.length, 0)}
                </div>
                <div className="stat-label">Open Partnership Slots</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">
                  {projects.reduce((sum, p) => sum + p.affiliateOpportunities.length, 0)}
                </div>
                <div className="stat-label">Affiliate Opportunities</div>
              </div>
            </div>
          </div>
        </section>

        {/* What We're Looking For */}
        <section className="section" style={{ background: '#f0fdf4' }}>
          <div className="container">
            <h2 className="section-title">What We&apos;re Looking For</h2>
            <p className="section-subtitle">
              Each Overlay365 initiative is an independent sub-business with its own partnership and affiliate programme.
            </p>
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
                gap: '1rem',
                marginTop: '1.5rem',
              }}
            >
              {ALL_RESOURCE_CATEGORIES.map((cat) => (
                <div
                  key={cat}
                  style={{
                    background: '#ffffff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.75rem',
                    padding: '1.25rem',
                    textAlign: 'center',
                  }}
                >
                  <div style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>
                    {categoryIcon(cat)}
                  </div>
                  <div style={{ fontWeight: '600', fontSize: '0.9rem' }}>{cat}</div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Per-Initiative Partnership Sections */}
        <section className="section">
          <div className="container">
            <h2 className="section-title">Partnership Opportunities by Initiative</h2>
            <p className="section-subtitle">
              Click an initiative to view its full detail page.
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', marginTop: '1.5rem' }}>
              {projects.map((project) => (
                <div
                  key={project.id}
                  style={{
                    background: '#ffffff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '0.75rem',
                    overflow: 'hidden',
                  }}
                >
                  {/* Card header */}
                  <div
                    style={{
                      background: withOpacity(project.color, 10),
                      padding: '1rem 1.5rem',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '1rem',
                    }}
                  >
                    <span style={{ fontSize: '2rem' }}>{project.icon}</span>
                    <div style={{ flex: 1 }}>
                      <h3 style={{ fontWeight: 'bold', fontSize: '1.1rem' }}>{project.name}</h3>
                      <p style={{ color: '#6b7280', fontSize: '0.85rem' }}>{project.type}</p>
                    </div>
                    <Link
                      href={`/projects/${project.code}`}
                      className="btn btn-primary"
                      style={{ fontSize: '0.85rem', padding: '0.5rem 1rem' }}
                    >
                      View Initiative →
                    </Link>
                  </div>

                  {/* Two-column body */}
                  <div
                    className="dashboard"
                    style={{
                      padding: '1.5rem',
                    }}
                  >
                    {/* Strategic Partnerships */}
                    <div>
                      <h4
                        style={{
                          fontSize: '0.85rem',
                          fontWeight: '700',
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                          color: project.color,
                          marginBottom: '0.75rem',
                        }}
                      >
                        🤝 Strategic Partnerships
                      </h4>
                      <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                        {project.partnershipNeeds.map((need, i) => (
                          <li key={i} style={{ fontSize: '0.875rem', color: '#374151', display: 'flex', gap: '0.5rem' }}>
                            <span style={{ color: '#9ca3af', flexShrink: 0 }}>•</span>
                            {need}
                          </li>
                        ))}
                      </ul>
                    </div>

                    {/* Affiliate Opportunities */}
                    <div>
                      <h4
                        style={{
                          fontSize: '0.85rem',
                          fontWeight: '700',
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                          color: project.color,
                          marginBottom: '0.75rem',
                        }}
                      >
                        📣 Affiliate Marketing
                      </h4>
                      <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.4rem' }}>
                        {project.affiliateOpportunities.map((opp, i) => (
                          <li key={i} style={{ fontSize: '0.875rem', color: '#374151', display: 'flex', gap: '0.5rem' }}>
                            <span style={{ color: '#9ca3af', flexShrink: 0 }}>•</span>
                            {opp}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>

                  {/* Resource tags */}
                  <div
                    style={{
                      padding: '0.75rem 1.5rem',
                      borderTop: '1px solid #e5e7eb',
                      display: 'flex',
                      flexWrap: 'wrap',
                      gap: '0.5rem',
                    }}
                  >
                    {project.resourceNeeds.map((rn) => (
                      <span
                        key={rn.category}
                        style={{
                          background: withOpacity(project.color, 10),
                          color: project.color,
                          padding: '0.25rem 0.75rem',
                          borderRadius: '9999px',
                          fontSize: '0.75rem',
                          fontWeight: '600',
                        }}
                      >
                        {rn.category}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="section" style={{ background: '#10b98110', padding: '4rem 0' }}>
          <div className="container" style={{ textAlign: 'center' }}>
            <h2 className="section-title">Ready to Partner with Overlay365?</h2>
            <p className="section-subtitle" style={{ marginBottom: '2rem' }}>
              Browse individual initiatives to see detailed resource requirements, or explore the full dashboard.
            </p>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              <Link href="/projects" className="btn btn-primary">
                Browse All Initiatives
              </Link>
              <Link href="/dashboard" className="btn btn-secondary">
                Open Dashboard
              </Link>
            </div>
          </div>
        </section>
      </main>
      <Footer />
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

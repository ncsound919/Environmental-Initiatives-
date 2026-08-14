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
        <h2 className="section-heading">What We&apos;re Looking For</h2>
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

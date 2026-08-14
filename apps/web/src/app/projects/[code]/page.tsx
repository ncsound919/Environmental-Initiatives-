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

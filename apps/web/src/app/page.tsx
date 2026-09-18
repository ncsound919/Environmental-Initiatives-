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
          <KpiCard value="13" label="Defined Asks" accent="cyan" />
          <KpiCard value="4" label="Funding Tracks" accent="violet" />
          <KpiCard value="70%" label="Build Checklist (self-assessed)" accent="amber" />
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        <h2 className="section-heading">The Overlay365 Ecosystem</h2>
        <p className="section-sub">
          Explore our 13 sub-businesses organized by deployment phase. Each seeks strategic partners and affiliate marketing teams.
        </p>

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

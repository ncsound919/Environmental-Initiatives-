'use client';

import Link from 'next/link';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { Card } from '@/components/Card';
import { ProjectCard } from '@/components/ProjectCard';
import { PortfolioReadiness } from '@/components/viz/PortfolioReadiness';
import { projects, phases } from '@/lib/data';
import { initiativeSpecs } from '@/lib/initiatives';

export default function ProjectsPage() {
  const specs = Object.values(initiativeSpecs);
  const verifiedTiers = specs.reduce(
    (n, s) => n + (s.hardware.individual.status === 'verified' ? 1 : 0) + (s.hardware.enterprise.status === 'verified' ? 1 : 0),
    0,
  );
  const specReady = specs.filter(
    (s) => s.hardware.individual.status === 'verified' && s.hardware.enterprise.status === 'verified',
  ).length;

  return (
    <>
      <PageHeader title="All Initiatives" subtitle="Explore all 13 Overlay365 sub-businesses. Click any card to view partnership and resource details." accent="emerald">
        <StatBand>
          <KpiCard value="13" label="Initiatives" accent="emerald" />
          <KpiCard value={`${specReady}/13`} label="Spec-ready (both tiers)" accent="cyan" />
          <KpiCard value={`${verifiedTiers}`} label="Verified Hardware Tiers" accent="violet" />
          <KpiCard value="0/13" label="Founding-ready (pilot·LOI·econ)" accent="amber" />
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
        <Card style={{ padding: '1.5rem', marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.25rem' }}>Portfolio Spec Readiness</h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '0.75rem' }}>
            Community and enterprise hardware tiers per initiative, from the Initiative Development Specs.
          </p>
          <PortfolioReadiness />
        </Card>

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

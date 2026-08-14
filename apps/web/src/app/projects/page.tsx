'use client';

import Link from 'next/link';
import { PageHeader } from '@/components/PageHeader';
import { StatBand } from '@/components/StatBand';
import { KpiCard } from '@/components/KpiCard';
import { ProjectCard } from '@/components/ProjectCard';
import { projects, phases } from '@/lib/data';

export default function ProjectsPage() {
  return (
    <>
      <PageHeader title="All Initiatives" subtitle="Explore all 13 Overlay365 sub-businesses. Click any card to view partnership and resource details." accent="emerald">
        <StatBand>
          <KpiCard value="13" label="Initiatives" accent="emerald" />
          <KpiCard value={`${phases.length}`} label="Phases" accent="cyan" />
          <KpiCard value="70%" label="Avg Readiness" accent="violet" />
          <KpiCard value="12" label="Active" accent="amber" />
        </StatBand>
      </PageHeader>

      <div className="page-container page-section">
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

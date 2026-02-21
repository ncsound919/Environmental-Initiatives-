'use client';

import Link from 'next/link';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { ProjectCard } from '@/components/ProjectCard';
import { projects, phases } from '@/lib/data';

export default function ProjectsPage() {
  return (
    <>
      <Header />
      <main className="section">
        <div className="container">
          <h1 className="section-title">All Initiatives</h1>
          <p className="section-subtitle">
            Explore all 13 Overlay365 sub-businesses. Click any card to view partnership and resource details.
          </p>

          {phases.map((phase) => (
            <div key={phase.id} className="phase-section">
              <div className="phase-header">
                <div className="phase-number">{phase.id}</div>
                <div>
                  <h3 className="phase-title">{phase.name}</h3>
                  <p className="phase-subtitle">{phase.description}</p>
                </div>
              </div>
              <div className="projects-grid">
                {projects
                  .filter(p => p.phase === phase.id)
                  .map(project => (
                    <Link key={project.id} href={`/projects/${project.code}`}>
                      <ProjectCard project={project} />
                    </Link>
                  ))}
              </div>
            </div>
          ))}
        </div>
      </main>
      <Footer />
    </>
  );
}

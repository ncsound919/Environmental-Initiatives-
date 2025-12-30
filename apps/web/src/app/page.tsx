'use client';

import Link from 'next/link';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { ProjectCard } from '@/components/ProjectCard';
import { projects, phases } from '@/lib/data';

export default function Home() {
  return (
    <>
      <Header />
      <main>
        {/* Hero Section */}
        <section className="hero">
          <div className="container">
            <h1 className="hero-title">ECOS Ecosystem</h1>
            <p className="hero-subtitle">
              13 interconnected climate-tech businesses sharing unified infrastructure. 
              Building a sustainable future through innovation.
            </p>
            <div className="hero-stats">
              <div className="stat-item">
                <div className="stat-value">13</div>
                <div className="stat-label">Projects</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">$183M</div>
                <div className="stat-label">Year 3 ARR Target</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">41%</div>
                <div className="stat-label">Cost Reduction</div>
              </div>
              <div className="stat-item">
                <div className="stat-value">20%</div>
                <div className="stat-label">Current Readiness</div>
              </div>
            </div>
          </div>
        </section>

        {/* Projects by Phase */}
        <section className="section">
          <div className="container">
            <h2 className="section-title">The RegenCity Ecosystem</h2>
            <p className="section-subtitle">
              Explore our 13 projects organized by deployment phase in the 20-acre compound.
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
        </section>

        {/* CTA Section */}
        <section className="section" style={{ background: '#10b98110', padding: '4rem 0' }}>
          <div className="container" style={{ textAlign: 'center' }}>
            <h2 className="section-title">Ready to Explore?</h2>
            <p className="section-subtitle" style={{ marginBottom: '2rem' }}>
              View the system dashboard for real-time monitoring and analytics.
            </p>
            <Link href="/dashboard" className="btn btn-primary">
              Open Dashboard
            </Link>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

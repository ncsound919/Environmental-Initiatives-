'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { projects } from '@/lib/data';

export default function ProjectDetailPage() {
  const params = useParams();
  const code = params.code as string;
  
  const project = projects.find(p => p.code === code);

  if (!project) {
    return (
      <>
        <Header />
        <main className="section">
          <div className="container">
            <h1 className="section-title">Project Not Found</h1>
            <p className="section-subtitle">The requested project does not exist.</p>
            <Link href="/projects" className="btn btn-primary">
              Back to Projects
            </Link>
          </div>
        </main>
        <Footer />
      </>
    );
  }

  return (
    <>
      <Header />
      <main>
        {/* Hero Section */}
        <section style={{ 
          background: `linear-gradient(135deg, ${project.color}20 0%, ${project.color}10 100%)`,
          padding: '3rem 0'
        }}>
          <div className="container">
            <Link href="/projects" style={{ color: '#6b7280', marginBottom: '1rem', display: 'inline-block' }}>
              ← Back to Projects
            </Link>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
              <div style={{ 
                fontSize: '3rem', 
                width: '80px', 
                height: '80px', 
                borderRadius: '1rem',
                background: `${project.color}30`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                {project.icon}
              </div>
              <div>
                <h1 style={{ fontSize: '2.5rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>
                  {project.name}
                </h1>
                <p style={{ color: '#6b7280', fontSize: '1.125rem' }}>{project.type}</p>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '1.5rem' }}>
              <span className={`project-badge ${project.readiness > 0 ? 'badge-active' : 'badge-reserved'}`} style={{ fontSize: '0.875rem', padding: '0.5rem 1rem' }}>
                {project.readiness}% Ready
              </span>
              <span style={{ 
                background: '#3b82f620', 
                color: '#3b82f6', 
                padding: '0.5rem 1rem', 
                borderRadius: '9999px',
                fontSize: '0.875rem',
                fontWeight: 'bold'
              }}>
                Phase {project.phase}
              </span>
            </div>
          </div>
        </section>

        {/* Project Details */}
        <section className="section">
          <div className="container">
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
              {/* Main Content */}
              <div>
                <div className="dashboard-card" style={{ marginBottom: '1.5rem' }}>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                    Description
                  </h2>
                  <p style={{ lineHeight: '1.75', color: '#374151' }}>
                    {project.description}
                  </p>
                </div>

                <div className="dashboard-card" style={{ marginBottom: '1.5rem' }}>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                    Business Model
                  </h2>
                  <p style={{ lineHeight: '1.75', color: '#374151' }}>
                    {project.businessModel}
                  </p>
                </div>

                <div className="dashboard-card" style={{ marginBottom: '1.5rem' }}>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                    RegenCity Role
                  </h2>
                  <p style={{ lineHeight: '1.75', color: '#374151' }}>
                    {project.regenCityRole}
                  </p>
                </div>

                <div className="dashboard-card">
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                    Features
                  </h2>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {project.features.map((feature, index) => (
                      <span 
                        key={index} 
                        style={{ 
                          background: `${project.color}20`,
                          color: project.color,
                          padding: '0.5rem 1rem',
                          borderRadius: '0.5rem',
                          fontSize: '0.875rem',
                          fontWeight: '500'
                        }}
                      >
                        {feature}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Sidebar */}
              <div>
                <div className="dashboard-card" style={{ marginBottom: '1.5rem' }}>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                    Tech Stack
                  </h2>
                  <ul style={{ listStyle: 'none' }}>
                    {project.techStack.map((tech, index) => (
                      <li 
                        key={index} 
                        style={{ 
                          padding: '0.75rem 0',
                          borderBottom: index < project.techStack.length - 1 ? '1px solid #e5e7eb' : 'none',
                          display: 'flex',
                          alignItems: 'center',
                          gap: '0.5rem'
                        }}
                      >
                        <span style={{ color: project.color }}>•</span>
                        {tech}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="dashboard-card" style={{ marginBottom: '1.5rem' }}>
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                    API Endpoints
                  </h2>
                  {project.apiEndpoints.length > 0 ? (
                    <ul style={{ listStyle: 'none' }}>
                      {project.apiEndpoints.map((endpoint, index) => (
                        <li 
                          key={index} 
                          style={{ 
                            padding: '0.75rem',
                            background: '#f9fafb',
                            borderRadius: '0.375rem',
                            marginBottom: '0.5rem',
                            fontFamily: 'monospace',
                            fontSize: '0.875rem'
                          }}
                        >
                          {endpoint}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p style={{ color: '#6b7280' }}>No API endpoints available yet.</p>
                  )}
                </div>

                <div className="dashboard-card">
                  <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '1rem' }}>
                    Project Info
                  </h2>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#6b7280' }}>Project ID</span>
                      <span style={{ fontWeight: '500' }}>{project.id}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#6b7280' }}>Code</span>
                      <span style={{ fontFamily: 'monospace', fontSize: '0.875rem' }}>{project.code}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#6b7280' }}>Phase</span>
                      <span style={{ fontWeight: '500' }}>{project.phase}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: '#6b7280' }}>Readiness</span>
                      <span style={{ fontWeight: '500', color: project.readiness > 0 ? '#10b981' : '#6b7280' }}>
                        {project.readiness}%
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>
      <Footer />
    </>
  );
}

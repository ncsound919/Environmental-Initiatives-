import type { Project } from '@/lib/data';
import { withOpacity } from '@/lib/utils';
import { Badge } from '@/components/Badge';

interface ProjectCardProps {
  project: Project;
}

export function ProjectCard({ project }: ProjectCardProps) {
  return (
    <div className="card hoverable" style={{ padding: '1.5rem', height: '100%', display: 'flex', flexDirection: 'column', '--accent': project.color } as React.CSSProperties}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
        <div style={{ fontSize: '1.8rem', width: 52, height: 52, borderRadius: 12, background: withOpacity(project.color, 12), display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          {project.icon}
        </div>
        <Badge tone={project.readiness > 0 ? 'emerald' : 'dim'}>
          {project.readiness > 0 ? `${project.readiness}% Ready` : 'Reserved'}
        </Badge>
      </div>
      <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{project.name}</h3>
      <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', margin: '0.15rem 0 0.6rem' }}>{project.type}</div>
      <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem', lineHeight: 1.5, flex: 1 }}>{project.description}</p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginTop: '1rem' }}>
        {project.features.slice(0, 3).map((feature, index) => (
          <span key={index} className="badge badge-dim">{feature}</span>
        ))}
      </div>
    </div>
  );
}
